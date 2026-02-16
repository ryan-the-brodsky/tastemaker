"""
Component Studio business logic.

Manages studio progress, dimension choices, component locking,
and checkpoint workflows.
"""
import json
import uuid
from typing import Optional, Dict, Any, List

from sqlalchemy.orm import Session

from models import (
    ExtractionSessionModel,
    ComponentStudioChoiceModel,
    StyleRuleModel,
    StudioProgressResponse,
    ComponentStateResponse,
    CheckpointData,
)
from component_dimensions import (
    COMPONENT_TYPES,
    COMPONENT_DIMENSIONS,
    CHECKPOINT_GROUPS,
    get_dimensions_for_component,
    get_component_label,
    is_checkpoint_trigger,
    get_checkpoint_for_component,
)


def _load_studio_progress(session: ExtractionSessionModel) -> Dict[str, Any]:
    """Load studio progress from session JSON field."""
    if session.studio_progress:
        try:
            return json.loads(session.studio_progress)
        except json.JSONDecodeError:
            pass
    return {
        "completed_components": [],
        "current_component": COMPONENT_TYPES[0],
        "current_dimension_index": 0,
        "checkpoint_approvals": [],
    }


def _save_studio_progress(session: ExtractionSessionModel, progress: Dict[str, Any], db: Session):
    """Save studio progress to session JSON field."""
    session.studio_progress = json.dumps(progress)
    db.flush()


def get_studio_progress(session: ExtractionSessionModel) -> StudioProgressResponse:
    """Get the current studio progress for a session."""
    progress = _load_studio_progress(session)
    completed = progress.get("completed_components", [])
    current = progress.get("current_component")
    approvals = progress.get("checkpoint_approvals", [])

    # Check if studio is complete
    is_complete = len(completed) >= len(COMPONENT_TYPES)

    # Check for pending checkpoint
    pending_checkpoint = None
    if not is_complete and current is None:
        # All components done but maybe a checkpoint is pending
        for group in CHECKPOINT_GROUPS:
            if group["id"] not in approvals:
                if all(c in completed for c in group["components"]):
                    pending_checkpoint = group["id"]
                    break

    return StudioProgressResponse(
        current_component=current if not is_complete else None,
        current_dimension_index=progress.get("current_dimension_index", 0),
        completed_components=completed,
        total_components=len(COMPONENT_TYPES),
        checkpoint_approvals=approvals,
        pending_checkpoint=pending_checkpoint,
        is_complete=is_complete,
    )


def get_component_state(
    session: ExtractionSessionModel,
    component_type: str,
    db: Session,
) -> ComponentStateResponse:
    """Get all choices made for a specific component."""
    choices = (
        db.query(ComponentStudioChoiceModel)
        .filter(
            ComponentStudioChoiceModel.session_id == session.id,
            ComponentStudioChoiceModel.component_type == component_type,
        )
        .all()
    )

    choices_dict: Dict[str, Dict[str, Any]] = {}
    for choice in choices:
        choices_dict[choice.dimension] = {
            "option_id": choice.selected_option_id,
            "value": choice.fine_tuned_value or choice.selected_value,
            "original_value": choice.selected_value,
            "fine_tuned_value": choice.fine_tuned_value,
            "css_property": choice.css_property,
        }

    return ComponentStateResponse(
        component_type=component_type,
        choices=choices_dict,
    )


