"""
Interactive UX Baseline Rules - TML v2.0

This module defines baseline rules for interactive UX principles that go beyond
static visual design. These rules cover temporal, behavioral, spatial, and pattern-based
violations that require interaction analysis (video/replay) to detect.

Rule Categories:
- STATIC: Traditional visual rules (existing)
- TEMPORAL: Time-based rules (response times, animations)
- BEHAVIORAL: Interaction pattern rules (form validation, loading states)
- SPATIAL: Layout/position rules (thumb zones, target sizes)
- PATTERN: Dark pattern detection rules

High Priority UX Principles Covered:
1. Fitts's Law - Target size and distance
2. Hick's Law - Decision complexity
3. Miller's Law - Working memory limits
4. Doherty Threshold - Response time
5. Form Validation - Error feedback
6. Loading States - Progress indication
7. Empty States - Guidance when empty
8. Dark Pattern Detection - Manipulative tactics
9. Mobile Thumb Zone - Reachability
10. Cognitive Accessibility - Clear language
"""

from typing import List, Dict, Any


# ============================================================================
# FITTS'S LAW RULES (8 rules)
# Principle: Time to acquire target = f(distance/size)
# ============================================================================

FITTS_LAW_RULES: List[Dict[str, Any]] = [
    {
        "rule_id": "fitts-cta-min-size",
        "rule_category": "SPATIAL",
        "component_type": "button",
        "property": "cta_touch_target_size",
        "operator": ">=",
        "value": "44",
        "severity": "error",
        "message": "Primary CTA must be at least 44x44px for reliable targeting (WCAG 2.5.5)",
    },
    {
        "rule_id": "fitts-button-min-size",
        "rule_category": "SPATIAL",
        "component_type": "button",
        "property": "button_min_dimension",
        "operator": ">=",
        "value": "24",
        "severity": "warning",
        "message": "All interactive buttons should be at least 24px in smallest dimension",
    },
    {
        "rule_id": "fitts-button-spacing",
        "rule_category": "SPATIAL",
        "component_type": "button",
        "property": "button_spacing",
        "operator": ">=",
        "value": "8",
        "severity": "warning",
        "message": "Adjacent buttons should have 8px+ spacing to prevent misclicks",
    },
    {
        "rule_id": "fitts-form-submit-distance",
        "rule_category": "SPATIAL",
        "component_type": "form",
        "property": "form_to_submit_distance",
        "operator": "<=",
        "value": "300",
        "severity": "warning",
        "message": "Submit button should be within 300px of last form field",
    },
    {
        "rule_id": "fitts-link-min-area",
        "rule_category": "SPATIAL",
        "component_type": None,
        "property": "link_click_area",
        "operator": ">=",
        "value": "400",
        "severity": "info",
        "message": "Link click areas should be at least 400 sq px (20x20 minimum)",
    },
    {
        "rule_id": "fitts-close-button-position",
        "rule_category": "SPATIAL",
        "component_type": "modal",
        "property": "close_button_distance_from_corner",
        "operator": "<=",
        "value": "48",
        "severity": "warning",
        "message": "Modal close button should be within 48px of top-right corner",
    },
    {
        "rule_id": "fitts-destructive-spacing",
        "rule_category": "SPATIAL",
        "component_type": "button",
        "property": "destructive_button_spacing",
        "operator": ">=",
        "value": "16",
        "severity": "warning",
        "message": "Destructive actions should have 16px+ spacing from confirm buttons",
    },
    {
        "rule_id": "fitts-nav-item-size",
        "rule_category": "SPATIAL",
        "component_type": "navigation",
        "property": "nav_item_click_height",
        "operator": ">=",
        "value": "40",
        "severity": "warning",
        "message": "Navigation items should be at least 40px tall for easy selection",
    },
]


# ============================================================================
# HICK'S LAW RULES (7 rules)
# Principle: Decision time increases with number and complexity of choices
# ============================================================================

