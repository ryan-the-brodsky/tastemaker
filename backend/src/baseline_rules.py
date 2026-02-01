"""
Baseline rules for WCAG accessibility and Nielsen usability heuristics.
These rules are included by default in all generated skill packages.

Rule Categories (TML v2.0):
- STATIC: Visual/design rules that can be checked from a single screenshot
- TEMPORAL: Time-based rules requiring interaction measurement
- BEHAVIORAL: Interaction pattern rules
- SPATIAL: Position/size rules requiring layout analysis
- PATTERN: Dark pattern and manipulation detection
"""

WCAG_RULES = [
    {
        "id": "wcag-001",
        "rule_category": "STATIC",
        "component_type": None,
        "property": "contrast_ratio_text",
        "operator": ">=",
        "value": 4.5,
        "severity": "error",
        "message": "Text must have contrast ratio of at least 4.5:1 (WCAG AA)",
        "source": "baseline"
    },
    {
        "id": "wcag-002",
        "rule_category": "STATIC",
        "component_type": None,
        "property": "contrast_ratio_large_text",
        "operator": ">=",
        "value": 3.0,
        "severity": "error",
        "message": "Large text (18px+ or 14px+ bold) must have contrast ratio of at least 3:1 (WCAG AA)",
        "source": "baseline"
    },
    {
        "id": "wcag-003",
        "rule_category": "SPATIAL",
        "component_type": "button",
        "property": "touch_target_size",
        "operator": ">=",
        "value": 44,
        "severity": "warning",
        "message": "Touch targets should be at least 44x44px (WCAG)",
        "source": "baseline"
    },
    {
        "id": "wcag-004",
        "rule_category": "BEHAVIORAL",
        "component_type": None,
        "property": "focus_indicator",
        "operator": "!=",
        "value": "none",
        "severity": "error",
        "message": "Interactive elements must have visible focus indicators (WCAG 2.4.7)",
        "source": "baseline"
    },
    {
        "id": "wcag-005",
        "rule_category": "STATIC",
        "component_type": "input",
        "property": "label_present",
        "operator": "=",
        "value": True,
        "severity": "error",
        "message": "Form inputs must have associated labels (WCAG 1.3.1)",
        "source": "baseline"
    },
    {
        "id": "wcag-006",
        "rule_category": "STATIC",
        "component_type": None,
        "property": "color_only_indicator",
        "operator": "=",
        "value": False,
        "severity": "error",
        "message": "Color must not be the only visual means of conveying information (WCAG 1.4.1)",
        "source": "baseline"
    },
    {
        "id": "wcag-007",
        "rule_category": "STATIC",
        "component_type": "typography",
        "property": "line_height",
        "operator": ">=",
        "value": 1.5,
        "severity": "warning",
        "message": "Line height should be at least 1.5 times the font size (WCAG 1.4.12)",
        "source": "baseline"
    },
    {
        "id": "wcag-008",
        "rule_category": "STATIC",
        "component_type": "typography",
        "property": "paragraph_spacing",
        "operator": ">=",
        "value": 2.0,
        "severity": "warning",
        "message": "Paragraph spacing should be at least 2 times the font size (WCAG 1.4.12)",
        "source": "baseline"
    }
]

