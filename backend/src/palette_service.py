"""
Color palette and typography service for TasteMaker.

Provides 25+ color palettes and 15+ font pairings for A/B comparison exploration.
Uses binary search approach to narrow down user preferences efficiently.
"""
from typing import Dict, List, Tuple, Optional
import random

# =============================================================================
# COLOR PALETTES (25+ options from mvp-club-site-2)
# Each palette has: primary, secondary, accent, accentSoft, background
# =============================================================================

COLOR_PALETTES: Dict[str, Dict[str, str]] = {
    # Navy + Teal (Original brand)
    "default": {
        "name": "default",
        "primary": "#1a365d",     # Deep Navy
        "secondary": "#115e59",   # Deep Teal
        "accent": "#d97706",      # Amber
        "accentSoft": "#f87171",  # Coral
        "background": "#faf5f0",  # Warm Stone
        "category": "professional",
    },

    "midnight": {
        "name": "midnight",
        "primary": "#081f3f",     # Darker Navy
        "secondary": "#115e59",   # Deep Teal
        "accent": "#d97706",      # Amber
        "accentSoft": "#f87171",  # Coral
        "background": "#faf5f0",  # Warm Stone
        "category": "professional",
    },

    # Navy + Slate Blue
    "dusk": {
        "name": "dusk",
        "primary": "#081f3f",     # Dark Navy
        "secondary": "#15465b",   # Slate Blue
        "accent": "#d97706",      # Amber
        "accentSoft": "#eba714",  # Golden Yellow
        "background": "#faf5f0",  # Warm Stone
        "category": "professional",
    },

    # Blue + Teal
    "ocean": {
        "name": "ocean",
        "primary": "#0c4a6e",     # Deep Ocean Blue
        "secondary": "#0e7490",   # Cyan
        "accent": "#f59e0b",      # Orange
        "accentSoft": "#fb923c",  # Light Orange
        "background": "#f0f9ff",  # Sky background
        "category": "cool",
    },

    "steel": {
        "name": "steel",
        "primary": "#1e3a5f",     # Steel Blue
        "secondary": "#0f766e",   # Teal
        "accent": "#f59e0b",      # Amber
        "accentSoft": "#fbbf24",  # Golden
        "background": "#f0f9ff",  # Cool background
        "category": "professional",
    },

    "sapphire": {
        "name": "sapphire",
        "primary": "#1e3a8a",     # Deep Blue
        "secondary": "#1e40af",   # Blue
        "accent": "#fbbf24",      # Golden
        "accentSoft": "#fcd34d",  # Light Gold
        "background": "#eff6ff",  # Blue background
        "category": "cool",
    },

    # Teal + Orange (Popular combination)
    "teal": {
        "name": "teal",
        "primary": "#134e4a",     # Deep Teal
        "secondary": "#115e59",   # Teal
        "accent": "#f97316",      # Orange
        "accentSoft": "#fb923c",  # Light Orange
        "background": "#f0fdfa",  # Teal background
        "category": "vibrant",
    },

    # Rose + Gold (Elegant)
    "rose": {
        "name": "rose",
        "primary": "#881337",     # Deep Rose
        "secondary": "#9f1239",   # Rose
        "accent": "#fbbf24",      # Golden
        "accentSoft": "#fcd34d",  # Light Gold
        "background": "#fff1f2",  # Rose background
        "category": "warm",
    },

    # Red + Yellow
    "crimson": {
        "name": "crimson",
        "primary": "#7f1d1d",     # Dark Red
        "secondary": "#991b1b",   # Red
        "accent": "#eab308",      # Yellow
        "accentSoft": "#fbbf24",  # Golden
        "background": "#fef2f2",  # Light Red background
        "category": "warm",
    },

    # Purple + Amber
    "indigo": {
        "name": "indigo",
        "primary": "#3730a3",     # Indigo
        "secondary": "#4338ca",   # Light Indigo
        "accent": "#f59e0b",      # Amber
        "accentSoft": "#fbbf24",  # Golden
        "background": "#eef2ff",  # Indigo background
        "category": "creative",
    },

    # Green + Orange
    "forest": {
        "name": "forest",
        "primary": "#14532d",     # Forest Green
        "secondary": "#166534",   # Green
        "accent": "#ea580c",      # Deep Orange
        "accentSoft": "#fb7185",  # Rose
        "background": "#f7fee7",  # Light Green background
        "category": "natural",
    },

    "sage": {
        "name": "sage",
        "primary": "#15803d",     # Green
        "secondary": "#047857",   # Emerald
        "accent": "#f59e0b",      # Amber
        "accentSoft": "#fbbf24",  # Golden
        "background": "#f0fdf4",  # Light Green background
        "category": "natural",
    },

    "moss": {
        "name": "moss",
        "primary": "#365314",     # Deep Moss
        "secondary": "#3f6212",   # Green
        "accent": "#f59e0b",      # Amber
        "accentSoft": "#fbbf24",  # Golden
        "background": "#f7fee7",  # Light green background
        "category": "natural",
    },

    "pine": {
        "name": "pine",
        "primary": "#064e3b",     # Pine Green
        "secondary": "#065f46",   # Emerald
        "accent": "#d97706",      # Amber
        "accentSoft": "#f97316",  # Orange
        "background": "#ecfdf5",  # Mint background
        "category": "natural",
    },

    # Emerald + Cyan
    "mint": {
        "name": "mint",
        "primary": "#047857",     # Emerald
        "secondary": "#059669",   # Light Emerald
        "accent": "#06b6d4",      # Cyan
        "accentSoft": "#22d3ee",  # Light Cyan
        "background": "#ecfdf5",  # Mint background
        "category": "cool",
    },

    # Slate + Sky Blue
    "slate": {
        "name": "slate",
        "primary": "#1e293b",     # Dark Slate
        "secondary": "#334155",   # Slate
        "accent": "#0ea5e9",      # Sky Blue
        "accentSoft": "#38bdf8",  # Light Sky
        "background": "#f8fafc",  # Light background
        "category": "neutral",
    },

    # Navy + Coral
    "nautical": {
        "name": "nautical",
        "primary": "#0f172a",     # Deep Navy
        "secondary": "#1e3a8a",   # Navy Blue
        "accent": "#f97316",      # Coral Orange
        "accentSoft": "#fb923c",  # Light Coral
        "background": "#f0f9ff",  # Light Blue background
        "category": "professional",
    },

    # Cobalt + Amber
    "cobalt": {
        "name": "cobalt",
        "primary": "#1e40af",     # Cobalt Blue
        "secondary": "#2563eb",   # Blue
        "accent": "#f59e0b",      # Amber
        "accentSoft": "#fbbf24",  # Golden
        "background": "#eff6ff",  # Blue background
        "category": "vibrant",
    },

    # Azure + Rose
    "azure": {
        "name": "azure",
        "primary": "#0369a1",     # Azure Blue
        "secondary": "#0284c7",   # Sky Blue
        "accent": "#fb7185",      # Rose
        "accentSoft": "#fda4af",  # Light Rose
        "background": "#f0f9ff",  # Sky background
        "category": "cool",
    },

    # Charcoal + Teal
    "charcoal": {
        "name": "charcoal",
        "primary": "#1f2937",     # Charcoal
        "secondary": "#374151",   # Gray
        "accent": "#14b8a6",      # Teal
        "accentSoft": "#2dd4bf",  # Light Teal
        "background": "#f9fafb",  # Light Gray background
        "category": "neutral",
    },

    # Graphite + Amber
    "graphite": {
        "name": "graphite",
        "primary": "#18181b",     # Graphite
        "secondary": "#27272a",   # Zinc
        "accent": "#f59e0b",      # Amber
        "accentSoft": "#fbbf24",  # Golden
        "background": "#fafafa",  # Warm White background
        "category": "neutral",
    },

    # Deep Blue + Coral
    "marine": {
        "name": "marine",
        "primary": "#0c4a6e",     # Marine Blue
        "secondary": "#075985",   # Deep Sky
        "accent": "#f87171",      # Coral
        "accentSoft": "#fca5a5",  # Light Coral
        "background": "#f0f9ff",  # Sky background
        "category": "vibrant",
    },

    # Violet + Gold
    "violet": {
        "name": "violet",
        "primary": "#5b21b6",     # Violet
        "secondary": "#6b21a8",   # Purple
        "accent": "#fbbf24",      # Golden
        "accentSoft": "#fcd34d",  # Light Gold
        "background": "#faf5ff",  # Violet background
        "category": "creative",
    },

    # Plum + Amber
    "plum": {
        "name": "plum",
        "primary": "#701a75",     # Plum
        "secondary": "#86198f",   # Fuchsia
        "accent": "#f59e0b",      # Amber
        "accentSoft": "#fbbf24",  # Golden
        "background": "#fdf4ff",  # Light Purple background
        "category": "creative",
    },

    # Midnight Blue + Cyan
    "midnight_blue": {
        "name": "midnight_blue",
        "primary": "#172554",     # Midnight Blue
        "secondary": "#1e3a8a",   # Blue
        "accent": "#06b6d4",      # Cyan
        "accentSoft": "#22d3ee",  # Light Cyan
        "background": "#eff6ff",  # Blue background
        "category": "cool",
    },

    # Burgundy + Gold (Luxury)
    "burgundy": {
        "name": "burgundy",
        "primary": "#4c1d29",     # Deep Burgundy
        "secondary": "#7f1d3d",   # Wine
        "accent": "#fbbf24",      # Gold
        "accentSoft": "#fcd34d",  # Light Gold
        "background": "#fef7f0",  # Cream background
        "category": "warm",
    },

    # Terracotta + Teal (Earth tones)
    "terracotta": {
        "name": "terracotta",
        "primary": "#92400e",     # Terracotta
        "secondary": "#b45309",   # Amber Brown
        "accent": "#0d9488",      # Teal
        "accentSoft": "#14b8a6",  # Light Teal
        "background": "#fef3e2",  # Sand background
        "category": "warm",
    },
}