HICKS_LAW_RULES: List[Dict[str, Any]] = [
    {
        "rule_id": "hicks-nav-items",
        "rule_category": "BEHAVIORAL",
        "component_type": "navigation",
        "property": "primary_nav_item_count",
        "operator": "<=",
        "value": "7",
        "count_property": "primary_nav_items",
        "severity": "warning",
        "message": "Primary navigation should have 7 or fewer items (Hick's Law)",
    },
    {
        "rule_id": "hicks-dropdown-options",
        "rule_category": "BEHAVIORAL",
        "component_type": "input",
        "property": "dropdown_option_count",
        "operator": "<=",
        "value": "10",
        "count_property": "dropdown_options",
        "severity": "warning",
        "message": "Dropdown menus should have 10 or fewer options without grouping",
    },
    {
        "rule_id": "hicks-form-fields-visible",
        "rule_category": "BEHAVIORAL",
        "component_type": "form",
        "property": "visible_form_fields",
        "operator": "<=",
        "value": "5",
        "count_property": "visible_fields",
        "severity": "info",
        "message": "Consider progressive disclosure if showing 5+ form fields simultaneously",
    },
    {
        "rule_id": "hicks-action-buttons",
        "rule_category": "BEHAVIORAL",
        "component_type": None,
        "property": "primary_action_count",
        "operator": "<=",
        "value": "3",
        "count_property": "primary_actions",
        "severity": "warning",
        "message": "Limit primary actions to 3 per view to reduce decision paralysis",
    },
    {
        "rule_id": "hicks-tab-count",
        "rule_category": "BEHAVIORAL",
        "component_type": "navigation",
        "property": "tab_count",
        "operator": "<=",
        "value": "5",
        "count_property": "tabs",
        "severity": "info",
        "message": "Tab interfaces should have 5 or fewer tabs for quick scanning",
    },
    {
        "rule_id": "hicks-menu-depth",
        "rule_category": "BEHAVIORAL",
        "component_type": "navigation",
        "property": "menu_nesting_depth",
        "operator": "<=",
        "value": "2",
        "count_property": "menu_depth",
        "severity": "warning",
        "message": "Menu nesting should not exceed 2 levels deep",
    },
    {
        "rule_id": "hicks-search-suggestions",
        "rule_category": "BEHAVIORAL",
        "component_type": "input",
        "property": "search_suggestion_count",
        "operator": "<=",
        "value": "8",
        "count_property": "suggestions",
        "severity": "info",
        "message": "Search suggestions should be limited to 8 for quick selection",
    },
]


# ============================================================================
# MILLER'S LAW RULES (6 rules)
# Principle: Working memory limited to 7±2 chunks
# ============================================================================

MILLERS_LAW_RULES: List[Dict[str, Any]] = [
    {
        "rule_id": "miller-form-sections",
        "rule_category": "BEHAVIORAL",
        "component_type": "form",
        "property": "form_fields_per_section",
        "operator": "<=",
        "value": "7",
        "count_property": "fields_per_section",
        "severity": "warning",
        "message": "Form sections should contain 7 or fewer fields (Miller's Law)",
    },
    {
        "rule_id": "miller-wizard-steps",
        "rule_category": "BEHAVIORAL",
        "component_type": "form",
        "property": "wizard_step_count",
        "operator": "<=",
        "value": "7",
        "count_property": "wizard_steps",
        "severity": "warning",
        "message": "Multi-step wizards should have 7 or fewer steps",
    },
    {
        "rule_id": "miller-breadcrumb-depth",
        "rule_category": "BEHAVIORAL",
        "component_type": "navigation",
        "property": "breadcrumb_level_count",
        "operator": "<=",
        "value": "5",
        "count_property": "breadcrumb_levels",
        "severity": "info",
        "message": "Breadcrumb depth beyond 5 levels suggests overly complex IA",
    },
    {
        "rule_id": "miller-list-items-visible",
        "rule_category": "BEHAVIORAL",
        "component_type": None,
        "property": "list_items_without_pagination",
        "operator": "<=",
        "value": "9",
        "count_property": "visible_list_items",
        "severity": "info",
        "message": "Lists should show ~9 items before pagination/scroll for memorability",
    },
    {
        "rule_id": "miller-card-info-chunks",
        "rule_category": "BEHAVIORAL",
        "component_type": "card",
        "property": "info_chunks_per_card",
        "operator": "<=",
        "value": "7",
        "count_property": "card_info_chunks",
        "severity": "info",
        "message": "Cards should contain 7 or fewer distinct information chunks",
    },
    {
        "rule_id": "miller-stepper-indicators",
        "rule_category": "BEHAVIORAL",
        "component_type": "form",
        "property": "has_step_indicators",
        "operator": "=",
        "value": "true",
        "severity": "warning",
        "message": "Multi-step forms with 4+ steps must show progress indicators",
    },
]


