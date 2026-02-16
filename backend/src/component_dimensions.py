"""
Component Studio dimension definitions.

Defines all 12 component types, their customizable dimensions,
option values, and checkpoint groupings for the Component Studio flow.
"""
from typing import Dict, List, Any

# Ordered list of component types for the studio flow
COMPONENT_TYPES: List[str] = [
    "button", "input", "card", "typography",
    "navigation", "form", "modal", "feedback",
    "table", "badge", "tabs", "toggle",
]

# Checkpoint groups: full-page mockup reviews after every 4 components
CHECKPOINT_GROUPS: List[Dict[str, Any]] = [
    {
        "id": "checkpoint_1",
        "components": ["button", "input", "card", "typography"],
        "mockup_type": "landing",
        "label": "Landing Page Review",
        "description": "Review how your button, input, card, and typography choices look together on a landing page.",
    },
    {
        "id": "checkpoint_2",
        "components": ["navigation", "form", "modal", "feedback"],
        "mockup_type": "dashboard",
        "label": "Dashboard Review",
        "description": "Review how your navigation, form, modal, and feedback choices look together on a dashboard.",
    },
    {
        "id": "checkpoint_3",
        "components": ["table", "badge", "tabs", "toggle"],
        "mockup_type": "settings",
        "label": "Settings Page Review",
        "description": "Review how your table, badge, tabs, and toggle choices look together on a settings page.",
    },
]


def get_checkpoint_for_component(component_type: str) -> Dict[str, Any] | None:
    """Return the checkpoint group that a component belongs to, or None."""
    for group in CHECKPOINT_GROUPS:
        if component_type in group["components"]:
            return group
    return None


def is_checkpoint_trigger(component_type: str) -> bool:
    """Return True if completing this component should trigger a checkpoint review."""
    for group in CHECKPOINT_GROUPS:
        if group["components"][-1] == component_type:
            return True
    return False


# ============================================================================
# DIMENSION DEFINITIONS PER COMPONENT TYPE
# ============================================================================