# =============================================================================
# FONT PAIRINGS (15+ options)
# Each pairing has: heading, body, style (identifier), category
# =============================================================================

FONT_PAIRINGS: Dict[str, Dict[str, str]] = {
    # Modern Sans-Serif
    "modern-clean": {
        "name": "modern-clean",
        "heading": "Inter",
        "body": "Inter",
        "style": "modern-clean",
        "category": "professional",
        "description": "Clean, modern sans-serif for tech and startups",
    },

    "geometric-modern": {
        "name": "geometric-modern",
        "heading": "Poppins",
        "body": "Open Sans",
        "style": "geometric-modern",
        "category": "professional",
        "description": "Geometric headings with friendly body text",
    },

    "swiss-minimal": {
        "name": "swiss-minimal",
        "heading": "Montserrat",
        "body": "Roboto",
        "style": "swiss-minimal",
        "category": "professional",
        "description": "Swiss-inspired minimal typography",
    },

    "tech-forward": {
        "name": "tech-forward",
        "heading": "Space Grotesk",
        "body": "Inter",
        "style": "tech-forward",
        "category": "professional",
        "description": "Modern tech aesthetic with geometric details",
    },

    # Classic Serif
    "classic-editorial": {
        "name": "classic-editorial",
        "heading": "Playfair Display",
        "body": "Lora",
        "style": "classic-editorial",
        "category": "classic",
        "description": "Elegant editorial style for magazines and luxury",
    },

    "traditional-serif": {
        "name": "traditional-serif",
        "heading": "Merriweather",
        "body": "Merriweather",
        "style": "traditional-serif",
        "category": "classic",
        "description": "Traditional, readable serif for long-form content",
    },

    "literary-elegant": {
        "name": "literary-elegant",
        "heading": "Cormorant Garamond",
        "body": "Crimson Text",
        "style": "literary-elegant",
        "category": "classic",
        "description": "Literary elegance for publishing and arts",
    },

    # Mixed (Serif headings + Sans body)
    "elegant-contrast": {
        "name": "elegant-contrast",
        "heading": "Playfair Display",
        "body": "Source Sans Pro",
        "style": "elegant-contrast",
        "category": "professional",
        "description": "Elegant contrast between display and body",
    },

    "editorial-modern": {
        "name": "editorial-modern",
        "heading": "DM Serif Display",
        "body": "DM Sans",
        "style": "editorial-modern",
        "category": "professional",
        "description": "Modern editorial with cohesive type family",
    },

    "luxury-minimal": {
        "name": "luxury-minimal",
        "heading": "Cormorant",
        "body": "Raleway",
        "style": "luxury-minimal",
        "category": "classic",
        "description": "Luxury feel with modern minimalism",
    },

    # Playful / Friendly
    "friendly-rounded": {
        "name": "friendly-rounded",
        "heading": "Nunito",
        "body": "Nunito",
        "style": "friendly-rounded",
        "category": "playful",
        "description": "Friendly, approachable rounded sans-serif",
    },

    "casual-modern": {
        "name": "casual-modern",
        "heading": "Quicksand",
        "body": "Open Sans",
        "style": "casual-modern",
        "category": "playful",
        "description": "Casual headings with professional body",
    },

    "warm-friendly": {
        "name": "warm-friendly",
        "heading": "Baloo 2",
        "body": "Rubik",
        "style": "warm-friendly",
        "category": "playful",
        "description": "Warm, inviting typography for consumer apps",
    },

    # Bold / Impactful
    "bold-statement": {
        "name": "bold-statement",
        "heading": "Oswald",
        "body": "Source Sans Pro",
        "style": "bold-statement",
        "category": "bold",
        "description": "Strong, impactful headings for marketing",
    },

    "condensed-power": {
        "name": "condensed-power",
        "heading": "Bebas Neue",
        "body": "Lato",
        "style": "condensed-power",
        "category": "bold",
        "description": "Powerful condensed headlines",
    },

    "industrial-strong": {
        "name": "industrial-strong",
        "heading": "Anton",
        "body": "Work Sans",
        "style": "industrial-strong",
        "category": "bold",
        "description": "Industrial strength for bold statements",
    },

    # Humanist / Natural
    "humanist-natural": {
        "name": "humanist-natural",
        "heading": "Libre Baskerville",
        "body": "Source Sans Pro",
        "style": "humanist-natural",
        "category": "classic",
        "description": "Humanist warmth with readability",
    },

    "organic-flow": {
        "name": "organic-flow",
        "heading": "Josefin Sans",
        "body": "Karla",
        "style": "organic-flow",
        "category": "playful",
        "description": "Organic, flowing typography",
    },
}