# ============================================================================
# DOHERTY THRESHOLD RULES (8 rules)
# Principle: System response <400ms maintains user flow state
# ============================================================================

DOHERTY_THRESHOLD_RULES: List[Dict[str, Any]] = [
    {
        "rule_id": "doherty-feedback-time",
        "rule_category": "TEMPORAL",
        "component_type": None,
        "property": "interaction_feedback_time",
        "operator": "<=",
        "value": "100",
        "timing_constraint_ms": 100,
        "severity": "error",
        "message": "Visual feedback must appear within 100ms of user action",
    },
    {
        "rule_id": "doherty-state-transition",
        "rule_category": "TEMPORAL",
        "component_type": None,
        "property": "state_transition_time",
        "operator": "<=",
        "value": "400",
        "timing_constraint_ms": 400,
        "severity": "warning",
        "message": "State transitions should complete within 400ms (Doherty Threshold)",
    },
    {
        "rule_id": "doherty-loading-indicator",
        "rule_category": "TEMPORAL",
        "component_type": "feedback",
        "property": "loading_indicator_delay",
        "operator": "<=",
        "value": "1000",
        "timing_constraint_ms": 1000,
        "severity": "error",
        "message": "Loading indicator must appear within 1 second for operations >1s",
    },
    {
        "rule_id": "doherty-button-feedback",
        "rule_category": "TEMPORAL",
        "component_type": "button",
        "property": "button_press_feedback",
        "operator": "<=",
        "value": "50",
        "timing_constraint_ms": 50,
        "severity": "warning",
        "message": "Button press visual feedback should appear within 50ms",
    },
    {
        "rule_id": "doherty-hover-response",
        "rule_category": "TEMPORAL",
        "component_type": None,
        "property": "hover_state_delay",
        "operator": "<=",
        "value": "100",
        "timing_constraint_ms": 100,
        "severity": "info",
        "message": "Hover states should appear within 100ms",
    },
    {
        "rule_id": "doherty-input-validation",
        "rule_category": "TEMPORAL",
        "component_type": "input",
        "property": "validation_feedback_time",
        "operator": "<=",
        "value": "300",
        "timing_constraint_ms": 300,
        "severity": "warning",
        "message": "Input validation feedback should appear within 300ms of blur/change",
    },
    {
        "rule_id": "doherty-animation-duration",
        "rule_category": "TEMPORAL",
        "component_type": None,
        "property": "animation_duration",
        "operator": "<=",
        "value": "300",
        "timing_constraint_ms": 300,
        "severity": "info",
        "message": "UI animations should not exceed 300ms to maintain responsiveness",
    },
    {
        "rule_id": "doherty-page-interactive",
        "rule_category": "TEMPORAL",
        "component_type": None,
        "property": "time_to_interactive",
        "operator": "<=",
        "value": "3000",
        "timing_constraint_ms": 3000,
        "severity": "error",
        "message": "Page should be interactive within 3 seconds of navigation",
    },
]


# ============================================================================
# FORM VALIDATION RULES (8 rules)
# Principle: Immediate, inline, accessible error feedback
# ============================================================================

