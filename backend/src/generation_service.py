"""
AI-powered component variation generation using Claude API.

HYBRID APPROACH:
- Territory Mapping phase: Uses Claude API for creative, adaptive exploration
- Dimension Isolation phase: Falls back to deterministic variation_service.py
  for precise single-property testing with established preferences

NOTE: Requires ANTHROPIC_API_KEY to be set. If not configured, the service
will raise an informative error when instantiated.
"""
import anthropic
import json
import time
import os
from typing import Dict, List, Any, Optional

from config import settings

# System prompt for component generation
COMPONENT_GENERATION_SYSTEM_PROMPT = """You are a UI design expert generating component variations for user preference extraction.

CRITICAL RULES:
1. All CSS values must be valid and immediately renderable by React inline styles
2. Colors: hex (#RRGGBB), rgb(r,g,b), or CSS color names
3. Sizes: always include units (px, rem, em, %)
4. Font weights: normal, bold, or numbers (400-800)
5. Border radius: integers with px (0px, 4px, 8px, 12px, 16px, 24px, 9999px for pill)
6. Shadows: CSS box-shadow format or "none"
7. **CRITICAL: Make variations DRAMATICALLY different - users must easily see the difference at a glance**
8. Maintain WCAG AA accessibility (4.5:1 contrast minimum)

**BRAND CONSTRAINT ENFORCEMENT:**
If a COLOR PALETTE is provided, you MUST use ONLY those exact colors:
- Use primary color for main elements (headers, primary buttons)
- Use secondary color for accent sections and secondary elements
- Use accent color for CTAs, highlights, and interactive elements
- Use accentSoft for borders, decorations, and subtle accents
- Use background color for backgrounds
- You may use white (#ffffff) and near-black (#111827) for text contrast
- DO NOT introduce any other colors

If TYPOGRAPHY is provided, you MUST use ONLY those fonts:
- Use heading font for headings, titles, and display text
- Use body font for body text, labels, and descriptions
- DO NOT introduce any other font families

When brand constraints are provided, vary ONLY:
- Shapes: borderRadius, borderWidth, boxShadow
- Spacing: padding, margin, gap
- Typography styling: fontWeight, fontSize, letterSpacing, textTransform
- Layout variations within the color/font constraints

DRAMATIC CONTRAST REQUIREMENTS (apply to NON-CONSTRAINED properties):
- Border radius: Compare extremes (0px sharp vs 16px+ rounded, NOT 4px vs 8px)
- Typography styling: Compare distinct weights (400 vs 700) or sizes (14px vs 18px)
- Spacing: Make padding differences obvious (8px vs 24px, NOT 12px vs 16px)
- Shadows: none vs prominent shadow (0px 8px 24px rgba(0,0,0,0.15))

OUTPUT: Return JSON with two variations and 3-4 questions about their differences.

STYLE CATEGORIES (when varying without brand constraints):
- typography: fontFamily, fontWeight, fontSize, letterSpacing
- color: backgroundColor, color (text), borderColor
- shape: borderRadius, borderWidth, boxShadow
- spacing: padding, margin, gap

QUESTION REQUIREMENTS - CRITICAL:
Questions must be DIRECT PREFERENCE questions about specific CSS properties.
- GOOD: "Which corner style do you prefer?" / "Which spacing do you prefer?" / "Which shadow style do you prefer?"
- BAD: "Which feels more modern?" / "Which is more trustworthy?" / "Which feels more comfortable?"

NEVER use subjective/semantic language like "modern", "trustworthy", "welcoming", "authoritative", "comfortable", "professional", "playful", etc.
Users should judge which option they PREFER, not which matches some abstract quality.
Always phrase as "Which [property] do you prefer?" where property is: corner style, spacing, shadow, font weight, background, border, etc.

IMPORTANT: Both must be usable, polished designs - but VISUALLY DISTINCT so users can immediately tell them apart."""


