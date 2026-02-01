# TasteMaker Technical Specification

**Purpose:** Comprehensive technical specification for TasteMaker v1 MVP - the UI/UX taste extraction tool.

---

## Project Structure

```
tastemaker/
├── backend/                    # FastAPI + SQLAlchemy + Alembic
│   ├── src/
│   │   ├── main.py            # FastAPI app entry
│   │   ├── models.py          # SQLAlchemy models + Pydantic schemas
│   │   ├── db_config.py       # Database configuration
│   │   ├── auth_routes.py     # Email/password authentication
│   │   ├── session_routes.py  # Extraction session management
│   │   ├── comparison_routes.py # A/B comparison handling
│   │   ├── rule_routes.py     # Rule synthesis and management
│   │   ├── skill_routes.py    # Skill package generation
│   │   ├── variation_service.py # Component variation generation
│   │   ├── pattern_analyzer.py # User choice pattern analysis
│   │   ├── rule_synthesizer.py # Pattern to rule conversion
│   │   ├── skill_packager.py  # Agent Skills format output
│   │   └── baseline_rules.py  # WCAG + Nielsen baseline rules
│   ├── migrations/            # Alembic migrations
│   ├── alembic.ini
│   ├── requirements.txt
│   └── .env
├── frontend/                   # React + TypeScript + Vite + Tailwind
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── ui/            # Base UI components (multiple libraries)
│   │   │   │   ├── shadcn/    # shadcn/ui components
│   │   │   │   ├── material/  # Material UI components
│   │   │   │   └── radix/     # Radix primitives
│   │   │   ├── comparison/    # A/B comparison UI
│   │   │   ├── extraction/    # Extraction flow components
│   │   │   └── review/        # Rule review components
│   │   ├── pages/
│   │   │   ├── Landing.tsx
│   │   │   ├── Login.tsx
│   │   │   ├── Register.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── ExtractionSession.tsx
│   │   │   ├── RuleReview.tsx
│   │   │   └── SkillDownload.tsx
│   │   ├── contexts/
│   │   │   ├── AuthContext.tsx
│   │   │   └── SessionContext.tsx
│   │   ├── services/
│   │   │   └── api.ts
│   │   └── types/
│   │       └── index.ts
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── tsconfig.json
├── CLAUDE.md                   # Project documentation for Claude
└── TASTEMAKER-RALPH-SPEC.md   # This file
```

---

## User Stories & Technical Specs

### Epic 1: Authentication & User Management

#### US-1.1: User Registration
**As a** vibe coder
**I want to** create an account with email and password
**So that** my extraction sessions are saved and I can download skills later

**Acceptance Criteria:**
- [ ] Registration form with email, password, confirm password, first name, last name
- [ ] Password minimum 8 characters with validation feedback
- [ ] Email uniqueness validation (400 error if exists)
- [ ] Successful registration returns JWT token
- [ ] User redirected to dashboard after registration

**Technical Spec:**
```python
# POST /api/auth/register
# Request: { email, password, first_name, last_name }
# Response: { access_token, user: { id, email, first_name, last_name } }
```

**Validation Command:**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@tastemaker.dev","password":"testpass123","first_name":"Test","last_name":"User"}'
# Expect: 201 with access_token
```

---

#### US-1.2: User Login
**As a** returning user
**I want to** log in with my email and password
**So that** I can access my previous sessions and skills

**Acceptance Criteria:**
- [ ] Login form with email and password
- [ ] Invalid credentials show error message
- [ ] Successful login returns JWT token
- [ ] User redirected to dashboard

**Technical Spec:**
```python
# POST /api/auth/login
# Request: { email, password }
# Response: { access_token, user: { id, email, first_name, last_name } }
```

**Validation Command:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@tastemaker.dev","password":"testpass123"}'
# Expect: 200 with access_token
```

---

#### US-1.3: Get Current User
**As an** authenticated user
**I want to** retrieve my profile information
**So that** the app can display my details and settings

**Acceptance Criteria:**
- [ ] GET /api/auth/me returns user profile
- [ ] Requires valid JWT in Authorization header
- [ ] 401 if token invalid/missing