FORM_VALIDATION_RULES: List[Dict[str, Any]] = [
    {
        "rule_id": "form-inline-validation",
        "rule_category": "BEHAVIORAL",
        "component_type": "form",
        "property": "has_inline_validation",
        "operator": "=",
        "value": "true",
        "severity": "warning",
        "message": "Forms should provide inline validation feedback",
    },
    {
        "rule_id": "form-error-proximity",
        "rule_category": "SPATIAL",
        "component_type": "input",
        "property": "error_message_distance",
        "operator": "<=",
        "value": "24",
        "severity": "error",
        "message": "Error messages must be within 24px of related field",
    },
    {
        "rule_id": "form-error-visibility",
        "rule_category": "BEHAVIORAL",
        "component_type": "input",
        "property": "error_uses_color_only",
        "operator": "=",
        "value": "false",
        "severity": "error",
        "message": "Error states must not rely on color alone (WCAG 1.4.1)",
    },
    {
        "rule_id": "form-error-icon",
        "rule_category": "BEHAVIORAL",
        "component_type": "input",
        "property": "error_has_icon",
        "operator": "=",
        "value": "true",
        "severity": "warning",
        "message": "Error states should include an icon in addition to color",
    },
    {
        "rule_id": "form-error-message-clarity",
        "rule_category": "BEHAVIORAL",
        "component_type": "input",
        "property": "error_message_is_actionable",
        "operator": "=",
        "value": "true",
        "severity": "warning",
        "message": "Error messages should explain how to fix the issue",
    },
    {
        "rule_id": "form-required-indicator",
        "rule_category": "BEHAVIORAL",
        "component_type": "input",
        "property": "required_fields_indicated",
        "operator": "=",
        "value": "true",
        "severity": "warning",
        "message": "Required fields must be clearly indicated before submission",
    },
    {
        "rule_id": "form-success-feedback",
        "rule_category": "BEHAVIORAL",
        "component_type": "form",
        "property": "has_success_feedback",
        "operator": "=",
        "value": "true",
        "severity": "info",
        "message": "Forms should provide success feedback on valid submission",
    },
    {
        "rule_id": "form-focus-on-error",
        "rule_category": "BEHAVIORAL",
        "component_type": "form",
        "property": "focus_moves_to_first_error",
        "operator": "=",
        "value": "true",
        "severity": "warning",
        "message": "Focus should move to first error field on form submission",
    },
]


# ============================================================================
# LOADING STATES RULES (6 rules)
# Principle: Clear feedback during async operations
# ============================================================================

LOADING_STATES_RULES: List[Dict[str, Any]] = [
    {
        "rule_id": "loading-skeleton-presence",
        "rule_category": "BEHAVIORAL",
        "component_type": "feedback",
        "property": "has_skeleton_loading",
        "operator": "=",
        "value": "true",
        "severity": "info",
        "message": "Consider skeleton screens for content-heavy loading states",
    },
    {
        "rule_id": "loading-progress-determinate",
        "rule_category": "BEHAVIORAL",
        "component_type": "feedback",
        "property": "long_operation_has_progress",
        "operator": "=",
        "value": "true",
        "severity": "warning",
        "message": "Operations >3s should show determinate progress when possible",
    },
    {
        "rule_id": "loading-spinner-visible",
        "rule_category": "BEHAVIORAL",
        "component_type": "feedback",
        "property": "loading_indicator_visible",
        "operator": "=",
        "value": "true",
        "severity": "error",
        "message": "Loading states must have visible spinner or progress indicator",
    },
    {
        "rule_id": "loading-button-disabled",
        "rule_category": "BEHAVIORAL",
        "component_type": "button",
        "property": "submit_disabled_during_loading",
        "operator": "=",
        "value": "true",
        "severity": "warning",
        "message": "Submit buttons should be disabled during form submission",
    },
    {
        "rule_id": "loading-optimistic-update",
        "rule_category": "BEHAVIORAL",
        "component_type": None,
        "property": "uses_optimistic_updates",
        "operator": "=",
        "value": "true",
        "severity": "info",
        "message": "Consider optimistic updates for common actions to feel instant",
    },
    {
        "rule_id": "loading-timeout-message",
        "rule_category": "BEHAVIORAL",
        "component_type": "feedback",
        "property": "shows_timeout_message",
        "operator": "=",
        "value": "true",
        "severity": "warning",
        "message": "Show helpful message if operation takes >10 seconds",
    },
]


# ============================================================================
# EMPTY STATES RULES (5 rules)
# Principle: Guide users when no content exists
# ============================================================================

