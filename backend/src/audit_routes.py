"""
Audit routes for screenshot-based style analysis.
Uses Claude Vision API to EXTRACT values, then programmatically applies TML rules.

IMPORTANT: Audits are DETERMINISTIC rule application, not LLM opinions.
Claude Vision extracts colors/values from images, rules are checked programmatically.
"""
import base64
import json
import os
import re
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel

from db_config import get_db
from models import UserModel, ExtractionSessionModel, StyleRuleModel
from auth_routes import get_current_user
from baseline_rules import get_baseline_rules
from interactive_baseline_rules import (
    INTERACTIVE_BASELINE_RULES,
    get_rules_by_category,
    get_temporal_rules,
    get_spatial_rules,
    get_pattern_rules,
)

router = APIRouter(tags=["audit"])


class Violation(BaseModel):
    rule_id: str
    severity: str
    property: str
    expected: str
    found: str
    message: str
    suggestion: str


class AuditResult(BaseModel):
    violations: List[Violation]
    summary: str
    score: int


def parse_color(color_str: str) -> Optional[tuple]:
    """Parse a color string to RGB tuple."""
    if not color_str:
        return None
    # Handle hex colors
    if color_str.startswith('#'):
        hex_color = color_str.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        if len(hex_color) == 6:
            # Validate hex characters
            try:
                return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            except ValueError:
                return None
    # Handle rgb() format
    match = re.match(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', color_str)
    if match:
        return tuple(int(x) for x in match.groups())
    return None


def colors_match(expected: str, found: str, tolerance: int = 20) -> bool:
    """Check if two colors match within tolerance."""
    exp_rgb = parse_color(expected)
    found_rgb = parse_color(found)
    if not exp_rgb or not found_rgb:
        return expected.lower() == found.lower()
    return all(abs(e - f) <= tolerance for e, f in zip(exp_rgb, found_rgb))


def calculate_relative_luminance(rgb: tuple) -> float:
    """
    Calculate relative luminance per WCAG 2.1.
    https://www.w3.org/WAI/GL/wiki/Relative_luminance
    """
    def channel_luminance(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = rgb
    return 0.2126 * channel_luminance(r) + 0.7152 * channel_luminance(g) + 0.0722 * channel_luminance(b)


def calculate_contrast_ratio(color1: str, color2: str) -> Optional[float]:
    """
    Calculate WCAG contrast ratio between two colors.
    Returns ratio like 4.5 or 21.0
    WCAG AA requires 4.5:1 for normal text, 3:1 for large text
    WCAG AAA requires 7:1 for normal text, 4.5:1 for large text
    """
    rgb1 = parse_color(color1)
    rgb2 = parse_color(color2)

    if not rgb1 or not rgb2:
        return None

    l1 = calculate_relative_luminance(rgb1)
    l2 = calculate_relative_luminance(rgb2)

    lighter = max(l1, l2)
    darker = min(l1, l2)

    return (lighter + 0.05) / (darker + 0.05)


def parse_size(size_str: str) -> Optional[float]:
    """Parse a size string to number (px assumed)."""
    if not size_str:
        return None
    # Strip whitespace before matching
    cleaned = str(size_str).strip()
    match = re.match(r'(\d+(?:\.\d+)?)', cleaned)
    if match:
        return float(match.group(1))
    return None


def check_rule(rule_operator: str, expected: str, found: str, property_name: str) -> bool:
    """Programmatically check if a value satisfies a rule."""
    # Color comparison
    if 'color' in property_name.lower():
        if rule_operator == '=':
            return colors_match(expected, found)
        return colors_match(expected, found)

    # Size comparison
    expected_num = parse_size(expected)
    found_num = parse_size(found)

    if expected_num is not None and found_num is not None:
        if rule_operator == '>=':
            return found_num >= expected_num
        elif rule_operator == '<=':
            return found_num <= expected_num
        elif rule_operator == '>':
            return found_num > expected_num
        elif rule_operator == '<':
            return found_num < expected_num
        elif rule_operator == '=':
            return abs(found_num - expected_num) < 1

    # String comparison
    if rule_operator == '=':
        return expected.lower() == found.lower()
    elif rule_operator == 'contains':
        return expected.lower() in found.lower()
    elif rule_operator == 'one_of':
        options = [o.strip().lower() for o in expected.split(',')]
        return found.lower() in options

    return True  # Default pass for unsupported operators


def apply_rules_to_extracted_values(
    extracted_values: dict,
    rules: list,
    chosen_colors: Optional[dict],
    chosen_typography: Optional[dict]
) -> List[Violation]:
    """Apply TML rules to extracted values - DETERMINISTIC, no LLM opinion."""
    violations = []

    # Check color rules from chosen palette
    if chosen_colors and 'colors' in extracted_values:
        found_colors = extracted_values.get('colors', [])
        expected_palette = [
            chosen_colors.get('primary'),
            chosen_colors.get('secondary'),
            chosen_colors.get('accent'),
            chosen_colors.get('accentSoft'),
            chosen_colors.get('background')
        ]
        expected_palette = [c for c in expected_palette if c]

        for color_info in found_colors:
            found_color = color_info.get('color', '')
            element = color_info.get('element', 'unknown')

            # Check if found color is in palette (with tolerance)
            in_palette = any(colors_match(exp, found_color) for exp in expected_palette)

            if not in_palette and found_color:
                violations.append(Violation(
                    rule_id="color-palette",
                    severity="warning",
                    property=f"{element} color",
                    expected=f"One of: {', '.join(expected_palette)}",
                    found=found_color,
                    message=f"Color not in defined palette",
                    suggestion=f"Use one of your defined palette colors instead of {found_color}"
                ))

    # Check typography rules
    if chosen_typography and 'fonts' in extracted_values:
        found_fonts = extracted_values.get('fonts', [])
        expected_heading = chosen_typography.get('heading', '')
        expected_body = chosen_typography.get('body', '')

        for font_info in found_fonts:
            found_font = font_info.get('font', '').split(',')[0].strip()
            element_type = font_info.get('element', '')

            is_heading = 'heading' in element_type.lower() or element_type in ['h1', 'h2', 'h3', 'h4']
            expected = expected_heading if is_heading else expected_body

            if expected and expected.lower() not in found_font.lower():
                violations.append(Violation(
                    rule_id="typography-font",
                    severity="warning",
                    property=f"{element_type} font",
                    expected=expected,
                    found=found_font,
                    message=f"Font doesn't match typography profile",
                    suggestion=f"Use '{expected}' for {element_type}"
                ))

    # Check WCAG contrast ratios
    if 'contrast_pairs' in extracted_values:
        for pair in extracted_values.get('contrast_pairs', []):
            fg = pair.get('foreground', '')
            bg = pair.get('background', '')
            element = pair.get('element', 'unknown')
            is_large = pair.get('is_large_text', False)

            ratio = calculate_contrast_ratio(fg, bg)
            if ratio:
                # WCAG AA requirements
                min_ratio = 3.0 if is_large else 4.5

                if ratio < min_ratio:
                    violations.append(Violation(
                        rule_id="wcag-contrast",
                        severity="error",
                        property=f"{element} contrast",
                        expected=f">= {min_ratio}:1 (WCAG AA)",
                        found=f"{ratio:.2f}:1",
                        message=f"Contrast ratio too low for {'large ' if is_large else ''}text",
                        suggestion=f"Increase contrast between {fg} and {bg} to at least {min_ratio}:1"
                    ))

    # Apply explicit TML rules
    for rule in rules:
        rule_id = rule.rule_id
        prop = rule.property
        operator = rule.operator
        expected_value = rule.value
        severity = rule.severity or 'warning'

        # Find matching extracted values
        found_values = extracted_values.get('measurements', {})

        # Check if we have a measurement for this property
        # Normalize hyphens/underscores for matching
        prop_normalized = prop.lower().replace('-', '_').replace(' ', '_')
        for key, found_value in found_values.items():
            key_normalized = key.lower().replace('-', '_').replace(' ', '_')
            if prop_normalized in key_normalized:
                if not check_rule(operator, expected_value, str(found_value), prop):
                    violations.append(Violation(
                        rule_id=rule_id,
                        severity=severity,
                        property=prop,
                        expected=f"{operator} {expected_value}",
                        found=str(found_value),
                        message=rule.message or f"{prop} violates rule",
                        suggestion=f"Adjust {prop} to be {operator} {expected_value}"
                    ))

    return violations


@router.post("/api/audit/screenshot", response_model=AuditResult)
async def audit_screenshot(
    file: UploadFile = File(...),
    session_id: str = Form(...),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Audit a screenshot against TML rules.

    Process:
    1. Claude Vision EXTRACTS colors, fonts, and measurements from the image
    2. TML rules are applied PROGRAMMATICALLY to the extracted values
    3. Violations are reported based on deterministic rule checking

    This is NOT LLM opinion - it's programmatic rule application.
    """
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

    # Get rules for this session
    rules = (
        db.query(StyleRuleModel)
        .filter(StyleRuleModel.session_id == session_id)
        .all()
    )

    # Parse style choices
    chosen_colors = None
    chosen_typography = None

    if session.chosen_colors:
        chosen_colors = json.loads(session.chosen_colors) if isinstance(session.chosen_colors, str) else session.chosen_colors
    if session.chosen_typography:
        chosen_typography = json.loads(session.chosen_typography) if isinstance(session.chosen_typography, str) else session.chosen_typography

    # Read and encode the image
    contents = await file.read()
    base64_image = base64.b64encode(contents).decode('utf-8')
    media_type = file.content_type or 'image/png'

    # Step 1: Use AI Vision to EXTRACT values (not judge them)
    try:
        from ai_providers import get_default_provider, ImageContent, ModelTier, has_any_provider

        if not has_any_provider():
            return AuditResult(
                violations=[
                    Violation(
                        rule_id="demo-001",
                        severity="warning",
                        property="color",
                        expected=str(chosen_colors) if chosen_colors else "defined palette",
                        found="unknown",
                        message="No AI provider configured",
                        suggestion="Set ANTHROPIC_API_KEY or OPENAI_API_KEY in .env"
                    )
                ],
                summary="Demo mode - No AI provider configured for value extraction",
                score=75
            )

        extraction_prompt = """Analyze this UI screenshot and EXTRACT the following values.
DO NOT judge whether they are good or bad - just extract the raw values.

Extract:
1. colors - List of colors found with their elements
2. fonts - List of fonts found with their usage
3. measurements - Object with approximate measurements
4. contrast_pairs - Text/background color pairs for WCAG contrast checking

Respond with ONLY valid JSON in this exact format:
{
  "colors": [
    {"element": "primary button background", "color": "#hex"},
    {"element": "text", "color": "#hex"}
  ],
  "fonts": [
    {"element": "heading", "font": "FontName"},
    {"element": "body text", "font": "FontName"}
  ],
  "measurements": {
    "button_border_radius": "Npx",
    "spacing": "Npx"
  },
  "contrast_pairs": [
    {"element": "button text", "foreground": "#ffffff", "background": "#1a365d", "is_large_text": false},
    {"element": "heading", "foreground": "#1a365d", "background": "#ffffff", "is_large_text": true}
  ]
}

Be specific about hex colors. For contrast_pairs, include text/background pairs you can identify.
Large text is 18px+ regular or 14px+ bold. Return ONLY the JSON, no explanation."""

        provider = get_default_provider()
        image = ImageContent.from_base64(base64_image, media_type)

        response = provider.complete_with_vision(
            text_prompt=extraction_prompt,
            images=[image],
            model_tier=ModelTier.CAPABLE,
            max_tokens=1500
        )

        # Parse extracted values
        response_text = response.content

        # Clean up potential markdown
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        extracted_values = json.loads(response_text.strip())

        # Step 2: Apply rules PROGRAMMATICALLY
        violations = apply_rules_to_extracted_values(
            extracted_values,
            rules,
            chosen_colors,
            chosen_typography
        )

        # Calculate score based on violations
        error_count = sum(1 for v in violations if v.severity == 'error')
        warning_count = sum(1 for v in violations if v.severity == 'warning')
        score = max(0, 100 - (error_count * 15) - (warning_count * 5))

        # Generate summary
        if not violations:
            summary = "All extracted values match your TML style rules."
        else:
            summary = f"Found {len(violations)} rule violation(s): {error_count} error(s), {warning_count} warning(s)."

        return AuditResult(
            violations=violations,
            summary=summary,
            score=score
        )

    except json.JSONDecodeError:
        return AuditResult(
            violations=[],
            summary="Could not extract values from screenshot. Try a clearer image.",
            score=50
        )
    except ValueError as e:
        # No AI provider configured
        return AuditResult(
            violations=[
                Violation(
                    rule_id="demo-001",
                    severity="warning",
                    property="color",
                    expected=str(chosen_colors) if chosen_colors else "defined palette",
                    found="unknown",
                    message="No AI provider configured",
                    suggestion="Set ANTHROPIC_API_KEY or OPENAI_API_KEY in .env"
                )
            ],
            summary="Demo mode - No AI provider configured for value extraction",
            score=75
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audit failed: {str(e)}"
        )


class UrlAuditRequest(BaseModel):
    url: str
    session_id: str


@router.post("/api/audit/url", response_model=AuditResult)
async def audit_url(
    request: UrlAuditRequest,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Audit a live URL against TML rules.

    Process:
    1. Playwright captures a screenshot of the URL
    2. Claude Vision EXTRACTS colors, fonts, and measurements from the image
    3. TML rules are applied PROGRAMMATICALLY to the extracted values
    4. Violations are reported based on deterministic rule checking
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

    # Parse style choices
    chosen_colors = None
    chosen_typography = None

    if session.chosen_colors:
        chosen_colors = json.loads(session.chosen_colors) if isinstance(session.chosen_colors, str) else session.chosen_colors
    if session.chosen_typography:
        chosen_typography = json.loads(session.chosen_typography) if isinstance(session.chosen_typography, str) else session.chosen_typography

    # Capture screenshot with Playwright
    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={'width': 1366, 'height': 768})

            try:
                await page.goto(request.url, timeout=30000, wait_until='networkidle')
            except Exception as nav_error:
                await browser.close()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to load URL: {str(nav_error)}"
                )

            screenshot_bytes = await page.screenshot(full_page=False)
            await browser.close()

    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Playwright not installed. Run: pip install playwright && playwright install chromium"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Screenshot capture failed: {str(e)}"
        )

    # Encode screenshot for Claude Vision
    base64_image = base64.b64encode(screenshot_bytes).decode('utf-8')

    # Run through the same audit pipeline as screenshot audit
    try:
        from ai_providers import get_default_provider, ImageContent, ModelTier, has_any_provider

        if not has_any_provider():
            return AuditResult(
                violations=[
                    Violation(
                        rule_id="demo-001",
                        severity="warning",
                        property="url-audit",
                        expected=str(chosen_colors) if chosen_colors else "defined palette",
                        found="unknown",
                        message="No AI provider configured",
                        suggestion="Set ANTHROPIC_API_KEY or OPENAI_API_KEY in .env"
                    )
                ],
                summary="Demo mode - No AI provider configured for URL audit",
                score=75
            )

        extraction_prompt = """Analyze this UI screenshot and EXTRACT the following values.
DO NOT judge whether they are good or bad - just extract the raw values.

Extract:
1. colors - List of colors found with their elements
2. fonts - List of fonts found with their usage
3. measurements - Object with approximate measurements
4. contrast_pairs - Text/background color pairs for WCAG contrast checking

Respond with ONLY valid JSON in this exact format:
{
  "colors": [
    {"element": "primary button background", "color": "#hex"},
    {"element": "text", "color": "#hex"}
  ],
  "fonts": [
    {"element": "heading", "font": "FontName"},
    {"element": "body text", "font": "FontName"}
  ],
  "measurements": {
    "button_border_radius": "Npx",
    "spacing": "Npx"
  },
  "contrast_pairs": [
    {"element": "button text", "foreground": "#ffffff", "background": "#1a365d", "is_large_text": false},
    {"element": "heading", "foreground": "#1a365d", "background": "#ffffff", "is_large_text": true}
  ]
}

Be specific about hex colors. For contrast_pairs, include text/background pairs you can identify.
Large text is 18px+ regular or 14px+ bold. Return ONLY the JSON, no explanation."""

        provider = get_default_provider()
        image = ImageContent.from_base64(base64_image, "image/png")

        response = provider.complete_with_vision(
            text_prompt=extraction_prompt,
            images=[image],
            model_tier=ModelTier.CAPABLE,
            max_tokens=1500
        )

        # Parse extracted values
        response_text = response.content

        # Clean up potential markdown
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        extracted_values = json.loads(response_text.strip())

        # Apply rules PROGRAMMATICALLY
        violations = apply_rules_to_extracted_values(
            extracted_values,
            rules,
            chosen_colors,
            chosen_typography
        )

        # Calculate score based on violations
        error_count = sum(1 for v in violations if v.severity == 'error')
        warning_count = sum(1 for v in violations if v.severity == 'warning')
        score = max(0, 100 - (error_count * 15) - (warning_count * 5))

        # Generate summary
        if not violations:
            summary = f"All extracted values from {request.url} match your TML style rules."
        else:
            summary = f"Found {len(violations)} rule violation(s) on {request.url}: {error_count} error(s), {warning_count} warning(s)."

        return AuditResult(
            violations=violations,
            summary=summary,
            score=score
        )

    except json.JSONDecodeError:
        return AuditResult(
            violations=[],
            summary="Could not extract values from URL screenshot. Try a different URL.",
            score=50
        )
    except ValueError as e:
        # No AI provider configured
        return AuditResult(
            violations=[
                Violation(
                    rule_id="demo-001",
                    severity="warning",
                    property="url-audit",
                    expected=str(chosen_colors) if chosen_colors else "defined palette",
                    found="unknown",
                    message="No AI provider configured",
                    suggestion="Set ANTHROPIC_API_KEY or OPENAI_API_KEY in .env"
                )
            ],
            summary="Demo mode - No AI provider configured for URL audit",
            score=75
        )
    except Exception as e:
        # Handle API errors gracefully
        error_str = str(e).lower()
        if "not_found" in error_str or "model" in error_str or "404" in error_str:
            return AuditResult(
                violations=[],
                summary=f"URL captured successfully. AI API model not available for extraction.",
                score=60
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"URL audit failed: {str(e)}"
        )


@router.get("/api/audit/rules/available")
async def get_available_audit_rules():
    """
    Get all available audit rules including static and interactive.

    Returns rules grouped by category (STATIC, TEMPORAL, BEHAVIORAL, SPATIAL, PATTERN).
    """
    # Get static baseline rules (WCAG + Nielsen)
    static_rules = get_baseline_rules()

    # Get interactive rules by category
    temporal_rules = get_temporal_rules()
    spatial_rules = get_spatial_rules()
    pattern_rules = get_pattern_rules()
    behavioral_rules = get_rules_by_category("BEHAVIORAL")

    return {
        "summary": {
            "total_rules": len(static_rules) + len(INTERACTIVE_BASELINE_RULES),
            "static_rules": len(static_rules),
            "interactive_rules": len(INTERACTIVE_BASELINE_RULES),
            "by_category": {
                "STATIC": len(static_rules),
                "TEMPORAL": len(temporal_rules),
                "BEHAVIORAL": len(behavioral_rules),
                "SPATIAL": len(spatial_rules),
                "PATTERN": len(pattern_rules),
            }
        },
        "static": static_rules,
        "interactive": {
            "temporal": temporal_rules,
            "behavioral": behavioral_rules,
            "spatial": spatial_rules,
            "pattern": pattern_rules,
        }
    }


@router.get("/api/audit/rules/{category}")
async def get_rules_by_category_endpoint(category: str):
    """
    Get audit rules for a specific category.

    Categories: static, temporal, behavioral, spatial, pattern
    """
    category_upper = category.upper()

    if category_upper == "STATIC":
        return {
            "category": "STATIC",
            "description": "Visual rules that can be checked from a single screenshot (WCAG, Nielsen)",
            "rules": get_baseline_rules()
        }
    elif category_upper == "TEMPORAL":
        return {
            "category": "TEMPORAL",
            "description": "Time-based rules requiring interaction measurement (Doherty Threshold)",
            "rules": get_temporal_rules()
        }
    elif category_upper == "BEHAVIORAL":
        return {
            "category": "BEHAVIORAL",
            "description": "Interaction pattern rules (form validation, loading states)",
            "rules": get_rules_by_category("BEHAVIORAL")
        }
    elif category_upper == "SPATIAL":
        return {
            "category": "SPATIAL",
            "description": "Position and size rules (Fitts's Law, thumb zones)",
            "rules": get_spatial_rules()
        }
    elif category_upper == "PATTERN":
        return {
            "category": "PATTERN",
            "description": "Dark pattern detection rules",
            "rules": get_pattern_rules()
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown category: {category}. Valid: static, temporal, behavioral, spatial, pattern"
        )