**Validation Command:**
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer ${TOKEN}"
# Expect: 200 with user object
```

---

### Epic 2: Extraction Session Management

#### US-2.1: Create New Session
**As a** user
**I want to** start a new extraction session
**So that** I can begin defining my style preferences

**Acceptance Criteria:**
- [ ] Create session with name and optional brand colors
- [ ] Session gets unique ID
- [ ] Session starts in "territory_mapping" phase
- [ ] Session linked to authenticated user

**Technical Spec:**
```python
# POST /api/sessions
# Request: { name, brand_colors?: string[] }
# Response: { id, name, phase, created_at, comparison_count, confidence_score }
```

**Database Model:**
```python
class ExtractionSessionModel(Base):
    __tablename__ = "extraction_sessions"
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String, nullable=False)
    phase = Column(String, default="territory_mapping")  # territory_mapping, dimension_isolation, stated_preferences, complete
    brand_colors = Column(Text, nullable=True)  # JSON array
    comparison_count = Column(Integer, default=0)
    confidence_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
```

**Validation Command:**
```bash
curl -X POST http://localhost:8000/api/sessions \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"name":"My Style Profile"}'
# Expect: 201 with session object
```

---

#### US-2.2: List User Sessions
**As a** user
**I want to** see all my extraction sessions
**So that** I can continue a previous session or start fresh

**Acceptance Criteria:**
- [ ] List shows all sessions for current user
- [ ] Sessions sorted by updated_at descending
- [ ] Each session shows name, phase, comparison_count, confidence_score

**Validation Command:**
```bash
curl -X GET http://localhost:8000/api/sessions \
  -H "Authorization: Bearer ${TOKEN}"
# Expect: 200 with array of sessions
```

---

#### US-2.3: Get Session Details
**As a** user
**I want to** view details of a specific session
**So that** I can see my progress and continue the extraction

**Acceptance Criteria:**
- [ ] Returns session with all comparisons and extracted rules
- [ ] 404 if session doesn't exist or belongs to another user

**Validation Command:**
```bash
curl -X GET http://localhost:8000/api/sessions/1 \
  -H "Authorization: Bearer ${TOKEN}"
# Expect: 200 with session details
```

---

### Epic 3: A/B Comparison Flow

#### US-3.1: Get Next Comparison (Territory Mapping)
**As a** user in the territory mapping phase
**I want to** see two dramatically different UI variations
**So that** I can indicate which aesthetic direction I prefer

**Acceptance Criteria:**
- [ ] Returns two component variations (option_a, option_b)
- [ ] Variations differ across 5-8 style properties
- [ ] Component type cycles through: button, input, card, typography, navigation, form, feedback, modal
- [ ] Each variation has unique ID and full style specification

**Technical Spec:**
```python
# GET /api/sessions/{session_id}/comparison
# Response: {
#   comparison_id: int,
#   component_type: string,
#   phase: string,
#   option_a: { id, styles: {...} },
#   option_b: { id, styles: {...} },
#   context: string  # "landing_hero" | "dashboard" | "form_wizard" | "settings"
# }
```

**Component Variation Generation:**
```python
# variation_service.py generates variations with these property ranges:
BUTTON_PROPERTIES = {
    "border_radius": [0, 4, 8, 12, 16, 9999],  # px
    "padding_x": [12, 16, 20, 24, 32],
    "padding_y": [8, 10, 12, 14, 16],
    "font_weight": [400, 500, 600, 700],
    "font_size": [12, 14, 16, 18],
    "text_transform": ["none", "uppercase"],
    "shadow": ["none", "sm", "md", "lg"],
    "background_style": ["solid", "gradient", "outline"],
}

INPUT_PROPERTIES = {
    "border_radius": [0, 4, 8, 12],
    "border_width": [1, 2],
    "padding_x": [12, 16, 20],
    "padding_y": [10, 12, 14],
    "label_position": ["above", "floating", "inline"],
    "focus_ring": ["none", "thin", "thick"],
}

# ... similar for other component types
```

**Validation Command:**
```bash
curl -X GET http://localhost:8000/api/sessions/1/comparison \
  -H "Authorization: Bearer ${TOKEN}"