EMPTY_STATES_RULES: List[Dict[str, Any]] = [
    {
        "rule_id": "empty-state-guidance",
        "rule_category": "BEHAVIORAL",
        "component_type": None,
        "property": "empty_state_has_cta",
        "operator": "=",
        "value": "true",
        "severity": "warning",
        "message": "Empty states should include actionable guidance",
    },
    {
        "rule_id": "empty-state-explanation",
        "rule_category": "BEHAVIORAL",
        "component_type": None,
        "property": "empty_state_has_explanation",
        "operator": "=",
        "value": "true",
        "severity": "info",
        "message": "Empty states should explain why content is missing",
    },
    {
        "rule_id": "empty-state-illustration",
        "rule_category": "BEHAVIORAL",
        "component_type": None,
        "property": "empty_state_has_visual",
        "operator": "=",
        "value": "true",
        "severity": "info",
        "message": "Empty states benefit from illustrations to reduce emptiness",
    },
    {
        "rule_id": "empty-state-no-error-style",
        "rule_category": "BEHAVIORAL",
        "component_type": None,
        "property": "empty_state_uses_error_styling",
        "operator": "=",
        "value": "false",
        "severity": "warning",
        "message": "Empty states should not use error/warning styling",
    },
    {
        "rule_id": "empty-state-search-suggestion",
        "rule_category": "BEHAVIORAL",
        "component_type": None,
        "property": "no_results_has_suggestions",
        "operator": "=",
        "value": "true",
        "severity": "info",
        "message": "No-results states should suggest alternative searches or actions",
    },
]


# ============================================================================
# DARK PATTERN DETECTION RULES (10 rules)
# Principle: Detect manipulative UI tactics
# ============================================================================

DARK_PATTERN_RULES: List[Dict[str, Any]] = [
    {
        "rule_id": "dark-confirm-shaming",
        "rule_category": "PATTERN",
        "component_type": "button",
        "property": "decline_button_shame_language",
        "operator": "=",
        "value": "false",
        "pattern_indicators": [
            "No thanks, I don't want",
            "I'll stay poor",
            "I prefer not to save",
            "No, I hate saving money",
            "I don't want to be successful",
        ],
        "severity": "error",
        "message": "Decline options must not use shame language (dark pattern: confirmshaming)",
    },
    {
        "rule_id": "dark-hidden-costs",
        "rule_category": "PATTERN",
        "component_type": None,
        "property": "late_fee_disclosure",
        "operator": "=",
        "value": "false",
        "pattern_indicators": ["service fee", "processing fee", "convenience fee"],
        "severity": "error",
        "message": "All costs must be disclosed upfront, not at checkout (dark pattern: hidden costs)",
    },
    {
        "rule_id": "dark-preselected-options",
        "rule_category": "PATTERN",
        "component_type": "input",
        "property": "has_preselected_addons",
        "operator": "=",
        "value": "false",
        "severity": "error",
        "message": "Optional add-ons must not be pre-selected (dark pattern: sneak into basket)",
    },
    {
        "rule_id": "dark-cancel-difficulty",
        "rule_category": "PATTERN",
        "component_type": None,
        "property": "cancel_steps",
        "operator": "<=",
        "value": "2",
        "count_property": "cancellation_steps",
        "severity": "error",
        "message": "Cancellation should require no more than 2 steps (dark pattern: roach motel)",
    },
    {
        "rule_id": "dark-fake-urgency",
        "rule_category": "PATTERN",
        "component_type": None,
        "property": "has_fake_countdown",
        "operator": "=",
        "value": "false",
        "pattern_indicators": ["Only X left", "Offer expires", "Limited time"],
        "severity": "error",
        "message": "Do not use fake urgency countdowns (dark pattern: fake urgency)",
    },
    {
        "rule_id": "dark-misdirection",
        "rule_category": "PATTERN",
        "component_type": "button",
        "property": "primary_style_on_unwanted_action",
        "operator": "=",
        "value": "false",
        "severity": "error",
        "message": "Don't use primary button styles on unwanted actions (dark pattern: misdirection)",
    },
    {
        "rule_id": "dark-trick-questions",
        "rule_category": "PATTERN",
        "component_type": "input",
        "property": "double_negative_labels",
        "operator": "=",
        "value": "false",
        "pattern_indicators": ["Don't not", "Uncheck to not"],
        "severity": "error",
        "message": "Do not use confusing double negatives (dark pattern: trick questions)",
    },
    {
        "rule_id": "dark-privacy-zuckering",
        "rule_category": "PATTERN",
        "component_type": None,
        "property": "privacy_defaults_to_share",
        "operator": "=",
        "value": "false",
        "severity": "error",
        "message": "Privacy settings should default to private (dark pattern: privacy zuckering)",
    },
    {
        "rule_id": "dark-forced-continuity",
        "rule_category": "PATTERN",
        "component_type": None,
        "property": "trial_requires_payment_upfront",
        "operator": "=",
        "value": "false",
        "severity": "warning",
        "message": "Free trials requiring payment info should clearly indicate auto-charge date",
    },
    {
        "rule_id": "dark-disguised-ads",
        "rule_category": "PATTERN",
        "component_type": None,
        "property": "ads_clearly_labeled",
        "operator": "=",
        "value": "true",
        "pattern_indicators": ["Sponsored", "Ad", "Promoted"],
        "severity": "error",
        "message": "Advertisements must be clearly distinguishable from content",
    },
]


