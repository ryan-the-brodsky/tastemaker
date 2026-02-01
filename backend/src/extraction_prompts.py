"""
Claude Extraction Prompts for Interactive UX Audits

These prompts are used with Claude Vision to extract measurable values
from UI screenshots for rule validation. The extraction is deterministic
once values are extracted - Claude extracts, rules engine validates.

Prompt Categories:
1. STATIC_EXTRACTION: Single screenshot analysis
2. TEMPORAL_COMPARISON: Comparing two sequential frames
3. SPATIAL_ANALYSIS: Element positions and sizes
4. PATTERN_DETECTION: Dark pattern indicators
5. BEHAVIORAL_STATE: Form states, loading, errors
"""

from typing import Dict, Any


# ============================================================================
# COMPREHENSIVE FRAME EXTRACTION PROMPT
# Used for each keyframe to extract all measurable UX properties
# ============================================================================

INTERACTIVE_EXTRACTION_PROMPT = """Analyze this UI screenshot and extract the following measurements for UX rule validation.
Return a JSON object with these exact keys. Use null for values you cannot determine.

## 1. SPATIAL MEASUREMENTS (Fitts's Law)

```json
{
  "spatial": {
    "touch_targets": [
      {
        "element_type": "button|link|input|checkbox",
        "label": "element text or aria-label",
        "width_px": number,
        "height_px": number,
        "position": {"x": number, "y": number},
        "is_primary_cta": boolean
      }
    ],
    "button_spacing_min_px": number,
    "form_to_submit_distance_px": number or null,
    "destructive_button_spacing_px": number or null,
    "close_button_corner_distance_px": number or null
  }
}
```

## 2. COUNT PROPERTIES (Hick's Law / Miller's Law)

```json
{
  "counts": {
    "primary_nav_items": number,
    "dropdown_options_visible": number or null,
    "visible_form_fields": number,
    "form_fields_per_section": number,
    "wizard_steps_total": number or null,
    "wizard_current_step": number or null,
    "breadcrumb_levels": number or null,
    "primary_action_buttons": number,
    "tab_count": number or null,
    "list_items_visible": number or null
  }
}
```

## 3. STATE DETECTION (Loading, Empty, Error)

```json
{
  "states": {
    "has_loading_indicator": boolean,
    "loading_type": "spinner|skeleton|progress_bar|none",
    "has_empty_state": boolean,
    "empty_state_has_cta": boolean or null,
    "empty_state_has_explanation": boolean or null,
    "has_error_messages": boolean,
    "error_messages": [
      {
        "text": "error message text",
        "distance_from_field_px": number,
        "uses_color_only": boolean,
        "has_icon": boolean
      }
    ],
    "has_success_feedback": boolean,
    "form_state": "idle|validating|submitting|success|error"
  }
}
```

## 4. DARK PATTERN INDICATORS

```json
{
  "dark_patterns": {
    "decline_button_texts": ["exact text of any decline/cancel buttons"],
    "has_shame_language": boolean,
    "shame_indicators": ["any phrases that shame the user"],
    "has_preselected_checkboxes": boolean,
    "preselected_checkbox_labels": ["labels of pre-checked optional items"],
    "has_fake_urgency": boolean,
    "urgency_text": "countdown or scarcity text if present",
    "primary_style_on_unwanted": boolean,
    "double_negative_labels": boolean,
    "hidden_costs_detected": boolean
  }
}
```

## 5. MOBILE LAYOUT (if mobile viewport)

```json
{
  "mobile": {
    "is_mobile_viewport": boolean,
    "viewport_width_px": number,
    "primary_cta_position": "top|middle|bottom",
    "primary_cta_in_thumb_zone": boolean,
    "nav_position": "top|bottom",
    "frequent_actions_in_corners": boolean
  }
}
```

## 6. COGNITIVE ACCESSIBILITY

```json
{
  "cognitive": {
    "button_labels": ["list of all button labels"],
    "button_labels_are_verbs": boolean,
    "visible_text_sample": "first 200 chars of visible body text",
    "has_jargon": boolean,
    "jargon_terms_found": ["technical terms detected"]
  }
}
```

## 7. GENERAL UI STATE

```json
{
  "ui_state": {
    "current_url": "URL if visible in browser chrome",
    "page_title": "visible page title",
    "has_modal": boolean,
    "modal_type": "dialog|popup|overlay|none",
    "has_content": boolean,
    "visible_elements": ["list of major UI elements visible"],
    "focused_element": "description of focused element or null",
    "has_feedback_message": boolean,
    "button_states": {"button_label": "default|hover|active|disabled"}
  }
}
```

Return ONLY valid JSON, no explanations or markdown formatting.
Measure pixel values as accurately as possible from the screenshot.
For counts, count only visible items without scrolling.
"""