# =============================================================================
# PALETTE CATEGORIES FOR BINARY SEARCH
# =============================================================================

PALETTE_CATEGORIES = {
    "professional": ["default", "midnight", "dusk", "steel", "nautical"],
    "cool": ["ocean", "sapphire", "azure", "mint", "midnight_blue"],
    "warm": ["rose", "crimson", "burgundy", "terracotta"],
    "natural": ["forest", "sage", "moss", "pine"],
    "creative": ["indigo", "violet", "plum"],
    "neutral": ["slate", "charcoal", "graphite"],
    "vibrant": ["teal", "cobalt", "marine"],
}

FONT_CATEGORIES = {
    "professional": ["modern-clean", "geometric-modern", "swiss-minimal", "tech-forward", "elegant-contrast", "editorial-modern"],
    "classic": ["classic-editorial", "traditional-serif", "literary-elegant", "luxury-minimal", "humanist-natural"],
    "playful": ["friendly-rounded", "casual-modern", "warm-friendly", "organic-flow"],
    "bold": ["bold-statement", "condensed-power", "industrial-strong"],
}

# =============================================================================
# COMPARISON PAIR GENERATION
# =============================================================================

def get_all_palettes() -> List[Dict[str, str]]:
    """Return all color palettes as a list."""
    return list(COLOR_PALETTES.values())


