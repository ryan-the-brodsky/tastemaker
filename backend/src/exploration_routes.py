"""
Exploration routes for trie-style color and typography discovery.

Provides endpoints for:
- Getting 5 color/typography options at a time
- Submitting selections and getting refined options
- Locking in final choices
"""
import json
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from db_config import get_db
from models import UserModel, ExtractionSessionModel
from auth_routes import get_current_user

try:
    from exploration_service import get_exploration_service
    EXPLORATION_SERVICE_AVAILABLE = True
except Exception as e:
    print(f"Warning: Exploration service not available: {e}")
    EXPLORATION_SERVICE_AVAILABLE = False

router = APIRouter(prefix="/api/sessions", tags=["exploration"])


# ============================================================================
# Request/Response Models
# ============================================================================

class ColorOption(BaseModel):
    """A single color option."""
    hex: str
    name: str
    family: Optional[str] = None
    description: Optional[str] = None


class PaletteOption(BaseModel):
    """A complete color palette option."""
    id: str
    name: str
    category: str
    primary: str
    secondary: str
    accent: str
    accentSoft: str
    background: str
    description: Optional[str] = None


class TypographyOption(BaseModel):
    """A typography pairing option."""
    id: str
    name: str
    category: str
    heading: str
    body: str
    headingCategory: Optional[str] = None
    bodyCategory: Optional[str] = None
    description: Optional[str] = None


class ExplorationResponse(BaseModel):
    """Response containing exploration options."""
    options: List[dict]
    context: Optional[str] = None
    exploration_depth: int = 0
    exploration_type: str  # "palette" or "typography"
    can_lock_in: bool = True  # User can lock in at any point


class ExplorationSelection(BaseModel):
    """User's selection from exploration options."""
    selected_option_id: str
    selected_option: dict  # Full option data for storage
    wants_refinement: bool = True  # False = lock in this selection


class ExplorationProgressResponse(BaseModel):
    """Response after making a selection."""
    success: bool
    exploration_depth: int
    next_options: Optional[List[dict]] = None
    locked_in: bool = False
    new_phase: Optional[str] = None
    message: str


# ============================================================================
# Color Palette Exploration
# ============================================================================

@router.get("/{session_id}/explore/palettes", response_model=ExplorationResponse)
def get_palette_options(
    session_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get 5 color palette options for exploration.

    Uses Claude API to generate contextually relevant palettes based on
    the project description and any previous selections.
    """
    session = _get_session_or_404(session_id, current_user.id, db)

    # Verify we're in color exploration phase
    if session.phase != "color_exploration":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Not in color exploration phase. Current phase: {session.phase}"
        )

    # Get exploration state
    exploration_state = _get_exploration_state(session, "color")

    if not EXPLORATION_SERVICE_AVAILABLE:
        return _get_fallback_palette_response(exploration_state["depth"])

    try:
        service = get_exploration_service()
        result = service.generate_full_palette_options(
            project_description=session.project_description,
            exploration_depth=exploration_state["depth"],
            previous_selection=exploration_state.get("last_selection")
        )

        return ExplorationResponse(
            options=result["options"],
            context=result.get("context"),
            exploration_depth=result["exploration_depth"],
            exploration_type="palette",
            can_lock_in=True
        )
    except Exception as e:
        print(f"Error generating palette options: {e}")
        return _get_fallback_palette_response(exploration_state["depth"])


@router.post("/{session_id}/explore/palettes/select", response_model=ExplorationProgressResponse)
def select_palette(
    session_id: int,
    selection: ExplorationSelection,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a palette selection.

    If wants_refinement=True, generates 5 refined options within the selected family.
    If wants_refinement=False, locks in the selection and moves to typography.
    """
    session = _get_session_or_404(session_id, current_user.id, db)

    if session.phase != "color_exploration":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Not in color exploration phase. Current phase: {session.phase}"
        )

    # Update exploration state
    exploration_state = _get_exploration_state(session, "color")
    exploration_state["depth"] += 1
    exploration_state["history"] = exploration_state.get("history", [])
    exploration_state["history"].append(selection.selected_option.get("name", selection.selected_option_id))
    exploration_state["last_selection"] = selection.selected_option
    _save_exploration_state(session, "color", exploration_state, db)

    # Lock in if requested or max depth reached
    max_depth = 3
    if not selection.wants_refinement or exploration_state["depth"] >= max_depth:
        # Lock in the selection
        session.chosen_colors = json.dumps(selection.selected_option)
        session.phase = "typography_exploration"

        # Reset exploration state for typography
        _save_exploration_state(session, "typography", {"depth": 0, "history": []}, db)

        db.commit()

        return ExplorationProgressResponse(
            success=True,
            exploration_depth=exploration_state["depth"],
            locked_in=True,
            new_phase="typography_exploration",
            message=f"Color palette '{selection.selected_option.get('name', 'selected')}' locked in! Moving to typography exploration."
        )

    # Generate refined options
    if not EXPLORATION_SERVICE_AVAILABLE:
        return _get_fallback_refinement_response(exploration_state["depth"], "palette")

    try:
        service = get_exploration_service()
        result = service.generate_full_palette_options(
            project_description=session.project_description,
            exploration_depth=exploration_state["depth"],
            previous_selection=selection.selected_option
        )

        db.commit()

        # Prepend the original selection so user can still choose it
        # Mark it as the "original" so frontend can highlight it
        original_option = selection.selected_option.copy()
        original_option["is_original"] = True
        all_options = [original_option] + result["options"]

        return ExplorationProgressResponse(
            success=True,
            exploration_depth=exploration_state["depth"],
            next_options=all_options,
            locked_in=False,
            message=f"Showing similar options to '{selection.selected_option.get('name', 'selected')}'. Your original is included - choose a variation or lock in."
        )
    except Exception as e:
        print(f"Error generating refined palettes: {e}")
        db.commit()
        return _get_fallback_refinement_response(exploration_state["depth"], "palette")


