"""
Component Studio API routes.

Provides endpoints for the systematic component customization flow.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db_config import get_db
from models import (
    UserModel,
    ExtractionSessionModel,
    ComponentDimensionsResponse,
    DimensionDefinition,
    DimensionOption,
    FineTuneConfig,
    DimensionChoiceSubmit,
    ComponentStateResponse,
    StudioProgressResponse,
    CheckpointData,
    LockComponentResponse,
)
from auth_routes import get_current_user
from component_dimensions import (
    COMPONENT_TYPES,
    get_dimensions_for_component,
    get_component_label,
)
import component_studio_service as service

router = APIRouter(prefix="/api/sessions/{session_id}/studio", tags=["component_studio"])


def _get_session(session_id: int, user: UserModel, db: Session) -> ExtractionSessionModel:
    """Helper to fetch and validate a session."""
    session = (
        db.query(ExtractionSessionModel)
        .filter(
            ExtractionSessionModel.id == session_id,
            ExtractionSessionModel.user_id == user.id,
        )
        .first()
    )
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
    return session


@router.get("/progress", response_model=StudioProgressResponse)
def get_studio_progress(
    session_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the current studio progress state."""
    session = _get_session(session_id, current_user, db)
    return service.get_studio_progress(session)


@router.get("/component/{component_type}/dimensions", response_model=ComponentDimensionsResponse)
def get_component_dimensions(
    session_id: int,
    component_type: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get dimension definitions for a component type."""
    _get_session(session_id, current_user, db)

    if component_type not in COMPONENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown component type: {component_type}",
        )

    raw_dimensions = get_dimensions_for_component(component_type)
    dimensions = []
    for d in raw_dimensions:
        fine_tune = None
        if "fine_tune" in d and d["fine_tune"]:
            fine_tune = FineTuneConfig(**d["fine_tune"])

        options = [DimensionOption(**opt) for opt in d["options"]]
        dimensions.append(
            DimensionDefinition(
                key=d["key"],
                label=d["label"],
                css_property=d["css_property"],
                options=options,
                fine_tune=fine_tune,
                order=d["order"],
            )
        )

    return ComponentDimensionsResponse(
        component_type=component_type,
        component_label=get_component_label(component_type),
        dimensions=dimensions,
    )


@router.get("/component/{component_type}/state", response_model=ComponentStateResponse)
def get_component_state(
    session_id: int,
    component_type: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current choices for a component."""
    session = _get_session(session_id, current_user, db)

    if component_type not in COMPONENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown component type: {component_type}",
        )

    return service.get_component_state(session, component_type, db)


@router.post("/component/{component_type}/dimension")
def submit_dimension_choice(
    session_id: int,
    component_type: str,
    choice: DimensionChoiceSubmit,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit a dimension choice for a component."""
    session = _get_session(session_id, current_user, db)

    if component_type not in COMPONENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown component type: {component_type}",
        )

    result = service.submit_dimension_choice(
        session=session,
        component_type=component_type,
        dimension=choice.dimension,
        selected_option_id=choice.selected_option_id,
        selected_value=choice.selected_value,
        css_property=choice.css_property,
        db=db,
        fine_tuned_value=choice.fine_tuned_value,
    )
    db.commit()
    return result


@router.post("/component/lock", response_model=LockComponentResponse)
def lock_component(
    session_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lock the current component and advance to the next."""
    session = _get_session(session_id, current_user, db)
    progress = service.get_studio_progress(session)

    if not progress.current_component:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No current component to lock",
        )

    result = service.lock_component(session, progress.current_component, db)
    return LockComponentResponse(**result)


@router.get("/checkpoint/{checkpoint_id}", response_model=CheckpointData)
def get_checkpoint(
    session_id: int,
    checkpoint_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get checkpoint data for a mockup review."""
    session = _get_session(session_id, current_user, db)
    data = service.get_checkpoint_data(session, checkpoint_id, db)

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Checkpoint not found: {checkpoint_id}",
        )

    return data


@router.post("/checkpoint/{checkpoint_id}/approve")
def approve_checkpoint(
    session_id: int,
    checkpoint_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Approve a checkpoint and advance to the next component group."""
    session = _get_session(session_id, current_user, db)
    result = service.approve_checkpoint(session, checkpoint_id, db)

    # If studio is complete, transition to stated_preferences phase
    if result.get("is_studio_complete"):
        session.phase = "stated_preferences"
        db.commit()

    return result


@router.post("/component/{component_type}/go-back")
def go_back_to_component(
    session_id: int,
    component_type: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Navigate back to a previously completed component for editing."""
    session = _get_session(session_id, current_user, db)

    if component_type not in COMPONENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown component type: {component_type}",
        )

    return service.go_back_to_component(session, component_type, db)


@router.get("/preview-styles")
def get_preview_styles(
    session_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all accumulated component styles for live preview."""
    session = _get_session(session_id, current_user, db)
    return service.get_all_preview_styles(session, db)