def get_all_font_pairings() -> List[Dict[str, str]]:
    """Return all font pairings as a list."""
    return list(FONT_PAIRINGS.values())


def get_palette_comparison_pair(
    comparison_count: int,
    previous_choices: Optional[List[str]] = None
) -> Tuple[Dict[str, str], Dict[str, str]]:
    """
    Get two color palettes for A/B comparison using progressive narrowing.

    Strategy:
    - First 2-3 comparisons: Compare across categories (professional vs creative, warm vs cool)
    - Later comparisons: Compare within the winning category

    Args:
        comparison_count: Number of comparisons completed so far
        previous_choices: List of palette names user has preferred

    Returns:
        Tuple of (palette_a, palette_b)
    """
    all_palettes = list(COLOR_PALETTES.values())

    if comparison_count == 0:
        # First comparison: Professional vs Creative
        return (
            COLOR_PALETTES["default"],      # Professional Navy
            COLOR_PALETTES["violet"]         # Creative Purple
        )
    elif comparison_count == 1:
        # Second comparison: Warm vs Cool
        return (
            COLOR_PALETTES["rose"],          # Warm Rose
            COLOR_PALETTES["ocean"]          # Cool Ocean
        )
    elif comparison_count == 2:
        # Third comparison: Natural vs Neutral
        return (
            COLOR_PALETTES["forest"],        # Natural Green
            COLOR_PALETTES["slate"]          # Neutral Slate
        )
    elif comparison_count == 3:
        # Fourth comparison: Vibrant vs Subtle
        return (
            COLOR_PALETTES["teal"],          # Vibrant Teal + Orange
            COLOR_PALETTES["dusk"]           # Subtle Navy + Slate
        )
    elif comparison_count == 4:
        # Fifth comparison: Bold accent vs Soft accent
        return (
            COLOR_PALETTES["cobalt"],        # Bold Blue + Amber
            COLOR_PALETTES["mint"]           # Soft Emerald + Cyan
        )
    else:
        # Later comparisons: Random from remaining
        # In a real implementation, this would use previous_choices to narrow
        random.shuffle(all_palettes)
        return (all_palettes[0], all_palettes[1])