def submit_dimension_choice(
    session: ExtractionSessionModel,
    component_type: str,
    dimension: str,
    selected_option_id: str,
    selected_value: str,
    css_property: str,
    db: Session,
    fine_tuned_value: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Store a dimension choice and create/update the corresponding StyleRule.

    Returns dict with success status and updated dimension index.
    """
    # Upsert the studio choice
    existing = (
        db.query(ComponentStudioChoiceModel)
        .filter(
            ComponentStudioChoiceModel.session_id == session.id,
            ComponentStudioChoiceModel.component_type == component_type,
            ComponentStudioChoiceModel.dimension == dimension,
        )
        .first()
    )

    if existing:
        existing.selected_option_id = selected_option_id
        existing.selected_value = selected_value
        existing.fine_tuned_value = fine_tuned_value
        existing.css_property = css_property
    else:
        choice = ComponentStudioChoiceModel(
            session_id=session.id,
            component_type=component_type,
            dimension=dimension,
            selected_option_id=selected_option_id,
            selected_value=selected_value,
            fine_tuned_value=fine_tuned_value,
            css_property=css_property,
        )
        db.add(choice)

    # Create/update a StyleRuleModel for this choice
    final_value = fine_tuned_value or selected_value
    rule_id = f"studio-{component_type}-{dimension}"

    existing_rule = (
        db.query(StyleRuleModel)
        .filter(
            StyleRuleModel.session_id == session.id,
            StyleRuleModel.rule_id == rule_id,
        )
        .first()
    )

    # Build a human-readable message
    dim_def = _find_dimension_def(component_type, dimension)
    dim_label = dim_def["label"] if dim_def else dimension
    component_label = get_component_label(component_type)
    message = f"{component_label} {dim_label}: {final_value}"

    if existing_rule:
        existing_rule.value = json.dumps(final_value)
        existing_rule.message = message
        existing_rule.confidence = 1.0
    else:
        rule = StyleRuleModel(
            session_id=session.id,
            rule_id=rule_id,
            component_type=component_type,
            property=css_property,
            operator="=",
            value=json.dumps(final_value),
            severity="warning",
            confidence=1.0,
            source="extracted",
            message=message,
        )
        db.add(rule)

    # Advance dimension index in progress
    progress = _load_studio_progress(session)
    dimensions = get_dimensions_for_component(component_type)
    current_idx = progress.get("current_dimension_index", 0)

    # Find this dimension's index
    dim_indices = {d["key"]: i for i, d in enumerate(dimensions)}
    if dimension in dim_indices:
        # Advance past this dimension if it's the current one
        if dim_indices[dimension] == current_idx:
            progress["current_dimension_index"] = current_idx + 1
            _save_studio_progress(session, progress, db)

    db.flush()

    return {
        "success": True,
        "dimension_index": progress.get("current_dimension_index", 0),
        "total_dimensions": len(dimensions),
    }


def lock_component(
    session: ExtractionSessionModel,
    component_type: str,
    db: Session,
) -> Dict[str, Any]:
    """
    Mark a component as complete and determine next step.

    Returns dict with next_component, trigger_checkpoint, is_studio_complete.
    """
    progress = _load_studio_progress(session)
    completed = progress.get("completed_components", [])

    if component_type not in completed:
        completed.append(component_type)
        progress["completed_components"] = completed

    # Check if this triggers a checkpoint
    trigger_checkpoint = None
    if is_checkpoint_trigger(component_type):
        group = get_checkpoint_for_component(component_type)
        if group and group["id"] not in progress.get("checkpoint_approvals", []):
            trigger_checkpoint = group["id"]

    # Determine next component
    next_component = None
    is_studio_complete = False

    if trigger_checkpoint:
        # Pause at checkpoint — don't advance to next component yet
        progress["current_component"] = None
        progress["current_dimension_index"] = 0
    else:
        # Find next uncompleted component
        for ct in COMPONENT_TYPES:
            if ct not in completed:
                next_component = ct
                break

        if next_component:
            progress["current_component"] = next_component
            progress["current_dimension_index"] = 0
        else:
            # All components done
            is_studio_complete = True
            progress["current_component"] = None

    _save_studio_progress(session, progress, db)
    db.commit()

    return {
        "success": True,
        "next_component": next_component,
        "trigger_checkpoint": trigger_checkpoint,
        "is_studio_complete": is_studio_complete,
    }


def approve_checkpoint(
    session: ExtractionSessionModel,
    checkpoint_id: str,
    db: Session,
) -> Dict[str, Any]:
    """
    Approve a checkpoint and advance to the next component group.

    Returns dict with next_component and is_studio_complete.
    """
    progress = _load_studio_progress(session)
    approvals = progress.get("checkpoint_approvals", [])

    if checkpoint_id not in approvals:
        approvals.append(checkpoint_id)
        progress["checkpoint_approvals"] = approvals

    # Find the next uncompleted component
    completed = progress.get("completed_components", [])
    next_component = None
    is_studio_complete = False

    for ct in COMPONENT_TYPES:
        if ct not in completed:
            next_component = ct
            break

    if next_component:
        progress["current_component"] = next_component
        progress["current_dimension_index"] = 0
    else:
        is_studio_complete = True
        progress["current_component"] = None

    _save_studio_progress(session, progress, db)
    db.commit()

    return {
        "success": True,
        "next_component": next_component,
        "is_studio_complete": is_studio_complete,
    }


def go_back_to_component(
    session: ExtractionSessionModel,
    component_type: str,
    db: Session,
) -> Dict[str, Any]:
    """Navigate back to a previously completed component for editing."""
    progress = _load_studio_progress(session)

    if component_type not in COMPONENT_TYPES:
        return {"success": False, "error": f"Unknown component type: {component_type}"}

    progress["current_component"] = component_type
    progress["current_dimension_index"] = 0
    _save_studio_progress(session, progress, db)
    db.commit()

    return {"success": True, "component_type": component_type}


def get_checkpoint_data(
    session: ExtractionSessionModel,
    checkpoint_id: str,
    db: Session,
) -> Optional[CheckpointData]:
    """Gather all locked component styles + colors + typography for a checkpoint."""
    group = None
    for g in CHECKPOINT_GROUPS:
        if g["id"] == checkpoint_id:
            group = g
            break

    if not group:
        return None

    # Gather styles for all components in this group (and previous groups)
    component_styles: Dict[str, Dict[str, str]] = {}

    progress = _load_studio_progress(session)
    completed = progress.get("completed_components", [])

    for comp_type in completed:
        state = get_component_state(session, comp_type, db)
        styles: Dict[str, str] = {}
        for dim_key, choice_data in state.choices.items():
            styles[choice_data["css_property"]] = choice_data["value"]
        component_styles[comp_type] = styles

    # Parse colors and typography
    colors = None
    typography = None
    if session.chosen_colors:
        try:
            colors = json.loads(session.chosen_colors)
        except json.JSONDecodeError:
            pass
    if session.chosen_typography:
        try:
            typography = json.loads(session.chosen_typography)
        except json.JSONDecodeError:
            pass

    return CheckpointData(
        checkpoint_id=group["id"],
        label=group["label"],
        description=group["description"],
        mockup_type=group["mockup_type"],
        components=group["components"],
        component_styles=component_styles,
        colors=colors,
        typography=typography,
    )


def get_all_preview_styles(
    session: ExtractionSessionModel,
    db: Session,
) -> Dict[str, Dict[str, str]]:
    """Get all accumulated component styles for live preview."""
    all_choices = (
        db.query(ComponentStudioChoiceModel)
        .filter(ComponentStudioChoiceModel.session_id == session.id)
        .all()
    )

    styles: Dict[str, Dict[str, str]] = {}
    for choice in all_choices:
        if choice.component_type not in styles:
            styles[choice.component_type] = {}
        value = choice.fine_tuned_value or choice.selected_value
        styles[choice.component_type][choice.css_property] = value

    return styles


def _find_dimension_def(component_type: str, dimension_key: str) -> Optional[Dict[str, Any]]:
    """Find a dimension definition by component type and key."""
    dimensions = COMPONENT_DIMENSIONS.get(component_type, [])
    for d in dimensions:
        if d["key"] == dimension_key:
            return d
    return None
