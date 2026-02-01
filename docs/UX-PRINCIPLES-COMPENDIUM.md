# UX Principles Compendium for TML Enhancement

**Purpose:** Comprehensive research document cataloging all major UX principles, laws, and patterns that could potentially be incorporated into the Taste Markup Language (TML) specification for programmatic UI/UX auditing.

**Date:** January 2026

---

## Table of Contents

1. [Current TML Coverage](#current-tml-coverage)
2. [UX Laws (Yablonski's 21 Laws)](#ux-laws-yablonskis-21-laws)
3. [Gestalt Principles](#gestalt-principles)
4. [Cognitive Psychology Principles](#cognitive-psychology-principles)
5. [Visual Design Principles](#visual-design-principles)
6. [Interaction Design Principles](#interaction-design-principles)
7. [Information Architecture](#information-architecture)
8. [Form Design](#form-design)
9. [Navigation Patterns](#navigation-patterns)
10. [Feedback & System Status](#feedback--system-status)
11. [Loading & Performance Perception](#loading--performance-perception)
12. [Emotional Design](#emotional-design)
13. [Persuasive Design & Gamification](#persuasive-design--gamification)
14. [Trust & Credibility](#trust--credibility)
15. [Mobile & Touch Design](#mobile--touch-design)
16. [Accessibility Beyond WCAG](#accessibility-beyond-wcag)
17. [Content UX & Microcopy](#content-ux--microcopy)
18. [Empty States & Onboarding](#empty-states--onboarding)
19. [Dark Patterns (Anti-Patterns)](#dark-patterns-anti-patterns)
20. [Gap Analysis: TML Coverage](#gap-analysis-tml-coverage)

---

## Current TML Coverage

### Already Implemented in TML Baseline Rules

#### WCAG Accessibility (8 rules)
| Rule ID | Property | Description | Measurable? |
|---------|----------|-------------|-------------|
| wcag-001 | contrast_ratio_text | Text contrast ≥ 4.5:1 | Yes |
| wcag-002 | contrast_ratio_large_text | Large text contrast ≥ 3:1 | Yes |
| wcag-003 | touch_target_size | Touch targets ≥ 44px | Yes |
| wcag-004 | focus_indicator | Focus states must be visible | Partial |
| wcag-005 | label_present | Form fields must have labels | Yes |
| wcag-006 | color_only_indicator | Don't rely solely on color | Partial |
| wcag-007 | line_height | Line height ≥ 1.5 for body text | Yes |
| wcag-008 | paragraph_spacing | Paragraph spacing ≥ 2x font size | Yes |

#### Nielsen's 10 Heuristics (10 rules)
| Rule ID | Property | Description | Measurable? |
|---------|----------|-------------|-------------|
| nielsen-001 | system_status_visibility | Keep users informed | Qualitative |
| nielsen-002 | real_world_match | Use familiar language | Qualitative |
| nielsen-003 | user_control_freedom | Support undo/redo | Partial |
| nielsen-004 | consistency_standards | Be consistent | Partial |
| nielsen-005 | error_prevention | Prevent errors before they occur | Qualitative |
| nielsen-006 | recognition_over_recall | Minimize memory load | Qualitative |
| nielsen-007 | flexibility_efficiency | Support shortcuts | Qualitative |
| nielsen-008 | aesthetic_minimal_design | Remove unnecessary elements | Qualitative |
| nielsen-009 | error_recovery_help | Help users recover from errors | Qualitative |
| nielsen-010 | help_documentation | Provide help when needed | Qualitative |

#### Visual Properties (Currently Tracked)
- `border_radius`, `padding`, `font_weight`, `font_size`, `text_transform`
- `shadow`, `background_style`, `label_position`, `focus_ring`
- `palette` (colors), `font_pair` (typography)

---

## UX Laws (Yablonski's 21 Laws)

*Source: [Laws of UX](https://lawsofux.com/) by Jon Yablonski*

### Heuristics

#### 1. Fitts's Law
> "The time to acquire a target is a function of the distance to and size of the target."

**TML Applicability:** HIGH
- **Measurable Properties:**
  - `button_size` >= 44px (already partial via touch_target_size)
  - `cta_prominence` - distance from common cursor positions
  - `clickable_area_ratio` - ratio of clickable to visual area
  - `important_element_position` - placement of key actions

**Audit Rules:**
```json
{
  "rule_id": "fitts-001",
  "property": "primary_cta_size",
  "operator": ">=",
  "value": "48px",
  "message": "Primary CTAs should be large enough for easy acquisition"
}
```

#### 2. Hick's Law
> "The time to make a decision increases with the number and complexity of choices."

**TML Applicability:** HIGH
- **Measurable Properties:**
  - `navigation_item_count` <= 7
  - `dropdown_option_count` <= 10
  - `form_field_count` per section
  - `visible_action_count` at any time

**Audit Rules:**
```json
{
  "rule_id": "hicks-001",
  "property": "primary_navigation_items",
  "operator": "<=",
  "value": 7,
  "message": "Limit primary navigation to 7±2 items to reduce decision time"
}
```

#### 3. Miller's Law
> "The average person can only keep about 7 (±2) items in working memory."

**TML Applicability:** HIGH
- **Measurable Properties:**
  - `chunk_size` - items per group
  - `form_sections` - logical groupings
  - `breadcrumb_depth` <= 5
  - `wizard_steps` <= 7

**Audit Rules:**
```json
{
  "rule_id": "miller-001",
  "property": "items_per_group",
  "operator": "<=",
  "value": 7,
  "message": "Group related items into chunks of 7 or fewer"
}
```

#### 4. Jakob's Law
> "Users prefer your site to work the same way as all the other sites they already know."

**TML Applicability:** MEDIUM
- **Measurable Properties:**
  - `standard_icon_usage` - magnifying glass for search, cart for checkout
  - `conventional_placement` - logo top-left, search top-right
  - `expected_interaction_patterns` - click vs hover expectations

**Audit Rules:**
```json
{
  "rule_id": "jakob-001",
  "property": "logo_position",
  "operator": "=",
  "value": "top-left",
  "message": "Place logo in expected top-left position for familiarity"
}
```

#### 5. Postel's Law
> "Be liberal in what you accept, conservative in what you send."

**TML Applicability:** MEDIUM
- **Measurable Properties:**
  - `input_format_flexibility` - accepts multiple date formats
  - `error_tolerance` - graceful handling of edge cases
  - `output_consistency` - consistent display format

### Gestalt Principles (Covered Separately Below)

### Cognitive Biases

#### 6. Peak-End Rule
> "People judge an experience largely based on how they felt at its peak and at its end."

**TML Applicability:** LOW (difficult to measure programmatically)
- **Potential Properties:**
  - `completion_celebration` - presence of success state
  - `final_screen_quality` - confirmation page design
  - `exit_experience` - logout/close experience

#### 7. Von Restorff Effect (Isolation Effect)
> "When multiple similar objects are present, the one that differs from the rest is most likely to be remembered."

**TML Applicability:** HIGH
- **Measurable Properties:**
  - `cta_contrast_ratio` vs surrounding elements
  - `highlight_distinctiveness` - visual differentiation
  - `important_element_isolation` - whitespace around key elements

**Audit Rules:**
```json
{
  "rule_id": "vonrestorff-001",
  "property": "primary_cta_visual_weight",
  "operator": ">",
  "value": "secondary_elements",
  "message": "Primary CTA should visually stand out from other elements"
}
```

#### 8. Serial Position Effect
> "Users have a propensity to best remember the first and last items in a series."

**TML Applicability:** MEDIUM
- **Measurable Properties:**
  - `important_items_position` - first or last in lists
  - `navigation_order` - most important items at edges

#### 9. Zeigarnik Effect
> "People remember uncompleted or interrupted tasks better than completed tasks."

**TML Applicability:** MEDIUM
- **Measurable Properties:**
  - `progress_indicator_presence` - shows incomplete status
  - `save_draft_availability` - allows resuming tasks
  - `step_completion_feedback` - marks completed steps

#### 10. Aesthetic-Usability Effect
> "Users often perceive aesthetically pleasing design as design that's more usable."

**TML Applicability:** LOW (subjective)
- **Potential Properties:**
  - `visual_consistency_score`
  - `whitespace_ratio`
  - `color_harmony_score`

### Principles

#### 11. Pareto Principle (80/20 Rule)
> "Roughly 80% of effects come from 20% of causes."

**TML Applicability:** MEDIUM
- **Audit Strategy:** Prioritize the 20% of UI elements that users interact with 80% of the time

#### 12. Parkinson's Law
> "Any task will inflate until all of the available time is spent."

**TML Applicability:** LOW
- **Potential Properties:**
  - `form_field_necessity` - only essential fields
  - `step_minimization` - fewest steps possible

#### 13. Tesler's Law (Conservation of Complexity)
> "For any system there is a certain amount of complexity which cannot be reduced."

**TML Applicability:** LOW (design philosophy)
- **Principle:** The system should absorb complexity, not the user

#### 14. Goal-Gradient Effect
> "People work harder as they get closer to achieving a goal."

**TML Applicability:** HIGH
- **Measurable Properties:**
  - `progress_bar_presence` - in multi-step flows
  - `completion_percentage_visibility`
  - `steps_remaining_indicator`

**Audit Rules:**
```json
{
  "rule_id": "goalgrad-001",
  "property": "multi_step_progress_indicator",
  "operator": "=",
  "value": "required",
  "message": "Multi-step processes must show progress indication"
}
```

#### 15. Doherty Threshold
> "Productivity increases when system response time is <400ms."

**TML Applicability:** HIGH
- **Measurable Properties:**
  - `interaction_response_time` <= 400ms
  - `feedback_delay` <= 100ms for immediate acknowledgment
  - `loading_state_trigger_time` - when to show loading indicators

**Audit Rules:**
```json
{
  "rule_id": "doherty-001",
  "property": "interaction_feedback_time",
  "operator": "<=",
  "value": "100ms",
  "message": "Provide immediate visual feedback within 100ms of interaction"
}
```

---

## Gestalt Principles

*Source: [Gestalt Principles - IxDF](https://www.interaction-design.org/literature/topics/gestalt-principles)*

### 1. Law of Proximity
> "Elements placed close together are perceived as a group."

**TML Applicability:** HIGH
- **Measurable Properties:**
  - `related_element_spacing` - spacing within groups < spacing between groups
  - `label_input_proximity` - labels near their inputs
  - `button_group_spacing` - consistent spacing in button groups

**Audit Rules:**
```json
{
  "rule_id": "gestalt-proximity-001",
  "property": "label_to_input_distance",
  "operator": "<=",
  "value": "8px",
  "message": "Labels should be close to their associated inputs"
}
```

### 2. Law of Similarity
> "Similar objects are perceived as related."

**TML Applicability:** HIGH
- **Measurable Properties:**
  - `link_style_consistency` - all links look the same
  - `button_style_consistency` - same-type buttons match
  - `icon_style_consistency` - unified icon style

**Audit Rules:**
```json
{
  "rule_id": "gestalt-similarity-001",
  "property": "link_visual_treatment",
  "operator": "=",
  "value": "consistent",
  "message": "All links should have consistent visual treatment"
}
```

### 3. Law of Common Region
> "Elements within a boundary are perceived as grouped."

**TML Applicability:** HIGH
- **Measurable Properties:**
  - `card_boundary_presence` - cards have visible boundaries
  - `section_delineation` - sections clearly separated
  - `modal_boundary` - modals clearly bounded

### 4. Law of Closure
> "The brain perceives incomplete objects as whole."

**TML Applicability:** LOW (design pattern, not measurable)

### 5. Law of Continuity
> "Elements on a line or curve are perceived as related."

**TML Applicability:** MEDIUM
- **Measurable Properties:**
  - `element_alignment` - items aligned on grid
  - `flow_direction_consistency` - consistent reading direction

### 6. Law of Prägnanz (Simplicity)
> "People perceive complex images in the simplest way possible."

**TML Applicability:** MEDIUM
- **Measurable Properties:**
  - `visual_complexity_score` - number of distinct elements
  - `layout_regularity` - adherence to grid

### 7. Figure-Ground
> "People perceive objects as either figure (foreground) or ground (background)."

**TML Applicability:** HIGH
- **Measurable Properties:**
  - `modal_overlay_contrast` - modal stands out from background
  - `focus_element_prominence` - focused element clearly in foreground
  - `layering_clarity` - clear z-index hierarchy

**Audit Rules:**
```json
{
  "rule_id": "gestalt-figureground-001",
  "property": "modal_backdrop_opacity",
  "operator": ">=",
  "value": "0.5",
  "message": "Modal backdrops should sufficiently dim background content"
}
```

### 8. Common Fate
> "Elements moving in the same direction are perceived as grouped."

**TML Applicability:** MEDIUM
- **Measurable Properties:**
  - `animation_direction_consistency` - grouped items animate together
  - `scroll_behavior_grouping` - related items scroll as unit

### 9. Focal Point
> "Whatever stands out visually captures attention first."

**TML Applicability:** HIGH
- **Measurable Properties:**
  - `primary_cta_visual_weight`
  - `heading_prominence`
  - `hero_element_contrast`

---

## Cognitive Psychology Principles

### Cognitive Load Theory

*Source: [NN/G - Minimize Cognitive Load](https://www.nngroup.com/articles/minimize-cognitive-load/)*

**Types of Cognitive Load:**
1. **Intrinsic Load** - inherent task complexity (unavoidable)
2. **Extraneous Load** - caused by poor design (minimize!)
3. **Germane Load** - productive learning effort (optimize)

**TML Applicability:** HIGH
- **Measurable Properties:**
  - `simultaneous_choices` <= 4
  - `visible_information_density`
  - `required_memory_items` - items user must remember
  - `instruction_clarity` - presence of inline help

**Audit Rules:**
```json
{
  "rule_id": "cogload-001",
  "property": "visible_form_fields",
  "operator": "<=",
  "value": 7,
  "message": "Show no more than 7 form fields at once to reduce cognitive load"
}
```

### Recognition Over Recall

*Already in Nielsen's heuristics*

**TML Applicability:** HIGH
- **Measurable Properties:**
  - `recent_items_visibility` - show recent selections
  - `autocomplete_presence` - for text inputs
  - `visual_cues_for_actions` - icons with labels

### Chunking

**TML Applicability:** HIGH
- **Measurable Properties:**
  - `phone_number_formatting` - groups of 3-4 digits
  - `credit_card_formatting` - groups of 4
  - `content_section_size` - logical content chunks

---

## Visual Design Principles

### Visual Hierarchy

*Source: [IxDF - Visual Hierarchy](https://www.interaction-design.org/literature/topics/visual-hierarchy)*

**TML Applicability:** HIGH
- **Measurable Properties:**
  - `heading_size_progression` - H1 > H2 > H3
  - `contrast_hierarchy` - important items have higher contrast
  - `size_hierarchy` - important items are larger
  - `position_hierarchy` - important items positioned prominently

**Audit Rules:**
```json
{
  "rule_id": "hierarchy-001",
  "property": "heading_size_ratio",
  "operator": ">=",
  "value": 1.25,
  "message": "Each heading level should be at least 1.25x larger than the next"
}
```

### F-Pattern & Z-Pattern

*Source: [99designs - F and Z Patterns](https://99designs.com/blog/tips/visual-hierarchy-landing-page-designs/)*

**F-Pattern:** For text-heavy pages (blogs, articles)
**Z-Pattern:** For minimal, CTA-focused pages (landing pages)

**TML Applicability:** MEDIUM
- **Measurable Properties:**
  - `key_content_position` - important content in pattern hotspots
  - `cta_position` - CTAs at pattern endpoints
  - `logo_position` - logo at pattern start (top-left)

### Whitespace

**TML Applicability:** HIGH
- **Measurable Properties:**
  - `element_breathing_room` - minimum padding around elements
  - `section_separation` - spacing between sections
  - `text_line_length` - 45-75 characters per line

**Audit Rules:**
```json
{
  "rule_id": "whitespace-001",
  "property": "paragraph_max_width",
  "operator": "<=",
  "value": "75ch",
  "message": "Text lines should not exceed 75 characters for readability"
}
```

### Color Psychology

**TML Applicability:** MEDIUM
- **Measurable Properties:**
  - `error_color` - red/orange for errors
  - `success_color` - green for success
  - `warning_color` - yellow/amber for warnings
  - `info_color` - blue for informational

---

## Interaction Design Principles

### Affordances & Signifiers

*Source: [IxDF - Affordances](https://www.interaction-design.org/literature/topics/affordances)*

**Don Norman's 6 Principles:**
1. Affordances - what actions are possible
2. Signifiers - cues indicating how to interact
3. Constraints - limiting possible actions
4. Mappings - relationship between controls and outcomes
5. Feedback - confirmation of actions
6. Conceptual Models - user's mental model

**TML Applicability:** HIGH
- **Measurable Properties:**
  - `button_affordance` - buttons look clickable
  - `link_signifier` - links are visually distinct
  - `draggable_signifier` - drag handles present
  - `scrollable_signifier` - scroll indicators visible

**Audit Rules:**
```json
{
  "rule_id": "affordance-001",
  "property": "button_visual_depth",
  "operator": "!=",
  "value": "flat_with_no_distinction",
  "message": "Buttons must visually indicate they are interactive"
}
```

### Direct Manipulation

**TML Applicability:** MEDIUM
- **Measurable Properties:**
  - `drag_drop_feedback` - visual feedback during drag
  - `inline_editing` - edit in place vs. modal
  - `undo_availability` - reversible actions

---

## Information Architecture

*Source: [NN/G - Card Sorting](https://www.nngroup.com/articles/card-sorting-definition/)*

### Peter Morville's 7 Principles

1. **Useful** - content fulfills a need
2. **Usable** - easy to use
3. **Desirable** - evokes emotion
4. **Findable** - navigable and locatable
5. **Accessible** - accessible to all
6. **Credible** - trustworthy
7. **Valuable** - delivers value

**TML Applicability:** MEDIUM (mostly qualitative)
- **Measurable Properties:**
  - `search_availability` - presence of search function
  - `breadcrumb_presence` - for deep hierarchies
  - `sitemap_availability` - for complex sites

### Navigation Depth

**TML Applicability:** HIGH
- **Measurable Properties:**
  - `click_depth_to_content` <= 3
  - `navigation_levels` <= 4
  - `back_button_presence`

**Audit Rules:**
```json
{
  "rule_id": "ia-001",
  "property": "maximum_click_depth",
  "operator": "<=",
  "value": 3,
  "message": "Key content should be reachable within 3 clicks"
}
```

---

## Form Design

*Source: [Smashing Magazine - Inline Validation](https://www.smashingmagazine.com/2022/09/inline-validation-web-forms-ux/)*

### Validation Patterns

**TML Applicability:** HIGH
- **Measurable Properties:**
  - `inline_validation_presence` - real-time feedback
  - `error_message_proximity` - errors near fields
  - `error_message_clarity` - actionable messages
  - `success_indication` - green checkmarks for valid

**Audit Rules:**
```json
{
  "rule_id": "form-001",
  "property": "form_error_placement",
  "operator": "=",
  "value": "adjacent_to_field",
  "message": "Error messages should appear next to the field with the error"
}
```

### Form Layout

**TML Applicability:** HIGH
- **Measurable Properties:**
  - `single_column_layout` - for most forms
  - `logical_field_grouping` - related fields together
  - `required_field_indication` - clear required markers
  - `optional_field_indication` - "(optional)" labels

**Audit Rules:**
```json
{
  "rule_id": "form-002",
  "property": "required_field_indicator",
  "operator": "=",
  "value": "present",
  "message": "Required fields must be clearly indicated"
}
```

### Input Optimization

**TML Applicability:** HIGH
- **Measurable Properties:**
  - `appropriate_input_type` - number for numbers, email for email
  - `autocomplete_attributes` - browser autofill support
  - `input_masking` - for formatted inputs (phone, CC)
  - `smart_defaults` - sensible pre-filled values

---

## Navigation Patterns

*Source: [NN/G - Menu Design](https://www.nngroup.com/articles/menu-design/)*

### Navigation Types

| Pattern | Best For | Max Items |
|---------|----------|-----------|
| Horizontal Nav | Primary navigation | 5-7 |
| Hamburger Menu | Mobile, secondary nav | Any |
| Tab Bar | Mobile primary nav | 3-5 |
| Mega Menu | Large sites, e-commerce | Complex hierarchies |
| Breadcrumbs | Deep hierarchies | n/a |
| Sidebar | Apps, dashboards | 10-15 |

**TML Applicability:** HIGH
- **Measurable Properties:**
  - `primary_nav_item_count` <= 7
  - `mobile_nav_pattern` - hamburger or tab bar
  - `breadcrumb_depth_threshold` - show for depth > 2

**Audit Rules:**
```json
{
  "rule_id": "nav-001",
  "property": "primary_navigation_items",
  "operator": "<=",
  "value": 7,
  "message": "Primary navigation should have 7 or fewer items"
}
```

---

## Feedback & System Status

### Microinteractions

*Source: [IxDF - Microinteractions](https://www.interaction-design.org/literature/article/micro-interactions-ux)*

**Dan Saffer's 4 Components:**
1. **Trigger** - what initiates the interaction
2. **Rules** - what happens next
3. **Feedback** - how the system responds
4. **Loops/Modes** - ongoing behavior

**TML Applicability:** HIGH
- **Measurable Properties:**
  - `button_press_feedback` - visual state change
  - `form_submit_feedback` - loading state
  - `hover_state_presence` - hover indication
  - `active_state_presence` - active/pressed state
  - `disabled_state_clarity` - obviously disabled

**Audit Rules:**
```json
{
  "rule_id": "micro-001",
  "property": "button_hover_state",
  "operator": "=",
  "value": "present",
  "message": "Buttons must have a visible hover state"
}
```

### System Status Indicators

**TML Applicability:** HIGH
- **Measurable Properties:**
  - `loading_indicator_presence`
  - `progress_bar_for_long_operations`
  - `success_confirmation_presence`
  - `error_notification_visibility`

---

## Loading & Performance Perception

*Source: [NN/G - Skeleton Screens](https://www.nngroup.com/articles/skeleton-screens/)*

### Loading Patterns

| Pattern | Use When | Perceived Speed Improvement |
|---------|----------|---------------------------|
| Spinner | 2-10 seconds | Baseline |
| Skeleton Screen | Full page load | 20-30% faster perception |
| Progress Bar | >10 seconds | Shows completion |
| Optimistic UI | Instant feedback | Near-instant |

**TML Applicability:** HIGH
- **Measurable Properties:**
  - `skeleton_screen_usage` - for full page loads
  - `spinner_usage` - for component loads
  - `progress_indicator_type` - determinate vs indeterminate
  - `loading_state_layout_stability` - no layout shift

**Audit Rules:**
```json
{
  "rule_id": "loading-001",
  "property": "full_page_loading_pattern",
  "operator": "=",
  "value": "skeleton_screen",
  "message": "Use skeleton screens for full-page loads to improve perceived performance"
}
```

### Response Time Thresholds

| Time | User Perception | Required Feedback |
|------|-----------------|-------------------|
| <100ms | Instantaneous | None needed |
| <400ms | Doherty threshold | Optional loading |
| <1000ms | Maintains flow | Show loading |
| <10s | Attention span limit | Progress bar |
| >10s | Task abandonment risk | Progress + time estimate |

---

## Emotional Design

*Source: [IxDF - Emotional Design](https://www.interaction-design.org/literature/topics/emotional-design)*

### Don Norman's 3 Levels

1. **Visceral** - immediate, sensory reaction (appearance)
2. **Behavioral** - usability and effectiveness (interaction)
3. **Reflective** - long-term impression and meaning (memory)

**TML Applicability:** LOW-MEDIUM (subjective)
- **Potential Properties:**
  - `visual_polish_score` - attention to detail
  - `delight_moments` - celebratory animations
  - `personality_consistency` - brand voice in UI

### Patrick Jordan's 4 Pleasures

1. **Physio-pleasure** - sensory pleasures
2. **Socio-pleasure** - social interactions
3. **Psycho-pleasure** - cognitive/emotional satisfaction
4. **Ideo-pleasure** - values and aspirations

---

## Persuasive Design & Gamification

*Source: [Think Design - Gamification](https://think.design/blog/gamification-in-ux-how-to-increase-engagement-and-retention-in-digital-products/)*

### Cialdini's 6 Principles of Persuasion

1. **Reciprocity** - give to receive
2. **Commitment/Consistency** - honor commitments
3. **Social Proof** - follow the crowd
4. **Authority** - trust experts
5. **Liking** - prefer those we like
6. **Scarcity** - value rare things

**TML Applicability:** MEDIUM
- **Measurable Properties:**
  - `social_proof_presence` - testimonials, reviews, counts
  - `scarcity_indicators` - "Only 3 left", time limits
  - `authority_signals` - certifications, logos, endorsements

### Gamification Elements

| Element | Purpose | TML Measurable? |
|---------|---------|-----------------|
| Progress bars | Goal gradient | Yes |
| Points/XP | Achievement | Partial |
| Badges | Recognition | Yes |
| Leaderboards | Competition | Yes |
| Streaks | Consistency | Partial |
| Levels | Progression | Partial |

**Audit Rules:**
```json
{
  "rule_id": "gamify-001",
  "property": "onboarding_progress_indicator",
  "operator": "=",
  "value": "present",
  "message": "Onboarding flows should show progress to encourage completion"
}
```

---

## Trust & Credibility

*Source: [Stanford Web Credibility Project](https://credibility.stanford.edu/guidelines/)*

### Stanford's 10 Web Credibility Guidelines

1. Make it easy to verify accuracy
2. Show there's a real organization behind the site
3. Highlight expertise in content and services
4. Show honest and trustworthy people behind the site
5. Make it easy to contact you
6. Design the site professionally
7. Make the site easy to use and useful
8. Update content frequently
9. Use restraint with promotional content
10. Avoid errors of all types

**TML Applicability:** HIGH
- **Measurable Properties:**
  - `contact_info_visibility` - phone, email, address
  - `about_page_presence`
  - `professional_design_signals` - no broken layouts
  - `ssl_certificate_presence`
  - `privacy_policy_presence`
  - `terms_of_service_presence`

**Audit Rules:**
```json
{
  "rule_id": "trust-001",
  "property": "contact_information",
  "operator": "=",
  "value": "visible",
  "message": "Contact information should be easily accessible"
}
```

### Trust Signals

**TML Applicability:** HIGH
- **Measurable Properties:**
  - `security_badge_presence` - SSL, security seals
  - `payment_security_indicators` - PCI compliance badges
  - `testimonial_authenticity` - named reviews with photos
  - `third_party_validation` - BBB, Trustpilot logos

---

## Mobile & Touch Design

*Source: [Smashing Magazine - Thumb Zone](https://www.smashingmagazine.com/2016/09/the-thumb-zone-designing-for-mobile-users/)*

### Thumb Zone

| Zone | Reachability | Best For |
|------|--------------|----------|
| Natural (bottom center) | Easy | Primary actions |
| Stretch (sides) | Moderate | Secondary actions |
| Hard (top corners) | Difficult | Rarely used |

**TML Applicability:** HIGH
- **Measurable Properties:**
  - `primary_cta_thumb_zone` - in natural zone
  - `bottom_navigation_presence` - for mobile
  - `floating_action_button_position`

**Audit Rules:**
```json
{
  "rule_id": "mobile-001",
  "property": "mobile_primary_action_position",
  "operator": "=",
  "value": "thumb_zone",
  "message": "Primary mobile actions should be in the thumb-friendly zone"
}
```

### Touch Targets

**TML Applicability:** HIGH (already partial in WCAG)
- **Measurable Properties:**
  - `touch_target_size` >= 44px (48px recommended)
  - `touch_target_spacing` >= 8px
  - `tap_feedback_time` <= 100ms

---

## Accessibility Beyond WCAG

*Source: [W3C - Cognitive Accessibility](https://www.w3.org/WAI/cognitive/)*

### Cognitive Accessibility

**TML Applicability:** HIGH
- **Measurable Properties:**
  - `clear_button_labels` - descriptive, not just icons
  - `consistent_navigation` - same on every page
  - `simple_language_level` - readability score
  - `timeout_extensions` - allow more time
  - `password_paste_allowed` - support password managers
  - `autosave_presence` - prevent data loss
  - `confirmation_before_destructive` - "Are you sure?"

**Audit Rules:**
```json
{
  "rule_id": "cog-access-001",
  "property": "destructive_action_confirmation",
  "operator": "=",
  "value": "required",
  "message": "Destructive actions must require confirmation"
}
```

### Motor Impairments

**TML Applicability:** HIGH
- **Measurable Properties:**
  - `generous_click_targets` >= 44px
  - `keyboard_navigation_support`
  - `no_hover_only_content` - important content accessible without hover
  - `minimal_precision_required` - no tiny targets

### Situational Disabilities

Consider users who are:
- In bright sunlight (need high contrast)
- One-handed (need thumb-friendly layout)
- Distracted (need clear focus states)
- In noisy environments (need visual alternatives to audio)

---

## Content UX & Microcopy

*Source: [Smashing Magazine - Microcopy](https://www.smashingmagazine.com/2024/06/how-improve-microcopy-ux-writing-tips-non-ux-writers/)*

### Error Message Guidelines

**TML Applicability:** HIGH
- **Measurable Properties:**
  - `error_message_tone` - not blaming ("We couldn't..." not "You failed...")
  - `error_message_actionability` - tells user what to do
  - `error_message_specificity` - explains what went wrong
  - `error_message_visibility` - clearly visible

**Audit Rules:**
```json
{
  "rule_id": "microcopy-001",
  "property": "error_message_format",
  "operator": "contains",
  "value": "actionable_suggestion",
  "message": "Error messages must include actionable next steps"
}
```

### Voice & Tone Consistency

**TML Applicability:** MEDIUM (qualitative)
- **Potential Properties:**
  - `brand_voice_consistency` - same tone throughout
  - `formality_level_consistency` - formal/casual match
  - `humor_appropriateness` - context-appropriate

---

## Empty States & Onboarding

*Source: [Smashing Magazine - Empty States](https://www.smashingmagazine.com/2017/02/user-onboarding-empty-states-mobile-apps/)*

### Empty State Types

1. **First-use** - new user, no data yet
2. **User-cleared** - user deleted all content
3. **No results** - search returned nothing
4. **Error** - something went wrong

**TML Applicability:** HIGH
- **Measurable Properties:**
  - `empty_state_guidance` - tells user what to do
  - `empty_state_illustration` - visual interest
  - `empty_state_cta` - clear action button
  - `empty_state_positivity` - encouraging tone

**Audit Rules:**
```json
{
  "rule_id": "empty-001",
  "property": "empty_state_content",
  "operator": "=",
  "value": "actionable",
  "message": "Empty states must guide users on what to do next"
}
```

### Onboarding Patterns

**TML Applicability:** HIGH
- **Measurable Properties:**
  - `onboarding_progress_indicator`
  - `onboarding_skip_option` - allow skipping
  - `onboarding_brevity` - minimal required steps
  - `contextual_help_availability` - tooltips, hints

---

## Dark Patterns (Anti-Patterns)

*Source: [NN/G - Deceptive Patterns](https://www.nngroup.com/articles/deceptive-patterns/)*

### Patterns to PREVENT (audit for absence)

| Dark Pattern | Description | TML Detection |
|--------------|-------------|---------------|
| Confirmshaming | Guilt-trip decline options | Text analysis |
| Forced Continuity | Hidden auto-renewal | Subscription flow analysis |
| Hidden Costs | Surprise fees at checkout | Price consistency check |
| Roach Motel | Easy to get in, hard to get out | Account deletion accessibility |
| Misdirection | Attention drawn from important info | Visual hierarchy analysis |
| Trick Questions | Confusing opt-in/opt-out | Checkbox default state |
| Sneaking | Adding unwanted items | Cart modification detection |
| Disguised Ads | Ads that look like content | Content/ad distinction |

**TML Applicability:** HIGH (audit for ABSENCE of dark patterns)
- **Measurable Properties:**
  - `unsubscribe_accessibility` - easy to find and use
  - `account_deletion_steps` <= 3
  - `preselected_upsells` = false
  - `decline_option_prominence` - not hidden or tiny
  - `price_transparency` - all costs shown upfront

**Audit Rules:**
```json
{
  "rule_id": "nodark-001",
  "property": "decline_button_size",
  "operator": ">=",
  "value": "accept_button_size * 0.8",
  "message": "Decline/cancel buttons must not be significantly smaller than accept buttons"
}
```

---

## Gap Analysis: TML Coverage

### Currently Well-Covered

| Category | Coverage | Notes |
|----------|----------|-------|
| WCAG Accessibility | 80% | Missing cognitive, situational |
| Nielsen Heuristics | 60% | Mostly qualitative |
| Visual Properties | 70% | Good CSS property coverage |
| Color/Typography | 90% | Strong palette/font extraction |

### Major Gaps to Address

#### HIGH PRIORITY (Highly Measurable, High Impact)

1. **Fitts's Law Properties**
   - Button sizes, CTA positions, clickable areas

2. **Hick's Law Properties**
   - Navigation item counts, choice counts, dropdown sizes

3. **Miller's Law Properties**
   - Chunk sizes, form field counts, wizard steps

4. **Response Time Thresholds**
   - Doherty threshold, feedback timing

5. **Form Validation Patterns**
   - Error placement, inline validation, success states

6. **Loading State Patterns**
   - Skeleton screens, progress indicators, optimistic UI

7. **Empty State Guidelines**
   - First-use guidance, no-results messaging

8. **Dark Pattern Detection**
   - Confirmshaming, hidden costs, misdirection

9. **Mobile Thumb Zone**
   - Primary action placement, touch target spacing

10. **Cognitive Accessibility**
    - Confirmation dialogs, autosave, password handling

#### MEDIUM PRIORITY (Partially Measurable)

1. **Gestalt Principles**
   - Proximity, similarity, common region (layout analysis)

2. **Visual Hierarchy**
   - Size progression, contrast hierarchy, Z-pattern compliance

3. **Trust Signals**
   - Contact visibility, security badges, social proof

4. **Navigation Depth**
   - Click depth, breadcrumb presence

5. **Progress Indicators**
   - Goal gradient, completion percentage

#### LOW PRIORITY (Qualitative/Subjective)

1. **Emotional Design**
   - Visceral/behavioral/reflective (subjective)

2. **Voice & Tone**
   - Brand consistency (requires NLP)

3. **Aesthetic-Usability Effect**
   - Visual polish (subjective)

---

## Recommended TML Schema Extensions

### New Property Categories

```json
{
  "tml_extensions": {
    "cognitive": {
      "navigation_item_count": "number",
      "visible_choices": "number",
      "form_fields_per_section": "number",
      "wizard_step_count": "number",
      "memory_required_items": "number"
    },
    "timing": {
      "interaction_feedback_ms": "number",
      "loading_indicator_trigger_ms": "number",
      "animation_duration_ms": "number"
    },
    "layout": {
      "click_depth_to_key_content": "number",
      "thumb_zone_primary_actions": "boolean",
      "single_column_form": "boolean"
    },
    "states": {
      "empty_state_guidance": "boolean",
      "loading_skeleton_screens": "boolean",
      "error_message_actionable": "boolean",
      "progress_indicator_present": "boolean"
    },
    "trust": {
      "contact_info_visible": "boolean",
      "security_badges_present": "boolean",
      "social_proof_present": "boolean"
    },
    "anti_patterns": {
      "confirmshaming_absent": "boolean",
      "equal_option_prominence": "boolean",
      "transparent_pricing": "boolean",
      "easy_unsubscribe": "boolean"
    }
  }
}
```

---

## Sources

### Primary References

- [Laws of UX](https://lawsofux.com/) - Jon Yablonski
- [Nielsen Norman Group](https://www.nngroup.com/) - Jakob Nielsen, Don Norman
- [Interaction Design Foundation](https://www.interaction-design.org/)
- [Stanford Web Credibility Project](https://credibility.stanford.edu/)
- [Smashing Magazine UX Articles](https://www.smashingmagazine.com/)
- [W3C Cognitive Accessibility](https://www.w3.org/WAI/cognitive/)
- [Deceptive Design](https://www.deceptive.design/) - Harry Brignull

### Key Books

- "Laws of UX" - Jon Yablonski
- "The Design of Everyday Things" - Don Norman
- "Emotional Design" - Don Norman
- "Don't Make Me Think" - Steve Krug
- "Microinteractions" - Dan Saffer
- "Designing Pleasurable Products" - Patrick Jordan

---

## Next Steps

1. **Prioritization Workshop** - Rank extensions by implementation feasibility and user impact
2. **Detection Algorithms** - Design programmatic detection methods for each property
3. **Scoring System** - Create weighted scoring for comprehensive UX audits
4. **Test Suite Development** - Build automated tests for new TML properties
5. **User Validation** - Test TML extensions with real design audits

---

*This document represents research completed January 2026. UX principles are continuously evolving and should be periodically reviewed and updated.*