# ============================================================================
# Typography Exploration
# ============================================================================

@router.get("/{session_id}/explore/typography", response_model=ExplorationResponse)
def get_typography_options(
    session_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get 5 typography pairing options for exploration.
    """
    session = _get_session_or_404(session_id, current_user.id, db)

    if session.phase != "typography_exploration":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Not in typography exploration phase. Current phase: {session.phase}"
        )

    exploration_state = _get_exploration_state(session, "typography")

    if not EXPLORATION_SERVICE_AVAILABLE:
        return _get_fallback_typography_response(exploration_state["depth"])

    try:
        service = get_exploration_service()
        result = service.generate_full_typography_options(
            project_description=session.project_description,
            exploration_depth=exploration_state["depth"],
            previous_selection=exploration_state.get("last_selection")
        )

        return ExplorationResponse(
            options=result["options"],
            context=result.get("context"),
            exploration_depth=result["exploration_depth"],
            exploration_type="typography",
            can_lock_in=True
        )
    except Exception as e:
        print(f"Error generating typography options: {e}")
        return _get_fallback_typography_response(exploration_state["depth"])


@router.post("/{session_id}/explore/typography/select", response_model=ExplorationProgressResponse)
def select_typography(
    session_id: int,
    selection: ExplorationSelection,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a typography selection.
    """
    session = _get_session_or_404(session_id, current_user.id, db)

    if session.phase != "typography_exploration":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Not in typography exploration phase. Current phase: {session.phase}"
        )

    exploration_state = _get_exploration_state(session, "typography")
    exploration_state["depth"] += 1
    exploration_state["history"] = exploration_state.get("history", [])
    exploration_state["history"].append(selection.selected_option.get("name", selection.selected_option_id))
    exploration_state["last_selection"] = selection.selected_option
    _save_exploration_state(session, "typography", exploration_state, db)

    max_depth = 3
    if not selection.wants_refinement or exploration_state["depth"] >= max_depth:
        # Lock in typography
        session.chosen_typography = json.dumps({
            "heading": selection.selected_option.get("heading"),
            "body": selection.selected_option.get("body"),
            "style": selection.selected_option.get("id"),
            "category": selection.selected_option.get("category")
        })
        session.phase = "component_studio"
        session.comparison_count = 0

        db.commit()

        return ExplorationProgressResponse(
            success=True,
            exploration_depth=exploration_state["depth"],
            locked_in=True,
            new_phase="component_studio",
            message=f"Typography '{selection.selected_option.get('name', 'selected')}' locked in! Moving to Component Studio."
        )

    if not EXPLORATION_SERVICE_AVAILABLE:
        return _get_fallback_refinement_response(exploration_state["depth"], "typography")

    try:
        service = get_exploration_service()
        result = service.generate_full_typography_options(
            project_description=session.project_description,
            exploration_depth=exploration_state["depth"],
            previous_selection=selection.selected_option
        )

        db.commit()

        # Prepend the original selection so user can still choose it
        # Mark it as the "original" so frontend can highlight it
        original_option = selection.selected_option.copy()
        original_option["is_original"] = True
        all_options = [original_option] + result["options"]

        return ExplorationProgressResponse(
            success=True,
            exploration_depth=exploration_state["depth"],
            next_options=all_options,
            locked_in=False,
            message=f"Showing similar options to '{selection.selected_option.get('name', 'selected')}'. Your original is included - choose a variation or lock in."
        )
    except Exception as e:
        print(f"Error generating refined typography: {e}")
        db.commit()
        return _get_fallback_refinement_response(exploration_state["depth"], "typography")


# ============================================================================
# Helper Functions
# ============================================================================

def _get_session_or_404(session_id: int, user_id: int, db: Session) -> ExtractionSessionModel:
    """Get session or raise 404."""
    session = (
        db.query(ExtractionSessionModel)
        .filter(
            ExtractionSessionModel.id == session_id,
            ExtractionSessionModel.user_id == user_id
        )
        .first()
    )
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return session


