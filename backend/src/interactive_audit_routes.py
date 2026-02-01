"""
Interactive Audit Routes - Video and Replay Analysis

API endpoints for auditing UX through:
1. User-uploaded video files
2. Playwright replay scripts

Processing mode depends on ENABLE_BACKGROUND_JOBS setting:
- When false (default): Processing runs synchronously (slower but simpler)
- When true: Processing dispatched to Celery workers (faster, requires Redis)
"""

import os
import json
import tempfile
from typing import List, Dict, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import threading

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session

from config import settings
from db_config import get_db
from models import (
    UserModel,
    ExtractionSessionModel,
    InteractionRecordingModel,
    InteractionFrameModel,
    TemporalMetricModel,
    InteractionRecordingResponse,
    InteractiveAuditResult,
)
from auth_routes import get_current_user
from video_processor import check_ffmpeg_installed
from interactive_baseline_rules import (
    INTERACTIVE_BASELINE_RULES,
    get_rules_by_category,
    get_temporal_rules,
    get_spatial_rules,
    get_pattern_rules,
)
from celery_app import is_celery_available
from tasks import (
    process_video_audit_sync,
    process_playwright_audit_sync,
)

# Only import Celery tasks if available
if is_celery_available():
    from tasks import process_video_audit_task, process_playwright_audit_task

# Thread pool for sync background processing
_executor = ThreadPoolExecutor(max_workers=2)


router = APIRouter(prefix="/api/audit/interactive", tags=["interactive-audit"])

# Upload configuration
MAX_VIDEO_SIZE_MB = 100
ALLOWED_VIDEO_TYPES = {
    "video/mp4",
    "video/webm",
    "video/quicktime",
    "video/x-msvideo",
}


@router.get("/check-ffmpeg")
async def check_ffmpeg():
    """Check if FFmpeg is installed for video processing."""
    available = check_ffmpeg_installed()
    return {
        "ffmpeg_available": available,
        "message": "FFmpeg is installed" if available else "FFmpeg is not installed. Video auditing requires FFmpeg."
    }


