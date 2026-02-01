"""
Extraction session management routes.
"""
import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db_config import get_db
from models import (
    UserModel, ExtractionSessionModel, ComparisonResultModel, StyleRuleModel,
    SessionCreate, SessionResponse, SessionDetailResponse,
    ComparisonResultResponse, StyleRuleResponse
)
from auth_routes import get_current_user

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    session_data: SessionCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new extraction session."""
    session = ExtractionSessionModel(
        user_id=current_user.id,
        name=session_data.name,
        brand_colors=json.dumps(session_data.brand_colors) if session_data.brand_colors else None,
        project_description=session_data.project_description,
        phase="color_exploration",
        comparison_count=0,
        confidence_score=0.0,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return SessionResponse(
        id=session.id,
        name=session.name,
        phase=session.phase,
        brand_colors=session.brand_colors,
        project_description=session.project_description,
        comparison_count=session.comparison_count,
        confidence_score=session.confidence_score,
        established_preferences=None,  # New session has no preferences yet
        chosen_colors=None,  # New session has no colors yet
        chosen_typography=None,  # New session has no typography yet
        created_at=session.created_at,
        updated_at=session.updated_at,
        completed_at=session.completed_at,
    )


@router.get("", response_model=List[SessionResponse])
def list_sessions(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all sessions for the current user."""
    sessions = (
        db.query(ExtractionSessionModel)
        .filter(ExtractionSessionModel.user_id == current_user.id)
        .order_by(ExtractionSessionModel.updated_at.desc().nullsfirst())
        .order_by(ExtractionSessionModel.created_at.desc())
        .all()
    )

    return [
        SessionResponse(
            id=s.id,
            name=s.name,
            phase=s.phase,
            brand_colors=s.brand_colors,
            project_description=s.project_description,
            comparison_count=s.comparison_count,
            confidence_score=s.confidence_score,
            established_preferences=json.loads(s.established_preferences) if s.established_preferences else None,
            chosen_colors=json.loads(s.chosen_colors) if s.chosen_colors else None,
            chosen_typography=json.loads(s.chosen_typography) if s.chosen_typography else None,
            created_at=s.created_at,
            updated_at=s.updated_at,
            completed_at=s.completed_at,
        )
        for s in sessions
    ]


@router.get("/{session_id}", response_model=SessionDetailResponse)
def get_session(
    session_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get details of a specific session."""
    session = (
        db.query(ExtractionSessionModel)
        .filter(
            ExtractionSessionModel.id == session_id,
            ExtractionSessionModel.user_id == current_user.id
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Get comparisons
    comparisons = (
        db.query(ComparisonResultModel)
        .filter(ComparisonResultModel.session_id == session_id)
        .order_by(ComparisonResultModel.created_at)
        .all()
    )

    # Get rules
    rules = (
        db.query(StyleRuleModel)
        .filter(StyleRuleModel.session_id == session_id)
        .order_by(StyleRuleModel.created_at)
        .all()
    )

    return SessionDetailResponse(
        id=session.id,
        name=session.name,
        phase=session.phase,
        brand_colors=session.brand_colors,
        project_description=session.project_description,
        comparison_count=session.comparison_count,
        confidence_score=session.confidence_score,
        established_preferences=json.loads(session.established_preferences) if session.established_preferences else None,
        chosen_colors=json.loads(session.chosen_colors) if session.chosen_colors else None,
        chosen_typography=json.loads(session.chosen_typography) if session.chosen_typography else None,
        created_at=session.created_at,
        updated_at=session.updated_at,
        completed_at=session.completed_at,
        comparisons=[
            ComparisonResultResponse(
                id=c.id,
                comparison_id=c.comparison_id,
                component_type=c.component_type,
                phase=c.phase,
                choice=c.choice,
                decision_time_ms=c.decision_time_ms,
                created_at=c.created_at,
            )
            for c in comparisons
        ],
        rules=[
            StyleRuleResponse(
                id=r.id,
                rule_id=r.rule_id,
                component_type=r.component_type,
                property=r.property,
                operator=r.operator,
                value=r.value,
                severity=r.severity,
                confidence=r.confidence,
                source=r.source,
                message=r.message,
                is_modified=r.is_modified,
                created_at=r.created_at,
            )
            for r in rules
        ],
    )


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a session."""
    session = (
        db.query(ExtractionSessionModel)
        .filter(
            ExtractionSessionModel.id == session_id,
            ExtractionSessionModel.user_id == current_user.id
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    db.delete(session)
    db.commit()
    return None
