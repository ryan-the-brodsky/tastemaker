"""
Component generator routes.
Uses Claude API to generate styled components based on user's rules.
"""
import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel

from db_config import get_db
from models import UserModel, ExtractionSessionModel, StyleRuleModel
from auth_routes import get_current_user

router = APIRouter(tags=["generator"])


class GenerateRequest(BaseModel):
    session_id: int
    component_type: str
    variant: str
    output_format: str  # 'react', 'html', 'vue'
    custom_prompt: Optional[str] = None


class GenerateResponse(BaseModel):
    code: str


@router.post("/api/generate/component", response_model=GenerateResponse)
async def generate_component(
    request: GenerateRequest,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a styled component using Claude API.
    """
    # Verify session ownership
    session = (
        db.query(ExtractionSessionModel)
        .filter(
            ExtractionSessionModel.id == request.session_id,
            ExtractionSessionModel.user_id == current_user.id
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Get rules for this session
    rules = (
        db.query(StyleRuleModel)
        .filter(StyleRuleModel.session_id == request.session_id)
        .all()
    )

    # Build style context
    style_context = ""
    if session.chosen_colors:
        colors = json.loads(session.chosen_colors) if isinstance(session.chosen_colors, str) else session.chosen_colors
        style_context += f"\nColor palette:\n"
        style_context += f"- Primary: {colors.get('primary', '#1a365d')}\n"
        style_context += f"- Secondary: {colors.get('secondary', '#115e59')}\n"
        style_context += f"- Accent: {colors.get('accent', '#d97706')}\n"
        style_context += f"- Accent Soft: {colors.get('accentSoft', '#f87171')}\n"
        style_context += f"- Background: {colors.get('background', '#faf5f0')}\n"

    if session.chosen_typography:
        typography = json.loads(session.chosen_typography) if isinstance(session.chosen_typography, str) else session.chosen_typography
        style_context += f"\nTypography:\n"
        style_context += f"- Heading font: {typography.get('heading', 'Inter')}\n"
        style_context += f"- Body font: {typography.get('body', 'Inter')}\n"

    # Build rules context
    rules_text = ""
    component_rules = [r for r in rules if r.component_type == request.component_type or r.component_type is None]
    if component_rules:
        rules_text = "\nStyle rules to follow:\n"
        for r in component_rules:
            rules_text += f"- {r.property} {r.operator} {r.value}: {r.message or ''}\n"

    # Format-specific instructions
    format_instructions = {
        'react': "Generate a React functional component using TypeScript and Tailwind CSS classes.",
        'html': "Generate plain HTML with inline CSS styles or a <style> block.",
        'vue': "Generate a Vue 3 Single File Component (SFC) with <script setup> and Tailwind CSS."
    }

    format_instruction = format_instructions.get(request.output_format, format_instructions['react'])

    # Build the prompt
    prompt = f"""Generate a {request.variant} {request.component_type} component.

{format_instruction}

{style_context}
{rules_text}

{f'Additional requirements: {request.custom_prompt}' if request.custom_prompt else ''}

Requirements:
1. Use the exact colors from the color palette
2. Apply the typography settings
3. Follow all style rules
4. Include hover and focus states where appropriate
5. Make it accessible (proper ARIA attributes, keyboard navigation)
6. Add an agent-handle attribute for testing

Return ONLY the code, no explanations or markdown formatting."""

    try:
        import anthropic
        client = anthropic.Anthropic()

        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        code = message.content[0].text

        # Clean up code if it's wrapped in markdown
        if code.startswith("```"):
            lines = code.split("\n")
            # Remove first and last lines if they're markdown delimiters
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            code = "\n".join(lines)

        return GenerateResponse(code=code)

    except ImportError:
        # Anthropic not installed - return template code
        return GenerateResponse(code=_get_template_code(
            request.component_type,
            request.variant,
            request.output_format,
            session.chosen_colors,
            session.chosen_typography
        ))
    except Exception as e:
        # API error (model not available, etc.) - fall back to template
        error_str = str(e).lower()
        if "not_found" in error_str or "model" in error_str or "404" in error_str:
            return GenerateResponse(code=_get_template_code(
                request.component_type,
                request.variant,
                request.output_format,
                session.chosen_colors,
                session.chosen_typography
            ))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generation failed: {str(e)}"
        )


def _get_template_code(
    component_type: str,
    variant: str,
    output_format: str,
    colors_json: str | None,
    typography_json: str | None
) -> str:
    """Generate template code when Claude API is not available."""
    colors = json.loads(colors_json) if colors_json else {
        'primary': '#1a365d',
        'secondary': '#115e59',
        'accent': '#d97706',
        'background': '#faf5f0'
    }
    typography = json.loads(typography_json) if typography_json else {
        'heading': 'Inter',
        'body': 'Inter'
    }

    primary = colors.get('primary', '#1a365d')
    bg = colors.get('background', '#faf5f0')
    font = typography.get('body', 'Inter')

    if component_type == 'button' and output_format == 'react':
        return f'''import React from 'react';

interface ButtonProps {{
  children: React.ReactNode;
  onClick?: () => void;
  variant?: '{variant}';
  disabled?: boolean;
}}

export function Button({{ children, onClick, variant = '{variant}', disabled }}: ButtonProps) {{
  return (
    <button
      onClick={{onClick}}
      disabled={{disabled}}
      agent-handle="generated-button-{variant}"
      className="px-6 py-3 rounded-lg font-semibold transition-all focus:outline-none focus:ring-2 focus:ring-offset-2"
      style={{{{
        backgroundColor: '{primary}',
        color: '{bg}',
        fontFamily: '{font}, sans-serif',
      }}}}
    >
      {{children}}
    </button>
  );
}}'''

    elif component_type == 'card' and output_format == 'react':
        return f'''import React from 'react';

interface CardProps {{
  title: string;
  children: React.ReactNode;
}}

export function Card({{ title, children }}: CardProps) {{
  return (
    <div
      agent-handle="generated-card-{variant}"
      className="rounded-xl shadow-md overflow-hidden"
      style={{{{
        backgroundColor: '{bg}',
        fontFamily: '{font}, sans-serif',
      }}}}
    >
      <div className="p-6">
        <h3
          className="text-xl font-semibold mb-4"
          style={{{{ color: '{primary}' }}}}
        >
          {{title}}
        </h3>
        <div style={{{{ color: '{primary}88' }}}}>
          {{children}}
        </div>
      </div>
    </div>
  );
}}'''

    else:
        # Generic template
        return f'''// Generated {component_type} component ({variant})
// Style profile colors: {json.dumps(colors)}
// Typography: {json.dumps(typography)}

// Install anthropic package and set ANTHROPIC_API_KEY
// for AI-generated components tailored to your style.

export function Generated{component_type.title()}() {{
  return (
    <div agent-handle="generated-{component_type}-{variant}">
      {component_type.title()} Component - {variant} variant
    </div>
  );
}}'''


# Component types for library export
COMPONENT_TYPES = ['button', 'input', 'card', 'modal', 'navigation', 'form', 'feedback']
VARIANTS = {
    'button': ['primary', 'secondary', 'destructive', 'ghost', 'outline'],
    'input': ['default', 'search', 'textarea'],
    'card': ['default', 'elevated', 'outlined'],
    'modal': ['default', 'alert', 'form'],
    'navigation': ['horizontal', 'vertical', 'sidebar'],
    'form': ['login', 'signup', 'contact'],
    'feedback': ['success', 'error', 'warning', 'info']
}


@router.post("/api/generate/library")
async def export_component_library(
    session_id: int = Form(...),
    output_format: str = Form(default="react"),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export a complete component library based on the session's TML rules.
    Returns a ZIP file with all component files.
    """
    from fastapi.responses import Response
    import zipfile
    import io

    # Verify session ownership
    session = (
        db.query(ExtractionSessionModel)
        .filter(
            ExtractionSessionModel.id == session_id,
            ExtractionSessionModel.user_id == current_user.id
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Parse colors and typography
    colors = json.loads(session.chosen_colors) if session.chosen_colors else {
        'primary': '#1a365d',
        'secondary': '#115e59',
        'accent': '#d97706',
        'background': '#faf5f0'
    }
    typography = json.loads(session.chosen_typography) if session.chosen_typography else {
        'heading': 'Inter',
        'body': 'Inter'
    }

    # Create ZIP in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Generate each component type with its primary variant
        for comp_type in COMPONENT_TYPES:
            variant = VARIANTS.get(comp_type, ['default'])[0]
            code = _get_template_code(
                comp_type,
                variant,
                output_format,
                session.chosen_colors,
                session.chosen_typography
            )
            filename = f"components/{comp_type.title()}.tsx"
            zip_file.writestr(filename, code)

        # Create theme.ts
        theme_content = f'''/**
 * Theme configuration generated by TasteMaker
 * Based on session: {session.name}
 */

export const colors = {{
  primary: '{colors.get("primary", "#1a365d")}',
  secondary: '{colors.get("secondary", "#115e59")}',
  accent: '{colors.get("accent", "#d97706")}',
  accentSoft: '{colors.get("accentSoft", "#fbbf24")}',
  background: '{colors.get("background", "#faf5f0")}',
}} as const;

export const typography = {{
  heading: '{typography.get("heading", "Inter")}',
  body: '{typography.get("body", "Inter")}',
}} as const;

export const theme = {{
  colors,
  typography,
  spacing: {{
    xs: '4px',
    sm: '8px',
    md: '16px',
    lg: '24px',
    xl: '32px',
  }},
  borderRadius: {{
    sm: '4px',
    md: '8px',
    lg: '12px',
    full: '9999px',
  }},
}};

export type Theme = typeof theme;
export default theme;
'''
        zip_file.writestr("theme.ts", theme_content)

        # Create index.ts
        index_content = '''// Component Library Index
// Generated by TasteMaker

export { Button } from './components/Button';
export { Card } from './components/Card';
export { Input } from './components/Input';
export { Modal } from './components/Modal';
export { Navigation } from './components/Navigation';
export { Form } from './components/Form';
export { Feedback } from './components/Feedback';

export { theme, colors, typography } from './theme';
export type { Theme } from './theme';
'''
        zip_file.writestr("index.ts", index_content)

        # Create README.md
        readme_content = f'''# TasteMaker Component Library

Generated from session: **{session.name}**

## Installation

Copy the `components/` folder and `theme.ts` into your project.

## Usage

```tsx
import {{ Button, Card, theme }} from './components';

function App() {{
  return (
    <div style={{{{ fontFamily: theme.typography.body }}}}>
      <Button>Click me</Button>
      <Card title="Hello">Content here</Card>
    </div>
  );
}}
```

## Theme

Your selected color palette:
- Primary: `{colors.get("primary", "#1a365d")}`
- Secondary: `{colors.get("secondary", "#115e59")}`
- Accent: `{colors.get("accent", "#d97706")}`
- Background: `{colors.get("background", "#faf5f0")}`

Typography:
- Headings: {typography.get("heading", "Inter")}
- Body: {typography.get("body", "Inter")}

## Components Included

- Button (primary, secondary, destructive, ghost, outline)
- Input (default, search, textarea)
- Card (default, elevated, outlined)
- Modal (default, alert, form)
- Navigation (horizontal, vertical, sidebar)
- Form (login, signup, contact)
- Feedback (success, error, warning, info)

---

Generated by [TasteMaker](https://tastemaker.io)
'''
        zip_file.writestr("README.md", readme_content)

    # Return ZIP file
    zip_buffer.seek(0)
    return Response(
        content=zip_buffer.getvalue(),
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=tastemaker-components-{session.id}.zip"
        }
    )
