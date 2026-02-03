"""
TasteMaker API - FastAPI application entry point.

Serves both the API and React frontend in production (Heroku).
"""
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from config import settings
from db_config import engine, Base
from auth_routes import router as auth_router
from session_routes import router as session_router
from comparison_routes import router as comparison_router
from rule_routes import router as rule_router
from skill_routes import router as skill_router
from audit_routes import router as audit_router
from generator_routes import router as generator_router
from mockup_routes import router as mockup_router
from exploration_routes import router as exploration_router
from interactive_audit_routes import router as interactive_audit_router

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="TasteMaker API",
    description="Extract UI/UX taste preferences through A/B comparisons",
    version="2.0.0"
)

# Configure CORS from settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers (must be before static file mount)
app.include_router(auth_router)
app.include_router(session_router)
app.include_router(comparison_router)
app.include_router(rule_router)
app.include_router(skill_router)
app.include_router(audit_router)
app.include_router(generator_router)
app.include_router(mockup_router)
app.include_router(exploration_router)
app.include_router(interactive_audit_router)


# SPA Static Files Handler - serves React build and handles client-side routing
class SPAStaticFiles(StaticFiles):
    """
    Custom StaticFiles handler for Single Page Applications.
    Returns index.html for any path that doesn't match a static file,
    allowing React Router to handle client-side routing.
    """
    async def get_response(self, path: str, scope):
        try:
            return await super().get_response(path, scope)
        except (StarletteHTTPException,) as ex:
            if ex.status_code == 404:
                # Return index.html for client-side routing
                return await super().get_response("index.html", scope)
            raise ex


@app.get("/health")
def health_check():
    """
    Health check endpoint with configuration status.

    Returns information about the current configuration for debugging
    and for frontend single-user mode detection.
    """
    # Determine active AI provider
    ai_provider_status = "not_configured"
    if settings.has_any_ai_provider:
        try:
            from ai_providers import get_default_provider
            provider = get_default_provider()
            ai_provider_status = provider.name
        except Exception:
            ai_provider_status = "error"

    return {
        "status": "ok",
        "config": {
            "single_user_mode": settings.single_user_mode,
            "database_type": "sqlite" if settings.is_sqlite else "postgresql",
            "ai_provider": ai_provider_status,
            "anthropic_api": "configured" if settings.has_anthropic_api_key else "not_configured",
            "openai_api": "configured" if settings.has_openai_api_key else "not_configured",
            "background_jobs": "enabled" if settings.enable_background_jobs else "disabled",
        }
    }


# Mount React build for production (Heroku)
# The frontend/dist folder is created by `npm run build` in heroku-postbuild
FRONTEND_BUILD_DIR = Path(__file__).parent.parent.parent / "frontend" / "dist"

if FRONTEND_BUILD_DIR.exists():
    # Production: Serve React build
    app.mount("/", SPAStaticFiles(directory=str(FRONTEND_BUILD_DIR), html=True), name="spa")
else:
    # Development: Show API info at root
    @app.get("/")
    def root():
        """Root endpoint - API info (development mode)."""
        return {
            "app": "TasteMaker",
            "version": "2.0.0",
            "description": "Extract UI/UX taste preferences through A/B comparisons",
            "mode": "development",
            "note": "In production, the React app is served here"
        }


@app.get("/agent-handles", response_class=PlainTextResponse)
def get_agent_handles():
    """
    Returns the agent-handles documentation in markdown format.
    This endpoint is designed for LLM consumption to understand
    available UI handles for automated testing.
    """
    return AGENT_HANDLES_DOC


