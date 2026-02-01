"""
Component variation generator for A/B comparison flow.
Generates deterministic variations without LLM calls.
"""
import random
import uuid
from typing import Dict, List, Tuple, Any

# Import color/typography generators
from palette_service import (
    generate_color_comparison,
    generate_typography_comparison,
)

# Component property ranges
BUTTON_PROPERTIES = {
    "border_radius": [0, 4, 8, 12, 16, 9999],  # px, 9999 = pill
    "padding_x": [12, 16, 20, 24, 32],
    "padding_y": [8, 10, 12, 14, 16],
    "font_weight": [400, 500, 600, 700],
    "font_size": [12, 14, 16, 18],
    "text_transform": ["none", "uppercase"],
    "shadow": ["none", "sm", "md", "lg"],
    "background_style": ["solid", "gradient", "outline"],
    "transition": ["none", "fast", "smooth"],
}

INPUT_PROPERTIES = {
    "border_radius": [0, 4, 8, 12],
    "border_width": [1, 2],
    "border_color": ["gray-300", "gray-400", "gray-500"],
    "padding_x": [12, 16, 20],
    "padding_y": [10, 12, 14],
    "font_size": [14, 16],
    "label_position": ["above", "floating", "inline"],
    "focus_ring": ["none", "thin", "thick"],
    "background": ["white", "gray-50", "transparent"],
}

CARD_PROPERTIES = {
    "border_radius": [0, 4, 8, 12, 16],
    "shadow": ["none", "sm", "md", "lg", "xl"],
    "border": ["none", "subtle", "prominent"],
    "padding": [16, 20, 24, 32],
    "background": ["white", "gray-50", "gray-100"],
    "hover_effect": ["none", "lift", "glow", "border"],
}

TYPOGRAPHY_PROPERTIES = {
    "heading_weight": [500, 600, 700, 800],
    "heading_size_scale": [1.125, 1.25, 1.333, 1.5],
    "body_line_height": [1.4, 1.5, 1.6, 1.75],
    "letter_spacing": [-0.02, 0, 0.02, 0.05],
    "font_family": ["system", "sans-serif", "serif", "mono"],
    "paragraph_spacing": [1.0, 1.5, 2.0],
}

NAVIGATION_PROPERTIES = {
    "style": ["horizontal", "vertical", "sidebar"],
    "item_padding_x": [12, 16, 20, 24],
    "item_padding_y": [8, 10, 12],
    "active_indicator": ["underline", "background", "border-left", "bold"],
    "hover_effect": ["underline", "background", "color"],
    "separator": ["none", "border", "space"],
}

FORM_PROPERTIES = {
    "layout": ["stacked", "inline", "grid"],
    "label_style": ["above", "inline", "floating"],
    "spacing": [16, 20, 24, 32],
    "error_style": ["inline", "tooltip", "border"],
    "required_indicator": ["asterisk", "text", "none"],
    "help_text_position": ["below", "tooltip"],
}

FEEDBACK_PROPERTIES = {
    "type": ["toast", "inline", "modal", "banner"],
    "position": ["top-right", "top-center", "bottom-right", "bottom-center"],
    "style": ["minimal", "bordered", "filled"],
    "icon": ["none", "left", "top"],
    "duration": [3000, 5000, 8000, "persistent"],
    "animation": ["none", "slide", "fade", "bounce"],
}

MODAL_PROPERTIES = {
    "size": ["sm", "md", "lg", "xl", "full"],
    "border_radius": [0, 8, 12, 16],
    "overlay": ["light", "medium", "dark"],
    "animation": ["none", "fade", "scale", "slide"],
    "close_button": ["icon", "text", "both"],
    "padding": [16, 24, 32],
    "header_style": ["simple", "border", "background"],
}

COMPONENT_PROPERTIES = {
    "button": BUTTON_PROPERTIES,
    "input": INPUT_PROPERTIES,
    "card": CARD_PROPERTIES,
    "typography": TYPOGRAPHY_PROPERTIES,
    "navigation": NAVIGATION_PROPERTIES,
    "form": FORM_PROPERTIES,
    "feedback": FEEDBACK_PROPERTIES,
    "modal": MODAL_PROPERTIES,
}

COMPONENT_TYPES = list(COMPONENT_PROPERTIES.keys())

CONTEXTS = ["landing_hero", "dashboard", "form_wizard", "settings"]


def generate_random_variation(component_type: str, seed: int = None) -> Dict[str, Any]:
    """Generate a random style variation for a component type."""
    if seed is not None:
        random.seed(seed)

    properties = COMPONENT_PROPERTIES.get(component_type, BUTTON_PROPERTIES)
    variation = {
        "id": str(uuid.uuid4()),
        "component_type": component_type,
        "styles": {}
    }

    for prop, values in properties.items():
        variation["styles"][prop] = random.choice(values)

    return variation


