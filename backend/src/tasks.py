"""
Celery Tasks for Background Processing

Contains long-running tasks that are executed by Celery workers:
- Video processing and frame extraction
- Claude AI analysis of frames
- Playwright replay sessions

NOTE: When ENABLE_BACKGROUND_JOBS=false (default), these tasks run synchronously
using the run_*_sync functions instead of Celery.
"""

import os
import json
import base64
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

import anthropic

from config import settings
from celery_app import celery_app, is_celery_available
from db_config import SessionLocal
from models import (
    InteractionRecordingModel,
    InteractionFrameModel,
    TemporalMetricModel,
)
from video_processor import VideoProcessor, VideoProcessorError
from extraction_prompts import get_extraction_prompt
from interactive_baseline_rules import (
    get_rules_by_category,
    get_temporal_rules,
    get_spatial_rules,
    get_pattern_rules,
)

logger = logging.getLogger(__name__)


def _get_anthropic_client():
    """Get Anthropic client, checking for API key."""
    if not settings.has_anthropic_api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY is not configured. "
            "Video audit requires Claude API for frame analysis. "
            "Get a key at: https://console.anthropic.com/"
        )
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)


# ============================================================================
# SYNCHRONOUS IMPLEMENTATIONS (for when Celery is not available)
# ============================================================================

def process_video_audit_sync(recording_id: int, video_path: str, session_id: int) -> Dict[str, Any]:
    """
    Synchronous video audit processing.

    Used when ENABLE_BACKGROUND_JOBS=false (default).
    Same logic as the Celery task, but runs in the request thread.
    """
    db = SessionLocal()
    client = _get_anthropic_client()

    try:
        logger.info(f"Starting synchronous video audit for recording {recording_id}")

        # Update status to processing
        recording = db.query(InteractionRecordingModel).filter(
            InteractionRecordingModel.id == recording_id
        ).first()

        if not recording:
            logger.error(f"Recording {recording_id} not found")
            return {"error": "Recording not found"}

        recording.status = "processing"
        db.commit()

        # Initialize video processor
        processor = VideoProcessor()

        # Validate and get metadata
        try:
            metadata = processor.validate_video(video_path)
            recording.duration_ms = metadata['duration_ms']
            db.commit()
        except VideoProcessorError as e:
            recording.status = "failed"
            recording.error_message = f"Video validation failed: {str(e)}"
            db.commit()
            return {"error": str(e)}

        # Extract keyframes
        try:
            frames = processor.extract_keyframes(video_path, recording_id)
            recording.frame_count = len(frames)
            db.commit()
            logger.info(f"Extracted {len(frames)} frames from video")
        except VideoProcessorError as e:
            recording.status = "failed"
            recording.error_message = f"Frame extraction failed: {str(e)}"
            db.commit()
            return {"error": str(e)}

        # Process each frame with Claude
        extracted_values = []
        for i, frame_data in enumerate(frames):
            # Create frame record
            frame = InteractionFrameModel(
                recording_id=recording_id,
                frame_number=i,
                timestamp_ms=frame_data['timestamp_ms'],
                frame_path=frame_data['path'],
                extraction_status="pending"
            )
            db.add(frame)
            db.commit()

            # Extract values using Claude
            try:
                values = _extract_values_from_frame(frame_data['path'], client)
                frame.extracted_values = values
                frame.extraction_status = "completed"
                extracted_values.append(values)
                logger.info(f"Processed frame {i+1}/{len(frames)}")
            except Exception as e:
                logger.warning(f"Frame {i} extraction failed: {e}")
                frame.extraction_status = "failed"
                extracted_values.append({})

            db.commit()

        # Calculate temporal metrics
        metrics = []
        if len(extracted_values) > 1:
            metrics = processor.calculate_temporal_metrics(frames, extracted_values)

            # Store metrics
            frame_records = db.query(InteractionFrameModel).filter(
                InteractionFrameModel.recording_id == recording_id
            ).order_by(InteractionFrameModel.frame_number).all()

            for metric in metrics:
                temporal_metric = TemporalMetricModel(
                    recording_id=recording_id,
                    metric_type=metric['metric_type'],
                    start_frame_id=frame_records[metric['start_frame']].id,
                    end_frame_id=frame_records[metric['end_frame']].id,
                    duration_ms=metric['duration_ms'],
                    details=metric.get('details')
                )
                db.add(temporal_metric)

            db.commit()
            logger.info(f"Calculated {len(metrics)} temporal metrics")

        # Mark as completed
        recording.status = "completed"
        recording.completed_at = datetime.utcnow()
        db.commit()

        # Cleanup temp files
        try:
            processor.cleanup(recording_id)
        except Exception as e:
            logger.warning(f"Cleanup failed: {e}")

        logger.info(f"Video audit completed for recording {recording_id}")
        return {
            "recording_id": recording_id,
            "status": "completed",
            "frames_processed": len(frames),
            "metrics_calculated": len(metrics)
        }

    except Exception as e:
        logger.exception(f"Video audit failed for recording {recording_id}: {e}")
        recording = db.query(InteractionRecordingModel).filter(
            InteractionRecordingModel.id == recording_id
        ).first()
        if recording:
            recording.status = "failed"
            recording.error_message = f"Unexpected error: {str(e)}"
            db.commit()
        return {"error": str(e)}

    finally:
        db.close()