def _get_exploration_state(session: ExtractionSessionModel, exploration_type: str) -> dict:
    """Get the current exploration state from session metadata."""
    # Store exploration state in established_preferences JSON
    if session.established_preferences:
        try:
            prefs = json.loads(session.established_preferences)
            state = prefs.get(f"_exploration_{exploration_type}", {})
            return {
                "depth": state.get("depth", 0),
                "history": state.get("history", []),
                "last_selection": state.get("last_selection")
            }
        except json.JSONDecodeError:
            pass
    return {"depth": 0, "history": [], "last_selection": None}


def _save_exploration_state(
    session: ExtractionSessionModel,
    exploration_type: str,
    state: dict,
    db: Session
):
    """Save exploration state to session metadata."""
    prefs = {}
    if session.established_preferences:
        try:
            prefs = json.loads(session.established_preferences)
        except json.JSONDecodeError:
            pass

    prefs[f"_exploration_{exploration_type}"] = state
    session.established_preferences = json.dumps(prefs)
    session.updated_at = datetime.utcnow()


def _get_fallback_palette_response(depth: int) -> ExplorationResponse:
    """Fallback palette response when Claude API unavailable."""
    return ExplorationResponse(
        options=[
            {
                "id": "professional-blue",
                "name": "Professional Blue",
                "category": "professional",
                "primary": "#1e3a8a",
                "secondary": "#0891b2",
                "accent": "#f59e0b",
                "accentSoft": "#fbbf24",
                "background": "#f8fafc",
                "description": "Clean and trustworthy"
            },
            {
                "id": "creative-purple",
                "name": "Creative Purple",
                "category": "creative",
                "primary": "#7c3aed",
                "secondary": "#a855f7",
                "accent": "#f97316",
                "accentSoft": "#fb923c",
                "background": "#faf5ff",
                "description": "Vibrant and innovative"
            },
            {
                "id": "playful-teal",
                "name": "Playful Teal",
                "category": "playful",
                "primary": "#0d9488",
                "secondary": "#14b8a6",
                "accent": "#f97316",
                "accentSoft": "#fb923c",
                "background": "#f0fdfa",
                "description": "Fun and approachable"
            },
            {
                "id": "warm-coral",
                "name": "Warm Coral",
                "category": "warm",
                "primary": "#dc2626",
                "secondary": "#f97316",
                "accent": "#0891b2",
                "accentSoft": "#22d3ee",
                "background": "#fef2f2",
                "description": "Energetic and welcoming"
            },
            {
                "id": "natural-green",
                "name": "Natural Green",
                "category": "natural",
                "primary": "#059669",
                "secondary": "#10b981",
                "accent": "#f59e0b",
                "accentSoft": "#fcd34d",
                "background": "#f0fdf4",
                "description": "Organic and growth-oriented"
            },
        ],
        context="Select a color palette that fits your project",
        exploration_depth=depth,
        exploration_type="palette",
        can_lock_in=True
    )


def _get_fallback_typography_response(depth: int) -> ExplorationResponse:
    """Fallback typography response when Claude API unavailable."""
    return ExplorationResponse(
        options=[
            {
                "id": "modern-clean",
                "name": "Modern Clean",
                "category": "modern",
                "heading": "Inter",
                "body": "Inter",
                "headingCategory": "sans-serif",
                "bodyCategory": "sans-serif",
                "description": "Clean and versatile"
            },
            {
                "id": "elegant-editorial",
                "name": "Elegant Editorial",
                "category": "elegant",
                "heading": "Playfair Display",
                "body": "Lora",
                "headingCategory": "serif",
                "bodyCategory": "serif",
                "description": "Classic elegance"
            },
            {
                "id": "friendly-rounded",
                "name": "Friendly Rounded",
                "category": "friendly",
                "heading": "Nunito",
                "body": "Nunito",
                "headingCategory": "sans-serif",
                "bodyCategory": "sans-serif",
                "description": "Approachable and warm"
            },
            {
                "id": "bold-statement",
                "name": "Bold Statement",
                "category": "bold",
                "heading": "Oswald",
                "body": "Open Sans",
                "headingCategory": "sans-serif",
                "bodyCategory": "sans-serif",
                "description": "Strong impact"
            },
            {
                "id": "minimal-swiss",
                "name": "Minimal Swiss",
                "category": "minimal",
                "heading": "Montserrat",
                "body": "Roboto",
                "headingCategory": "sans-serif",
                "bodyCategory": "sans-serif",
                "description": "Swiss-inspired minimal"
            },
        ],
        context="Select a typography style that fits your project",
        exploration_depth=depth,
        exploration_type="typography",
        can_lock_in=True
    )


def _get_fallback_refinement_response(depth: int, exploration_type: str) -> ExplorationProgressResponse:
    """Fallback refinement response."""
    return ExplorationProgressResponse(
        success=True,
        exploration_depth=depth,
        next_options=[],  # Empty = use fallback options from GET endpoint
        locked_in=False,
        message="Refinement options generated. Select a variation or lock in your choice."
    )