# ============================================================================
# TEMPORAL COMPARISON PROMPT
# Used to compare two sequential frames for timing analysis
# ============================================================================

TEMPORAL_COMPARISON_PROMPT = """Compare these two sequential UI screenshots and identify what changed.

Frame 1 timestamp: {timestamp_1}ms
Frame 2 timestamp: {timestamp_2}ms
Time delta: {delta}ms

Analyze both frames and return a JSON object describing the transition:

```json
{
  "transition": {
    "type": "navigation|modal_open|modal_close|form_submit|content_load|state_change|no_change",
    "description": "brief description of what changed",

    "user_action_inferred": "click|type|scroll|hover|none",
    "action_target": "description of element user likely interacted with",

    "feedback_appeared": boolean,
    "feedback_type": "visual|message|animation|sound_indicator|none",
    "feedback_element": "what element showed feedback",

    "loading_state_change": "started|ended|unchanged",
    "content_appeared": boolean,
    "content_type": "list|form|text|image|video|mixed|none",

    "error_appeared": boolean,
    "error_message": "error text if appeared",

    "modal_change": "opened|closed|unchanged",

    "elements_added": ["list of new elements"],
    "elements_removed": ["list of elements that disappeared"],

    "is_state_transition": boolean,
    "perceived_responsiveness": "instant|fast|noticeable|slow"
  }
}
```

Return ONLY valid JSON. Focus on identifying:
1. What user action likely triggered the change
2. How quickly visual feedback appeared
3. Whether loading indicators were shown appropriately
4. Any state transitions that should be timed for Doherty Threshold

The time between frames is {delta}ms.
"""


# ============================================================================
# FITTS'S LAW SPECIFIC PROMPT
# Deep analysis of touch targets and distances
# ============================================================================

FITTS_LAW_EXTRACTION_PROMPT = """Analyze this UI for Fitts's Law compliance.
Measure all interactive elements for target size and important distances.

Return JSON:
```json
{
  "fitts_analysis": {
    "primary_cta": {
      "text": "button text",
      "width": number,
      "height": number,
      "area_sq_px": number,
      "position": {"x": number, "y": number},
      "distance_from_screen_center": number
    },
    "all_buttons": [
      {
        "text": "button text",
        "width": number,
        "height": number,
        "is_destructive": boolean,
        "position": {"x": number, "y": number}
      }
    ],
    "button_pairs": [
      {
        "button_1": "label",
        "button_2": "label",
        "spacing_px": number,
        "is_adjacent": boolean
      }
    ],
    "form_analysis": {
      "has_form": boolean,
      "last_field_position_y": number or null,
      "submit_button_position_y": number or null,
      "distance_px": number or null
    },
    "modal_close_button": {
      "present": boolean,
      "distance_from_top_right_px": number or null
    },
    "links": [
      {
        "text": "link text",
        "clickable_area_px": number
      }
    ],
    "smallest_target_px": number,
    "violations": [
      "list of specific Fitts's Law concerns"
    ]
  }
}
```
"""


# ============================================================================
# HICK'S AND MILLER'S LAW PROMPT
# Count-based analysis for decision complexity
# ============================================================================

HICKS_MILLER_EXTRACTION_PROMPT = """Count all choice-related elements for Hick's Law and Miller's Law compliance.

Return JSON:
```json
{
  "choice_analysis": {
    "navigation": {
      "primary_nav_items": number,
      "secondary_nav_items": number,
      "total_nav_items": number,
      "nav_has_grouping": boolean
    },
    "forms": {
      "total_form_fields": number,
      "fields_per_section": [number],
      "has_section_headers": boolean,
      "uses_progressive_disclosure": boolean
    },
    "dropdowns": [
      {
        "label": "dropdown label",
        "visible_options": number,
        "has_search": boolean,
        "has_grouping": boolean
      }
    ],
    "wizards": {
      "has_wizard": boolean,
      "total_steps": number,
      "current_step": number,
      "has_progress_indicator": boolean
    },
    "action_buttons": {
      "primary_count": number,
      "secondary_count": number,
      "tertiary_count": number
    },
    "information_chunks": {
      "in_cards": number,
      "in_lists": number,
      "on_page_total": number
    },
    "violations": [
      "list of Hick's/Miller's Law concerns"
    ]
  }
}
```
"""


