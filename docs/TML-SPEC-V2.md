# TML Specification V2.0 - Interactive UX Rules

**Taste Markup Language (TML)** is a machine-readable format for expressing UI/UX design constraints and style rules. Version 2.0 extends the original static rule system to support **interactive UX principles** including temporal, behavioral, spatial, and pattern-based validations.

## Table of Contents

1. [Overview](#overview)
2. [Rule Categories](#rule-categories)
3. [Schema Extensions](#schema-extensions)
4. [Interactive UX Principles](#interactive-ux-principles)
5. [Video Audit Pipeline](#video-audit-pipeline)
6. [Rule Format](#rule-format)
7. [API Endpoints](#api-endpoints)
8. [Examples](#examples)

---

## Overview

TML V2.0 introduces four new rule categories beyond the original `STATIC` rules:

| Category | Purpose | Input Source |
|----------|---------|--------------|
| `STATIC` | Visual properties (color, font, spacing) | Screenshot/URL |
| `TEMPORAL` | Time-based constraints (response time, animation) | Video/Replay |
| `BEHAVIORAL` | Interaction patterns (form flow, counts) | Video/Replay |
| `SPATIAL` | Layout and positioning (touch targets, zones) | Screenshot/Video |
| `PATTERN` | Dark pattern detection (manipulative UI) | Video/Replay |

### Design Philosophy

1. **Separation of Concerns**: Claude Vision extracts measurable values from frames; the rules engine validates deterministically
2. **Frame-Based Analysis**: Videos are converted to keyframes for Claude Vision API compatibility
3. **Temporal Metrics as First-Class**: Timing between state changes is measured and stored explicitly
4. **Backward Compatible**: Existing static rules continue to work unchanged

---

## Rule Categories

### STATIC Rules (V1 Compatibility)

Static rules validate visual properties at a single point in time:

```json
{
  "rule_id": "wcag-contrast-text",
  "rule_category": "STATIC",
  "property": "text_contrast_ratio",
  "operator": ">=",
  "value": "4.5",
  "severity": "error",
  "message": "Text must have 4.5:1 contrast ratio (WCAG AA)"
}
```

### TEMPORAL Rules

Temporal rules validate timing between user actions and system responses:

```json
{
  "rule_id": "doherty-feedback-time",
  "rule_category": "TEMPORAL",
  "property": "interaction_feedback_time",
  "operator": "<=",
  "value": "100",
  "timing_constraint_ms": 100,
  "severity": "error",
  "message": "Visual feedback must appear within 100ms of user action"
}
```

Key temporal thresholds based on UX research:
- **100ms**: Perceptual instantaneous (Doherty Threshold)
- **400ms**: Maximum for maintaining flow state
- **1000ms**: Loading indicator must appear
- **10000ms**: Maximum attention span

### BEHAVIORAL Rules

Behavioral rules validate interaction patterns and cognitive load:

```json
{
  "rule_id": "hicks-nav-items",
  "rule_category": "BEHAVIORAL",
  "property": "primary_nav_item_count",
  "operator": "<=",
  "value": "7",
  "count_property": "primary_nav_items",
  "severity": "warning",
  "message": "Primary navigation should have 7 or fewer items (Hick's Law)"
}
```

### SPATIAL Rules

Spatial rules validate layout, positioning, and touch target sizes:

```json
{
  "rule_id": "fitts-cta-min-size",
  "rule_category": "SPATIAL",
  "property": "cta_touch_target_size",
  "operator": ">=",
  "value": "44px",
  "zone_definition": {"min_width": 44, "min_height": 44},
  "severity": "error",
  "message": "Primary CTA must be at least 44x44px for reliable targeting"
}
```

### PATTERN Rules

Pattern rules detect manipulative or deceptive UI patterns:

```json
{
  "rule_id": "dark-confirm-shaming",
  "rule_category": "PATTERN",
  "property": "decline_button_shame_language",
  "operator": "=",
  "value": "false",
  "pattern_indicators": ["No thanks, I don't want", "I'll stay", "I prefer not to save"],
  "severity": "error",
  "message": "Decline options must not use shame language (dark pattern)"
}
```

---

## Schema Extensions

### StyleRule Model

Extended from V1 with new fields:

```python
class StyleRuleModel(Base):
    __tablename__ = "style_rules"

    # V1 Fields
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("extraction_sessions.id"))
    component = Column(String)
    property = Column(String)
    value = Column(JSON)
    operator = Column(String, default="=")
    severity = Column(String, default="warning")
    message = Column(String)
    source = Column(String)  # "extracted", "stated", "baseline"

    # V2 Extensions
    rule_category = Column(String, default="STATIC")  # STATIC|TEMPORAL|BEHAVIORAL|SPATIAL|PATTERN
    timing_constraint_ms = Column(Integer, nullable=True)  # For temporal rules
    count_property = Column(String, nullable=True)  # For counting rules
    zone_definition = Column(JSON, nullable=True)  # For spatial rules
    pattern_indicators = Column(JSON, nullable=True)  # For dark pattern detection
```

### New Models

```python
class InteractionRecordingModel(Base):
    """Tracks video or Playwright recordings for interactive audit."""
    __tablename__ = "interaction_recordings"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("extraction_sessions.id"))
    source_type = Column(String)  # "video" | "playwright"
    status = Column(String, default="pending")  # pending|processing|completed|failed
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    duration_ms = Column(Integer, nullable=True)
    frame_count = Column(Integer, default=0)

class InteractionFrameModel(Base):
    """Individual frame extracted from recording."""
    __tablename__ = "interaction_frames"

    id = Column(Integer, primary_key=True)
    recording_id = Column(Integer, ForeignKey("interaction_recordings.id"))
    frame_number = Column(Integer)
    timestamp_ms = Column(Integer)
    frame_path = Column(String)
    extracted_values = Column(JSON, nullable=True)  # Claude-extracted data

class TemporalMetricModel(Base):
    """Timing measurements between frames."""
    __tablename__ = "temporal_metrics"

    id = Column(Integer, primary_key=True)
    recording_id = Column(Integer, ForeignKey("interaction_recordings.id"))
    metric_type = Column(String)  # response_time, animation_duration, etc.
    start_frame_id = Column(Integer, ForeignKey("interaction_frames.id"))
    end_frame_id = Column(Integer, ForeignKey("interaction_frames.id"))
    duration_ms = Column(Integer)
    context = Column(JSON, nullable=True)
```

---

## Interactive UX Principles

TML V2.0 implements rules for 10 core UX principles:

### 1. Fitts's Law
Target acquisition time depends on distance and size.

| Rule ID | Constraint |
|---------|------------|
| `fitts-cta-min-size` | CTA >= 44x44px |
| `fitts-button-spacing` | Button spacing >= 8px |
| `fitts-corner-targets` | Interactive elements avoid corners |

### 2. Hick's Law
Decision time increases logarithmically with choices.

| Rule ID | Constraint |
|---------|------------|
| `hicks-nav-items` | Primary nav <= 7 items |
| `hicks-dropdown-options` | Dropdown <= 10 options ungrouped |
| `hicks-action-buttons` | Modal <= 3 actions |

### 3. Miller's Law
Working memory limited to 7±2 items.

| Rule ID | Constraint |
|---------|------------|
| `miller-form-sections` | Form section <= 7 fields |
| `miller-wizard-steps` | Wizard <= 7 steps |
| `miller-breadcrumb-depth` | Breadcrumbs <= 5 levels |

### 4. Doherty Threshold
System response < 400ms maintains flow.

| Rule ID | Constraint |
|---------|------------|
| `doherty-feedback-time` | Feedback <= 100ms |
| `doherty-state-transition` | Transitions <= 400ms |
| `doherty-loading-indicator` | Loader appears <= 1000ms |

### 5. Form Validation
Immediate, inline feedback patterns.

| Rule ID | Constraint |
|---------|------------|
| `form-inline-validation` | Has inline validation |
| `form-error-proximity` | Error <= 24px from field |
| `form-submit-feedback` | Submit shows processing state |

### 6. Loading States
Progressive disclosure during waits.

| Rule ID | Constraint |
|---------|------------|
| `loading-skeleton-presence` | Has skeleton for content |
| `loading-progress-determinate` | Progress bar for >3s ops |

### 7. Empty States
Helpful guidance when no content.

| Rule ID | Constraint |
|---------|------------|
| `empty-state-guidance` | Has CTA in empty state |
| `empty-state-explanation` | Explains why empty |

### 8. Dark Pattern Detection
Identifies manipulative UI.

| Rule ID | Detects |
|---------|---------|
| `dark-confirm-shaming` | Shame language on decline |
| `dark-hidden-costs` | Late fee disclosure |
| `dark-preselected-options` | Pre-checked add-ons |
| `dark-roach-motel` | Cancel harder than signup |

### 9. Mobile Thumb Zone
Reachability for one-handed use.

| Rule ID | Constraint |
|---------|------------|
| `thumb-primary-cta-zone` | CTA in bottom 200px |
| `thumb-nav-reachability` | Nav in reachable zone |

### 10. Cognitive Accessibility
Clear language, predictable patterns.

| Rule ID | Constraint |
|---------|------------|
| `cognitive-reading-level` | Body text <= grade 8 |
| `cognitive-consistent-terminology` | Same terms for same concepts |

---

## Video Audit Pipeline

### Input Sources

```
User Video (.mp4/.webm) ──┐
                          ├──▶ Frame Extraction ──▶ Claude Vision ──▶ Rule Validation
Playwright Replay ────────┘           │
                                      ▼
                              Temporal Analysis
                              (timing between states)
```

### Frame Extraction (FFmpeg)

1. **Regular Sampling**: Extract frames every 500ms
2. **Scene Detection**: Capture on visual change threshold (>30%)
3. **Deduplication**: Skip near-identical consecutive frames

```bash
# Regular interval extraction
ffmpeg -i input.mp4 -vf "fps=2" frame_%04d.png

# Scene change detection
ffmpeg -i input.mp4 -vf "select='gt(scene,0.3)'" -vsync vfr scene_%04d.png
```

### Claude Vision Extraction

Each frame is analyzed with prompts like:

```
Analyze this UI screenshot and extract:

## Spatial Measurements (Fitts's Law)
- Touch target sizes (width x height in pixels)
- Distance between primary CTA and form fields
- Spacing between adjacent interactive elements

## Count Properties (Hick's/Miller's Law)
- Number of primary navigation items
- Number of options in visible dropdowns
- Number of form fields visible

## State Detection
- Is there a loading indicator visible?
- Is there an empty state?
- Are there error messages?

## Dark Pattern Indicators
- Text on decline/cancel buttons (exact wording)
- Are any checkboxes pre-selected?

Return as JSON with exact measurements.
```

### Temporal Metric Calculation

Compare sequential frames to measure:
- **Response Time**: Action → Feedback
- **State Transition**: Loading → Loaded
- **Animation Duration**: Start → End

---

## Rule Format

### Full Rule Schema

```typescript
interface TMLRule {
  // Required
  rule_id: string;           // Unique identifier
  property: string;          // What is being measured
  operator: string;          // Comparison: =, !=, <, <=, >, >=, contains
  value: string | number;    // Expected value
  severity: 'error' | 'warning' | 'info';
  message: string;           // Human-readable explanation

  // V2 Extensions
  rule_category: 'STATIC' | 'TEMPORAL' | 'BEHAVIORAL' | 'SPATIAL' | 'PATTERN';

  // Optional by category
  timing_constraint_ms?: number;  // TEMPORAL: threshold in ms
  count_property?: string;        // BEHAVIORAL: what to count
  zone_definition?: {             // SPATIAL: area constraints
    min_width?: number;
    min_height?: number;
    position?: 'top' | 'bottom' | 'center';
  };
  pattern_indicators?: string[];  // PATTERN: strings/patterns to detect
}
```

### Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `=` | Equals | `color = "#000000"` |
| `!=` | Not equals | `overlay != "none"` |
| `<` | Less than | `response_time < 100` |
| `<=` | Less than or equal | `nav_items <= 7` |
| `>` | Greater than | `contrast_ratio > 4.5` |
| `>=` | Greater than or equal | `touch_target >= 44` |
| `contains` | String contains | `error_text contains "required"` |

---

## API Endpoints

### Video Audit

```http
POST /api/audit/interactive/video
Content-Type: multipart/form-data

video: <file>
session_id: <int>

Response:
{
  "id": 1,
  "session_id": 5,
  "source_type": "video",
  "status": "processing",
  "frame_count": 0
}
```

### Get Recording Status

```http
GET /api/audit/interactive/recording/{recording_id}

Response:
{
  "id": 1,
  "session_id": 5,
  "source_type": "video",
  "status": "completed",
  "frame_count": 24,
  "duration_ms": 12000
}
```

### Get Audit Results

```http
GET /api/audit/interactive/recording/{recording_id}/results

Response:
{
  "recording_id": 1,
  "total_frames": 24,
  "duration_ms": 12000,
  "temporal_violations": [
    {
      "rule_id": "doherty-feedback-time",
      "severity": "error",
      "message": "Feedback took 450ms, exceeds 100ms threshold",
      "measured_value": 450,
      "threshold": 100
    }
  ],
  "spatial_violations": [...],
  "behavioral_violations": [...],
  "pattern_violations": [...],
  "summary": {
    "total_violations": 5,
    "errors": 2,
    "warnings": 3,
    "temporal_metrics_count": 8,
    "frames_analyzed": 24
  }
}
```

### Get Available Rules

```http
GET /api/audit/rules/available

Response:
{
  "total_rules": 140,
  "by_category": {
    "STATIC": 70,
    "TEMPORAL": 15,
    "BEHAVIORAL": 25,
    "SPATIAL": 15,
    "PATTERN": 15
  },
  "rules": [...]
}
```

---

## Examples

### Example 1: Slow Button Response

**Input**: User video showing button click with delayed feedback

**Extracted Data**:
```json
{
  "frame_5": {"state": "button_clicked", "timestamp_ms": 1500},
  "frame_8": {"state": "loading_shown", "timestamp_ms": 2100}
}
```

**Temporal Metric**:
```json
{
  "metric_type": "interaction_feedback_time",
  "duration_ms": 600
}
```

**Violation**:
```json
{
  "rule_id": "doherty-feedback-time",
  "severity": "error",
  "message": "Visual feedback must appear within 100ms of user action",
  "measured_value": 600,
  "threshold": 100
}
```

### Example 2: Dark Pattern Detection

**Input**: Screenshot of newsletter unsubscribe modal

**Extracted Data**:
```json
{
  "decline_button_text": "No thanks, I don't want to save money",
  "confirm_button_text": "Keep my subscription"
}
```

**Violation**:
```json
{
  "rule_id": "dark-confirm-shaming",
  "severity": "error",
  "message": "Decline options must not use shame language",
  "pattern_detected": "No thanks, I don't want"
}
```

### Example 3: Fitts's Law Violation

**Input**: Mobile screenshot with small buttons

**Extracted Data**:
```json
{
  "submit_button": {"width": 32, "height": 28}
}
```

**Violation**:
```json
{
  "rule_id": "fitts-cta-min-size",
  "severity": "error",
  "message": "Primary CTA must be at least 44x44px",
  "found": "32x28px",
  "expected": "44x44px minimum"
}
```

---

## Migration from V1

TML V2.0 is fully backward compatible. Existing V1 rules work unchanged:

1. All existing rules default to `rule_category: "STATIC"`
2. Static audit endpoints (`/audit/screenshot`, `/audit/url`) unchanged
3. New interactive endpoints are additive (`/audit/interactive/*`)

To upgrade rules to V2:
1. Add `rule_category` field to all rules
2. For temporal rules, add `timing_constraint_ms`
3. For behavioral rules, add `count_property`
4. For spatial rules, add `zone_definition`
5. For pattern rules, add `pattern_indicators`

---

## Appendix: Complete Rule Reference

See `backend/src/interactive_baseline_rules.py` for the complete list of 70+ interactive UX rules organized by principle.

See `backend/src/baseline_rules.py` for the complete list of 70+ static WCAG and Nielsen heuristic rules.
