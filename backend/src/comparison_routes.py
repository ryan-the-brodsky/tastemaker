"""
A/B comparison routes for the extraction flow.

HYBRID APPROACH:
- Territory Mapping: Uses Claude API (generation_service) for creative exploration
- Dimension Isolation: Uses deterministic (variation_service) for precise testing
"""
import json
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db_config import get_db
from pydantic import BaseModel
from models import (
    UserModel, ExtractionSessionModel, ComparisonResultModel,
    ComparisonResponse, ComparisonChoice, ComparisonOption, SessionProgress,
    ComparisonQuestion
)
from palette_service import get_palette_by_name, get_font_pairing_by_name
from auth_routes import get_current_user
from variation_service import generate_comparison, get_properties_for_component
from pattern_analyzer import (
    should_transition_to_dimension_isolation,
    get_property_to_test,
    calculate_session_confidence
)
# Import Claude API generation service for territory mapping
try:
    from generation_service import get_generation_service
    CLAUDE_API_AVAILABLE = True
except Exception as e:
    print(f"Warning: Claude API generation not available: {e}")
    CLAUDE_API_AVAILABLE = False

router = APIRouter(prefix="/api/sessions", tags=["comparisons"])


@router.get("/{session_id}/comparison", response_model=ComparisonResponse)
def get_next_comparison(
    session_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the next A/B comparison for the session.

    HYBRID APPROACH:
    - Territory Mapping: Uses Claude API for creative, multi-question variations
    - Dimension Isolation: Uses deterministic service for precise single-property testing
    """
    # Get session
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

    # Get all comparison results for this session
    results = (
        db.query(ComparisonResultModel)
        .filter(ComparisonResultModel.session_id == session_id)
        .all()
    )

    results_dicts = [
        {
            "option_a_styles": r.option_a_styles,
            "option_b_styles": r.option_b_styles,
            "choice": r.choice,
            "component_type": r.component_type,
        }
        for r in results
    ]

    # Handle color_exploration and typography_exploration phases (deterministic)
    if session.phase in ["color_exploration", "typography_exploration"]:
        comparison = generate_comparison(
            session_phase=session.phase,
            comparison_count=session.comparison_count,
        )
        questions = None
        if comparison.get("questions"):
            questions = [
                ComparisonQuestion(
                    category=q["category"],
                    property=q["property"],
                    question_text=q["question_text"],
                    option_a_value=str(q["option_a_value"]),
                    option_b_value=str(q["option_b_value"])
                )
                for q in comparison["questions"]
            ]
        return ComparisonResponse(
            comparison_id=comparison["comparison_id"],
            component_type=comparison["component_type"],
            phase=comparison["phase"],
            option_a=ComparisonOption(
                id=comparison["option_a"]["id"],
                styles=comparison["option_a"]["styles"]
            ),
            option_b=ComparisonOption(
                id=comparison["option_b"]["id"],
                styles=comparison["option_b"]["styles"]
            ),
            context=comparison.get("context", ""),
            questions=questions,
            generation_method="deterministic"
        )

    # Check for phase transition
    if session.phase == "territory_mapping":
        if should_transition_to_dimension_isolation(session.comparison_count, results_dicts):
            session.phase = "dimension_isolation"
            db.commit()

    # Parse established preferences for Claude API context
    established_preferences = None
    if session.established_preferences:
        try:
            established_preferences = json.loads(session.established_preferences)
        except json.JSONDecodeError:
            established_preferences = None

    # Parse chosen colors/typography for Claude API constraints
    chosen_colors = None
    chosen_typography = None
    if session.chosen_colors:
        try:
            chosen_colors = json.loads(session.chosen_colors)
        except json.JSONDecodeError:
            pass
    if session.chosen_typography:
        try:
            chosen_typography = json.loads(session.chosen_typography)
        except json.JSONDecodeError:
            pass

    # HYBRID: Use Claude API for territory mapping, deterministic for dimension isolation
    questions = None
    generation_method = "deterministic"

    if session.phase == "territory_mapping" and CLAUDE_API_AVAILABLE:
        # Use Claude API for creative exploration with multi-question
        try:
            from variation_service import get_next_component_type
            component_type = get_next_component_type(session.comparison_count)

            gen_service = get_generation_service()
            comparison = gen_service.generate_comparison_pair(
                component_type=component_type,
                session_id=str(session_id),
                phase=session.phase,
                comparison_count=session.comparison_count,
                established_preferences=established_preferences,
                project_description=session.project_description,
                chosen_colors=chosen_colors,
                chosen_typography=chosen_typography
            )

            # Convert questions to Pydantic models
            if comparison.get("questions"):
                questions = [
                    ComparisonQuestion(
                        category=q["category"],
                        property=q["property"],
                        question_text=q["question_text"],
                        option_a_value=str(q["option_a_value"]),
                        option_b_value=str(q["option_b_value"])
                    )
                    for q in comparison["questions"]
                ]
            generation_method = "claude_api"

        except Exception as e:
            # Fallback to deterministic if Claude API fails
            print(f"Claude API failed, falling back to deterministic: {e}")
            comparison = generate_comparison(
                session_phase=session.phase,
                comparison_count=session.comparison_count,
            )
    else:
        # Dimension isolation: Use deterministic service for precise testing
        base_styles = None
        property_to_test = None

        if session.phase == "dimension_isolation":
            tested_props = list(set(r.component_type for r in results if r.phase == "dimension_isolation"))
            property_to_test, base_styles = get_property_to_test(results_dicts, tested_props)

        comparison = generate_comparison(
            session_phase=session.phase,
            comparison_count=session.comparison_count,
            base_styles=base_styles,
            property_to_test=property_to_test
        )

    return ComparisonResponse(
        comparison_id=comparison["comparison_id"],
        component_type=comparison["component_type"],
        phase=comparison["phase"],
        option_a=ComparisonOption(
            id=comparison["option_a"]["id"],
            styles=comparison["option_a"]["styles"]
        ),
        option_b=ComparisonOption(
            id=comparison["option_b"]["id"],
            styles=comparison["option_b"]["styles"]
        ),
        context=comparison.get("context", ""),
        questions=questions,
        generation_method=generation_method
    )


@router.post("/{session_id}/comparison/{comparison_id}", response_model=SessionProgress)
def submit_comparison_choice(
    session_id: str,
    comparison_id: int,
    choice_data: ComparisonChoice,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a choice for a comparison.

    Supports both:
    - Legacy single-choice (choice_data.choice)
    - Multi-question answers (choice_data.answers)
    """
    # Validate choice (for backwards compatibility)
    if choice_data.choice not in ["a", "b", "none"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Choice must be 'a', 'b', or 'none'"
        )

    # Get session
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

    # Get the comparison styles - we need to regenerate or store them
    # For Claude API comparisons, we should ideally cache them, but for now regenerate
    comparison = None
    if session.phase == "territory_mapping" and CLAUDE_API_AVAILABLE:
        try:
            from variation_service import get_next_component_type
            component_type = get_next_component_type(session.comparison_count)

            established_preferences = None
            if session.established_preferences:
                try:
                    established_preferences = json.loads(session.established_preferences)
                except json.JSONDecodeError:
                    pass

            gen_service = get_generation_service()
            comparison = gen_service.generate_comparison_pair(
                component_type=component_type,
                session_id=str(session_id),
                phase=session.phase,
                comparison_count=session.comparison_count,
                established_preferences=established_preferences,
                project_description=session.project_description
            )
        except Exception as e:
            print(f"Claude API failed during submit, falling back: {e}")
            comparison = None

    if comparison is None:
        comparison = generate_comparison(
            session_phase=session.phase,
            comparison_count=session.comparison_count,
        )

    # Serialize multi-question answers if provided
    question_responses_json = None
    if choice_data.answers:
        question_responses_json = json.dumps([
            {"category": a.category, "property": a.property, "choice": a.choice}
            for a in choice_data.answers
        ])

    # Store the comparison result
    result = ComparisonResultModel(
        session_id=session_id,
        comparison_id=comparison_id,
        component_type=comparison["component_type"],
        phase=session.phase,
        option_a_styles=json.dumps(comparison["option_a"]["styles"]),
        option_b_styles=json.dumps(comparison["option_b"]["styles"]),
        choice=choice_data.choice,
        decision_time_ms=choice_data.decision_time_ms,
        question_responses=question_responses_json,
    )
    db.add(result)

    # Update session
    session.comparison_count += 1
    session.updated_at = datetime.utcnow()

    # Update established preferences from multi-question answers
    if choice_data.answers:
        _update_established_preferences(session, comparison, choice_data.answers)

    # Get all results for confidence calculation
    all_results = (
        db.query(ComparisonResultModel)
        .filter(ComparisonResultModel.session_id == session_id)
        .all()
    )
    results_dicts = [
        {
            "option_a_styles": r.option_a_styles,
            "option_b_styles": r.option_b_styles,
            "choice": r.choice,
            "question_responses": r.question_responses,
        }
        for r in all_results
    ]
    results_dicts.append({
        "option_a_styles": result.option_a_styles,
        "option_b_styles": result.option_b_styles,
        "choice": result.choice,
        "question_responses": result.question_responses,
    })

    session.confidence_score = calculate_session_confidence(results_dicts)

    # Check for phase transitions
    next_phase = None

    if session.phase == "color_exploration":
        # After 5-10 color comparisons, transition to typography
        # Also save the chosen palette based on most recent choice
        if session.comparison_count >= 5:
            # Get the chosen palette from this comparison
            if choice_data.choice == "a":
                chosen_palette = comparison["option_a"]["styles"]
            elif choice_data.choice == "b":
                chosen_palette = comparison["option_b"]["styles"]
            else:
                # Default to option_a if "none"
                chosen_palette = comparison["option_a"]["styles"]

            session.chosen_colors = json.dumps(chosen_palette)
            session.phase = "typography_exploration"
            session.comparison_count = 0  # Reset count for new phase
            next_phase = "typography_exploration"

    elif session.phase == "typography_exploration":
        # After 5-8 typography comparisons, transition to territory_mapping
        if session.comparison_count >= 5:
            # Get the chosen font pairing from this comparison
            if choice_data.choice == "a":
                chosen_fonts = comparison["option_a"]["styles"]
            elif choice_data.choice == "b":
                chosen_fonts = comparison["option_b"]["styles"]
            else:
                chosen_fonts = comparison["option_a"]["styles"]

            session.chosen_typography = json.dumps(chosen_fonts)
            session.phase = "component_studio"
            session.comparison_count = 0  # Reset count for new phase
            next_phase = "component_studio"

    elif session.phase == "territory_mapping":
        if should_transition_to_dimension_isolation(session.comparison_count, results_dicts):
            session.phase = "dimension_isolation"
            next_phase = "dimension_isolation"

    elif session.phase == "dimension_isolation":
        # After 30 total comparisons, move to stated preferences
        if session.comparison_count >= 30:
            session.phase = "stated_preferences"
            next_phase = "stated_preferences"

    db.commit()

    # Parse established preferences for response
    established_prefs = None
    if session.established_preferences:
        try:
            established_prefs = json.loads(session.established_preferences)
        except json.JSONDecodeError:
            established_prefs = None

    return SessionProgress(
        comparison_count=session.comparison_count,
        phase=session.phase,
        confidence_score=session.confidence_score,
        next_phase=next_phase,
        established_preferences=established_prefs
    )


def _update_established_preferences(
    session: ExtractionSessionModel,
    comparison: dict,
    answers: list
):
    """
    Update session's established_preferences based on multi-question answers.
    This enables progressive incorporation - user's choices appear in later comparisons.
    """
    # Load existing preferences
    established = {}
    if session.established_preferences:
        try:
            established = json.loads(session.established_preferences)
        except json.JSONDecodeError:
            established = {}

    # Get styles from comparison
    option_a_styles = comparison["option_a"]["styles"]
    option_b_styles = comparison["option_b"]["styles"]

    # Update preferences based on answers
    for answer in answers:
        prop = answer.property
        choice = answer.choice

        if choice == "a" and prop in option_a_styles:
            established[prop] = option_a_styles[prop]
        elif choice == "b" and prop in option_b_styles:
            established[prop] = option_b_styles[prop]
        # "none" means no preference, don't update

    # Save back to session
    session.established_preferences = json.dumps(established)


# ============================================================================
# BATCH COMPARISON ENDPOINT
# ============================================================================

class BatchComparisonRequest(BaseModel):
    """Request body for batch comparison generation."""
    batch_size: int = 5
    recent_choices: Optional[List[dict]] = None


class BatchComparisonResponse(BaseModel):
    """Response containing multiple comparisons."""
    comparisons: List[dict]
    batch_id: str
    has_more: bool = True


@router.post("/{session_id}/comparisons/batch", response_model=BatchComparisonResponse)
def get_batch_comparisons(
    session_id: str,
    request: BatchComparisonRequest,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a batch of comparisons for efficient pre-loading.

    This allows the frontend to request 5 comparisons at once,
    display the first immediately, and pre-load the rest for instant transitions.
    """
    import uuid

    # Get session
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

    # Only allow batch generation for territory_mapping and dimension_isolation phases
    if session.phase not in ["territory_mapping", "dimension_isolation"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Batch generation only available for component phases. Current phase: {session.phase}"
        )

    # Parse session context
    established_preferences = None
    chosen_colors = None
    chosen_typography = None

    if session.established_preferences:
        try:
            established_preferences = json.loads(session.established_preferences)
        except json.JSONDecodeError:
            pass

    if session.chosen_colors:
        try:
            chosen_colors = json.loads(session.chosen_colors)
        except json.JSONDecodeError:
            pass

    if session.chosen_typography:
        try:
            chosen_typography = json.loads(session.chosen_typography)
        except json.JSONDecodeError:
            pass

    # Generate batch using Claude API if available
    if CLAUDE_API_AVAILABLE:
        try:
            gen_service = get_generation_service()
            comparisons = gen_service.generate_batch_comparisons(
                session_id=str(session_id),
                phase=session.phase,
                batch_size=request.batch_size,
                start_comparison_count=session.comparison_count,
                established_preferences=established_preferences,
                project_description=session.project_description,
                chosen_colors=chosen_colors,
                chosen_typography=chosen_typography,
                recent_choices=request.recent_choices
            )

            return BatchComparisonResponse(
                comparisons=comparisons,
                batch_id=str(uuid.uuid4()),
                has_more=session.comparison_count + len(comparisons) < 15  # Territory mapping typically has 15 comparisons
            )
        except Exception as e:
            print(f"Batch generation failed, falling back to individual: {e}")

    # Fallback: generate individual comparisons deterministically
    comparisons = []
    for i in range(request.batch_size):
        comp = generate_comparison(
            session_phase=session.phase,
            comparison_count=session.comparison_count + i
        )
        comparisons.append(comp)

    return BatchComparisonResponse(
        comparisons=comparisons,
        batch_id=str(uuid.uuid4()),
        has_more=session.comparison_count + len(comparisons) < 15
    )


# Pydantic schema for lock-in request
class LockInChoice(BaseModel):
    """Request body for locking in a color or typography choice."""
    chosen_option_id: str  # The ID of the chosen palette/font pairing
    chosen_styles: dict    # The full styles object to save


class LockInResponse(BaseModel):
    """Response after locking in a choice."""
    success: bool
    new_phase: str
    message: str


@router.post("/{session_id}/lock-in", response_model=LockInResponse)
def lock_in_choice(
    session_id: str,
    choice_data: LockInChoice,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lock in the current phase choice early and advance to next phase.

    Used for "That's it!" button in color_exploration and typography_exploration phases.
    Allows users to commit to a choice without waiting for the minimum comparison count.
    """
    # Get session
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

    # Only allow lock-in during color and typography phases
    if session.phase not in ["color_exploration", "typography_exploration"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Lock-in is only available during color_exploration or typography_exploration phases. Current phase: {session.phase}"
        )

    # Process based on current phase
    if session.phase == "color_exploration":
        session.chosen_colors = json.dumps(choice_data.chosen_styles)
        session.phase = "typography_exploration"
        session.comparison_count = 0  # Reset for new phase
        new_phase = "typography_exploration"
        message = "Color palette locked in! Moving to typography selection."

    elif session.phase == "typography_exploration":
        session.chosen_typography = json.dumps(choice_data.chosen_styles)
        session.phase = "component_studio"
        session.comparison_count = 0  # Reset for new phase
        new_phase = "component_studio"
        message = "Typography locked in! Moving to Component Studio."

    session.updated_at = datetime.utcnow()
    db.commit()

    return LockInResponse(
        success=True,
        new_phase=new_phase,
        message=message
    )