class ComponentGenerationService:
    """
    AI-powered component variation generation using Claude API.
    Uses Claude Haiku for cost-effective generation (~$0.006/comparison).
    """

    def __init__(self):
        if not settings.has_anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY is not configured. "
                "Please add your API key to .env file. "
                "Get a key at: https://console.anthropic.com/"
            )
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = "claude-haiku-4-5-20251001"  # Cost-optimized Haiku

    def generate_comparison_pair(
        self,
        component_type: str,
        session_id: str,
        phase: str,
        comparison_count: int = 0,
        aesthetic_context: str = "",
        established_preferences: Optional[Dict[str, Any]] = None,
        project_description: Optional[str] = None,
        chosen_colors: Optional[Dict[str, str]] = None,
        chosen_typography: Optional[Dict[str, str]] = None
    ) -> Dict:
        """
        Generate creative A/B comparison with multiple visual differences.
        Returns variations with styles React can render directly.

        Args:
            component_type: button, card, input, typography, etc.
            session_id: User's extraction session ID
            phase: territory_mapping or dimension_isolation
            comparison_count: Number of comparisons completed so far
            aesthetic_context: User's stated aesthetic direction
            established_preferences: Dict of confirmed style preferences
            chosen_colors: User's chosen color palette (primary, secondary, accent, etc.)
            chosen_typography: User's chosen font pairing (heading, body)

        Returns:
            Dict with comparison_id, component_type, option_a, option_b, questions
        """
        # Build context from established preferences and project description
        context = self._build_preference_context(
            aesthetic_context, established_preferences, project_description,
            chosen_colors, chosen_typography
        )

        # Create prompt for this phase
        prompt = self._build_prompt(component_type, phase, context, established_preferences, chosen_colors, chosen_typography)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=COMPONENT_GENERATION_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse the response
            content = response.content[0].text

            # Extract JSON from response (handle markdown code blocks)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            result = json.loads(content)

            return {
                "comparison_id": comparison_count + 1,
                "component_type": component_type,
                "phase": phase,
                "option_a": {
                    "id": result["variation_a"]["id"],
                    "styles": result["variation_a"]["style"]
                },
                "option_b": {
                    "id": result["variation_b"]["id"],
                    "styles": result["variation_b"]["style"]
                },
                "questions": result.get("questions", []),
                "context": result.get("aesthetic_context", ""),
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
                "generation_method": "claude_api"
            }

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse Claude response as JSON: {e}")
        except anthropic.APIError as e:
            raise ValueError(f"Claude API error: {e}")

    def _build_preference_context(
        self,
        aesthetic_context: str,
        established_preferences: Optional[Dict[str, Any]],
        project_description: Optional[str] = None,
        chosen_colors: Optional[Dict[str, str]] = None,
        chosen_typography: Optional[Dict[str, str]] = None
    ) -> str:
        """Build context string from project description, brand choices, and previous preferences."""
        parts = []

        # Project description is the most important context - add first
        if project_description:
            parts.append(f"PROJECT CONTEXT: {project_description}")
            parts.append("Generate variations appropriate for this type of project - consider the target audience, industry, and use case.")

        # CRITICAL: Brand constraints (chosen colors and typography)
        if chosen_colors:
            color_constraint = f"""**REQUIRED COLOR PALETTE - USE THESE EXACT HEX VALUES:**
- Primary: {chosen_colors.get('primary', '#1a365d')} (for headers, primary buttons, main elements)
- Secondary: {chosen_colors.get('secondary', '#115e59')} (for accent sections, secondary elements)
- Accent: {chosen_colors.get('accent', '#d97706')} (for CTAs, highlights, interactive elements)
- Accent Soft: {chosen_colors.get('accentSoft', '#f87171')} (for borders, decorations, subtle accents)
- Background: {chosen_colors.get('background', '#faf5f0')} (for page/card backgrounds)

DO NOT use any other colors except white (#ffffff) and near-black (#111827) for text contrast.
All backgroundColor, color, borderColor values MUST come from this palette."""
            parts.append(color_constraint)

        if chosen_typography:
            font_constraint = f"""**REQUIRED TYPOGRAPHY - USE THESE EXACT FONTS:**
- Heading font: "{chosen_typography.get('heading', 'Inter')}" (for headings, titles, display text)
- Body font: "{chosen_typography.get('body', 'Inter')}" (for body text, labels, descriptions)

All fontFamily values MUST be one of these two fonts. DO NOT introduce other font families."""
            parts.append(font_constraint)

        if aesthetic_context:
            parts.append(f"User's stated aesthetic direction: {aesthetic_context}")

        if established_preferences:
            prefs = []
            for prop, value in established_preferences.items():
                prefs.append(f"- {prop}: {value}")
            if prefs:
                parts.append("Established preferences (incorporate these into both variations):\n" + "\n".join(prefs))

        return "\n\n".join(parts) if parts else "No previous preferences yet."

    def _build_prompt(
        self,
        component_type: str,
        phase: str,
        context: str,
        established_preferences: Optional[Dict[str, Any]],
        chosen_colors: Optional[Dict[str, str]] = None,
        chosen_typography: Optional[Dict[str, str]] = None
    ) -> str:
        """Build the prompt for Claude based on phase and component type."""

        # Component-specific guidance
        component_guidance = {
            "button": "Generate button styles with call-to-action text like 'Get Started' or 'Sign Up'.",
            "card": "Generate card container styles with title and description areas.",
            "input": "Generate text input field styles with label and placeholder.",
            "typography": "Generate heading and body text styles for a content section.",
            "navigation": "Generate navigation menu item styles.",
            "form": "Generate form layout and field grouping styles.",
            "feedback": "Generate notification/alert message styles.",
            "modal": "Generate modal dialog container styles."
        }

        guidance = component_guidance.get(component_type, "Generate professional UI component styles.")

        # Check if we have brand constraints
        has_brand_constraints = chosen_colors is not None or chosen_typography is not None

        if phase == "territory_mapping":
            if has_brand_constraints:
                # CONSTRAINED MODE: Colors and fonts are locked, vary only shape/spacing/shadows
                return f"""Generate 2 **DRAMATICALLY DIFFERENT** {component_type} variations for A/B comparison.

{guidance}

{context}

**BRAND CONSTRAINTS ARE ACTIVE** - You MUST use the required colors and fonts specified above.

Since colors and fonts are constrained, create dramatic differences using ONLY:
- borderRadius: 0px vs 16px or 24px (sharp vs rounded)
- boxShadow: "none" vs "0px 8px 24px rgba(0,0,0,0.15)" (flat vs dimensional)
- padding: "8px 16px" vs "16px 32px" (compact vs spacious)
- fontWeight: 400 vs 700 (light vs bold)
- fontSize: smaller vs larger
- borderWidth: 0px vs 2px (borderless vs bordered)
- textTransform: "none" vs "uppercase"

Variation A: Minimal, flat, sharp corners, compact spacing
Variation B: Dimensional, rounded, generous spacing, bold

CRITICAL: Both variations MUST use the exact same colors from the required palette.
Both variations MUST use only the required font families.

Return valid JSON with this exact structure:
{{
  "variation_a": {{
    "id": "var_a",
    "label": "Short label",
    "style": {{
      "backgroundColor": "#hex from palette",
      "color": "#hex from palette or white/black",
      "borderRadius": "Xpx",
      "padding": "Xpx Xpx",
      "fontSize": "Xpx",
      "fontWeight": "500",
      "fontFamily": "required font, sans-serif",
      "borderWidth": "Xpx",
      "borderColor": "#hex from palette",
      "boxShadow": "none or CSS shadow"
    }}
  }},
  "variation_b": {{
    "id": "var_b",
    "label": "Short label",
    "style": {{ ... same properties, different values for shape/spacing ... }}
  }},
  "questions": [
    {{
      "category": "shape",
      "property": "borderRadius",
      "question_text": "Which corner style do you prefer?",
      "option_a_value": "0px",
      "option_b_value": "16px"
    }},
    {{
      "category": "spacing",
      "property": "padding",
      "question_text": "Which spacing do you prefer?",
      "option_a_value": "8px 16px",
      "option_b_value": "16px 32px"
    }},
    {{
      "category": "shape",
      "property": "boxShadow",
      "question_text": "Which shadow style do you prefer?",
      "option_a_value": "none",
      "option_b_value": "shadow"
    }}
  ],
  "aesthetic_context": "Brief description of the shape/spacing directions explored"
}}"""
            else:
                # UNCONSTRAINED MODE: Full creative exploration
                return f"""Generate 2 **DRAMATICALLY DIFFERENT** {component_type} variations for A/B comparison.

{guidance}

{context}

CRITICAL: Users MUST be able to instantly tell the two options apart at a glance.
Create OBVIOUS, DRAMATIC differences - not subtle variations.

Variation A should explore ONE aesthetic direction (pick one):
- Light, minimal, flat with sharp corners and subtle colors
- Corporate, professional, structured with neutral palette

Variation B should explore the OPPOSITE direction:
- Dark, bold, dimensional with rounded corners and vivid colors
- Playful, modern, expressive with warm/cool accent palette

SPECIFIC CONTRAST EXAMPLES (use these ranges):
- backgroundColor: #ffffff vs #1f2937 (NOT #f5f5f5 vs #eeeeee)
- borderRadius: 0px vs 16px or 24px (NOT 4px vs 8px)
- fontWeight: 400 vs 700 (NOT 500 vs 600)
- padding: "8px 16px" vs "16px 32px" (NOT "12px 16px" vs "14px 18px")
- boxShadow: "none" vs "0px 8px 24px rgba(0,0,0,0.15)"
- color (text): dark on light vs light on dark

Return valid JSON with this exact structure:
{{
  "variation_a": {{
    "id": "var_a",
    "label": "Short label",
    "style": {{
      "backgroundColor": "#hex",
      "color": "#hex",
      "borderRadius": "Xpx",
      "padding": "Xpx Xpx",
      "fontSize": "Xpx",
      "fontWeight": "500",
      "fontFamily": "system-ui, sans-serif",
      "borderWidth": "Xpx",
      "borderColor": "#hex",
      "boxShadow": "none or CSS shadow"
    }}
  }},
  "variation_b": {{
    "id": "var_b",
    "label": "Short label",
    "style": {{ ... same properties ... }}
  }},
  "questions": [
    {{
      "category": "color",
      "property": "backgroundColor",
      "question_text": "Which background color do you prefer?",
      "option_a_value": "#fff",
      "option_b_value": "#1a1a2e"
    }},
    {{
      "category": "typography",
      "property": "fontWeight",
      "question_text": "Which font weight do you prefer?",
      "option_a_value": "400",
      "option_b_value": "700"
    }},
    {{
      "category": "shape",
      "property": "borderRadius",
      "question_text": "Which corner style do you prefer?",
      "option_a_value": "4px",
      "option_b_value": "12px"
    }}
  ],
  "aesthetic_context": "Brief description of the aesthetic directions explored"
}}"""

        else:  # dimension_isolation
            # In dimension isolation, we vary fewer properties but keep established ones
            established_str = ""
            if established_preferences:
                props = [f"{k}: {v}" for k, v in established_preferences.items()]
                established_str = f"\n\nKEEP THESE PROPERTIES CONSISTENT (user already chose these):\n" + "\n".join(props)

            constraint_reminder = ""
            if has_brand_constraints:
                constraint_reminder = "\n\nREMEMBER: Brand constraints are active - use ONLY the required colors and fonts."

            return f"""Generate 2 {component_type} variations that test SPECIFIC style properties.

{guidance}

{context}
{established_str}
{constraint_reminder}

For dimension isolation, make SMALL targeted differences:
- Both variations should feel cohesive with established preferences
- Vary 1-2 uncertain properties to refine user's preferences
- If brand constraints are active, vary only shape/spacing/shadow properties

Return valid JSON with the same structure as territory mapping."""

    def generate_batch_comparisons(
        self,
        session_id: str,
        phase: str,
        batch_size: int = 5,
        start_comparison_count: int = 0,
        established_preferences: Optional[Dict[str, Any]] = None,
        project_description: Optional[str] = None,
        chosen_colors: Optional[Dict[str, str]] = None,
        chosen_typography: Optional[Dict[str, str]] = None,
        recent_choices: Optional[List[Dict]] = None
    ) -> List[Dict]:
        """
        Generate multiple comparisons in a single API call for better UX.

        Args:
            session_id: User's extraction session ID
            phase: territory_mapping or dimension_isolation
            batch_size: Number of comparisons to generate (default 5)
            start_comparison_count: Starting comparison number
            established_preferences: Dict of confirmed style preferences
            project_description: User's project description
            chosen_colors: User's chosen color palette
            chosen_typography: User's chosen font pairing
            recent_choices: List of recent user choices for context

        Returns:
            List of comparison dicts
        """
        # Build context from established preferences and project description
        context = self._build_preference_context(
            "", established_preferences, project_description,
            chosen_colors, chosen_typography
        )

        # Add recent choices context if available
        choices_context = ""
        if recent_choices:
            choices_summary = []
            for choice in recent_choices[-3:]:  # Last 3 choices
                component = choice.get("component_type", "component")
                selection = choice.get("choice", "")
                choices_summary.append(f"- {component}: chose option {selection}")
            if choices_summary:
                choices_context = f"\n\nUser's recent choices (incorporate these preferences):\n" + "\n".join(choices_summary)

        # Define component types to cycle through
        component_types = ["button", "card", "input", "typography", "navigation", "form", "feedback", "modal"]

        # Build batch generation prompt
        prompt = self._build_batch_prompt(
            batch_size,
            start_comparison_count,
            phase,
            context + choices_context,
            component_types,
            chosen_colors,
            chosen_typography
        )

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=6000,  # More tokens for batch generation
                system=COMPONENT_GENERATION_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse the response
            content = response.content[0].text

            # Extract JSON from response (handle markdown code blocks)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            result = json.loads(content)
            comparisons = result.get("comparisons", [])

            # Format each comparison
            formatted = []
            for i, comp in enumerate(comparisons):
                formatted.append({
                    "comparison_id": start_comparison_count + i + 1,
                    "component_type": comp.get("component_type", component_types[i % len(component_types)]),
                    "phase": phase,
                    "option_a": {
                        "id": comp["variation_a"]["id"],
                        "styles": comp["variation_a"]["style"]
                    },
                    "option_b": {
                        "id": comp["variation_b"]["id"],
                        "styles": comp["variation_b"]["style"]
                    },
                    "questions": comp.get("questions", []),
                    "context": comp.get("aesthetic_context", ""),
                    "generation_method": "claude_api_batch"
                })

            return formatted

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse Claude batch response as JSON: {e}")
        except anthropic.APIError as e:
            raise ValueError(f"Claude API error during batch generation: {e}")

    def _build_batch_prompt(
        self,
        batch_size: int,
        start_count: int,
        phase: str,
        context: str,
        component_types: List[str],
        chosen_colors: Optional[Dict[str, str]] = None,
        chosen_typography: Optional[Dict[str, str]] = None
    ) -> str:
        """Build prompt for batch comparison generation."""

        # Select component types for this batch
        selected_components = []
        for i in range(batch_size):
            selected_components.append(component_types[(start_count + i) % len(component_types)])

        components_list = ", ".join(selected_components)

        has_brand_constraints = chosen_colors is not None or chosen_typography is not None

        if has_brand_constraints:
            variation_guidance = """Since colors and fonts are constrained, create dramatic differences using ONLY:
- borderRadius: 0px vs 16px or 24px (sharp vs rounded)
- boxShadow: "none" vs "0px 8px 24px rgba(0,0,0,0.15)" (flat vs dimensional)
- padding: "8px 16px" vs "16px 32px" (compact vs spacious)
- fontWeight: 400 vs 700 (light vs bold)
- fontSize: smaller vs larger
- borderWidth: 0px vs 2px (borderless vs bordered)
- textTransform: "none" vs "uppercase"

CRITICAL: ALL variations MUST use the exact same colors from the required palette.
ALL variations MUST use only the required font families."""
        else:
            variation_guidance = """Create OBVIOUS, DRAMATIC differences between variations:
- backgroundColor: light vs dark (e.g., #ffffff vs #1f2937)
- borderRadius: sharp vs rounded (0px vs 16px+)
- fontWeight: light vs bold (400 vs 700)
- boxShadow: flat vs dimensional"""

        return f"""Generate {batch_size} A/B comparison pairs for these component types: {components_list}

{context}

{variation_guidance}

For EACH component, generate dramatically different A and B variations.
Each comparison should test different style aspects.

QUESTION FORMAT REQUIREMENT:
All question_text values MUST be direct preference questions using the format "Which [property] do you prefer?"
Examples: "Which corner style do you prefer?", "Which spacing do you prefer?", "Which shadow do you prefer?"
NEVER use semantic language like "feels more modern", "is more trustworthy", "feels comfortable", etc.

Return valid JSON with this exact structure:
{{
  "comparisons": [
    {{
      "component_type": "button",
      "variation_a": {{
        "id": "var_a_1",
        "label": "Short label",
        "style": {{
          "backgroundColor": "#hex",
          "color": "#hex",
          "borderRadius": "Xpx",
          "padding": "Xpx Xpx",
          "fontSize": "Xpx",
          "fontWeight": "500",
          "fontFamily": "font, sans-serif",
          "borderWidth": "Xpx",
          "borderColor": "#hex",
          "boxShadow": "none or CSS shadow"
        }}
      }},
      "variation_b": {{
        "id": "var_b_1",
        "label": "Short label",
        "style": {{ ... different values ... }}
      }},
      "questions": [
        {{
          "category": "shape",
          "property": "borderRadius",
          "question_text": "Which corner style do you prefer?",
          "option_a_value": "value from A",
          "option_b_value": "value from B"
        }}
      ],
      "aesthetic_context": "Brief description"
    }},
    ... {batch_size - 1} more comparisons for other component types ...
  ]
}}

Generate exactly {batch_size} comparisons. Each must have unique variation IDs.
Make each comparison test different aesthetic aspects (shape, spacing, typography styling, etc.)."""

    def test_api_connection(self) -> Dict:
        """Test that the Claude API connection works."""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=100,
                messages=[{"role": "user", "content": "Say 'API connection successful' and nothing else."}]
            )
            return {
                "success": True,
                "message": response.content[0].text,
                "model": self.model,
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Singleton instance
_generation_service: Optional[ComponentGenerationService] = None


def get_generation_service() -> ComponentGenerationService:
    """Get or create the generation service singleton."""
    global _generation_service
    if _generation_service is None:
        _generation_service = ComponentGenerationService()
    return _generation_service