# ============================================================================
# DARK PATTERN DETECTION PROMPT
# Focused analysis for manipulative UI patterns
# ============================================================================

DARK_PATTERN_EXTRACTION_PROMPT = """Analyze this UI for dark patterns and manipulative design tactics.

Look for these specific patterns:
1. Confirmshaming (decline buttons with guilt-inducing text)
2. Hidden costs (fees revealed late in flow)
3. Pre-selected options (checkboxes checked by default)
4. Fake urgency (countdown timers, "only X left")
5. Misdirection (visual emphasis on unwanted actions)
6. Trick questions (confusing double negatives)
7. Roach motel (hard to unsubscribe/cancel)
8. Privacy zuckering (confusing privacy defaults)
9. Forced continuity (unclear trial-to-paid transition)
10. Disguised ads (ads that look like content)

Return JSON:
```json
{
  "dark_pattern_analysis": {
    "confirmshaming": {
      "detected": boolean,
      "decline_button_text": "exact text",
      "shame_phrases": ["list of shame phrases found"],
      "severity": "none|mild|moderate|severe"
    },
    "hidden_costs": {
      "detected": boolean,
      "price_shown": "initial price if any",
      "additional_fees_found": ["list of extra fees"],
      "fees_hidden_until": "cart|checkout|payment|none"
    },
    "preselected_options": {
      "detected": boolean,
      "preselected_items": [
        {
          "label": "checkbox label",
          "type": "addon|newsletter|terms|marketing",
          "financial_impact": boolean
        }
      ]
    },
    "fake_urgency": {
      "detected": boolean,
      "urgency_type": "countdown|scarcity|limited_time|none",
      "urgency_text": "exact text",
      "appears_genuine": boolean
    },
    "misdirection": {
      "detected": boolean,
      "primary_style_on": "wanted|unwanted action",
      "wanted_action_deemphasized": boolean
    },
    "trick_questions": {
      "detected": boolean,
      "confusing_labels": ["list of confusing text"],
      "double_negatives": boolean
    },
    "overall_score": number,  // 0-100, 100 = no dark patterns
    "violations": [
      {
        "pattern": "pattern name",
        "severity": "error|warning",
        "description": "specific violation"
      }
    ]
  }
}
```
"""


# ============================================================================
# FORM VALIDATION UX PROMPT
# Analyze form error handling and validation patterns
# ============================================================================

FORM_VALIDATION_PROMPT = """Analyze this form's validation and error handling UX.

Return JSON:
```json
{
  "form_validation_analysis": {
    "form_present": boolean,
    "total_fields": number,
    "required_fields": {
      "count": number,
      "clearly_indicated": boolean,
      "indication_method": "asterisk|text|border|none"
    },
    "error_states": {
      "errors_visible": boolean,
      "error_count": number,
      "errors": [
        {
          "field": "field name/label",
          "message": "error message text",
          "position": "inline|top|bottom|tooltip",
          "distance_from_field_px": number,
          "uses_color_only": boolean,
          "has_icon": boolean,
          "is_actionable": boolean
        }
      ]
    },
    "success_states": {
      "success_visible": boolean,
      "success_indication": "checkmark|message|color|none"
    },
    "inline_validation": {
      "appears_to_have": boolean,
      "validation_timing": "realtime|onblur|onsubmit|unknown"
    },
    "submit_button": {
      "text": "button text",
      "disabled_state": boolean,
      "shows_loading": boolean
    },
    "violations": [
      "list of form validation UX concerns"
    ]
  }
}
```
"""


# ============================================================================
# LOADING STATES PROMPT
# Analyze loading indicators and async feedback
# ============================================================================

