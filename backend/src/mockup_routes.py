"""
Mockup generation routes.
Handles PNG generation for mockups and public style data endpoint.
"""
import json
import os
import tempfile
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from db_config import get_db
from models import UserModel, ExtractionSessionModel
from auth_routes import get_current_user

router = APIRouter(tags=["mockups"])


class PublicStyleResponse(BaseModel):
    chosen_colors: Optional[dict] = None
    chosen_typography: Optional[dict] = None


class MockupGenerationResponse(BaseModel):
    success: bool
    mockups: list[str]
    message: str


@router.get("/api/sessions/{session_id}/public-style", response_model=PublicStyleResponse)
async def get_public_style(
    session_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get style data for a session.
    Used by MockupRender component to apply styles.
    """
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

    chosen_colors = None
    chosen_typography = None

    if session.chosen_colors:
        chosen_colors = json.loads(session.chosen_colors) if isinstance(session.chosen_colors, str) else session.chosen_colors

    if session.chosen_typography:
        chosen_typography = json.loads(session.chosen_typography) if isinstance(session.chosen_typography, str) else session.chosen_typography

    return PublicStyleResponse(
        chosen_colors=chosen_colors,
        chosen_typography=chosen_typography
    )


@router.post("/api/sessions/{session_id}/generate-mockup-pngs", response_model=MockupGenerationResponse)
async def generate_mockup_pngs_endpoint(
    session_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate PNG mockups for a session using Playwright.
    This endpoint is called before skill package generation to create mockup images.
    """
    from mockup_generator import generate_mockup_pngs_sync, MOCKUP_TYPES

    # Verify session ownership
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

    # Try to generate mockups with Playwright
    try:
        result = generate_mockup_pngs_sync(session_id)

        if result.get("success"):
            return MockupGenerationResponse(
                success=True,
                mockups=list(result.get("mockups", {}).keys()),
                message=f"Generated {len(result.get('mockups', {}))} mockup PNGs"
            )
        else:
            # Playwright not available or failed, return placeholder response
            return MockupGenerationResponse(
                success=False,
                mockups=MOCKUP_TYPES,
                message=result.get("error", "Mockup generation failed. Playwright may not be installed.")
            )
    except Exception as e:
        return MockupGenerationResponse(
            success=False,
            mockups=MOCKUP_TYPES,
            message=f"Mockup generation error: {str(e)}"
        )


@router.post("/api/sessions/{session_id}/upload-mockup")
async def upload_mockup(
    session_id: str,
    mockup_type: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a mockup PNG for a session.
    Called after client-side capture with html2canvas.
    """
    # Verify session ownership
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

    valid_types = ['landing', 'dashboard', 'form', 'settings']
    if mockup_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid mockup type. Must be one of: {valid_types}"
        )

    # Create mockups directory for this session
    mockups_dir = os.path.join(tempfile.gettempdir(), f"tastemaker-mockups-{session_id}")
    os.makedirs(mockups_dir, exist_ok=True)

    return JSONResponse({
        "success": True,
        "upload_path": os.path.join(mockups_dir, f"{mockup_type}.png"),
        "message": f"Ready to receive {mockup_type} mockup"
    })
