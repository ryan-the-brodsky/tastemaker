"""
Rule synthesizer for converting extracted patterns into structured style rules.
"""
import json
from typing import Dict, List, Any, Optional
from pattern_analyzer import aggregate_property_preferences


def synthesize_rules_from_patterns(
    comparison_results: List[dict],
    session_id: int,
    min_confidence: float = 0.6
) -> List[dict]:
    """
    Convert extracted patterns into structured style rules.

    Args:
        comparison_results: List of comparison result dicts
        session_id: ID of the extraction session
        min_confidence: Minimum confidence threshold for rule creation

    Returns:
        List of rule dicts ready for database insertion
    """
    preferences = aggregate_property_preferences(comparison_results)
    rules = []
    rule_counter = 0  # Global counter for unique IDs

    for prop, data in preferences.items():
        if data["confidence"] < min_confidence:
            continue

        # Determine component type from property name patterns
        component_type = _infer_component_type(prop)

        # Get rule ID prefix
        prefix = component_type[:3] if component_type else "gen"

        # Consolidate preferred values - pick the one with highest support
        # Instead of creating multiple rules for the same property
        if data["preferred_values"]:
            # For now, take the first (most common) preferred value
            # In a more sophisticated version, we'd score each value
            best_preferred = data["preferred_values"][0]

            # Check if value is a complex object (dict string) and decompose it
            decomposed = _decompose_complex_value(best_preferred, prop)

            if decomposed:
                # Create individual rules for each property in the complex object
                for sub_prop, sub_value in decomposed.items():
                    rule_counter += 1
                    rule_id = f"{prefix}-{rule_counter:03d}"
                    rule = {
                        "session_id": session_id,
                        "rule_id": rule_id,
                        "component_type": component_type,
                        "property": sub_prop,
                        "operator": "=",
                        "value": json.dumps(sub_value),
                        "severity": "warning",
                        "confidence": data["confidence"],
                        "source": "extracted",
                        "message": _generate_rule_message(sub_prop, "=", sub_value, component_type)
                    }
                    rules.append(rule)
            else:
                rule_counter += 1
                rule_id = f"{prefix}-{rule_counter:03d}"
                rule = {
                    "session_id": session_id,
                    "rule_id": rule_id,
                    "component_type": component_type,
                    "property": prop,
                    "operator": "=",
                    "value": json.dumps(best_preferred),
                    "severity": "warning",
                    "confidence": data["confidence"],
                    "source": "extracted",
                    "message": _generate_rule_message(prop, "=", best_preferred, component_type)
                }
                rules.append(rule)

        # Create rules for rejected values (limit to top 2 most rejected)
        if data["rejected_values"]:
            for value in data["rejected_values"][:2]:
                decomposed = _decompose_complex_value(value, prop)

                if decomposed:
                    for sub_prop, sub_value in decomposed.items():
                        rule_counter += 1
                        rule_id = f"{prefix}-{rule_counter:03d}"
                        rule = {
                            "session_id": session_id,
                            "rule_id": rule_id,
                            "component_type": component_type,
                            "property": sub_prop,
                            "operator": "!=",
                            "value": json.dumps(sub_value),
                            "severity": "warning",
                            "confidence": data["confidence"],
                            "source": "extracted",
                            "message": _generate_rule_message(sub_prop, "!=", sub_value, component_type)
                        }
                        rules.append(rule)
                else:
                    rule_counter += 1
                    rule_id = f"{prefix}-{rule_counter:03d}"
                    rule = {
                        "session_id": session_id,
                        "rule_id": rule_id,
                        "component_type": component_type,
                        "property": prop,
                        "operator": "!=",
                        "value": json.dumps(value),
                        "severity": "warning",
                        "confidence": data["confidence"],
                        "source": "extracted",
                        "message": _generate_rule_message(prop, "!=", value, component_type)
                    }
                    rules.append(rule)

    return rules


def _decompose_complex_value(value: Any, parent_prop: str) -> Optional[Dict[str, Any]]:
    """
    Decompose complex dict values into individual property rules.

    For example, if value is "{'color': '#111827', 'fontSize': '12px'}"
    returns {'color': '#111827', 'fontSize': '12px'}

    Returns None if value is a simple scalar.
    """
    if not isinstance(value, str):
        return None

    # Check if it looks like a Python dict string
    if value.startswith("{") and ":" in value:
        try:
            # Try to parse as Python dict (using ast.literal_eval would be safer)
            import ast
            parsed = ast.literal_eval(value)
            if isinstance(parsed, dict):
                return parsed
        except (ValueError, SyntaxError):
            pass

    return None