# ============================================================================
# MOBILE THUMB ZONE RULES (6 rules)
# Principle: Optimize for one-handed mobile use
# ============================================================================

THUMB_ZONE_RULES: List[Dict[str, Any]] = [
    {
        "rule_id": "thumb-primary-cta-zone",
        "rule_category": "SPATIAL",
        "component_type": "button",
        "property": "primary_cta_in_thumb_zone",
        "operator": "=",
        "value": "true",
        "zone_definition": {
            "bottom_percentage": 30,
            "horizontal_center_percentage": 60,
        },
        "severity": "warning",
        "message": "Primary CTAs should be in thumb-friendly zone (bottom 30% of screen)",
    },
    {
        "rule_id": "thumb-nav-reachability",
        "rule_category": "SPATIAL",
        "component_type": "navigation",
        "property": "nav_in_reachable_zone",
        "operator": "=",
        "value": "true",
        "severity": "info",
        "message": "Navigation should be reachable with one-handed use",
    },
    {
        "rule_id": "thumb-avoid-top-corners",
        "rule_category": "SPATIAL",
        "component_type": None,
        "property": "frequent_action_in_top_corner",
        "operator": "=",
        "value": "false",
        "zone_definition": {
            "top_percentage": 15,
            "edge_percentage": 15,
        },
        "severity": "info",
        "message": "Avoid placing frequent actions in hard-to-reach top corners on mobile",
    },
    {
        "rule_id": "thumb-bottom-nav",
        "rule_category": "SPATIAL",
        "component_type": "navigation",
        "property": "primary_nav_position",
        "operator": "=",
        "value": "bottom",
        "severity": "info",
        "message": "Consider bottom navigation for mobile apps with 3-5 main sections",
    },
    {
        "rule_id": "thumb-swipe-actions",
        "rule_category": "BEHAVIORAL",
        "component_type": None,
        "property": "supports_swipe_gestures",
        "operator": "=",
        "value": "true",
        "severity": "info",
        "message": "Consider swipe gestures for common actions on mobile lists",
    },
    {
        "rule_id": "thumb-fab-position",
        "rule_category": "SPATIAL",
        "component_type": "button",
        "property": "fab_in_reachable_position",
        "operator": "=",
        "value": "true",
        "zone_definition": {
            "bottom_right_offset_px": 16,
        },
        "severity": "warning",
        "message": "Floating action buttons should be in bottom-right reachable zone",
    },
]


# ============================================================================
# COGNITIVE ACCESSIBILITY RULES (6 rules)
# Principle: Clear language and predictable patterns
# ============================================================================