# Expect: 200 with comparison object containing option_a and option_b
```

---

#### US-3.2: Submit Comparison Choice
**As a** user viewing a comparison
**I want to** select my preferred option (or indicate no preference)
**So that** the system can learn my style preferences

**Acceptance Criteria:**
- [ ] Accept choice: "a", "b", or "none"
- [ ] Record decision time (ms) for implicit signal
- [ ] Store comparison result in database
- [ ] Return updated session progress

**Technical Spec:**
```python
# POST /api/sessions/{session_id}/comparison/{comparison_id}
# Request: { choice: "a" | "b" | "none", decision_time_ms: int }
# Response: { session_progress: {...}, next_phase?: string }

class ComparisonResultModel(Base):
    __tablename__ = "comparison_results"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("extraction_sessions.id", ondelete="CASCADE"))
    comparison_id = Column(Integer)
    component_type = Column(String)
    phase = Column(String)
    option_a_styles = Column(Text)  # JSON
    option_b_styles = Column(Text)  # JSON
    choice = Column(String)  # "a", "b", "none"
    decision_time_ms = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**Validation Command:**
```bash
curl -X POST http://localhost:8000/api/sessions/1/comparison/1 \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"choice":"a","decision_time_ms":2500}'
# Expect: 200 with session progress
```

---

#### US-3.3: Phase Transition to Dimension Isolation
**As a** user who completed territory mapping
**I want to** automatically transition to dimension isolation
**So that** the system can refine my preferences

**Acceptance Criteria:**
- [ ] After 10-15 territory mapping comparisons, phase changes
- [ ] System identifies high-signal properties from territory mapping
- [ ] Dimension isolation comparisons isolate single variables

**Technical Spec:**
```python
# pattern_analyzer.py
def analyze_territory_mapping(results: List[ComparisonResult]) -> Dict[str, float]:
    """
    Returns confidence scores for each property based on correlation
    between property values and user choices.
    """
    # Track which property values correlate with chosen options
    # Return dict like {"border_radius_high": 0.85, "shadow_present": 0.72, ...}
```

---

#### US-3.4: Dimension Isolation Comparisons
**As a** user in dimension isolation phase
**I want to** see comparisons that vary only one property
**So that** I can precisely define my preferences

**Acceptance Criteria:**
- [ ] Comparisons show same base component with ONE property difference
- [ ] Property to test selected based on Phase 1 uncertainty
- [ ] 20-30 comparisons in this phase
- [ ] Higher-confidence rules established

**Validation Command:**
```bash
# Get comparison in dimension_isolation phase
curl -X GET http://localhost:8000/api/sessions/1/comparison \
  -H "Authorization: Bearer ${TOKEN}"
# Expect: option_a and option_b differ by exactly one property
```

---

### Epic 4: Stated Preferences (Manual Rules)

#### US-4.1: Add Stated Preference
**As a** user
**I want to** add explicit rules via natural language
**So that** I can capture preferences that A/B testing might miss

**Acceptance Criteria:**
- [ ] Accept natural language input: "never use gradients"
- [ ] Parse into structured rule with property, operator, value
- [ ] Mark as "stated" (vs "extracted") with maximum confidence
- [ ] Allow component-specific or global rules

**Technical Spec:**
```python
# POST /api/sessions/{session_id}/rules
# Request: { statement: "never use gradients", component?: string }
# Response: { rule_id, property, operator, value, scope, confidence: 1.0, source: "stated" }

class StyleRuleModel(Base):
    __tablename__ = "style_rules"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("extraction_sessions.id", ondelete="CASCADE"))
    rule_id = Column(String)  # e.g., "btn-001"
    component_type = Column(String, nullable=True)  # null = global
    property = Column(String)
    operator = Column(String)  # "=", ">=", "<=", "!=", "contains", "not_contains"
    value = Column(Text)  # JSON for complex values
    severity = Column(String, default="warning")  # "error", "warning", "info"
    confidence = Column(Float)
    source = Column(String)  # "extracted", "stated", "baseline"
    message = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**Validation Command:**
```bash
curl -X POST http://localhost:8000/api/sessions/1/rules \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"statement":"never use drop shadows"}'
# Expect: 201 with parsed rule
```

---

#### US-4.2: Review Extracted Rules
**As a** user
**I want to** review all extracted and stated rules
**So that** I can validate and adjust before generating my skill

**Acceptance Criteria:**
- [ ] List all rules grouped by component type
- [ ] Show confidence score and source for each rule
- [ ] Allow editing rule values
- [ ] Allow deleting rules
- [ ] Flag baseline conflicts with warnings

**Validation Command:**
```bash
curl -X GET http://localhost:8000/api/sessions/1/rules \
  -H "Authorization: Bearer ${TOKEN}"
