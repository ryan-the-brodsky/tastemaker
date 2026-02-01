"""
Skill package generation and download routes.
"""
import os
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from db_config import get_db
from models import (
    UserModel, ExtractionSessionModel, StyleRuleModel, GeneratedSkillModel,
    SkillGenerateResponse
)
from auth_routes import get_current_user
from skill_packager import generate_skill_package, get_skill_preview

router = APIRouter(tags=["skills"])


@router.post("/api/sessions/{session_id}/generate-skill", response_model=SkillGenerateResponse)
def generate_skill(
    session_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a skill package for the session."""
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

    # Get rules
    rules = (
        db.query(StyleRuleModel)
        .filter(StyleRuleModel.session_id == session_id)
        .all()
    )

    rules_dicts = [
        {
            "rule_id": r.rule_id,
            "component_type": r.component_type,
            "property": r.property,
            "operator": r.operator,
            "value": r.value,
            "severity": r.severity,
            "confidence": r.confidence,
            "source": r.source,
            "message": r.message,
        }
        for r in rules
    ]

    # Try to generate mockups before packaging
    try:
        from mockup_generator import generate_mockup_pngs_sync
        generate_mockup_pngs_sync(session_id)
    except Exception as e:
        print(f"Note: Could not generate mockups: {e}")

    # Generate the package
    username = f"{current_user.first_name}_{current_user.last_name}".lower()
    zip_path = generate_skill_package(
        session_name=session.name,
        username=username,
        rules=rules_dicts,
        include_baseline=True,
        session_id=session_id
    )

    # Create skill record
    skill = GeneratedSkillModel(
        session_id=session_id,
        skill_name=f"tastemaker-{username}",
        file_path=zip_path,
    )
    db.add(skill)

    # Mark session as complete
    session.phase = "complete"
    session.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(skill)

    # Get preview
    preview = get_skill_preview(rules_dicts)

    return SkillGenerateResponse(
        skill_id=skill.id,
        download_url=f"/api/skills/{skill.id}/download",
        preview=preview
    )


@router.get("/api/skills/{skill_id}/download")
def download_skill(
    skill_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download a generated skill package."""
    # Get skill
    skill = (
        db.query(GeneratedSkillModel)
        .join(ExtractionSessionModel)
        .filter(
            GeneratedSkillModel.id == skill_id,
            ExtractionSessionModel.user_id == current_user.id
        )
        .first()
    )

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )

    if not skill.file_path or not os.path.exists(skill.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill file not found"
        )

    return FileResponse(
        path=skill.file_path,
        filename=f"{skill.skill_name}.zip",
        media_type="application/zip"
    )