COMPONENT_DIMENSIONS: Dict[str, List[Dict[str, Any]]] = {
    # ------------------------------------------------------------------
    # 1. BUTTON
    # ------------------------------------------------------------------
    "button": [
        {
            "key": "border_radius",
            "label": "Corner Style",
            "css_property": "borderRadius",
            "options": [
                {"id": "sharp", "label": "Sharp", "value": "0px"},
                {"id": "rounded", "label": "Rounded", "value": "8px"},
                {"id": "pill", "label": "Pill", "value": "9999px"},
            ],
            "fine_tune": {"min": 0, "max": 24, "step": 1, "unit": "px"},
            "order": 1,
        },
        {
            "key": "shadow",
            "label": "Shadow",
            "css_property": "boxShadow",
            "options": [
                {"id": "none", "label": "None", "value": "none"},
                {"id": "subtle", "label": "Subtle", "value": "0 1px 3px rgba(0,0,0,0.12)"},
                {"id": "medium", "label": "Medium", "value": "0 4px 6px rgba(0,0,0,0.1)"},
                {"id": "strong", "label": "Strong", "value": "0 10px 25px rgba(0,0,0,0.15)"},
            ],
            "order": 2,
        },
        {
            "key": "padding",
            "label": "Padding",
            "css_property": "padding",
            "options": [
                {"id": "compact", "label": "Compact", "value": "6px 12px"},
                {"id": "normal", "label": "Normal", "value": "10px 20px"},
                {"id": "spacious", "label": "Spacious", "value": "14px 28px"},
            ],
            "order": 3,
        },
        {
            "key": "font_weight",
            "label": "Font Weight",
            "css_property": "fontWeight",
            "options": [
                {"id": "normal", "label": "Normal", "value": "400"},
                {"id": "medium", "label": "Medium", "value": "500"},
                {"id": "semibold", "label": "Semi-Bold", "value": "600"},
                {"id": "bold", "label": "Bold", "value": "700"},
            ],
            "order": 4,
        },
        {
            "key": "font_size",
            "label": "Font Size",
            "css_property": "fontSize",
            "options": [
                {"id": "small", "label": "Small", "value": "13px"},
                {"id": "normal", "label": "Normal", "value": "15px"},
                {"id": "large", "label": "Large", "value": "17px"},
            ],
            "fine_tune": {"min": 12, "max": 20, "step": 1, "unit": "px"},
            "order": 5,
        },
        {
            "key": "text_transform",
            "label": "Text Case",
            "css_property": "textTransform",
            "options": [
                {"id": "none", "label": "Normal", "value": "none"},
                {"id": "uppercase", "label": "Uppercase", "value": "uppercase"},
            ],
            "order": 6,
        },
        {
            "key": "border",
            "label": "Border",
            "css_property": "border",
            "options": [
                {"id": "none", "label": "None", "value": "none"},
                {"id": "thin", "label": "Thin", "value": "1px solid"},
                {"id": "medium", "label": "Medium", "value": "2px solid"},
            ],
            "order": 7,
        },
        {
            "key": "background_style",
            "label": "Background Style",
            "css_property": "backgroundStyle",
            "options": [
                {"id": "solid", "label": "Solid", "value": "solid"},
                {"id": "outline", "label": "Outline", "value": "outline"},
                {"id": "ghost", "label": "Ghost", "value": "ghost"},
            ],
            "order": 8,
        },
        {
            "key": "hover_effect",
            "label": "Hover Effect",
            "css_property": "hoverEffect",
            "options": [
                {"id": "darken", "label": "Darken", "value": "darken"},
                {"id": "lighten", "label": "Lighten", "value": "lighten"},
                {"id": "lift", "label": "Lift (Shadow)", "value": "lift"},
                {"id": "scale", "label": "Scale Up", "value": "scale"},
            ],
            "order": 9,
        },
    ],

    # ------------------------------------------------------------------
    # 2. INPUT
    # ------------------------------------------------------------------
    "input": [
        {
            "key": "border_radius",
            "label": "Corner Style",
            "css_property": "borderRadius",
            "options": [
                {"id": "sharp", "label": "Sharp", "value": "0px"},
                {"id": "rounded", "label": "Rounded", "value": "6px"},
                {"id": "pill", "label": "Pill", "value": "9999px"},
            ],
            "fine_tune": {"min": 0, "max": 20, "step": 1, "unit": "px"},
            "order": 1,
        },
        {
            "key": "border_width",
            "label": "Border Width",
            "css_property": "borderWidth",
            "options": [
                {"id": "thin", "label": "Thin", "value": "1px"},
                {"id": "medium", "label": "Medium", "value": "2px"},
                {"id": "thick", "label": "Thick", "value": "3px"},
            ],
            "order": 2,
        },
        {
            "key": "padding",
            "label": "Padding",
            "css_property": "padding",
            "options": [
                {"id": "compact", "label": "Compact", "value": "8px 10px"},
                {"id": "normal", "label": "Normal", "value": "10px 14px"},
                {"id": "spacious", "label": "Spacious", "value": "14px 18px"},
            ],
            "order": 3,
        },
        {
            "key": "font_size",
            "label": "Font Size",
            "css_property": "fontSize",
            "options": [
                {"id": "small", "label": "Small", "value": "13px"},
                {"id": "normal", "label": "Normal", "value": "15px"},
                {"id": "large", "label": "Large", "value": "17px"},
            ],
            "fine_tune": {"min": 12, "max": 20, "step": 1, "unit": "px"},
            "order": 4,
        },
        {
            "key": "label_position",
            "label": "Label Position",
            "css_property": "labelPosition",
            "options": [
                {"id": "above", "label": "Above", "value": "above"},
                {"id": "floating", "label": "Floating", "value": "floating"},
                {"id": "inline", "label": "Inline", "value": "inline"},
            ],
            "order": 5,
        },
        {
            "key": "focus_ring",
            "label": "Focus Ring",
            "css_property": "focusRing",
            "options": [
                {"id": "none", "label": "None", "value": "none"},
                {"id": "subtle", "label": "Subtle", "value": "0 0 0 2px"},
                {"id": "strong", "label": "Strong", "value": "0 0 0 3px"},
            ],
            "order": 6,
        },
        {
            "key": "background",
            "label": "Background",
            "css_property": "inputBackground",
            "options": [
                {"id": "white", "label": "White", "value": "#ffffff"},
                {"id": "light_gray", "label": "Light Gray", "value": "#f9fafb"},
                {"id": "transparent", "label": "Transparent", "value": "transparent"},
            ],
            "order": 7,
        },
    ],

    # ------------------------------------------------------------------
    # 3. CARD
    # ------------------------------------------------------------------
    "card": [
        {
            "key": "border_radius",
            "label": "Corner Style",
            "css_property": "borderRadius",
            "options": [
                {"id": "sharp", "label": "Sharp", "value": "0px"},
                {"id": "rounded", "label": "Rounded", "value": "8px"},
                {"id": "extra_rounded", "label": "Extra Rounded", "value": "16px"},
            ],
            "fine_tune": {"min": 0, "max": 24, "step": 1, "unit": "px"},
            "order": 1,
        },
        {
            "key": "shadow",
            "label": "Shadow",
            "css_property": "boxShadow",
            "options": [
                {"id": "none", "label": "None", "value": "none"},
                {"id": "subtle", "label": "Subtle", "value": "0 1px 3px rgba(0,0,0,0.08)"},
                {"id": "medium", "label": "Medium", "value": "0 4px 12px rgba(0,0,0,0.1)"},
                {"id": "strong", "label": "Strong", "value": "0 8px 30px rgba(0,0,0,0.12)"},
            ],
            "order": 2,
        },
        {
            "key": "border",
            "label": "Border",
            "css_property": "border",
            "options": [
                {"id": "none", "label": "None", "value": "none"},
                {"id": "subtle", "label": "Subtle", "value": "1px solid #e5e7eb"},
                {"id": "accent", "label": "Accent", "value": "1px solid"},
            ],
            "order": 3,
        },
        {
            "key": "padding",
            "label": "Padding",
            "css_property": "padding",
            "options": [
                {"id": "compact", "label": "Compact", "value": "16px"},
                {"id": "normal", "label": "Normal", "value": "24px"},
                {"id": "spacious", "label": "Spacious", "value": "32px"},
            ],
            "fine_tune": {"min": 12, "max": 40, "step": 2, "unit": "px"},
            "order": 4,
        },
        {
            "key": "background",
            "label": "Background",
            "css_property": "backgroundColor",
            "options": [
                {"id": "white", "label": "White", "value": "#ffffff"},
                {"id": "light", "label": "Light Tint", "value": "#f9fafb"},
                {"id": "transparent", "label": "Transparent", "value": "transparent"},
            ],
            "order": 5,
        },
        {
            "key": "hover_effect",
            "label": "Hover Effect",
            "css_property": "hoverEffect",
            "options": [
                {"id": "none", "label": "None", "value": "none"},
                {"id": "lift", "label": "Lift", "value": "lift"},
                {"id": "glow", "label": "Glow", "value": "glow"},
                {"id": "border_accent", "label": "Border Accent", "value": "border_accent"},
            ],
            "order": 6,
        },
    ],

    # ------------------------------------------------------------------
    # 4. TYPOGRAPHY
    # ------------------------------------------------------------------
    "typography": [
        {
            "key": "heading_weight",
            "label": "Heading Weight",
            "css_property": "headingFontWeight",
            "options": [
                {"id": "medium", "label": "Medium", "value": "500"},
                {"id": "semibold", "label": "Semi-Bold", "value": "600"},
                {"id": "bold", "label": "Bold", "value": "700"},
                {"id": "extrabold", "label": "Extra Bold", "value": "800"},
            ],
            "order": 1,
        },
        {
            "key": "heading_size_scale",
            "label": "Heading Size Scale",
            "css_property": "headingSizeScale",
            "options": [
                {"id": "compact", "label": "Compact", "value": "1.125"},
                {"id": "normal", "label": "Normal", "value": "1.25"},
                {"id": "large", "label": "Large", "value": "1.5"},
            ],
            "order": 2,
        },
        {
            "key": "body_line_height",
            "label": "Body Line Height",
            "css_property": "lineHeight",
            "options": [
                {"id": "tight", "label": "Tight", "value": "1.4"},
                {"id": "normal", "label": "Normal", "value": "1.6"},
                {"id": "relaxed", "label": "Relaxed", "value": "1.8"},
            ],
            "order": 3,
        },
        {
            "key": "letter_spacing",
            "label": "Letter Spacing",
            "css_property": "letterSpacing",
            "options": [
                {"id": "tight", "label": "Tight", "value": "-0.025em"},
                {"id": "normal", "label": "Normal", "value": "0"},
                {"id": "wide", "label": "Wide", "value": "0.05em"},
            ],
            "order": 4,
        },
        {
            "key": "paragraph_spacing",
            "label": "Paragraph Spacing",
            "css_property": "paragraphSpacing",
            "options": [
                {"id": "compact", "label": "Compact", "value": "0.75em"},
                {"id": "normal", "label": "Normal", "value": "1em"},
                {"id": "spacious", "label": "Spacious", "value": "1.5em"},
            ],
            "order": 5,
        },
    ],

    # ------------------------------------------------------------------
    # 5. NAVIGATION
    # ------------------------------------------------------------------
    "navigation": [
        {
            "key": "style",
            "label": "Layout Style",
            "css_property": "navStyle",
            "options": [
                {"id": "horizontal", "label": "Horizontal", "value": "horizontal"},
                {"id": "vertical", "label": "Vertical", "value": "vertical"},
                {"id": "sidebar", "label": "Sidebar", "value": "sidebar"},
            ],
            "order": 1,
        },
        {
            "key": "item_padding",
            "label": "Item Padding",
            "css_property": "navItemPadding",
            "options": [
                {"id": "compact", "label": "Compact", "value": "6px 12px"},
                {"id": "normal", "label": "Normal", "value": "8px 16px"},
                {"id": "spacious", "label": "Spacious", "value": "12px 24px"},
            ],
            "order": 2,
        },
        {
            "key": "active_indicator",
            "label": "Active Indicator",
            "css_property": "activeIndicator",
            "options": [
                {"id": "underline", "label": "Underline", "value": "underline"},
                {"id": "background", "label": "Background", "value": "background"},
                {"id": "border_left", "label": "Left Border", "value": "border_left"},
                {"id": "bold", "label": "Bold Text", "value": "bold"},
            ],
            "order": 3,
        },
        {
            "key": "font_weight",
            "label": "Font Weight",
            "css_property": "fontWeight",
            "options": [
                {"id": "normal", "label": "Normal", "value": "400"},
                {"id": "medium", "label": "Medium", "value": "500"},
                {"id": "semibold", "label": "Semi-Bold", "value": "600"},
            ],
            "order": 4,
        },
        {
            "key": "separator",
            "label": "Separator",
            "css_property": "navSeparator",
            "options": [
                {"id": "none", "label": "None", "value": "none"},
                {"id": "line", "label": "Line", "value": "line"},
                {"id": "dot", "label": "Dot", "value": "dot"},
            ],
            "order": 5,
        },
    ],

    # ------------------------------------------------------------------
    # 6. FORM
    # ------------------------------------------------------------------
    "form": [
        {
            "key": "field_spacing",
            "label": "Field Spacing",
            "css_property": "fieldSpacing",
            "options": [
                {"id": "compact", "label": "Compact", "value": "12px"},
                {"id": "normal", "label": "Normal", "value": "20px"},
                {"id": "spacious", "label": "Spacious", "value": "28px"},
            ],
            "fine_tune": {"min": 8, "max": 36, "step": 2, "unit": "px"},
            "order": 1,
        },
        {
            "key": "label_style",
            "label": "Label Style",
            "css_property": "labelStyle",
            "options": [
                {"id": "default", "label": "Default", "value": "default"},
                {"id": "bold", "label": "Bold", "value": "bold"},
                {"id": "uppercase", "label": "Uppercase", "value": "uppercase"},
                {"id": "small_caps", "label": "Small Caps", "value": "small_caps"},
            ],
            "order": 2,
        },
        {
            "key": "required_indicator",
            "label": "Required Indicator",
            "css_property": "requiredIndicator",
            "options": [
                {"id": "asterisk", "label": "Asterisk *", "value": "asterisk"},
                {"id": "text", "label": "Text (required)", "value": "text"},
                {"id": "color", "label": "Color Highlight", "value": "color"},
            ],
            "order": 3,
        },
        {
            "key": "error_style",
            "label": "Error Style",
            "css_property": "errorStyle",
            "options": [
                {"id": "below", "label": "Text Below", "value": "below"},
                {"id": "inline", "label": "Inline", "value": "inline"},
                {"id": "border", "label": "Border Only", "value": "border"},
            ],
            "order": 4,
        },
        {
            "key": "group_style",
            "label": "Group Style",
            "css_property": "groupStyle",
            "options": [
                {"id": "none", "label": "None", "value": "none"},
                {"id": "card", "label": "Card", "value": "card"},
                {"id": "divider", "label": "Divider", "value": "divider"},
            ],
            "order": 5,
        },
    ],

    # ------------------------------------------------------------------
    # 7. MODAL
    # ------------------------------------------------------------------
    "modal": [
        {
            "key": "border_radius",
            "label": "Corner Style",
            "css_property": "borderRadius",
            "options": [
                {"id": "sharp", "label": "Sharp", "value": "0px"},
                {"id": "rounded", "label": "Rounded", "value": "12px"},
                {"id": "extra_rounded", "label": "Extra Rounded", "value": "20px"},
            ],
            "fine_tune": {"min": 0, "max": 28, "step": 2, "unit": "px"},
            "order": 1,
        },
        {
            "key": "shadow",
            "label": "Shadow",
            "css_property": "boxShadow",
            "options": [
                {"id": "subtle", "label": "Subtle", "value": "0 4px 12px rgba(0,0,0,0.15)"},
                {"id": "medium", "label": "Medium", "value": "0 10px 40px rgba(0,0,0,0.2)"},
                {"id": "strong", "label": "Strong", "value": "0 20px 60px rgba(0,0,0,0.3)"},
            ],
            "order": 2,
        },
        {
            "key": "overlay_opacity",
            "label": "Overlay Darkness",
            "css_property": "overlayOpacity",
            "options": [
                {"id": "light", "label": "Light", "value": "0.3"},
                {"id": "medium", "label": "Medium", "value": "0.5"},
                {"id": "dark", "label": "Dark", "value": "0.7"},
            ],
            "order": 3,
        },
        {
            "key": "width",
            "label": "Width",
            "css_property": "modalWidth",
            "options": [
                {"id": "narrow", "label": "Narrow", "value": "400px"},
                {"id": "medium", "label": "Medium", "value": "560px"},
                {"id": "wide", "label": "Wide", "value": "720px"},
            ],
            "order": 4,
        },
        {
            "key": "padding",
            "label": "Padding",
            "css_property": "padding",
            "options": [
                {"id": "compact", "label": "Compact", "value": "20px"},
                {"id": "normal", "label": "Normal", "value": "32px"},
                {"id": "spacious", "label": "Spacious", "value": "40px"},
            ],
            "fine_tune": {"min": 16, "max": 48, "step": 4, "unit": "px"},
            "order": 5,
        },
        {
            "key": "close_button_style",
            "label": "Close Button",
            "css_property": "closeButtonStyle",
            "options": [
                {"id": "icon", "label": "X Icon", "value": "icon"},
                {"id": "text", "label": "Text", "value": "text"},
                {"id": "outside", "label": "Outside", "value": "outside"},
            ],
            "order": 6,
        },
    ],

    # ------------------------------------------------------------------
    # 8. FEEDBACK
    # ------------------------------------------------------------------
    "feedback": [
        {
            "key": "style",
            "label": "Display Style",
            "css_property": "feedbackStyle",
            "options": [
                {"id": "toast", "label": "Toast", "value": "toast"},
                {"id": "inline", "label": "Inline", "value": "inline"},
                {"id": "banner", "label": "Banner", "value": "banner"},
            ],
            "order": 1,
        },
        {
            "key": "border_radius",
            "label": "Corner Style",
            "css_property": "borderRadius",
            "options": [
                {"id": "sharp", "label": "Sharp", "value": "0px"},
                {"id": "rounded", "label": "Rounded", "value": "8px"},
                {"id": "pill", "label": "Pill", "value": "9999px"},
            ],
            "fine_tune": {"min": 0, "max": 20, "step": 1, "unit": "px"},
            "order": 2,
        },
        {
            "key": "icon_style",
            "label": "Icon Style",
            "css_property": "iconStyle",
            "options": [
                {"id": "none", "label": "None", "value": "none"},
                {"id": "outline", "label": "Outline", "value": "outline"},
                {"id": "filled", "label": "Filled", "value": "filled"},
            ],
            "order": 3,
        },
        {
            "key": "position",
            "label": "Position",
            "css_property": "feedbackPosition",
            "options": [
                {"id": "top_right", "label": "Top Right", "value": "top_right"},
                {"id": "top_center", "label": "Top Center", "value": "top_center"},
                {"id": "bottom_right", "label": "Bottom Right", "value": "bottom_right"},
                {"id": "bottom_center", "label": "Bottom Center", "value": "bottom_center"},
            ],
            "order": 4,
        },
        {
            "key": "animation",
            "label": "Animation",
            "css_property": "feedbackAnimation",
            "options": [
                {"id": "none", "label": "None", "value": "none"},
                {"id": "slide", "label": "Slide In", "value": "slide"},
                {"id": "fade", "label": "Fade", "value": "fade"},
            ],
            "order": 5,
        },
    ],

    # ------------------------------------------------------------------
    # 9. TABLE
    # ------------------------------------------------------------------
    "table": [
        {
            "key": "border_style",
            "label": "Border Style",
            "css_property": "tableBorderStyle",
            "options": [
                {"id": "none", "label": "None", "value": "none"},
                {"id": "horizontal", "label": "Horizontal Lines", "value": "horizontal"},
                {"id": "full", "label": "Full Grid", "value": "full"},
            ],
            "order": 1,
        },
        {
            "key": "row_striping",
            "label": "Row Striping",
            "css_property": "rowStriping",
            "options": [
                {"id": "none", "label": "None", "value": "none"},
                {"id": "even", "label": "Even Rows", "value": "even"},
                {"id": "odd", "label": "Odd Rows", "value": "odd"},
            ],
            "order": 2,
        },
        {
            "key": "header_style",
            "label": "Header Style",
            "css_property": "tableHeaderStyle",
            "options": [
                {"id": "plain", "label": "Plain", "value": "plain"},
                {"id": "bold", "label": "Bold", "value": "bold"},
                {"id": "shaded", "label": "Shaded", "value": "shaded"},
            ],
            "order": 3,
        },
        {
            "key": "cell_padding",
            "label": "Cell Padding",
            "css_property": "cellPadding",
            "options": [
                {"id": "compact", "label": "Compact", "value": "8px 12px"},
                {"id": "normal", "label": "Normal", "value": "12px 16px"},
                {"id": "spacious", "label": "Spacious", "value": "16px 24px"},
            ],
            "order": 4,
        },
        {
            "key": "hover_row",
            "label": "Row Hover",
            "css_property": "hoverRow",
            "options": [
                {"id": "none", "label": "None", "value": "none"},
                {"id": "highlight", "label": "Highlight", "value": "highlight"},
                {"id": "accent", "label": "Accent", "value": "accent"},
            ],
            "order": 5,
        },
    ],

    # ------------------------------------------------------------------
    # 10. BADGE
    # ------------------------------------------------------------------
    "badge": [
        {
            "key": "border_radius",
            "label": "Corner Style",
            "css_property": "borderRadius",
            "options": [
                {"id": "sharp", "label": "Sharp", "value": "0px"},
                {"id": "rounded", "label": "Rounded", "value": "6px"},
                {"id": "pill", "label": "Pill", "value": "9999px"},
            ],
            "fine_tune": {"min": 0, "max": 20, "step": 1, "unit": "px"},
            "order": 1,
        },
        {
            "key": "padding",
            "label": "Padding",
            "css_property": "padding",
            "options": [
                {"id": "compact", "label": "Compact", "value": "2px 6px"},
                {"id": "normal", "label": "Normal", "value": "4px 10px"},
                {"id": "spacious", "label": "Spacious", "value": "6px 14px"},
            ],
            "order": 2,
        },
        {
            "key": "font_size",
            "label": "Font Size",
            "css_property": "fontSize",
            "options": [
                {"id": "small", "label": "Small", "value": "11px"},
                {"id": "normal", "label": "Normal", "value": "13px"},
                {"id": "large", "label": "Large", "value": "15px"},
            ],
            "order": 3,
        },
        {
            "key": "font_weight",
            "label": "Font Weight",
            "css_property": "fontWeight",
            "options": [
                {"id": "normal", "label": "Normal", "value": "400"},
                {"id": "medium", "label": "Medium", "value": "500"},
                {"id": "semibold", "label": "Semi-Bold", "value": "600"},
            ],
            "order": 4,
        },
        {
            "key": "style",
            "label": "Visual Style",
            "css_property": "badgeStyle",
            "options": [
                {"id": "solid", "label": "Solid", "value": "solid"},
                {"id": "outline", "label": "Outline", "value": "outline"},
                {"id": "subtle", "label": "Subtle", "value": "subtle"},
            ],
            "order": 5,
        },
    ],

    # ------------------------------------------------------------------
    # 11. TABS
    # ------------------------------------------------------------------
    "tabs": [
        {
            "key": "style",
            "label": "Tab Style",
            "css_property": "tabStyle",
            "options": [
                {"id": "underline", "label": "Underline", "value": "underline"},
                {"id": "boxed", "label": "Boxed", "value": "boxed"},
                {"id": "pill", "label": "Pill", "value": "pill"},
            ],
            "order": 1,
        },
        {
            "key": "spacing",
            "label": "Tab Spacing",
            "css_property": "tabSpacing",
            "options": [
                {"id": "compact", "label": "Compact", "value": "4px"},
                {"id": "normal", "label": "Normal", "value": "8px"},
                {"id": "spacious", "label": "Spacious", "value": "16px"},
            ],
            "order": 2,
        },
        {
            "key": "font_weight",
            "label": "Font Weight",
            "css_property": "fontWeight",
            "options": [
                {"id": "normal", "label": "Normal", "value": "400"},
                {"id": "medium", "label": "Medium", "value": "500"},
                {"id": "semibold", "label": "Semi-Bold", "value": "600"},
            ],
            "order": 3,
        },
        {
            "key": "indicator_style",
            "label": "Active Indicator",
            "css_property": "tabIndicatorStyle",
            "options": [
                {"id": "thin", "label": "Thin Line", "value": "thin"},
                {"id": "thick", "label": "Thick Line", "value": "thick"},
                {"id": "full", "label": "Full Background", "value": "full"},
            ],
            "order": 4,
        },
    ],

    # ------------------------------------------------------------------
    # 12. TOGGLE
    # ------------------------------------------------------------------
    "toggle": [
        {
            "key": "size",
            "label": "Size",
            "css_property": "toggleSize",
            "options": [
                {"id": "small", "label": "Small", "value": "small"},
                {"id": "medium", "label": "Medium", "value": "medium"},
                {"id": "large", "label": "Large", "value": "large"},
            ],
            "order": 1,
        },
        {
            "key": "border_radius",
            "label": "Corner Style",
            "css_property": "borderRadius",
            "options": [
                {"id": "sharp", "label": "Square", "value": "4px"},
                {"id": "rounded", "label": "Rounded", "value": "9999px"},
            ],
            "order": 2,
        },
        {
            "key": "label_position",
            "label": "Label Position",
            "css_property": "toggleLabelPosition",
            "options": [
                {"id": "left", "label": "Left", "value": "left"},
                {"id": "right", "label": "Right", "value": "right"},
            ],
            "order": 3,
        },
        {
            "key": "animation_style",
            "label": "Animation",
            "css_property": "toggleAnimation",
            "options": [
                {"id": "none", "label": "None", "value": "none"},
                {"id": "slide", "label": "Slide", "value": "slide"},
                {"id": "bounce", "label": "Bounce", "value": "bounce"},
            ],
            "order": 4,
        },
    ],
}


def get_dimensions_for_component(component_type: str) -> List[Dict[str, Any]]:
    """Get the dimension definitions for a given component type."""
    return COMPONENT_DIMENSIONS.get(component_type, [])


def get_component_label(component_type: str) -> str:
    """Get a human-readable label for a component type."""
    labels = {
        "button": "Button",
        "input": "Input",
        "card": "Card",
        "typography": "Typography",
        "navigation": "Navigation",
        "form": "Form Layout",
        "modal": "Modal / Dialog",
        "feedback": "Feedback / Notifications",
        "table": "Table",
        "badge": "Badge",
        "tabs": "Tabs",
        "toggle": "Toggle / Switch",
    }
    return labels.get(component_type, component_type.title())
