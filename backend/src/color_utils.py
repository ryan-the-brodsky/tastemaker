"""
Color utility functions for palette processing.
Ports the derived color calculations from ColorEditor.tsx to Python.
"""


def hex_to_hsl(hex_color: str) -> dict:
    """Convert hex color (#RRGGBB) to HSL dict {h, s, l}."""
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16) / 255, int(hex_color[2:4], 16) / 255, int(hex_color[4:6], 16) / 255

    max_c = max(r, g, b)
    min_c = min(r, g, b)
    delta = max_c - min_c

    # Lightness
    l = (max_c + min_c) / 2

    if delta == 0:
        h = 0
        s = 0
    else:
        # Saturation
        s = delta / (1 - abs(2 * l - 1))

        # Hue
        if max_c == r:
            h = 60 * (((g - b) / delta) % 6)
        elif max_c == g:
            h = 60 * (((b - r) / delta) + 2)
        else:
            h = 60 * (((r - g) / delta) + 4)

    return {'h': round(h, 1), 's': round(s * 100, 1), 'l': round(l * 100, 1)}


def hsl_to_hex(h: float, s: float, l: float) -> str:
    """Convert HSL values to hex color string (#rrggbb)."""
    s = s / 100
    l = l / 100

    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l - c / 2

    if h < 60:
        r1, g1, b1 = c, x, 0
    elif h < 120:
        r1, g1, b1 = x, c, 0
    elif h < 180:
        r1, g1, b1 = 0, c, x
    elif h < 240:
        r1, g1, b1 = 0, x, c
    elif h < 300:
        r1, g1, b1 = x, 0, c
    else:
        r1, g1, b1 = c, 0, x

    r = round((r1 + m) * 255)
    g = round((g1 + m) * 255)
    b = round((b1 + m) * 255)

    return f'#{r:02x}{g:02x}{b:02x}'


def adjust_lightness(hex_color: str, delta: float) -> str:
    """Adjust the lightness of a hex color by delta percentage points."""
    hsl = hex_to_hsl(hex_color)
    new_l = max(0, min(100, hsl['l'] + delta))
    return hsl_to_hex(hsl['h'], hsl['s'], new_l)


def get_contrast_color(hex_color: str) -> str:
    """Return white or dark gray text color based on background luminance."""
    hsl = hex_to_hsl(hex_color)
    return '#ffffff' if hsl['l'] < 50 else '#111827'


def calculate_derived_colors(colors: dict) -> dict:
    """
    Calculate all 11 derived colors from a base palette.

    Args:
        colors: dict with keys: primary, secondary, accent, accentSoft, background

    Returns:
        dict with all derived color values
    """
    return {
        'primaryLight': adjust_lightness(colors['primary'], 15),
        'primaryDark': adjust_lightness(colors['primary'], -15),
        'secondaryLight': adjust_lightness(colors['secondary'], 15),
        'secondaryDark': adjust_lightness(colors['secondary'], -15),
        'accentLight': adjust_lightness(colors['accent'], 20),
        'border': adjust_lightness(colors['background'], -10),
        'textOnPrimary': get_contrast_color(colors['primary']),
        'textOnSecondary': get_contrast_color(colors['secondary']),
        'textOnAccent': get_contrast_color(colors['accent']),
        'textPrimary': '#111827',
        'textSecondary': '#6b7280',
    }