# Expect: 200 with array of rules grouped by component
```

---

#### US-4.3: Update Rule
**As a** user reviewing rules
**I want to** modify a specific rule
**So that** I can fine-tune extracted preferences

**Acceptance Criteria:**
- [ ] Update value, severity, or message
- [ ] Keep original confidence if extracted
- [ ] Track that rule was manually modified

**Validation Command:**
```bash
curl -X PATCH http://localhost:8000/api/sessions/1/rules/btn-001 \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"value":12,"message":"Buttons must have 12px border-radius"}'
# Expect: 200 with updated rule
```

---

### Epic 5: Skill Package Generation

#### US-5.1: Generate Skill Package
**As a** user with a completed session
**I want to** generate an Agent Skills package
**So that** I can use it with Claude Code, Cursor, etc.

**Acceptance Criteria:**
- [ ] Generate SKILL.md with human-readable guide
- [ ] Generate rules.json with all programmatic rules
- [ ] Generate component-specific reference files
- [ ] Include baseline.md with WCAG/Nielsen rules
- [ ] Package as downloadable ZIP

**Technical Spec:**
```python
# POST /api/sessions/{session_id}/generate-skill
# Response: { skill_id, download_url, preview: {...} }

# skill_packager.py generates:
# - SKILL.md (templated markdown)
# - references/rules.json (complete rule set)
# - references/buttons.md, inputs.md, cards.md, etc.
# - references/baseline.md
# - scripts/audit.py (placeholder for v1.5)
```

**Validation Command:**
```bash
curl -X POST http://localhost:8000/api/sessions/1/generate-skill \
  -H "Authorization: Bearer ${TOKEN}"
# Expect: 200 with download_url
```

---

#### US-5.2: Download Skill Package
**As a** user
**I want to** download my generated skill as a ZIP file
**So that** I can install it in my development environment

**Acceptance Criteria:**
- [ ] ZIP contains full skill directory structure
- [ ] SKILL.md is properly formatted
- [ ] rules.json is valid JSON
- [ ] Download triggers browser file download

**Validation Command:**
```bash
curl -X GET http://localhost:8000/api/skills/1/download \
  -H "Authorization: Bearer ${TOKEN}" \
  -o skill-package.zip