COGNITIVE_ACCESSIBILITY_RULES: List[Dict[str, Any]] = [
    {
        "rule_id": "cognitive-reading-level",
        "rule_category": "BEHAVIORAL",
        "component_type": None,
        "property": "text_reading_level",
        "operator": "<=",
        "value": "8",
        "severity": "warning",
        "message": "Body text should be 8th grade reading level or below (Flesch-Kincaid)",
    },
    {
        "rule_id": "cognitive-jargon-density",
        "rule_category": "BEHAVIORAL",
        "component_type": None,
        "property": "jargon_percentage",
        "operator": "<=",
        "value": "10",
        "severity": "info",
        "message": "Technical jargon should be under 10% of content",
    },
    {
        "rule_id": "cognitive-consistent-terminology",
        "rule_category": "BEHAVIORAL",
        "component_type": None,
        "property": "terminology_consistent",
        "operator": "=",
        "value": "true",
        "severity": "warning",
        "message": "Use consistent terminology for same concepts throughout",
    },
    {
        "rule_id": "cognitive-clear-labels",
        "rule_category": "BEHAVIORAL",
        "component_type": "button",
        "property": "button_labels_are_verbs",
        "operator": "=",
        "value": "true",
        "severity": "warning",
        "message": "Button labels should use action verbs (Save, Submit, Delete)",
    },
    {
        "rule_id": "cognitive-predictable-layout",
        "rule_category": "BEHAVIORAL",
        "component_type": None,
        "property": "layout_consistent_across_pages",
        "operator": "=",
        "value": "true",
        "severity": "warning",
        "message": "Core layout elements should be in consistent positions across pages",
    },
    {
        "rule_id": "cognitive-undo-available",
        "rule_category": "BEHAVIORAL",
        "component_type": None,
        "property": "destructive_actions_have_undo",
        "operator": "=",
        "value": "true",
        "severity": "warning",
        "message": "Destructive actions should offer undo or require confirmation",
    },
]


# ============================================================================
# COMBINED RULES EXPORT
# ============================================================================

INTERACTIVE_BASELINE_RULES: List[Dict[str, Any]] = (
    FITTS_LAW_RULES +
    HICKS_LAW_RULES +
    MILLERS_LAW_RULES +
    DOHERTY_THRESHOLD_RULES +
    FORM_VALIDATION_RULES +
    LOADING_STATES_RULES +
    EMPTY_STATES_RULES +
    DARK_PATTERN_RULES +
    THUMB_ZONE_RULES +
    COGNITIVE_ACCESSIBILITY_RULES
)


def get_rules_by_category(category: str) -> List[Dict[str, Any]]:
    """Get all rules for a specific category (TEMPORAL, BEHAVIORAL, SPATIAL, PATTERN)."""
    return [r for r in INTERACTIVE_BASELINE_RULES if r.get("rule_category") == category]


def get_rules_by_principle(principle: str) -> List[Dict[str, Any]]:
    """Get all rules for a specific UX principle."""
    prefix_map = {
        "fitts": "fitts-",
        "hicks": "hicks-",
        "miller": "miller-",
        "doherty": "doherty-",
        "form": "form-",
        "loading": "loading-",
        "empty": "empty-",
        "dark": "dark-",
        "thumb": "thumb-",
        "cognitive": "cognitive-",
    }
    prefix = prefix_map.get(principle.lower(), "")
    return [r for r in INTERACTIVE_BASELINE_RULES if r["rule_id"].startswith(prefix)]


def get_temporal_rules() -> List[Dict[str, Any]]:
    """Get all rules that require timing measurement."""
    return [r for r in INTERACTIVE_BASELINE_RULES if r.get("timing_constraint_ms") is not None]


def get_counting_rules() -> List[Dict[str, Any]]:
    """Get all rules that count elements (Hick's/Miller's Law)."""
    return [r for r in INTERACTIVE_BASELINE_RULES if r.get("count_property") is not None]


def get_spatial_rules() -> List[Dict[str, Any]]:
    """Get all rules that check element positions/sizes."""
    return [r for r in INTERACTIVE_BASELINE_RULES if r.get("rule_category") == "SPATIAL"]


def get_pattern_rules() -> List[Dict[str, Any]]:
    """Get all rules that detect dark patterns."""
    return [r for r in INTERACTIVE_BASELINE_RULES if r.get("rule_category") == "PATTERN"]


# Summary statistics
print(f"Total interactive rules: {len(INTERACTIVE_BASELINE_RULES)}")
print(f"  - TEMPORAL: {len(get_rules_by_category('TEMPORAL'))}")
print(f"  - BEHAVIORAL: {len(get_rules_by_category('BEHAVIORAL'))}")
print(f"  - SPATIAL: {len(get_rules_by_category('SPATIAL'))}")
print(f"  - PATTERN: {len(get_rules_by_category('PATTERN'))}")