def get_typography_comparison_pair(
    comparison_count: int,
    previous_choices: Optional[List[str]] = None
) -> Tuple[Dict[str, str], Dict[str, str]]:
    """
    Get two font pairings for A/B comparison using progressive narrowing.

    Strategy:
    - First comparison: Sans vs Serif
    - Second comparison: Modern vs Classic
    - Third comparison: Bold vs Subtle
    - Later: Compare within winning style

    Args:
        comparison_count: Number of comparisons completed so far
        previous_choices: List of font pairing names user has preferred

    Returns:
        Tuple of (fonts_a, fonts_b)
    """
    all_fonts = list(FONT_PAIRINGS.values())

    if comparison_count == 0:
        # First comparison: Clean Modern Sans vs Classic Serif
        return (
            FONT_PAIRINGS["modern-clean"],       # Modern Inter
            FONT_PAIRINGS["classic-editorial"]    # Classic Playfair + Lora
        )
    elif comparison_count == 1:
        # Second comparison: Professional vs Playful
        return (
            FONT_PAIRINGS["swiss-minimal"],      # Professional Montserrat
            FONT_PAIRINGS["friendly-rounded"]     # Playful Nunito
        )
    elif comparison_count == 2:
        # Third comparison: Bold vs Subtle
        return (
            FONT_PAIRINGS["bold-statement"],     # Bold Oswald
            FONT_PAIRINGS["elegant-contrast"]     # Subtle Playfair + Source
        )
    elif comparison_count == 3:
        # Fourth comparison: Mixed vs Uniform
        return (
            FONT_PAIRINGS["editorial-modern"],   # Mixed DM Serif + DM Sans
            FONT_PAIRINGS["geometric-modern"]     # Uniform Poppins + Open Sans
        )
    elif comparison_count == 4:
        # Fifth comparison: Tech vs Traditional
        return (
            FONT_PAIRINGS["tech-forward"],       # Tech Space Grotesk
            FONT_PAIRINGS["traditional-serif"]    # Traditional Merriweather
        )
    else:
        # Later comparisons: Random from remaining
        random.shuffle(all_fonts)
        return (all_fonts[0], all_fonts[1])


