"""
Exploration service for trie-style color and typography discovery.

Uses AI API to generate contextual options based on:
- Project description
- Previous selections (gradient descent toward preferred styles)
- Current exploration depth

Instead of binary A/B comparisons, shows 5 options that progressively
narrow down as users make selections.

NOTE: Requires an AI provider (ANTHROPIC_API_KEY or OPENAI_API_KEY).
Falls back to static options if no provider is available.
"""
import json
import os
from typing import List, Dict, Optional, Any

from config import settings
from ai_providers import get_default_provider, AIMessage, ModelTier, has_any_provider


class ExplorationService:
    """AI-powered exploration for colors and typography."""

    def __init__(self):
        self._provider = None
        self._api_available = settings.has_any_ai_provider

    @property
    def provider(self):
        """Lazy initialization of AI provider."""
        if self._provider is None:
            if not self._api_available:
                raise ValueError(
                    "No AI provider configured. "
                    "Please add ANTHROPIC_API_KEY or OPENAI_API_KEY to .env file."
                )
            self._provider = get_default_provider()
        return self._provider

    def generate_color_options(
        self,
        project_description: Optional[str],
        color_role: str,  # "primary", "secondary", "accent", "accentSoft", "background"
        previous_selection: Optional[str] = None,  # e.g., "#5b21b6" or "purple"
        exploration_depth: int = 0,
        exploration_history: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate 5 color options for a specific role.

        Args:
            project_description: User's project context
            color_role: Which color we're selecting (primary, secondary, etc.)
            previous_selection: The color/family they chose in the last round
            exploration_depth: How many refinement rounds we've done (0=initial, 1=first refinement, etc.)
            exploration_history: List of previous selections for context

        Returns:
            Dict with 5 color options, each with hex, name, and description
        """
        history_context = ""
        if exploration_history:
            history_context = f"\n\nExploration path so far: {' → '.join(exploration_history)}"

        depth_instruction = self._get_depth_instruction(exploration_depth, previous_selection, "color")

        role_descriptions = {
            "primary": "headers, navigation, key UI elements - should be distinctive and brand-defining",
            "secondary": "accents, containers, supporting elements - should complement the primary",
            "accent": "CTAs, highlights, important actions - should stand out and draw attention",
            "accentSoft": "borders, decorations, subtle highlights - should be gentle and supportive",
            "background": "page backgrounds, content areas - should provide comfortable contrast"
        }

        prompt = f"""Generate exactly 5 color options for the "{color_role}" color role.

PROJECT CONTEXT:
{project_description or "General web application"}

COLOR ROLE: {color_role}
Purpose: {role_descriptions.get(color_role, "UI element coloring")}
{depth_instruction}
{history_context}

Return a JSON object with this exact structure:
{{
    "options": [
        {{
            "hex": "#XXXXXX",
            "name": "Color Name",
            "family": "color family (e.g., 'blue', 'warm red', 'forest green')",
            "description": "Brief explanation of why this fits the project"
        }},
        // ... 4 more options
    ],
    "context": "Brief explanation of the overall direction for these options"
}}

REQUIREMENTS:
1. Return exactly 5 options
2. All hex codes must be valid 6-character hex colors
3. Options should be distinctly different from each other
4. Consider the project context and target audience
5. For refinement rounds, stay within the selected family but offer meaningful variations
6. ONLY return valid JSON, no other text"""

        try:
            response = self.provider.complete(
                messages=[AIMessage(role="user", content=prompt)],
                model_tier=ModelTier.COST_EFFECTIVE,
                max_tokens=1500
            )

            response_text = response.content

            # Parse JSON from response
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]

            result = json.loads(response_text.strip())
            result["color_role"] = color_role
            result["exploration_depth"] = exploration_depth
            return result

        except Exception as e:
            # Fallback to static options if AI fails
            return self._get_fallback_color_options(color_role, exploration_depth)

    def generate_typography_options(
        self,
        project_description: Optional[str],
        font_role: str,  # "heading" or "body"
        previous_selection: Optional[str] = None,  # e.g., "Inter" or "sans-serif"
        exploration_depth: int = 0,
        exploration_history: Optional[List[str]] = None,
        paired_with: Optional[str] = None  # If selecting body, what heading was chosen
    ) -> Dict[str, Any]:
        """
        Generate 5 typography options for headings or body text.

        Args:
            project_description: User's project context
            font_role: "heading" or "body"
            previous_selection: The font/family they chose in the last round
            exploration_depth: How many refinement rounds we've done
            exploration_history: List of previous selections for context
            paired_with: If selecting body font, what heading font was chosen

        Returns:
            Dict with 5 font options, each with font name, category, and description
        """
        history_context = ""
        if exploration_history:
            history_context = f"\n\nExploration path so far: {' → '.join(exploration_history)}"

        pairing_context = ""
        if paired_with:
            pairing_context = f"\n\nMust pair well with: {paired_with} (heading font)"

        depth_instruction = self._get_depth_instruction(exploration_depth, previous_selection, "typography")

        role_descriptions = {
            "heading": "titles, headers, prominent text - should be distinctive and impactful",
            "body": "paragraphs, descriptions, readable content - should be highly legible"
        }

        prompt = f"""Generate exactly 5 Google Fonts options for the "{font_role}" font role.

PROJECT CONTEXT:
{project_description or "General web application"}

FONT ROLE: {font_role}
Purpose: {role_descriptions.get(font_role, "text display")}
{depth_instruction}
{pairing_context}
{history_context}

Return a JSON object with this exact structure:
{{
    "options": [
        {{
            "fontName": "Font Name",
            "category": "sans-serif|serif|display|handwriting|monospace",
            "style": "style description (e.g., 'geometric modern', 'humanist classic')",
            "description": "Brief explanation of why this fits the project",
            "googleFontsUrl": "https://fonts.google.com/specimen/FontName"
        }},
        // ... 4 more options
    ],
    "context": "Brief explanation of the overall direction for these options"
}}

REQUIREMENTS:
1. Return exactly 5 options
2. All fonts must be available on Google Fonts
3. Options should represent different style directions
4. Consider the project context, target audience, and readability needs
5. For refinement rounds, stay within the selected style but offer meaningful variations
6. ONLY return valid JSON, no other text"""

        try:
            response = self.provider.complete(
                messages=[AIMessage(role="user", content=prompt)],
                model_tier=ModelTier.COST_EFFECTIVE,
                max_tokens=1500
            )

            response_text = response.content

            # Parse JSON from response
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]

            result = json.loads(response_text.strip())
            result["font_role"] = font_role
            result["exploration_depth"] = exploration_depth
            return result

        except Exception as e:
            # Fallback to static options if AI fails
            return self._get_fallback_typography_options(font_role, exploration_depth)

    def generate_full_palette_options(
        self,
        project_description: Optional[str],
        exploration_depth: int = 0,
        previous_selection: Optional[Dict] = None  # Previous palette choice
    ) -> Dict[str, Any]:
        """
        Generate 5 complete color palettes for initial exploration.

        Instead of choosing colors one-by-one, shows complete palettes
        that can then be refined.
        """
        refinement_context = ""
        num_options = 5  # Default for initial exploration
        if previous_selection and exploration_depth > 0:
            num_options = 4  # Only 4 new options since we'll include the original
            refinement_context = f"""
REFINEMENT DIRECTION:
User previously selected a palette with these characteristics:
- Primary: {previous_selection.get('primary', 'unknown')}
- Style: {previous_selection.get('category', 'unknown')}

Generate 4 variations that stay within this color family but offer meaningful differences:
- Lighter/darker variations
- More/less saturated versions
- Subtle hue shifts (e.g., if they chose blue, try blue-green or blue-purple)
- Different accent color pairings

NOTE: Generate exactly 4 options (not 5) - the user's original selection will be shown alongside these.
"""
        else:
            refinement_context = """
INITIAL EXPLORATION:
Generate 5 distinctly different palettes spanning different color families and moods:
- Professional/corporate options
- Creative/playful options
- Warm/inviting options
- Cool/modern options
- Natural/organic options
"""

        prompt = f"""Generate exactly {num_options} complete color palettes for a web application.

PROJECT CONTEXT:
{project_description or "General web application"}

{refinement_context}

Return a JSON object with this exact structure:
{{
    "options": [
        {{
            "id": "palette-name",
            "name": "Descriptive Name",
            "category": "professional|creative|warm|cool|natural|playful|elegant|bold",
            "primary": "#XXXXXX",
            "secondary": "#XXXXXX",
            "accent": "#XXXXXX",
            "accentSoft": "#XXXXXX",
            "background": "#XXXXXX",
            "description": "Brief explanation of the palette's mood and fit"
        }},
        // ... {num_options - 1} more palettes
    ],
    "context": "Brief explanation of the exploration direction"
}}

REQUIREMENTS:
1. Return exactly {num_options} complete palettes
2. All hex codes must be valid 6-character hex colors
3. Each palette should feel cohesive and usable
4. Consider contrast and accessibility
5. Match palettes to the project's target audience and purpose
6. ONLY return valid JSON, no other text"""

        try:
            response = self.provider.complete(
                messages=[AIMessage(role="user", content=prompt)],
                model_tier=ModelTier.COST_EFFECTIVE,
                max_tokens=2000
            )

            response_text = response.content

            # Parse JSON from response
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]

            result = json.loads(response_text.strip())
            result["exploration_depth"] = exploration_depth
            return result

        except Exception as e:
            print(f"AI API error: {e}")
            return self._get_fallback_palette_options(exploration_depth)

    def generate_full_typography_options(
        self,
        project_description: Optional[str],
        exploration_depth: int = 0,
        previous_selection: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate 5 complete typography pairings (heading + body).
        When refining, generates 4 new options (original will be included separately).
        """
        refinement_context = ""
        num_options = 5  # Default for initial exploration
        if previous_selection and exploration_depth > 0:
            num_options = 4  # Only 4 new options since we'll include the original
            refinement_context = f"""
REFINEMENT DIRECTION:
User previously selected typography with these characteristics:
- Heading: {previous_selection.get('heading', 'unknown')}
- Body: {previous_selection.get('body', 'unknown')}
- Style: {previous_selection.get('category', 'unknown')}

Generate 4 variations that stay within this style family but offer meaningful differences:
- Different weights/widths
- Similar geometric vs humanist feel
- Fonts from the same design era or movement
- Complementary alternatives that maintain the vibe

NOTE: Generate exactly 4 options (not 5) - the user's original selection will be shown alongside these.
"""
        else:
            refinement_context = """
INITIAL EXPLORATION:
Generate 5 distinctly different typography pairings spanning different styles:
- Modern/tech (geometric sans-serif)
- Classic/editorial (serif combinations)
- Friendly/approachable (rounded, casual)
- Bold/impactful (display fonts)
- Clean/minimal (neutral, highly readable)
"""

        prompt = f"""Generate exactly {num_options} typography pairings (heading + body fonts) for a web application.

PROJECT CONTEXT:
{project_description or "General web application"}

{refinement_context}

Return a JSON object with this exact structure:
{{
    "options": [
        {{
            "id": "style-name",
            "name": "Descriptive Name",
            "category": "modern|classic|friendly|bold|minimal|playful|elegant|tech",
            "heading": "Heading Font Name",
            "body": "Body Font Name",
            "headingCategory": "sans-serif|serif|display",
            "bodyCategory": "sans-serif|serif",
            "description": "Brief explanation of the pairing's character and fit"
        }},
        // ... {num_options - 1} more pairings
    ],
    "context": "Brief explanation of the exploration direction"
}}

REQUIREMENTS:
1. Return exactly {num_options} complete pairings
2. All fonts must be available on Google Fonts
3. Heading and body fonts should work well together
4. Consider readability for body text
5. Match typography to the project's tone and audience
6. ONLY return valid JSON, no other text"""

        try:
            response = self.provider.complete(
                messages=[AIMessage(role="user", content=prompt)],
                model_tier=ModelTier.COST_EFFECTIVE,
                max_tokens=2000
            )

            response_text = response.content

            # Parse JSON from response
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]

            result = json.loads(response_text.strip())
            result["exploration_depth"] = exploration_depth
            return result

        except Exception as e:
            print(f"AI API error: {e}")
            return self._get_fallback_typography_pairing_options(exploration_depth)

    def _get_depth_instruction(
        self,
        depth: int,
        previous_selection: Optional[str],
        exploration_type: str
    ) -> str:
        """Get appropriate instruction based on exploration depth."""
        if depth == 0:
            return f"""
INITIAL EXPLORATION (Depth 0):
Generate 5 distinctly different options spanning the full range of possibilities.
Show diverse choices to help the user discover their preferences."""

        elif depth == 1:
            return f"""
FIRST REFINEMENT (Depth 1):
User selected: {previous_selection}
Generate 5 options within this family/direction, but with meaningful variations.
Think of it as showing different "shades" or "flavors" within the chosen direction."""

        elif depth == 2:
            return f"""
SECOND REFINEMENT (Depth 2):
User is narrowing down within: {previous_selection}
Generate 5 very specific variations - subtle differences that matter for fine-tuning.
These should be close to each other but still distinguishable."""

        else:
            return f"""
DEEP REFINEMENT (Depth {depth}):
User has been refining: {previous_selection}
Generate 5 micro-variations for final selection.
Very subtle differences for precise preference capture."""

    def _get_fallback_color_options(self, color_role: str, depth: int) -> Dict:
        """Fallback static colors if Claude API fails."""
        fallback_options = {
            "primary": [
                {"hex": "#1e3a8a", "name": "Deep Blue", "family": "blue", "description": "Professional and trustworthy"},
                {"hex": "#059669", "name": "Emerald", "family": "green", "description": "Natural and growth-oriented"},
                {"hex": "#7c3aed", "name": "Violet", "family": "purple", "description": "Creative and innovative"},
                {"hex": "#dc2626", "name": "Red", "family": "red", "description": "Bold and energetic"},
                {"hex": "#ca8a04", "name": "Amber", "family": "yellow", "description": "Warm and optimistic"},
            ],
            "secondary": [
                {"hex": "#0891b2", "name": "Cyan", "family": "cyan", "description": "Fresh and modern"},
                {"hex": "#4f46e5", "name": "Indigo", "family": "indigo", "description": "Deep and sophisticated"},
                {"hex": "#16a34a", "name": "Green", "family": "green", "description": "Balanced and natural"},
                {"hex": "#9333ea", "name": "Purple", "family": "purple", "description": "Creative accent"},
                {"hex": "#0284c7", "name": "Sky Blue", "family": "blue", "description": "Light and approachable"},
            ],
        }

        options = fallback_options.get(color_role, fallback_options["primary"])
        return {
            "options": options,
            "context": "Fallback options (Claude API unavailable)",
            "color_role": color_role,
            "exploration_depth": depth
        }

    def _get_fallback_typography_options(self, font_role: str, depth: int) -> Dict:
        """Fallback static typography if Claude API fails."""
        fallback_options = {
            "heading": [
                {"fontName": "Inter", "category": "sans-serif", "style": "modern clean", "description": "Clean and versatile"},
                {"fontName": "Playfair Display", "category": "serif", "style": "elegant editorial", "description": "Classic elegance"},
                {"fontName": "Poppins", "category": "sans-serif", "style": "geometric friendly", "description": "Friendly and modern"},
                {"fontName": "Oswald", "category": "sans-serif", "style": "condensed bold", "description": "Strong impact"},
                {"fontName": "Merriweather", "category": "serif", "style": "traditional readable", "description": "Warm and readable"},
            ],
            "body": [
                {"fontName": "Inter", "category": "sans-serif", "style": "modern clean", "description": "Highly readable"},
                {"fontName": "Open Sans", "category": "sans-serif", "style": "neutral friendly", "description": "Versatile and clear"},
                {"fontName": "Lora", "category": "serif", "style": "elegant readable", "description": "Classic readability"},
                {"fontName": "Roboto", "category": "sans-serif", "style": "mechanical modern", "description": "Tech-forward"},
                {"fontName": "Source Sans Pro", "category": "sans-serif", "style": "professional clean", "description": "Professional clarity"},
            ],
        }

        options = fallback_options.get(font_role, fallback_options["heading"])
        return {
            "options": options,
            "context": "Fallback options (Claude API unavailable)",
            "font_role": font_role,
            "exploration_depth": depth
        }

    def _get_fallback_palette_options(self, depth: int) -> Dict:
        """Fallback complete palettes if Claude API fails."""
        return {
            "options": [
                {
                    "id": "professional-blue",
                    "name": "Professional Blue",
                    "category": "professional",
                    "primary": "#1e3a8a",
                    "secondary": "#0891b2",
                    "accent": "#f59e0b",
                    "accentSoft": "#fbbf24",
                    "background": "#f8fafc",
                    "description": "Clean and trustworthy for business applications"
                },
                {
                    "id": "creative-purple",
                    "name": "Creative Purple",
                    "category": "creative",
                    "primary": "#7c3aed",
                    "secondary": "#a855f7",
                    "accent": "#f97316",
                    "accentSoft": "#fb923c",
                    "background": "#faf5ff",
                    "description": "Vibrant and innovative for creative projects"
                },
                {
                    "id": "natural-green",
                    "name": "Natural Green",
                    "category": "natural",
                    "primary": "#059669",
                    "secondary": "#10b981",
                    "accent": "#f59e0b",
                    "accentSoft": "#fcd34d",
                    "background": "#f0fdf4",
                    "description": "Organic and growth-oriented"
                },
                {
                    "id": "warm-coral",
                    "name": "Warm Coral",
                    "category": "warm",
                    "primary": "#dc2626",
                    "secondary": "#f97316",
                    "accent": "#0891b2",
                    "accentSoft": "#22d3ee",
                    "background": "#fef2f2",
                    "description": "Energetic and welcoming"
                },
                {
                    "id": "playful-teal",
                    "name": "Playful Teal",
                    "category": "playful",
                    "primary": "#0d9488",
                    "secondary": "#14b8a6",
                    "accent": "#f97316",
                    "accentSoft": "#fb923c",
                    "background": "#f0fdfa",
                    "description": "Fun and approachable"
                },
            ],
            "context": "Fallback palettes (Claude API unavailable)",
            "exploration_depth": depth
        }

    def _get_fallback_typography_pairing_options(self, depth: int) -> Dict:
        """Fallback typography pairings if Claude API fails."""
        return {
            "options": [
                {
                    "id": "modern-clean",
                    "name": "Modern Clean",
                    "category": "modern",
                    "heading": "Inter",
                    "body": "Inter",
                    "headingCategory": "sans-serif",
                    "bodyCategory": "sans-serif",
                    "description": "Clean and versatile for tech products"
                },
                {
                    "id": "elegant-editorial",
                    "name": "Elegant Editorial",
                    "category": "elegant",
                    "heading": "Playfair Display",
                    "body": "Lora",
                    "headingCategory": "serif",
                    "bodyCategory": "serif",
                    "description": "Classic elegance for editorial content"
                },
                {
                    "id": "friendly-rounded",
                    "name": "Friendly Rounded",
                    "category": "friendly",
                    "heading": "Nunito",
                    "body": "Nunito",
                    "headingCategory": "sans-serif",
                    "bodyCategory": "sans-serif",
                    "description": "Approachable and warm for consumer apps"
                },
                {
                    "id": "bold-statement",
                    "name": "Bold Statement",
                    "category": "bold",
                    "heading": "Oswald",
                    "body": "Open Sans",
                    "headingCategory": "sans-serif",
                    "bodyCategory": "sans-serif",
                    "description": "Strong impact for marketing sites"
                },
                {
                    "id": "minimal-swiss",
                    "name": "Minimal Swiss",
                    "category": "minimal",
                    "heading": "Montserrat",
                    "body": "Roboto",
                    "headingCategory": "sans-serif",
                    "bodyCategory": "sans-serif",
                    "description": "Swiss-inspired minimal design"
                },
            ],
            "context": "Fallback typography (Claude API unavailable)",
            "exploration_depth": depth
        }


# Singleton instance
_exploration_service = None

def get_exploration_service() -> ExplorationService:
    """Get or create the exploration service singleton."""
    global _exploration_service
    if _exploration_service is None:
        _exploration_service = ExplorationService()
    return _exploration_service