def process_playwright_audit_sync(
    recording_id: int,
    target_url: str,
    actions: List[Dict],
    session_id: int
) -> Dict[str, Any]:
    """
    Synchronous Playwright audit processing.

    Used when ENABLE_BACKGROUND_JOBS=false (default).
    """
    db = SessionLocal()

    try:
        logger.info(f"Starting synchronous Playwright audit for recording {recording_id}")

        recording = db.query(InteractionRecordingModel).filter(
            InteractionRecordingModel.id == recording_id
        ).first()

        if not recording:
            logger.error(f"Recording {recording_id} not found")
            return {"error": "Recording not found"}

        recording.status = "processing"
        db.commit()

        # TODO: Implement full Playwright integration
        # For now, create a placeholder frame
        frame = InteractionFrameModel(
            recording_id=recording_id,
            frame_number=0,
            timestamp_ms=0,
            frame_path="placeholder",
            extraction_status="pending"
        )
        db.add(frame)
        db.commit()

        # Mark as completed (placeholder)
        recording.status = "completed"
        recording.completed_at = datetime.utcnow()
        recording.frame_count = 1
        db.commit()

        logger.info(f"Playwright audit completed for recording {recording_id}")
        return {
            "recording_id": recording_id,
            "status": "completed",
            "message": "Playwright audit placeholder completed"
        }

    except Exception as e:
        logger.exception(f"Playwright audit failed for recording {recording_id}: {e}")
        recording = db.query(InteractionRecordingModel).filter(
            InteractionRecordingModel.id == recording_id
        ).first()
        if recording:
            recording.status = "failed"
            recording.error_message = str(e)
            db.commit()
        return {"error": str(e)}

    finally:
        db.close()


def _extract_values_from_frame(frame_path: str, client=None) -> Dict[str, Any]:
    """
    Extract values from a frame using Claude Vision.

    Args:
        frame_path: Path to the frame image
        client: Optional Anthropic client (creates one if not provided)

    Returns:
        Dict of extracted values
    """
    if client is None:
        client = _get_anthropic_client()

    # Read and encode image
    with open(frame_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    # Determine media type
    suffix = Path(frame_path).suffix.lower()
    media_type = "image/png" if suffix == ".png" else "image/jpeg"

    # Call Claude with vision
    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": get_extraction_prompt("full")
                        }
                    ],
                }
            ],
        )

        # Parse response
        response_text = message.content[0].text

        # Clean up JSON if wrapped in code blocks
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        return json.loads(response_text.strip())

    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse Claude response as JSON: {e}")
        return {"extraction_error": "Failed to parse Claude response as JSON"}
    except Exception as e:
        logger.error(f"Claude extraction failed: {e}")
        return {"extraction_error": str(e)}