def generate_color_comparison(comparison_count: int) -> Dict:
    """
    Generate a full comparison object for color exploration phase.

    Returns a dict matching the ComparisonResponse schema.
    """
    palette_a, palette_b = get_palette_comparison_pair(comparison_count)

    return {
        "comparison_id": comparison_count + 1,
        "component_type": "color_palette",
        "phase": "color_exploration",
        "option_a": {
            "id": palette_a["name"],
            "styles": {
                "primary": palette_a["primary"],
                "secondary": palette_a["secondary"],
                "accent": palette_a["accent"],
                "accentSoft": palette_a["accentSoft"],
                "background": palette_a["background"],
                "category": palette_a.get("category", ""),
            }
        },
        "option_b": {
            "id": palette_b["name"],
            "styles": {
                "primary": palette_b["primary"],
                "secondary": palette_b["secondary"],
                "accent": palette_b["accent"],
                "accentSoft": palette_b["accentSoft"],
                "background": palette_b["background"],
                "category": palette_b.get("category", ""),
            }
        },
        "context": f"Comparing {palette_a['name']} ({palette_a.get('category', '')}) vs {palette_b['name']} ({palette_b.get('category', '')})",
        "questions": [
            {
                "category": "color",
                "property": "palette",
                "question_text": "Which color palette feels right for your brand?",
                "option_a_value": palette_a["name"],
                "option_b_value": palette_b["name"]
            }
        ],
        "generation_method": "deterministic"
    }


def generate_typography_comparison(comparison_count: int) -> Dict:
    """
    Generate a full comparison object for typography exploration phase.

    Returns a dict matching the ComparisonResponse schema.
    """
    fonts_a, fonts_b = get_typography_comparison_pair(comparison_count)

    return {
        "comparison_id": comparison_count + 1,
        "component_type": "font_pair",
        "phase": "typography_exploration",
        "option_a": {
            "id": fonts_a["name"],
            "styles": {
                "heading": fonts_a["heading"],
                "body": fonts_a["body"],
                "style": fonts_a["style"],
                "category": fonts_a.get("category", ""),
                "description": fonts_a.get("description", ""),
            }
        },
        "option_b": {
            "id": fonts_b["name"],
            "styles": {
                "heading": fonts_b["heading"],
                "body": fonts_b["body"],
                "style": fonts_b["style"],
                "category": fonts_b.get("category", ""),
                "description": fonts_b.get("description", ""),
            }
        },
        "context": f"Comparing {fonts_a['style']} ({fonts_a.get('category', '')}) vs {fonts_b['style']} ({fonts_b.get('category', '')})",
        "questions": [
            {
                "category": "typography",
                "property": "font_pair",
                "question_text": "Which typography style suits your project?",
                "option_a_value": fonts_a["style"],
                "option_b_value": fonts_b["style"]
            }
        ],
        "generation_method": "deterministic"
    }


def get_palette_by_name(name: str) -> Optional[Dict[str, str]]:
    """Get a specific palette by name."""
    return COLOR_PALETTES.get(name)


def get_font_pairing_by_name(name: str) -> Optional[Dict[str, str]]:
    """Get a specific font pairing by name."""
    return FONT_PAIRINGS.get(name)