AGENT_HANDLES_DOC = """# TasteMaker Agent Handles Documentation

This document describes all available `agent-handle` attributes in the TasteMaker application.
These handles provide stable selectors for automated testing and AI-driven interactions.

## Overview

Agent handles follow the naming convention: `{context}-{component}-{element}-{identifier}`

Use CSS selector `[agent-handle="handle-name"]` to target elements.

---

## Landing Page (`/`)

| Handle | Element Type | Purpose |
|--------|--------------|---------|
| `landing-hero-button-getstarted` | Button | Primary CTA to navigate to registration |
| `landing-hero-button-login` | Button | Secondary CTA to navigate to login |

---

## Authentication Pages

### Login Page (`/login`)

| Handle | Element Type | Purpose |
|--------|--------------|---------|
| `auth-login-input-email` | Input | Email address input field |
| `auth-login-input-password` | Input | Password input field |
| `auth-login-button-submit` | Button | Submit login form |

### Registration Page (`/register`)

| Handle | Element Type | Purpose |
|--------|--------------|---------|
| `auth-register-input-email` | Input | Email address input |
| `auth-register-input-password` | Input | Password input (min 8 chars) |
| `auth-register-input-confirmpassword` | Input | Password confirmation input |
| `auth-register-input-firstname` | Input | User's first name |
| `auth-register-input-lastname` | Input | User's last name |
| `auth-register-button-submit` | Button | Submit registration form |

---

## Dashboard Page (`/dashboard`)

| Handle | Element Type | Purpose |
|--------|--------------|---------|
| `dashboard-sessions-button-create` | Button | Open new session creation form |
| `dashboard-sessions-card-{sessionId}` | Div | Session card container (dynamic ID) |
| `dashboard-sessions-button-continue-{sessionId}` | Button | Continue specific session (dynamic ID) |

---

## Extraction Session Page (`/session/{id}`)

| Handle | Element Type | Purpose |
|--------|--------------|---------|
| `extraction-comparison-option-a` | Div | Left comparison option (clickable) |
| `extraction-comparison-option-b` | Div | Right comparison option (clickable) |
| `extraction-comparison-button-nopreference` | Button | Indicate no preference |
| `extraction-progress-indicator` | Div | Shows current phase and progress |

### Keyboard Shortcuts
- `1` - Select Option A
- `2` - Select Option B
- `0` - No Preference

---

## Rule Review Page (`/session/{id}/review`)

| Handle | Element Type | Purpose |
|--------|--------------|---------|
| `review-rules-input-newrule` | Input | Text input for stated preferences |
| `review-rules-button-addrule` | Button | Submit new stated preference |
| `review-rules-button-generate` | Button | Generate skill package |
| `review-rules-section-{componentType}` | Div | Rules section for component type |

---

## Skill Download Page (`/session/{id}/download`)

| Handle | Element Type | Purpose |
|--------|--------------|---------|
| `skill-download-button-zip` | Button | Download skill package as ZIP |
| `skill-preview-content` | Div | Preview of package contents |

---

## Quick Reference - All Handles

```
landing-hero-button-getstarted
landing-hero-button-login
auth-login-input-email
auth-login-input-password
auth-login-button-submit
auth-register-input-email
auth-register-input-password
auth-register-input-confirmpassword
auth-register-input-firstname
auth-register-input-lastname
auth-register-button-submit
dashboard-sessions-button-create
dashboard-sessions-card-{sessionId}
dashboard-sessions-button-continue-{sessionId}
extraction-comparison-option-a
extraction-comparison-option-b
extraction-comparison-button-nopreference
extraction-progress-indicator
review-rules-input-newrule
review-rules-button-addrule
review-rules-button-generate
review-rules-section-{componentType}
skill-download-button-zip
skill-preview-content
```

## Selector Pattern

```css
[agent-handle="handle-name"]
```

## Example Flow

```javascript
// 1. Navigate to app and register
await click('[agent-handle="landing-hero-button-getstarted"]');
await fill('[agent-handle="auth-register-input-firstname"]', 'Test');
await fill('[agent-handle="auth-register-input-lastname"]', 'User');
await fill('[agent-handle="auth-register-input-email"]', 'test@example.com');
await fill('[agent-handle="auth-register-input-password"]', 'testpass123');
await fill('[agent-handle="auth-register-input-confirmpassword"]', 'testpass123');
await click('[agent-handle="auth-register-button-submit"]');

// 2. Create session from dashboard
await click('[agent-handle="dashboard-sessions-button-create"]');

// 3. Complete comparisons
await click('[agent-handle="extraction-comparison-option-a"]');

// 4. Add rule and generate
await fill('[agent-handle="review-rules-input-newrule"]', 'never use gradients');
await click('[agent-handle="review-rules-button-addrule"]');
await click('[agent-handle="review-rules-button-generate"]');

// 5. Download
await click('[agent-handle="skill-download-button-zip"]');
```
"""