NIELSEN_RULES = [
    {
        "id": "nielsen-001",
        "rule_category": "BEHAVIORAL",
        "component_type": None,
        "property": "system_status_visibility",
        "operator": "=",
        "value": True,
        "severity": "warning",
        "message": "System should always keep users informed about what is going on (Nielsen #1)",
        "source": "baseline"
    },
    {
        "id": "nielsen-002",
        "rule_category": "BEHAVIORAL",
        "component_type": None,
        "property": "real_world_match",
        "operator": "=",
        "value": True,
        "severity": "info",
        "message": "Use language and concepts familiar to users, not system-oriented terms (Nielsen #2)",
        "source": "baseline"
    },
    {
        "id": "nielsen-003",
        "rule_category": "BEHAVIORAL",
        "component_type": None,
        "property": "user_control_freedom",
        "operator": "=",
        "value": True,
        "severity": "warning",
        "message": "Provide 'emergency exit' to leave unwanted states without extended dialogue (Nielsen #3)",
        "source": "baseline"
    },
    {
        "id": "nielsen-004",
        "rule_category": "BEHAVIORAL",
        "component_type": None,
        "property": "consistency_standards",
        "operator": "=",
        "value": True,
        "severity": "warning",
        "message": "Follow platform conventions; same words/actions should mean the same thing (Nielsen #4)",
        "source": "baseline"
    },
    {
        "id": "nielsen-005",
        "rule_category": "BEHAVIORAL",
        "component_type": "form",
        "property": "error_prevention",
        "operator": "=",
        "value": True,
        "severity": "warning",
        "message": "Prevent errors with careful design; eliminate error-prone conditions (Nielsen #5)",
        "source": "baseline"
    },
    {
        "id": "nielsen-006",
        "rule_category": "BEHAVIORAL",
        "component_type": None,
        "property": "recognition_over_recall",
        "operator": "=",
        "value": True,
        "severity": "info",
        "message": "Make options visible; minimize memory load between dialogue sections (Nielsen #6)",
        "source": "baseline"
    },
    {
        "id": "nielsen-007",
        "rule_category": "BEHAVIORAL",
        "component_type": None,
        "property": "flexibility_efficiency",
        "operator": "=",
        "value": True,
        "severity": "info",
        "message": "Provide accelerators for expert users without confusing novices (Nielsen #7)",
        "source": "baseline"
    },
    {
        "id": "nielsen-008",
        "rule_category": "STATIC",
        "component_type": None,
        "property": "aesthetic_minimal_design",
        "operator": "=",
        "value": True,
        "severity": "info",
        "message": "Avoid irrelevant or rarely needed information in dialogues (Nielsen #8)",
        "source": "baseline"
    },
    {
        "id": "nielsen-009",
        "rule_category": "BEHAVIORAL",
        "component_type": "feedback",
        "property": "error_recovery_help",
        "operator": "=",
        "value": True,
        "severity": "error",
        "message": "Error messages must be in plain language, indicate problem, suggest solution (Nielsen #9)",
        "source": "baseline"
    },
    {
        "id": "nielsen-010",
        "rule_category": "BEHAVIORAL",
        "component_type": None,
        "property": "help_documentation",
        "operator": "=",
        "value": True,
        "severity": "info",
        "message": "Provide help and documentation that is easy to search and task-focused (Nielsen #10)",
        "source": "baseline"
    }
]

ALL_BASELINE_RULES = WCAG_RULES + NIELSEN_RULES


def get_baseline_rules():
    """Return all baseline rules."""
    return ALL_BASELINE_RULES


def get_wcag_rules():
    """Return only WCAG accessibility rules."""
    return WCAG_RULES


def get_nielsen_rules():
    """Return only Nielsen heuristic rules."""
    return NIELSEN_RULES


def check_baseline_conflict(user_rule: dict) -> list:
    """
    Check if a user-defined rule conflicts with any baseline rule.
    Returns list of conflicting baseline rules.
    """
    conflicts = []
    for baseline in ALL_BASELINE_RULES:
        if (baseline["property"] == user_rule.get("property") and
            baseline.get("component_type") == user_rule.get("component_type")):
            # Check for value conflicts
            if baseline["operator"] in [">=", ">"] and user_rule.get("operator") in ["<=", "<", "="]:
                try:
                    if float(user_rule.get("value", 0)) < float(baseline["value"]):
                        conflicts.append(baseline)
                except (ValueError, TypeError):
                    pass
            elif baseline["operator"] == "!=" and user_rule.get("operator") == "=" and user_rule.get("value") == baseline["value"]:
                conflicts.append(baseline)
            elif baseline["operator"] == "=" and user_rule.get("operator") == "!=" and user_rule.get("value") == baseline["value"]:
                conflicts.append(baseline)
    return conflicts