LOADING_STATES_PROMPT = """Analyze loading states and async operation feedback in this UI.

Return JSON:
```json
{
  "loading_analysis": {
    "loading_indicator_present": boolean,
    "loading_type": "spinner|skeleton|progress_bar|shimmer|none",
    "loading_context": "page|section|button|inline|none",
    "progress_indicator": {
      "present": boolean,
      "is_determinate": boolean,
      "percentage_shown": boolean,
      "estimated_time_shown": boolean
    },
    "skeleton_screens": {
      "present": boolean,
      "matches_final_layout": boolean,
      "content_types_shown": ["text|image|card|list"]
    },
    "button_loading_state": {
      "any_loading_buttons": boolean,
      "buttons": [
        {
          "text": "button text",
          "shows_spinner": boolean,
          "is_disabled": boolean,
          "text_changes": boolean
        }
      ]
    },
    "content_status": {
      "has_content": boolean,
      "partial_content": boolean,
      "empty_placeholders": boolean
    },
    "timeout_handling": {
      "appears_to_handle": boolean,
      "retry_option_visible": boolean
    },
    "violations": [
      "list of loading state UX concerns"
    ]
  }
}
```
"""


# ============================================================================
# MOBILE THUMB ZONE PROMPT
# Analyze reachability for one-handed mobile use
# ============================================================================

MOBILE_THUMB_ZONE_PROMPT = """Analyze this mobile UI for thumb-zone reachability.

The thumb zone is typically:
- Easy reach: Bottom center (30% of screen)
- OK reach: Middle of screen
- Hard reach: Top corners

Return JSON:
```json
{
  "thumb_zone_analysis": {
    "is_mobile_layout": boolean,
    "viewport_dimensions": {"width": number, "height": number},

    "primary_cta": {
      "present": boolean,
      "position": {"x": number, "y": number},
      "zone": "easy|ok|hard",
      "in_thumb_zone": boolean
    },

    "navigation": {
      "position": "top|bottom|side",
      "nav_items_reachable": boolean,
      "hamburger_position": "top_left|top_right|bottom"
    },

    "frequent_actions": [
      {
        "action": "action description",
        "position": {"x": number, "y": number},
        "zone": "easy|ok|hard"
      }
    ],

    "floating_elements": {
      "fab_present": boolean,
      "fab_position": "bottom_right|bottom_left|other",
      "fab_reachable": boolean
    },

    "hard_to_reach_elements": [
      {
        "element": "element description",
        "position": "top_left|top_right|other",
        "importance": "critical|frequent|occasional"
      }
    ],

    "violations": [
      "list of thumb zone reachability concerns"
    ]
  }
}
```
"""


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_extraction_prompt(category: str = "full") -> str:
    """
    Get the appropriate extraction prompt.

    Args:
        category: One of "full", "fitts", "hicks_miller", "dark_patterns",
                 "form_validation", "loading", "mobile"

    Returns:
        The prompt string
    """
    prompts = {
        "full": INTERACTIVE_EXTRACTION_PROMPT,
        "fitts": FITTS_LAW_EXTRACTION_PROMPT,
        "hicks_miller": HICKS_MILLER_EXTRACTION_PROMPT,
        "dark_patterns": DARK_PATTERN_EXTRACTION_PROMPT,
        "form_validation": FORM_VALIDATION_PROMPT,
        "loading": LOADING_STATES_PROMPT,
        "mobile": MOBILE_THUMB_ZONE_PROMPT,
    }
    return prompts.get(category, INTERACTIVE_EXTRACTION_PROMPT)


def get_temporal_comparison_prompt(
    timestamp_1: int,
    timestamp_2: int
) -> str:
    """
    Get the temporal comparison prompt with timestamps filled in.

    Args:
        timestamp_1: First frame timestamp in ms
        timestamp_2: Second frame timestamp in ms

    Returns:
        Formatted prompt string
    """
    delta = timestamp_2 - timestamp_1
    return TEMPORAL_COMPARISON_PROMPT.format(
        timestamp_1=timestamp_1,
        timestamp_2=timestamp_2,
        delta=delta
    )


# Expected response schema for validation
EXTRACTION_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "spatial": {"type": "object"},
        "counts": {"type": "object"},
        "states": {"type": "object"},
        "dark_patterns": {"type": "object"},
        "mobile": {"type": "object"},
        "cognitive": {"type": "object"},
        "ui_state": {"type": "object"}
    }
}
