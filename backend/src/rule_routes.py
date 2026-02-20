"""
Style rule management routes.
"""
import json
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db_config import get_db
from models import (
    UserModel, ExtractionSessionModel, StyleRuleModel, ComparisonResultModel,
    RuleCreate, RuleUpdate, StyleRuleResponse
)
from auth_routes import get_current_user
from rule_synthesizer import parse_stated_preference, synthesize_rules_from_patterns
from baseline_rules import check_baseline_conflict

router = APIRouter(prefix="/api/sessions", tags=["rules"])


@router.get("/{session_id}/rules", response_model=List[StyleRuleResponse])
def get_session_rules(
    session_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all rules for a session."""
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

    # Check if we need to synthesize rules from comparisons
    existing_rules = (
        db.query(StyleRuleModel)
        .filter(StyleRuleModel.session_id == session_id)
        .all()
    )

    # If no extracted rules exist, synthesize them
    extracted_rules = [r for r in existing_rules if r.source == "extracted"]
    if not extracted_rules and session.comparison_count > 0:
        comparisons = (
            db.query(ComparisonResultModel)
            .filter(ComparisonResultModel.session_id == session_id)
            .all()
        )
        comparison_dicts = [
            {
                "option_a_styles": c.option_a_styles,
                "option_b_styles": c.option_b_styles,
                "choice": c.choice,
            }
            for c in comparisons
        ]

        new_rules = synthesize_rules_from_patterns(comparison_dicts, session_id)
        for rule_data in new_rules:
            rule = StyleRuleModel(**rule_data)
            db.add(rule)
        db.commit()

        # Refresh rules list
        existing_rules = (
            db.query(StyleRuleModel)
            .filter(StyleRuleModel.session_id == session_id)
            .all()
        )

    return [
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
        for r in existing_rules
    ]


@router.post("/{session_id}/rules", response_model=StyleRuleResponse, status_code=status.HTTP_201_CREATED)
def add_stated_rule(
    session_id: str,
    rule_data: RuleCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a stated preference rule."""
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

    # Parse the natural language statement
    parsed = parse_stated_preference(rule_data.statement, rule_data.component)

    # Generate rule ID
    prefix = parsed.get("component_type", "gen")[:3] if parsed.get("component_type") else "gen"
    rule_id = f"{prefix}-stated-{uuid.uuid4().hex[:6]}"

    # Create rule
    rule = StyleRuleModel(
        session_id=session_id,
        rule_id=rule_id,
        component_type=parsed.get("component_type"),
        property=parsed["property"],
        operator=parsed["operator"],
        value=parsed["value"],
        severity=parsed["severity"],
        confidence=parsed["confidence"],
        source="stated",
        message=parsed["message"],
    )

    # Check for baseline conflicts
    conflicts = check_baseline_conflict({
        "property": parsed["property"],
        "component_type": parsed.get("component_type"),
        "operator": parsed["operator"],
        "value": json.loads(parsed["value"]) if isinstance(parsed["value"], str) else parsed["value"],
    })

    db.add(rule)
    db.commit()
    db.refresh(rule)

    response = StyleRuleResponse(
        id=rule.id,
        rule_id=rule.rule_id,
        component_type=rule.component_type,
        property=rule.property,
        operator=rule.operator,
        value=rule.value,
        severity=rule.severity,
        confidence=rule.confidence,
        source=rule.source,
        message=rule.message,
        is_modified=rule.is_modified,
        created_at=rule.created_at,
    )

    # Add warning header if conflicts exist
    if conflicts:
        response.message = f"WARNING: Conflicts with baseline rules: {[c['id'] for c in conflicts]}. {response.message or ''}"

    return response


@router.patch("/{session_id}/rules/{rule_id}", response_model=StyleRuleResponse)
def update_rule(
    session_id: str,
    rule_id: str,
    update_data: RuleUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a rule."""
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

    # Find the rule
    rule = (
        db.query(StyleRuleModel)
        .filter(
            StyleRuleModel.session_id == session_id,
            StyleRuleModel.rule_id == rule_id
        )
        .first()
    )

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found"
        )

    # Update fields
    if update_data.value is not None:
        rule.value = json.dumps(update_data.value)
    if update_data.severity is not None:
        rule.severity = update_data.severity
    if update_data.message is not None:
        rule.message = update_data.message

    rule.is_modified = True
    db.commit()
    db.refresh(rule)

    return StyleRuleResponse(
        id=rule.id,
        rule_id=rule.rule_id,
        component_type=rule.component_type,
        property=rule.property,
        operator=rule.operator,
        value=rule.value,
        severity=rule.severity,
        confidence=rule.confidence,
        source=rule.source,
        message=rule.message,
        is_modified=rule.is_modified,
        created_at=rule.created_at,
    )


@router.delete("/{session_id}/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule(
    session_id: str,
    rule_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a rule."""
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

    # Find and delete the rule
    rule = (
        db.query(StyleRuleModel)
        .filter(
            StyleRuleModel.session_id == session_id,
            StyleRuleModel.rule_id == rule_id
        )
        .first()
    )

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found"
        )

    db.delete(rule)
    db.commit()
    return None