@router.post("/video", response_model=InteractionRecordingResponse)
async def audit_video(
    session_id: int = Form(...),
    video: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Start a video-based UX audit.

    Accepts a video file, extracts keyframes, and queues analysis via Celery.
    Returns immediately with recording ID - use GET /recording/{id} to check progress.

    Args:
        session_id: The extraction session to audit against
        video: Video file (mp4, webm, mov, avi)

    Returns:
        Recording metadata with status "pending"
    """
    # Validate session access
    session = db.query(ExtractionSessionModel).filter(
        ExtractionSessionModel.id == session_id,
        ExtractionSessionModel.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Validate video file
    if video.content_type not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid video type. Allowed: {', '.join(ALLOWED_VIDEO_TYPES)}"
        )

    # Check file size
    video.file.seek(0, 2)  # Seek to end
    file_size = video.file.tell()
    video.file.seek(0)  # Reset to beginning

    if file_size > MAX_VIDEO_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"Video too large. Maximum size: {MAX_VIDEO_SIZE_MB}MB"
        )

    # Check FFmpeg availability
    if not check_ffmpeg_installed():
        raise HTTPException(
            status_code=503,
            detail="Video processing requires FFmpeg, which is not installed"
        )

    # Save video to temp file
    temp_dir = tempfile.mkdtemp(prefix="tastemaker_video_")
    video_path = os.path.join(temp_dir, video.filename or "upload.mp4")

    with open(video_path, "wb") as f:
        content = await video.read()
        f.write(content)

    # Create recording entry
    recording = InteractionRecordingModel(
        session_id=session_id,
        source_type="video",
        source_path=video_path,
        status="pending"
    )
    db.add(recording)
    db.commit()
    db.refresh(recording)

    # Dispatch processing based on configuration
    if is_celery_available():
        # Background processing via Celery
        process_video_audit_task.delay(
            recording.id,
            video_path,
            session_id
        )
    else:
        # Synchronous processing in background thread
        # This allows the endpoint to return immediately while processing continues
        _executor.submit(
            process_video_audit_sync,
            recording.id,
            video_path,
            session_id
        )

    return recording


@router.post("/replay")
async def audit_replay(
    session_id: int = Form(...),
    target_url: str = Form(...),
    actions: str = Form(default="[]"),  # JSON array of actions
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Start a Playwright replay-based UX audit.

    Executes a series of actions on a URL, capturing screenshots at each step.
    Processing is dispatched to a Celery worker.

    Args:
        session_id: The extraction session to audit against
        target_url: URL to navigate to
        actions: JSON array of Playwright actions (optional)
                 Format: [{"action": "click", "selector": "#btn"}, ...]

    Returns:
        Recording metadata with status "pending"
    """
    # Validate session access
    session = db.query(ExtractionSessionModel).filter(
        ExtractionSessionModel.id == session_id,
        ExtractionSessionModel.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Parse actions
    try:
        action_list = json.loads(actions)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid actions JSON")

    # Create recording entry
    recording = InteractionRecordingModel(
        session_id=session_id,
        source_type="playwright",
        source_path=target_url,
        status="pending"
    )
    db.add(recording)
    db.commit()
    db.refresh(recording)

    # Dispatch processing based on configuration
    if is_celery_available():
        # Background processing via Celery
        process_playwright_audit_task.delay(
            recording.id,
            target_url,
            action_list,
            session_id
        )
    else:
        # Synchronous processing in background thread
        _executor.submit(
            process_playwright_audit_sync,
            recording.id,
            target_url,
            action_list,
            session_id
        )

    return {
        "id": recording.id,
        "session_id": session_id,
        "source_type": "playwright",
        "status": "pending",
        "message": "Playwright audit queued. Use GET /recording/{id} to check progress."
    }


@router.get("/recording/{recording_id}")
async def get_recording_status(
    recording_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get the status of a recording and its analysis results."""
    recording = db.query(InteractionRecordingModel).filter(
        InteractionRecordingModel.id == recording_id
    ).first()

    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    # Verify access through session
    session = db.query(ExtractionSessionModel).filter(
        ExtractionSessionModel.id == recording.session_id,
        ExtractionSessionModel.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=403, detail="Access denied")

    # Get frame count
    frame_count = db.query(InteractionFrameModel).filter(
        InteractionFrameModel.recording_id == recording_id
    ).count()

    # Get temporal metrics if completed
    temporal_metrics = []
    if recording.status == "completed":
        metrics = db.query(TemporalMetricModel).filter(
            TemporalMetricModel.recording_id == recording_id
        ).all()
        temporal_metrics = [
            {
                "metric_type": m.metric_type,
                "duration_ms": m.duration_ms,
                "details": m.details
            }
            for m in metrics
        ]

    return {
        "id": recording.id,
        "session_id": recording.session_id,
        "source_type": recording.source_type,
        "status": recording.status,
        "error_message": recording.error_message,
        "frame_count": frame_count,
        "duration_ms": recording.duration_ms,
        "created_at": recording.created_at,
        "completed_at": recording.completed_at,
        "temporal_metrics": temporal_metrics
    }


@router.get("/recording/{recording_id}/results")
async def get_audit_results(
    recording_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get the full audit results for a completed recording."""
    recording = db.query(InteractionRecordingModel).filter(
        InteractionRecordingModel.id == recording_id
    ).first()

    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    # Verify access
    session = db.query(ExtractionSessionModel).filter(
        ExtractionSessionModel.id == recording.session_id,
        ExtractionSessionModel.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=403, detail="Access denied")

    if recording.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Recording not completed. Status: {recording.status}"
        )

    # Get all frames with extracted values
    frames = db.query(InteractionFrameModel).filter(
        InteractionFrameModel.recording_id == recording_id
    ).order_by(InteractionFrameModel.frame_number).all()

    # Get temporal metrics
    temporal_metrics = db.query(TemporalMetricModel).filter(
        TemporalMetricModel.recording_id == recording_id
    ).all()

    # Apply rules to extracted values
    violations = apply_interactive_rules(
        [f.extracted_values for f in frames if f.extracted_values],
        [
            {
                "metric_type": m.metric_type,
                "duration_ms": m.duration_ms,
                "details": m.details,
                "start_frame": m.start_frame_id,
                "end_frame": m.end_frame_id
            }
            for m in temporal_metrics
        ]
    )

    return {
        "recording_id": recording_id,
        "total_frames": len(frames),
        "duration_ms": recording.duration_ms,
        "temporal_violations": violations.get("temporal", []),
        "spatial_violations": violations.get("spatial", []),
        "behavioral_violations": violations.get("behavioral", []),
        "pattern_violations": violations.get("pattern", []),
        "summary": {
            "total_violations": sum(len(v) for v in violations.values()),
            "errors": sum(1 for cat in violations.values() for v in cat if v.get("severity") == "error"),
            "warnings": sum(1 for cat in violations.values() for v in cat if v.get("severity") == "warning"),
            "temporal_metrics_count": len(temporal_metrics),
            "frames_analyzed": len([f for f in frames if f.extracted_values])
        }
    }


# ============================================================================
# RULE APPLICATION FUNCTIONS
# ============================================================================

def apply_interactive_rules(
    extracted_values_list: List[Dict],
    temporal_metrics: List[Dict]
) -> Dict[str, List[Dict]]:
    """
    Apply interactive UX rules to extracted values.

    Args:
        extracted_values_list: List of extracted values from each frame
        temporal_metrics: List of calculated temporal metrics

    Returns:
        Dict of violations grouped by category
    """
    violations = {
        "temporal": [],
        "spatial": [],
        "behavioral": [],
        "pattern": []
    }

    # Check temporal rules against metrics
    temporal_rules = get_temporal_rules()
    for metric in temporal_metrics:
        for rule in temporal_rules:
            if metric['metric_type'] == rule.get('property'):
                constraint = rule.get('timing_constraint_ms')
                if constraint and metric['duration_ms'] > constraint:
                    violations["temporal"].append({
                        "rule_id": rule['rule_id'],
                        "severity": rule['severity'],
                        "message": rule['message'],
                        "measured_value": metric['duration_ms'],
                        "threshold": constraint,
                        "metric_type": metric['metric_type']
                    })

    # Check spatial rules against latest frame
    if extracted_values_list:
        latest_values = extracted_values_list[-1]
        spatial_rules = get_spatial_rules()

        for rule in spatial_rules:
            violation = check_spatial_rule(rule, latest_values)
            if violation:
                violations["spatial"].append(violation)

    # Check pattern rules for dark patterns
    if extracted_values_list:
        latest_values = extracted_values_list[-1]
        pattern_rules = get_pattern_rules()

        for rule in pattern_rules:
            violation = check_pattern_rule(rule, latest_values)
            if violation:
                violations["pattern"].append(violation)

    # Check behavioral rules
    for rule in get_rules_by_category("BEHAVIORAL"):
        for values in extracted_values_list:
            violation = check_behavioral_rule(rule, values)
            if violation and violation not in violations["behavioral"]:
                violations["behavioral"].append(violation)

    return violations


def check_spatial_rule(rule: Dict, values: Dict) -> Optional[Dict]:
    """Check a spatial rule against extracted values."""
    spatial_data = values.get("spatial", {})
    prop = rule.get("property")

    # Handle touch target size
    if prop == "cta_touch_target_size":
        targets = spatial_data.get("touch_targets", [])
        for target in targets:
            if target.get("is_primary_cta"):
                min_dim = min(target.get("width_px", 0), target.get("height_px", 0))
                threshold = int(rule.get("value", 44))
                if min_dim < threshold:
                    return {
                        "rule_id": rule["rule_id"],
                        "severity": rule["severity"],
                        "message": rule["message"],
                        "measured_value": min_dim,
                        "threshold": threshold
                    }

    # Handle button spacing
    if prop == "button_spacing":
        spacing = spatial_data.get("button_spacing_min_px")
        if spacing is not None:
            threshold = int(rule.get("value", 8))
            if spacing < threshold:
                return {
                    "rule_id": rule["rule_id"],
                    "severity": rule["severity"],
                    "message": rule["message"],
                    "measured_value": spacing,
                    "threshold": threshold
                }

    return None


def check_pattern_rule(rule: Dict, values: Dict) -> Optional[Dict]:
    """Check a dark pattern rule against extracted values."""
    dark_pattern_data = values.get("dark_patterns", {})
    prop = rule.get("property")

    # Check for shame language
    if prop == "decline_button_shame_language":
        if dark_pattern_data.get("has_shame_language"):
            return {
                "rule_id": rule["rule_id"],
                "severity": rule["severity"],
                "message": rule["message"],
                "indicators_found": dark_pattern_data.get("shame_indicators", [])
            }

    # Check for preselected options
    if prop == "has_preselected_addons":
        if dark_pattern_data.get("has_preselected_checkboxes"):
            return {
                "rule_id": rule["rule_id"],
                "severity": rule["severity"],
                "message": rule["message"],
                "preselected_items": dark_pattern_data.get("preselected_checkbox_labels", [])
            }

    # Check for fake urgency
    if prop == "has_fake_countdown":
        if dark_pattern_data.get("has_fake_urgency"):
            return {
                "rule_id": rule["rule_id"],
                "severity": rule["severity"],
                "message": rule["message"],
                "urgency_text": dark_pattern_data.get("urgency_text")
            }

    return None


def check_behavioral_rule(rule: Dict, values: Dict) -> Optional[Dict]:
    """Check a behavioral rule against extracted values."""
    counts = values.get("counts", {})
    states = values.get("states", {})
    prop = rule.get("property")

    # Check count-based rules (Hick's/Miller's)
    count_prop = rule.get("count_property")
    if count_prop and count_prop in counts:
        actual = counts[count_prop]
        threshold = int(rule.get("value", 0))
        operator = rule.get("operator", "<=")

        violated = False
        if operator == "<=" and actual > threshold:
            violated = True
        elif operator == "<" and actual >= threshold:
            violated = True

        if violated:
            return {
                "rule_id": rule["rule_id"],
                "severity": rule["severity"],
                "message": rule["message"],
                "measured_value": actual,
                "threshold": threshold
            }

    # Check boolean state rules
    if prop in states:
        actual = states[prop]
        expected = rule.get("value")

        if isinstance(expected, str):
            expected = expected.lower() == "true"

        if actual != expected:
            return {
                "rule_id": rule["rule_id"],
                "severity": rule["severity"],
                "message": rule["message"],
                "actual_value": actual,
                "expected_value": expected
            }

    return None