# Expect: Valid ZIP file
unzip -l skill-package.zip
# Should list: SKILL.md, references/rules.json, references/buttons.md, etc.
```

---

### Epic 6: Frontend UI Components

#### US-6.1: Landing Page
**As a** visitor
**I want to** see what TasteMaker does
**So that** I can decide whether to sign up

**Acceptance Criteria:**
- [ ] Hero section with value proposition
- [ ] How it works section (3-4 steps)
- [ ] CTA buttons: "Get Started" → Register, "Login" → Login
- [ ] Responsive design

---

#### US-6.2: A/B Comparison Component
**As a** user in extraction flow
**I want to** see two options side by side
**So that** I can easily compare and choose

**Acceptance Criteria:**
- [ ] Full-width layout with 50/50 split
- [ ] Each option shows component in context (mock page)
- [ ] Click anywhere on option to select it
- [ ] "No Preference" button at bottom
- [ ] Progress indicator showing phase and count
- [ ] Keyboard shortcuts: 1 for A, 2 for B, 0 for no preference

**Component Structure:**
```tsx
// ComparisonView.tsx
interface ComparisonViewProps {
  comparison: Comparison;
  onChoice: (choice: "a" | "b" | "none") => void;
  progress: { current: number; total: number; phase: string };
}
```

---

#### US-6.3: Mock Context Renderer
**As a** user viewing comparisons
**I want to** see components in realistic page contexts
**So that** I can evaluate them properly

**Acceptance Criteria:**
- [ ] 4 context templates: Landing Hero, Dashboard, Form Wizard, Settings
- [ ] Component variation injected into template
- [ ] Neutral surrounding elements that don't bias choice
- [ ] Scaled appropriately for side-by-side view

**Context Templates:**
```tsx
// contexts/LandingHeroContext.tsx - Shows buttons in hero CTA position
// contexts/DashboardContext.tsx - Shows cards, navigation in dashboard layout
// contexts/FormWizardContext.tsx - Shows inputs, forms in multi-step form
// contexts/SettingsContext.tsx - Shows modals, feedback in settings page
```

---

#### US-6.4: Rule Review Interface
**As a** user reviewing extracted rules
**I want to** see rules in an organized, editable format
**So that** I can validate my preferences before download

**Acceptance Criteria:**
- [ ] Rules grouped by component type (tabs or accordion)
- [ ] Each rule shows: property, value, confidence, source
- [ ] Inline edit capability
- [ ] Delete button with confirmation
- [ ] Baseline conflict warnings highlighted
- [ ] "Add Rule" button for stated preferences

---

#### US-6.5: Component Library Showcase
**As a** user starting an extraction
**I want to** see examples from different component libraries
**So that** my preferences can be extracted across design systems

**Acceptance Criteria:**
- [ ] During extraction, show same component from:
  - shadcn/ui
  - Material UI
  - Tailwind/Radix
- [ ] Variations include library-specific styling
- [ ] User's preferences should generalize across libraries

---

### Epic 7: Baseline Rules System

#### US-7.1: WCAG Baseline Rules
**As a** user generating a skill
**I want** accessibility rules included by default
**So that** my designs meet minimum accessibility standards

**Acceptance Criteria:**
- [ ] Contrast ratio rules (4.5:1 text, 3:1 large text)
- [ ] Touch target size (44x44px minimum)
- [ ] Focus indicator requirements
- [ ] Rules marked with source: "baseline"

**Technical Spec:**
```python
# baseline_rules.py
WCAG_RULES = [
    {
        "id": "wcag-001",
        "property": "contrast_ratio_text",
        "operator": ">=",
        "value": 4.5,
        "severity": "error",
        "message": "Text must have contrast ratio of at least 4.5:1 (WCAG AA)"
    },
    {
        "id": "wcag-002",
        "property": "touch_target_size",
        "operator": ">=",
        "value": 44,
        "severity": "warning",
        "message": "Touch targets should be at least 44x44px (WCAG)"
    },
    # ... more rules
]
```

---

#### US-7.2: Nielsen Heuristic Rules
**As a** user generating a skill
**I want** usability heuristic rules included
**So that** my designs follow established UX principles

**Acceptance Criteria:**
- [ ] Rules for system status visibility
- [ ] Rules for error prevention and recovery
- [ ] Rules for consistency
- [ ] Rules marked with source: "baseline"

---

#### US-7.3: Baseline Conflict Detection
**As a** user whose preferences conflict with baseline
**I want to** be warned about the conflict
**So that** I can make an informed decision

**Acceptance Criteria:**
- [ ] Detect when user rule conflicts with baseline
- [ ] Show warning with explanation
- [ ] Allow user to acknowledge and override
- [ ] Track override in rules.json

---

## Database Schema Summary

```sql
-- Users (similar to my_people pattern)
CREATE TABLE users (
    id VARCHAR PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    first_name VARCHAR,
    last_name VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Extraction Sessions
CREATE TABLE extraction_sessions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    phase VARCHAR DEFAULT 'territory_mapping',
    brand_colors TEXT,
    comparison_count INTEGER DEFAULT 0,
    confidence_score FLOAT DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Comparison Results
CREATE TABLE comparison_results (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES extraction_sessions(id) ON DELETE CASCADE,
    comparison_id INTEGER NOT NULL,
    component_type VARCHAR NOT NULL,
    phase VARCHAR NOT NULL,
    option_a_styles TEXT NOT NULL,
    option_b_styles TEXT NOT NULL,
    choice VARCHAR NOT NULL,
    decision_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Style Rules
CREATE TABLE style_rules (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES extraction_sessions(id) ON DELETE CASCADE,
    rule_id VARCHAR NOT NULL,
    component_type VARCHAR,
    property VARCHAR NOT NULL,
    operator VARCHAR NOT NULL,
    value TEXT NOT NULL,
    severity VARCHAR DEFAULT 'warning',
    confidence FLOAT,
    source VARCHAR NOT NULL,
    message VARCHAR,
    is_modified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Generated Skills
CREATE TABLE generated_skills (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES extraction_sessions(id) ON DELETE CASCADE,
    skill_name VARCHAR NOT NULL,
    file_path VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register | Create new user |
| POST | /api/auth/login | Authenticate user |
| GET | /api/auth/me | Get current user |
| POST | /api/sessions | Create extraction session |
| GET | /api/sessions | List user's sessions |
| GET | /api/sessions/{id} | Get session details |
| DELETE | /api/sessions/{id} | Delete session |
| GET | /api/sessions/{id}/comparison | Get next comparison |
| POST | /api/sessions/{id}/comparison/{cid} | Submit choice |
| GET | /api/sessions/{id}/rules | List session rules |
| POST | /api/sessions/{id}/rules | Add stated rule |
| PATCH | /api/sessions/{id}/rules/{rid} | Update rule |
| DELETE | /api/sessions/{id}/rules/{rid} | Delete rule |
| POST | /api/sessions/{id}/generate-skill | Generate skill package |
| GET | /api/skills/{id}/download | Download skill ZIP |

---

## Validation Test Suite

Ralph should run these tests after each major feature:

```bash
#!/bin/bash
# validation-tests.sh

set -e

BASE_URL="http://localhost:8000"
TOKEN=""

echo "=== TasteMaker Validation Tests ==="

# 1. Health check
echo "1. Health check..."
curl -sf ${BASE_URL}/health | grep -q "ok" && echo "PASS" || echo "FAIL"

# 2. Register user
echo "2. Register user..."
REGISTER_RESP=$(curl -sf -X POST ${BASE_URL}/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@tastemaker.dev","password":"testpass123","first_name":"Test","last_name":"User"}')
TOKEN=$(echo $REGISTER_RESP | jq -r '.access_token')
[ -n "$TOKEN" ] && echo "PASS" || echo "FAIL"

# 3. Login
echo "3. Login..."
LOGIN_RESP=$(curl -sf -X POST ${BASE_URL}/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@tastemaker.dev","password":"testpass123"}')
TOKEN=$(echo $LOGIN_RESP | jq -r '.access_token')
[ -n "$TOKEN" ] && echo "PASS" || echo "FAIL"

# 4. Create session
echo "4. Create session..."
SESSION_RESP=$(curl -sf -X POST ${BASE_URL}/api/sessions \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Profile"}')
SESSION_ID=$(echo $SESSION_RESP | jq -r '.id')
[ -n "$SESSION_ID" ] && echo "PASS" || echo "FAIL"

# 5. Get comparison
echo "5. Get comparison..."
COMP_RESP=$(curl -sf -X GET "${BASE_URL}/api/sessions/${SESSION_ID}/comparison" \
  -H "Authorization: Bearer ${TOKEN}")
COMP_ID=$(echo $COMP_RESP | jq -r '.comparison_id')
[ -n "$COMP_ID" ] && echo "PASS" || echo "FAIL"

# 6. Submit choice
echo "6. Submit choice..."
curl -sf -X POST "${BASE_URL}/api/sessions/${SESSION_ID}/comparison/${COMP_ID}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"choice":"a","decision_time_ms":2000}' && echo "PASS" || echo "FAIL"

# 7. Add stated rule
echo "7. Add stated rule..."
curl -sf -X POST "${BASE_URL}/api/sessions/${SESSION_ID}/rules" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"statement":"never use gradients"}' && echo "PASS" || echo "FAIL"

# 8. Get rules
echo "8. Get rules..."
RULES_RESP=$(curl -sf -X GET "${BASE_URL}/api/sessions/${SESSION_ID}/rules" \
  -H "Authorization: Bearer ${TOKEN}")
[ $(echo $RULES_RESP | jq 'length') -gt 0 ] && echo "PASS" || echo "FAIL"

echo "=== Validation Complete ==="
```

---

## Frontend Development Server

```bash
# Start frontend
cd frontend
npm run dev
# Should be accessible at http://localhost:5173

# Validate frontend running
curl -sf http://localhost:5173 | grep -q "TasteMaker" && echo "Frontend PASS" || echo "Frontend FAIL"
```

---

## Component Libraries to Include

Ralph should install and configure these libraries for the component showcase:

```bash
# shadcn/ui (via CLI)
npx shadcn-ui@latest init
npx shadcn-ui@latest add button input card

# Material UI
npm install @mui/material @emotion/react @emotion/styled

# Radix Primitives
npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu @radix-ui/react-tabs
```

---

## Critical Files Ralph Must Create

1. **Backend:**
   - [ ] `backend/src/main.py` - FastAPI app with CORS, routers
   - [ ] `backend/src/models.py` - All SQLAlchemy models + Pydantic schemas
   - [ ] `backend/src/db_config.py` - Database connection
   - [ ] `backend/src/auth_routes.py` - Registration, login, JWT
   - [ ] `backend/src/session_routes.py` - Session CRUD
   - [ ] `backend/src/comparison_routes.py` - A/B comparison logic
   - [ ] `backend/src/rule_routes.py` - Rule management
   - [ ] `backend/src/skill_routes.py` - Skill generation
   - [ ] `backend/src/variation_service.py` - Generate component variations
   - [ ] `backend/src/pattern_analyzer.py` - Analyze user choices
   - [ ] `backend/src/rule_synthesizer.py` - Extract rules from patterns
   - [ ] `backend/src/skill_packager.py` - Create skill ZIP
   - [ ] `backend/src/baseline_rules.py` - WCAG + Nielsen rules
   - [ ] `backend/requirements.txt`
   - [ ] `backend/alembic.ini`
   - [ ] `backend/migrations/` - Alembic migration files

2. **Frontend:**
   - [ ] `frontend/package.json`
   - [ ] `frontend/vite.config.ts`
   - [ ] `frontend/tailwind.config.js`
   - [ ] `frontend/src/main.tsx`
   - [ ] `frontend/src/App.tsx` - Router setup
   - [ ] `frontend/src/pages/` - All page components
   - [ ] `frontend/src/components/comparison/` - A/B UI
   - [ ] `frontend/src/components/contexts/` - Mock page templates
   - [ ] `frontend/src/contexts/AuthContext.tsx`
   - [ ] `frontend/src/services/api.ts`

3. **Project Root:**
   - [ ] `CLAUDE.md` - Project documentation

---

## Agent Handle Standard (CRITICAL)

**All UI elements MUST include `agent-handle` attributes** following the pattern from the PRD. This allows Ralph to test the app using Puppeteer via the very system being designed.

### Naming Convention
Pattern: `{context}-{component}-{element}-{identifier}`

### Required Agent Handles

**Landing Page:**
```html
<button agent-handle="landing-hero-button-getstarted">Get Started</button>
<button agent-handle="landing-hero-button-login">Login</button>
```

**Auth Pages:**
```html
<!-- Register -->
<input agent-handle="auth-register-input-email" />
<input agent-handle="auth-register-input-password" />
<input agent-handle="auth-register-input-confirmpassword" />
<input agent-handle="auth-register-input-firstname" />
<input agent-handle="auth-register-input-lastname" />
<button agent-handle="auth-register-button-submit">Create Account</button>

<!-- Login -->
<input agent-handle="auth-login-input-email" />
<input agent-handle="auth-login-input-password" />
<button agent-handle="auth-login-button-submit">Sign In</button>
```

**Dashboard:**
```html
<button agent-handle="dashboard-sessions-button-create">New Session</button>
<div agent-handle="dashboard-sessions-card-{sessionId}">...</div>
<button agent-handle="dashboard-sessions-button-continue-{sessionId}">Continue</button>
```

**Extraction Flow:**
```html
<div agent-handle="extraction-comparison-option-a">...</div>
<div agent-handle="extraction-comparison-option-b">...</div>
<button agent-handle="extraction-comparison-button-nopreference">No Preference</button>
<div agent-handle="extraction-progress-indicator">...</div>
```

**Rule Review:**
```html
<div agent-handle="review-rules-section-{componentType}">...</div>
<input agent-handle="review-rules-input-newrule" />
<button agent-handle="review-rules-button-addrule">Add Rule</button>
<button agent-handle="review-rules-button-generate">Generate Skill</button>
```

**Skill Download:**
```html
<button agent-handle="skill-download-button-zip">Download Skill Package</button>
<div agent-handle="skill-preview-content">...</div>
```

### Puppeteer Test Commands for Ralph

Ralph should use these to validate the UI flow:

```bash
# Test registration flow
curl -X POST "http://localhost:3000/api/test/puppeteer" \
  -d '{"action":"click","selector":"[agent-handle=\"landing-hero-button-getstarted\"]"}'

# Fill registration form
curl -X POST "http://localhost:3000/api/test/puppeteer" \
  -d '{"action":"type","selector":"[agent-handle=\"auth-register-input-email\"]","value":"test@example.com"}'

# Submit form
curl -X POST "http://localhost:3000/api/test/puppeteer" \
  -d '{"action":"click","selector":"[agent-handle=\"auth-register-button-submit\"]"}'
```

### MCP Puppeteer Commands

If Puppeteer MCP is available, Ralph can use:

```
mcp__puppeteer__puppeteer_navigate → http://localhost:5173
mcp__puppeteer__puppeteer_click → [agent-handle="auth-login-button-submit"]
mcp__puppeteer__puppeteer_fill → [agent-handle="auth-login-input-email"], test@example.com
mcp__puppeteer__puppeteer_screenshot → name: "after-login"
```

### Validation Script with Agent Handles

```bash
#!/bin/bash
# validate-ui-handles.sh

echo "=== Validating Agent Handles ==="

# Check that key elements exist in the built frontend
FRONTEND_BUILD="frontend/dist"

# Check landing page handles
grep -r "agent-handle=\"landing-hero-button-getstarted\"" frontend/src/ && echo "PASS: Get Started button" || echo "FAIL: Get Started button missing"
grep -r "agent-handle=\"auth-login-button-submit\"" frontend/src/ && echo "PASS: Login button" || echo "FAIL: Login button missing"
grep -r "agent-handle=\"auth-register-button-submit\"" frontend/src/ && echo "PASS: Register button" || echo "FAIL: Register button missing"
grep -r "agent-handle=\"extraction-comparison-option-a\"" frontend/src/ && echo "PASS: Option A" || echo "FAIL: Option A missing"
grep -r "agent-handle=\"extraction-comparison-option-b\"" frontend/src/ && echo "PASS: Option B" || echo "FAIL: Option B missing"
grep -r "agent-handle=\"skill-download-button-zip\"" frontend/src/ && echo "PASS: Download button" || echo "FAIL: Download button missing"

echo "=== Handle Validation Complete ==="
```

---

## Ralph Completion Checklist

Before outputting `TASTEMAKER_V1_COMPLETE`, verify:

- [ ] Backend server starts: `cd backend/src && uvicorn main:app --reload`
- [ ] Frontend dev server starts: `cd frontend && npm run dev`
- [ ] All API validation tests pass: `./validation-tests.sh`
- [ ] All agent-handle attributes present: `./validate-ui-handles.sh`
- [ ] Can complete full extraction flow using Puppeteer:
  1. Navigate to http://localhost:5173
  2. Click `[agent-handle="landing-hero-button-getstarted"]`
  3. Fill registration form via agent-handle selectors
  4. Submit and verify redirect to dashboard
  5. Create new session via `[agent-handle="dashboard-sessions-button-create"]`
  6. Complete 10+ comparisons clicking option-a or option-b
  7. Add stated rule via `[agent-handle="review-rules-button-addrule"]`
  8. Generate skill via `[agent-handle="review-rules-button-generate"]`
  9. Download via `[agent-handle="skill-download-button-zip"]`
- [ ] Downloaded ZIP contains valid SKILL.md and rules.json

---

## Development Notes

1. **Auth:** Simple JWT using python-jose and passlib
2. **Database:** SQLite by default, PostgreSQL for production
3. **Commit frequently:** Every major feature should be a commit
4. **Test as you go:** Run validation tests after each feature