def _infer_component_type(property_name: str) -> Optional[str]:
    """Infer component type from property name."""
    property_component_map = {
        "border_radius": None,  # Generic
        "padding_x": None,
        "padding_y": None,
        "shadow": None,
        "background": None,
        "font_weight": "typography",
        "font_size": "typography",
        "text_transform": "button",
        "background_style": "button",
        "transition": "button",
        "border_width": "input",
        "border_color": "input",
        "label_position": "input",
        "focus_ring": "input",
        "hover_effect": "card",
        "heading_weight": "typography",
        "heading_size_scale": "typography",
        "body_line_height": "typography",
        "letter_spacing": "typography",
        "font_family": "typography",
        "paragraph_spacing": "typography",
        "style": "navigation",
        "item_padding_x": "navigation",
        "item_padding_y": "navigation",
        "active_indicator": "navigation",
        "separator": "navigation",
        "layout": "form",
        "label_style": "form",
        "spacing": "form",
        "error_style": "form",
        "required_indicator": "form",
        "help_text_position": "form",
        "type": "feedback",
        "position": "feedback",
        "icon": "feedback",
        "duration": "feedback",
        "animation": None,
        "size": "modal",
        "overlay": "modal",
        "close_button": "modal",
        "header_style": "modal",
    }
    return property_component_map.get(property_name)


def _generate_rule_message(
    property_name: str,
    operator: str,
    value: Any,
    component_type: Optional[str]
) -> str:
    """Generate human-readable message for a rule."""
    component_str = f"{component_type} " if component_type else ""

    if operator == "=":
        return f"Prefer {component_str}{property_name} of {value}"
    elif operator == "!=":
        return f"Avoid {component_str}{property_name} of {value}"
    elif operator == ">=":
        return f"{component_str}{property_name} should be at least {value}"
    elif operator == "<=":
        return f"{component_str}{property_name} should not exceed {value}"
    else:
        return f"{component_str}{property_name} {operator} {value}"


def parse_stated_preference(statement: str, component: Optional[str] = None) -> dict:
    """
    Parse a natural language stated preference into a structured rule.

    Examples:
        "never use gradients" -> {property: "background_style", operator: "!=", value: "gradient"}
        "always use rounded corners" -> {property: "border_radius", operator: ">=", value: 8}
        "prefer large buttons" -> {property: "padding", operator: ">=", value: 16}
    """
    statement_lower = statement.lower().strip()

    # Common patterns
    patterns = [
        # Never/avoid patterns
        (r"never use (\w+)", "!="),
        (r"avoid (\w+)", "!="),
        (r"no (\w+)", "!="),
        (r"don't use (\w+)", "!="),
        # Always/prefer patterns
        (r"always use (\w+)", "="),
        (r"prefer (\w+)", "="),
        (r"use (\w+)", "="),
    ]

    # Keyword mappings
    keyword_rules = {
        "gradients": {"property": "background_style", "value": "gradient"},
        "gradient": {"property": "background_style", "value": "gradient"},
        "shadows": {"property": "shadow", "value": "none"},
        "shadow": {"property": "shadow", "value": "md"},
        "drop shadows": {"property": "shadow", "value": "lg"},
        "rounded": {"property": "border_radius", "value": 8},
        "rounded corners": {"property": "border_radius", "value": 8},
        "square": {"property": "border_radius", "value": 0},
        "square corners": {"property": "border_radius", "value": 0},
        "pill": {"property": "border_radius", "value": 9999},
        "uppercase": {"property": "text_transform", "value": "uppercase"},
        "lowercase": {"property": "text_transform", "value": "none"},
        "bold": {"property": "font_weight", "value": 700},
        "thin": {"property": "font_weight", "value": 400},
        "large": {"property": "font_size", "value": 18},
        "small": {"property": "font_size", "value": 12},
        "outline": {"property": "background_style", "value": "outline"},
        "solid": {"property": "background_style", "value": "solid"},
        "minimal": {"property": "style", "value": "minimal"},
        "floating labels": {"property": "label_position", "value": "floating"},
        "inline labels": {"property": "label_position", "value": "inline"},
    }

    # Determine operator from statement
    operator = "="
    if any(word in statement_lower for word in ["never", "avoid", "no ", "don't", "without"]):
        operator = "!="

    # Find matching keyword
    matched_rule = None
    for keyword, rule in keyword_rules.items():
        if keyword in statement_lower:
            matched_rule = rule
            break

    if matched_rule:
        return {
            "property": matched_rule["property"],
            "operator": operator,
            "value": json.dumps(matched_rule["value"]),
            "component_type": component,
            "confidence": 1.0,
            "source": "stated",
            "severity": "warning" if operator == "!=" else "info",
            "message": statement.strip()
        }

    # Default fallback - create a generic rule
    return {
        "property": "custom",
        "operator": operator,
        "value": json.dumps(statement),
        "component_type": component,
        "confidence": 1.0,
        "source": "stated",
        "severity": "info",
        "message": statement.strip()
    }


def merge_rules(extracted_rules: List[dict], stated_rules: List[dict]) -> List[dict]:
    """
    Merge extracted and stated rules, with stated rules taking priority.
    """
    # Index rules by property + component
    rule_map = {}

    # Add extracted rules first
    for rule in extracted_rules:
        key = (rule["property"], rule.get("component_type"), rule["operator"])
        rule_map[key] = rule

    # Override with stated rules
    for rule in stated_rules:
        key = (rule["property"], rule.get("component_type"), rule["operator"])
        rule_map[key] = rule

    return list(rule_map.values())


def group_rules_by_component(rules: List[dict]) -> Dict[str, List[dict]]:
    """
    Group rules by component type for display.
    """
    grouped = {"global": []}

    for rule in rules:
        component = rule.get("component_type") or "global"
        if component not in grouped:
            grouped[component] = []
        grouped[component].append(rule)

    return grouped