def generate_territory_mapping_pair(component_type: str, comparison_id: int) -> Tuple[Dict, Dict]:
    """
    Generate two dramatically different variations for territory mapping.
    Uses "pole" strategy: A picks from first third, B picks from last third of each property range.
    This ensures visually obvious differences for every comparison.
    """
    properties = COMPONENT_PROPERTIES.get(component_type, BUTTON_PROPERTIES)
    random.seed(comparison_id * 1000)

    var_a = {
        "id": str(uuid.uuid4()),
        "component_type": component_type,
        "styles": {}
    }
    var_b = {
        "id": str(uuid.uuid4()),
        "component_type": component_type,
        "styles": {}
    }

    for prop, values in properties.items():
        if len(values) <= 2:
            # For binary properties, just pick opposites
            var_a["styles"][prop] = values[0]
            var_b["styles"][prop] = values[-1]
        else:
            # For multi-value properties, pick from opposite ends
            # First third for A, last third for B, with some randomness within those thirds
            third = max(1, len(values) // 3)

            # A picks from first third (indices 0 to third-1)
            a_candidates = values[:third]
            # B picks from last third (indices -third to end)
            b_candidates = values[-third:]

            var_a["styles"][prop] = random.choice(a_candidates)
            var_b["styles"][prop] = random.choice(b_candidates)

    # Randomly swap A and B for some properties to avoid A always being "minimal" and B always "maximal"
    random.seed(comparison_id * 1000 + 123)
    for prop in properties.keys():
        if random.random() < 0.4:  # 40% chance to swap
            var_a["styles"][prop], var_b["styles"][prop] = var_b["styles"][prop], var_a["styles"][prop]

    return var_a, var_b


def generate_dimension_isolation_pair(
    component_type: str,
    base_styles: Dict[str, Any],
    property_to_test: str,
    comparison_id: int
) -> Tuple[Dict, Dict]:
    """
    Generate two variations that differ in exactly one property.
    Used for dimension isolation phase.
    """
    properties = COMPONENT_PROPERTIES.get(component_type, {})
    values = properties.get(property_to_test, [])

    if len(values) < 2:
        return generate_territory_mapping_pair(component_type, comparison_id)

    # Create two variations with same base but different value for target property
    var_a = {
        "id": str(uuid.uuid4()),
        "component_type": component_type,
        "styles": base_styles.copy()
    }
    var_b = {
        "id": str(uuid.uuid4()),
        "component_type": component_type,
        "styles": base_styles.copy()
    }

    # Select two different values for the property
    random.seed(comparison_id)
    value_indices = random.sample(range(len(values)), min(2, len(values)))
    var_a["styles"][property_to_test] = values[value_indices[0]]
    var_b["styles"][property_to_test] = values[value_indices[1] if len(value_indices) > 1 else 0]

    return var_a, var_b


def get_context_for_component(component_type: str) -> str:
    """Get appropriate context template for component type."""
    context_mapping = {
        "button": "landing_hero",
        "input": "form_wizard",
        "card": "dashboard",
        "typography": "landing_hero",
        "navigation": "dashboard",
        "form": "form_wizard",
        "feedback": "settings",
        "modal": "settings",
    }
    return context_mapping.get(component_type, "dashboard")


def get_next_component_type(comparison_count: int) -> str:
    """Cycle through component types based on comparison count."""
    return COMPONENT_TYPES[comparison_count % len(COMPONENT_TYPES)]


def generate_comparison(
    session_phase: str,
    comparison_count: int,
    base_styles: Dict[str, Any] = None,
    property_to_test: str = None
) -> Dict:
    """
    Generate a comparison based on current phase and count.

    Args:
        session_phase: Current extraction phase
        comparison_count: Number of comparisons completed
        base_styles: Base styles for dimension isolation
        property_to_test: Property to isolate in dimension isolation

    Returns:
        Comparison dict with option_a, option_b, component_type, context
    """
    # Handle color exploration phase
    if session_phase == "color_exploration":
        return generate_color_comparison(comparison_count)

    # Handle typography exploration phase
    if session_phase == "typography_exploration":
        return generate_typography_comparison(comparison_count)

    # Handle component phases (territory_mapping, dimension_isolation)
    component_type = get_next_component_type(comparison_count)
    context = get_context_for_component(component_type)

    comparison_id = comparison_count + 1

    if session_phase == "territory_mapping":
        var_a, var_b = generate_territory_mapping_pair(component_type, comparison_id)
    elif session_phase == "dimension_isolation" and base_styles and property_to_test:
        var_a, var_b = generate_dimension_isolation_pair(
            component_type, base_styles, property_to_test, comparison_id
        )
    else:
        var_a, var_b = generate_territory_mapping_pair(component_type, comparison_id)

    return {
        "comparison_id": comparison_id,
        "component_type": component_type,
        "phase": session_phase,
        "option_a": {
            "id": var_a["id"],
            "styles": var_a["styles"]
        },
        "option_b": {
            "id": var_b["id"],
            "styles": var_b["styles"]
        },
        "context": context
    }


def get_properties_for_component(component_type: str) -> List[str]:
    """Get list of property names for a component type."""
    return list(COMPONENT_PROPERTIES.get(component_type, {}).keys())


def get_property_values(component_type: str, property_name: str) -> List[Any]:
    """Get possible values for a property."""
    return COMPONENT_PROPERTIES.get(component_type, {}).get(property_name, [])
