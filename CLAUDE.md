# CLAUDE.md - TasteMaker

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

**TasteMaker** is a web application that extracts UI/UX taste preferences from users through A/B comparisons and generates machine-readable style profiles (Agent Skills) that AI coding tools can use to make consistent design decisions.

**Core Problem:** AI agents cannot make taste judgments about UI/UX. TasteMaker solves this by capturing human preferences as structured rulesets.

## Architecture

```
tastemaker/
├── backend/           # FastAPI REST API server
│   └── src/           # Source code (run uvicorn from HERE)
├── frontend/          # React + Vite + TypeScript + Tailwind
└── SPEC.md            # Full technical specification
```

### Backend (FastAPI)
- **Location**: `backend/src/`
- **Framework**: FastAPI with SQLAlchemy ORM
- **Database**: SQLite (default) or PostgreSQL (see `.env.example`)
- **Migrations**: Alembic
- **Auth**: JWT (python-jose + passlib), or single-user mode for local use

### Frontend (React)
- **Location**: `frontend/`
- **Framework**: React 18 + TypeScript + Vite
- **Styling**: Tailwind CSS
- **Component Libraries**: shadcn/ui, Material UI, Radix primitives
- **Router**: React Router v6

## Quick Start Commands

### Configure Environment
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Start Backend
```bash
cd backend
source venv/bin/activate  # Create with: python -m venv venv
pip install -r requirements.txt
cd src
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Endpoints:**
- Root: http://localhost:8000/
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### Start Frontend
```bash
cd frontend
npm install
npm run dev
```

**Web Interface:** http://localhost:5173

### Run Migrations
```bash
cd backend
alembic upgrade head                          # Apply migrations
alembic revision --autogenerate -m "desc"     # Create migration
```

## Key Files

### Backend (`backend/src/`)
| File | Purpose |
|------|---------|
| `main.py` | FastAPI app entry point |
| `config.py` | Centralized settings from environment |
| `models.py` | SQLAlchemy models + Pydantic schemas |
| `auth_routes.py` | Registration, login, JWT |
| `single_user.py` | Single-user mode support |
| `session_routes.py` | Extraction session CRUD |
| `comparison_routes.py` | A/B comparison flow |
| `rule_routes.py` | Style rule management |
| `skill_routes.py` | Skill package generation |
| `generation_service.py` | AI component variation generator |
| `exploration_service.py` | Color/typography exploration |
| `variation_service.py` | Deterministic variation generator |
| `pattern_analyzer.py` | User choice analysis |
| `rule_synthesizer.py` | Pattern to rule conversion |
| `skill_packager.py` | Agent Skills ZIP creator |
| `baseline_rules.py` | WCAG + Nielsen baseline |
| `db_config.py` | Database configuration |

### Frontend (`frontend/src/`)
| Directory | Purpose |
|-----------|---------|
| `pages/` | Route page components |
| `components/comparison/` | A/B comparison UI |
| `components/contexts/` | Mock page templates |
| `components/ui/` | Multi-library component variants |
| `contexts/` | React contexts (Auth, Session) |
| `services/` | API client |

## Database

- **Default**: SQLite (`sqlite:///./tastemaker.db`)
- **Production**: PostgreSQL (configure via `DATABASE_URL` in `.env`)
- **Tables**: users, extraction_sessions, comparison_results, style_rules, generated_skills

## Validation Tests

Run the validation script to test all functionality:
```bash
chmod +x validation-tests.sh
./validation-tests.sh
```

## Common Issues

### Backend won't start
1. **CRITICAL**: Run from `backend/src/` directory, not `backend/`
2. Verify venv is activated
3. If using PostgreSQL: ensure it's running (`pg_isready -h localhost`) and database exists

### Import errors
The backend must be run from inside `backend/src/`:
```bash
# CORRECT
cd backend/src && uvicorn main:app --reload

# WRONG - will fail with import errors
cd backend && python -m src.main
```

## Core Concepts

### Extraction Phases
1. **Territory Mapping** (10-15 comparisons): Broad aesthetic direction
2. **Dimension Isolation** (20-30 comparisons): Single-variable refinement
3. **Stated Preferences**: User adds explicit rules
4. **Generation**: Output Agent Skills package

### Component Types
8 components for v1: Button, Input, Card, Typography, Navigation, Form, Feedback, Modal

### Rule Sources
- `extracted`: Derived from A/B choices
- `stated`: User explicitly added
- `baseline`: WCAG/Nielsen defaults

### Agent Skills Output
```
tastemaker-{username}/
├── SKILL.md              # Human-readable guide
├── references/
│   ├── rules.json        # Programmatic rules
│   ├── baseline.md       # Accessibility baseline
│   ├── buttons.md        # Component-specific docs
│   └── ...
└── scripts/
    └── audit.py          # (placeholder for v1.5)
```

## Development Notes

- **Claude API**: Requires ANTHROPIC_API_KEY for color/typography exploration and component generation
- **Multiple component libraries**: Show shadcn, MUI, Radix variants
- **Single-user mode**: Default for local development (no login required)
- **SQLite default**: Simple local database, PostgreSQL optional

## Specification

See `SPEC.md` for complete user stories, acceptance criteria, and technical specs.