# ============================================================================
# CELERY TASKS (only defined when Celery is available)
# ============================================================================

if is_celery_available():
    from celery.exceptions import SoftTimeLimitExceeded

    @celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
    def process_video_audit_task(self, recording_id: int, video_path: str, session_id: int):
        """
        Celery task to process a video for UX audit.

        Steps:
        1. Extract keyframes using FFmpeg
        2. Send each frame to Claude for value extraction
        3. Calculate temporal metrics between frames
        4. Store results in database
        """
        try:
            return process_video_audit_sync(recording_id, video_path, session_id)
        except SoftTimeLimitExceeded:
            logger.error(f"Video audit timed out for recording {recording_id}")
            db = SessionLocal()
            try:
                recording = db.query(InteractionRecordingModel).filter(
                    InteractionRecordingModel.id == recording_id
                ).first()
                if recording:
                    recording.status = "failed"
                    recording.error_message = "Task timed out"
                    db.commit()
            finally:
                db.close()
            raise
        except Exception as e:
            if self.request.retries < self.max_retries:
                raise self.retry(exc=e)
            raise

    @celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
    def process_playwright_audit_task(
        self,
        recording_id: int,
        target_url: str,
        actions: List[Dict],
        session_id: int
    ):
        """
        Celery task to process a Playwright replay audit.
        """
        try:
            return process_playwright_audit_sync(recording_id, target_url, actions, session_id)
        except SoftTimeLimitExceeded:
            logger.error(f"Playwright audit timed out for recording {recording_id}")
            db = SessionLocal()
            try:
                recording = db.query(InteractionRecordingModel).filter(
                    InteractionRecordingModel.id == recording_id
                ).first()
                if recording:
                    recording.status = "failed"
                    recording.error_message = "Task timed out"
                    db.commit()
            finally:
                db.close()
            raise
        except Exception as e:
            if self.request.retries < self.max_retries:
                raise self.retry(exc=e)
            raise

    @celery_app.task
    def cleanup_old_recordings_task(days_old: int = 7):
        """
        Periodic task to clean up old recording files.
        """
        db = SessionLocal()
        try:
            from datetime import timedelta
            cutoff = datetime.utcnow() - timedelta(days=days_old)

            old_recordings = db.query(InteractionRecordingModel).filter(
                InteractionRecordingModel.created_at < cutoff,
                InteractionRecordingModel.status.in_(["completed", "failed"])
            ).all()

            processor = VideoProcessor()
            for recording in old_recordings:
                try:
                    processor.cleanup(recording.id)
                    logger.info(f"Cleaned up recording {recording.id}")
                except Exception as e:
                    logger.warning(f"Failed to cleanup recording {recording.id}: {e}")

            return {"cleaned_up": len(old_recordings)}

        finally:
            db.close()

    @celery_app.task
    def health_check_task():
        """Simple health check task to verify Celery is working."""
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat()
        }

else:
    # Provide stub functions when Celery is not available
    # These should not be called directly - use the sync versions instead
    def process_video_audit_task(*args, **kwargs):
        raise RuntimeError("Celery is not configured. Use process_video_audit_sync instead.")

    def process_playwright_audit_task(*args, **kwargs):
        raise RuntimeError("Celery is not configured. Use process_playwright_audit_sync instead.")

    def cleanup_old_recordings_task(*args, **kwargs):
        raise RuntimeError("Celery is not configured.")

    def health_check_task(*args, **kwargs):
        raise RuntimeError("Celery is not configured.")


# Alias for backward compatibility
extract_values_from_frame_sync = _extract_values_from_frame
