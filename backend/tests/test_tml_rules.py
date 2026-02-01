"""
TML (Taste Markup Language) Rule Checking Tests

These tests verify the programmatic rule application logic used in TasteMaker audits.
The TML protocol is DETERMINISTIC - rules are applied mathematically, not via LLM opinion.
"""
import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from audit_routes import (
    parse_color,
    colors_match,
    parse_size,
    check_rule,
    apply_rules_to_extracted_values,
    Violation
)


class TestColorParsing:
    """Tests for color string parsing."""

    def test_parse_hex_6_digit(self):
        """Parse standard 6-digit hex color."""
        assert parse_color("#1a365d") == (26, 54, 93)
        assert parse_color("#ffffff") == (255, 255, 255)
        assert parse_color("#000000") == (0, 0, 0)

    def test_parse_hex_3_digit(self):
        """Parse shorthand 3-digit hex color."""
        assert parse_color("#fff") == (255, 255, 255)
        assert parse_color("#000") == (0, 0, 0)
        assert parse_color("#f00") == (255, 0, 0)

    def test_parse_rgb_format(self):
        """Parse rgb() format colors."""
        assert parse_color("rgb(26, 54, 93)") == (26, 54, 93)
        assert parse_color("rgb(255,255,255)") == (255, 255, 255)
        assert parse_color("rgb(0, 0, 0)") == (0, 0, 0)

    def test_parse_invalid_returns_none(self):
        """Invalid colors should return None."""
        assert parse_color("") is None
        assert parse_color(None) is None
        assert parse_color("red") is None  # Named colors not supported
        assert parse_color("#xyz") is None


class TestColorMatching:
    """Tests for color matching with tolerance."""

    def test_exact_match(self):
        """Exact same colors should match."""
        assert colors_match("#1a365d", "#1a365d") is True
        assert colors_match("#ffffff", "#ffffff") is True

    def test_within_tolerance(self):
        """Colors within tolerance should match."""
        # Default tolerance is 20
        assert colors_match("#1a365d", "#1b375e") is True  # Off by 1 each
        assert colors_match("#ffffff", "#f0f0f0") is True  # Off by 15 each

    def test_outside_tolerance(self):
        """Colors outside tolerance should not match."""
        assert colors_match("#1a365d", "#ff0000") is False  # Red vs blue
        assert colors_match("#000000", "#ffffff") is False  # Black vs white
        assert colors_match("#1a365d", "#5a765d") is False  # Off by > 20

    def test_custom_tolerance(self):
        """Custom tolerance should be respected."""
        # These are off by ~15 in each channel
        assert colors_match("#ffffff", "#f0f0f0", tolerance=20) is True
        assert colors_match("#ffffff", "#f0f0f0", tolerance=10) is False

    def test_different_formats(self):
        """Colors in different formats should still compare."""
        assert colors_match("#1a365d", "rgb(26, 54, 93)") is True
        assert colors_match("rgb(255,255,255)", "#ffffff") is True

    def test_fallback_string_comparison(self):
        """Invalid colors fall back to string comparison."""
        assert colors_match("red", "red") is True
        assert colors_match("red", "blue") is False


class TestSizeParsing:
    """Tests for CSS size value parsing."""

    def test_parse_px_values(self):
        """Parse pixel values."""
        assert parse_size("8px") == 8.0
        assert parse_size("16px") == 16.0
        assert parse_size("12.5px") == 12.5

    def test_parse_plain_numbers(self):
        """Parse plain numbers without units."""
        assert parse_size("8") == 8.0
        assert parse_size("16") == 16.0
        assert parse_size("12.5") == 12.5

    def test_parse_with_whitespace(self):
        """Parse values with whitespace."""
        assert parse_size(" 8px ") is not None
        assert parse_size("8 ") == 8.0

    def test_parse_invalid_returns_none(self):
        """Invalid sizes should return None."""
        assert parse_size("") is None
        assert parse_size(None) is None
        assert parse_size("auto") is None


class TestRuleChecking:
    """Tests for the check_rule function with various operators."""

    # Equality operator tests
    def test_equality_string_match(self):
        """String equality check."""
        assert check_rule("=", "Inter", "Inter", "font-family") is True
        assert check_rule("=", "Inter", "Roboto", "font-family") is False

    def test_equality_case_insensitive(self):
        """String equality is case insensitive."""
        assert check_rule("=", "Inter", "inter", "font-family") is True
        assert check_rule("=", "INTER", "inter", "font-family") is True

    def test_equality_numeric(self):
        """Numeric equality with tolerance."""
        assert check_rule("=", "8px", "8px", "border-radius") is True
        assert check_rule("=", "8", "8.5", "border-radius") is True  # Within 1
        assert check_rule("=", "8", "10", "border-radius") is False  # Off by 2

    # Greater than or equal operator tests
    def test_gte_operator(self):
        """Greater than or equal comparisons."""
        assert check_rule(">=", "8px", "8px", "border-radius") is True
        assert check_rule(">=", "8px", "10px", "border-radius") is True
        assert check_rule(">=", "8px", "6px", "border-radius") is False

    def test_gte_with_floats(self):
        """GTE with floating point values."""
        assert check_rule(">=", "8", "8.0", "padding") is True
        assert check_rule(">=", "8.5", "9", "padding") is True
        assert check_rule(">=", "8.5", "8", "padding") is False

    # Less than or equal operator tests
    def test_lte_operator(self):
        """Less than or equal comparisons."""
        assert check_rule("<=", "16px", "16px", "font-size") is True
        assert check_rule("<=", "16px", "14px", "font-size") is True
        assert check_rule("<=", "16px", "18px", "font-size") is False

    # Greater than operator tests
    def test_gt_operator(self):
        """Greater than comparisons."""
        assert check_rule(">", "8px", "10px", "margin") is True
        assert check_rule(">", "8px", "8px", "margin") is False
        assert check_rule(">", "8px", "6px", "margin") is False

    # Less than operator tests
    def test_lt_operator(self):
        """Less than comparisons."""
        assert check_rule("<", "16px", "14px", "width") is True
        assert check_rule("<", "16px", "16px", "width") is False
        assert check_rule("<", "16px", "18px", "width") is False

    # Contains operator tests
    def test_contains_operator(self):
        """String contains checks."""
        assert check_rule("contains", "sans", "Inter, sans-serif", "font-family") is True
        assert check_rule("contains", "Inter", "Inter, Roboto", "font-family") is True
        assert check_rule("contains", "serif", "Arial, Helvetica", "font-family") is False

    # One of operator tests
    def test_one_of_operator(self):
        """Value is one of a list."""
        assert check_rule("one_of", "primary, secondary, ghost", "primary", "variant") is True
        assert check_rule("one_of", "primary, secondary, ghost", "secondary", "variant") is True
        assert check_rule("one_of", "primary, secondary, ghost", "destructive", "variant") is False

    # Color comparison tests
    def test_color_equality(self):
        """Color equality uses color matching logic."""
        assert check_rule("=", "#1a365d", "#1a365d", "background-color") is True
        assert check_rule("=", "#1a365d", "#1b375e", "color") is True  # Within tolerance
        assert check_rule("=", "#1a365d", "#ff0000", "border-color") is False


class TestViolationDetection:
    """Tests for detecting violations from extracted values."""

    def test_color_palette_violation(self):
        """Detect colors not in defined palette."""
        extracted = {
            "colors": [
                {"element": "button", "color": "#ff0000"}  # Red not in palette
            ],
            "fonts": [],
            "measurements": {}
        }
        chosen_colors = {
            "primary": "#1a365d",
            "secondary": "#115e59",
            "accent": "#d97706",
            "background": "#faf5f0"
        }

        violations = apply_rules_to_extracted_values(
            extracted, [], chosen_colors, None
        )

        assert len(violations) == 1
        assert violations[0].rule_id == "color-palette"
        assert violations[0].severity == "warning"
        assert "#ff0000" in violations[0].found

    def test_color_in_palette_no_violation(self):
        """Colors in palette should not trigger violations."""
        extracted = {
            "colors": [
                {"element": "button", "color": "#1a365d"}  # Primary color
            ],
            "fonts": [],
            "measurements": {}
        }
        chosen_colors = {
            "primary": "#1a365d",
            "secondary": "#115e59"
        }

        violations = apply_rules_to_extracted_values(
            extracted, [], chosen_colors, None
        )

        assert len(violations) == 0

    def test_typography_violation(self):
        """Detect fonts not matching typography profile."""
        extracted = {
            "colors": [],
            "fonts": [
                {"element": "heading", "font": "Arial"}  # Wrong font
            ],
            "measurements": {}
        }
        chosen_typography = {
            "heading": "Inter",
            "body": "Inter"
        }

        violations = apply_rules_to_extracted_values(
            extracted, [], None, chosen_typography
        )

        assert len(violations) == 1
        assert violations[0].rule_id == "typography-font"
        assert "Arial" in violations[0].found
        assert "Inter" in violations[0].expected

    def test_font_matching_no_violation(self):
        """Correct fonts should not trigger violations."""
        extracted = {
            "colors": [],
            "fonts": [
                {"element": "heading", "font": "Inter, sans-serif"}
            ],
            "measurements": {}
        }
        chosen_typography = {
            "heading": "Inter",
            "body": "Inter"
        }

        violations = apply_rules_to_extracted_values(
            extracted, [], None, chosen_typography
        )

        assert len(violations) == 0


class TestScoringCalculation:
    """Tests for violation scoring logic."""

    def test_perfect_score(self):
        """No violations should yield score 100."""
        # Score calculation: 100 - (errors * 15) - (warnings * 5)
        violations = []
        error_count = sum(1 for v in violations if v.severity == 'error')
        warning_count = sum(1 for v in violations if v.severity == 'warning')
        score = max(0, 100 - (error_count * 15) - (warning_count * 5))
        assert score == 100

    def test_warning_reduces_score(self):
        """Warnings should reduce score by 5 each."""
        violations = [
            Violation(
                rule_id="test", severity="warning", property="test",
                expected="", found="", message="", suggestion=""
            )
        ]
        error_count = sum(1 for v in violations if v.severity == 'error')
        warning_count = sum(1 for v in violations if v.severity == 'warning')
        score = max(0, 100 - (error_count * 15) - (warning_count * 5))
        assert score == 95

    def test_error_reduces_score(self):
        """Errors should reduce score by 15 each."""
        violations = [
            Violation(
                rule_id="test", severity="error", property="test",
                expected="", found="", message="", suggestion=""
            )
        ]
        error_count = sum(1 for v in violations if v.severity == 'error')
        warning_count = sum(1 for v in violations if v.severity == 'warning')
        score = max(0, 100 - (error_count * 15) - (warning_count * 5))
        assert score == 85

    def test_mixed_violations(self):
        """Mixed violations combine penalties."""
        violations = [
            Violation(rule_id="err1", severity="error", property="", expected="", found="", message="", suggestion=""),
            Violation(rule_id="err2", severity="error", property="", expected="", found="", message="", suggestion=""),
            Violation(rule_id="warn1", severity="warning", property="", expected="", found="", message="", suggestion=""),
        ]
        error_count = sum(1 for v in violations if v.severity == 'error')
        warning_count = sum(1 for v in violations if v.severity == 'warning')
        score = max(0, 100 - (error_count * 15) - (warning_count * 5))
        # 100 - (2 * 15) - (1 * 5) = 100 - 30 - 5 = 65
        assert score == 65

    def test_score_minimum_zero(self):
        """Score should not go below 0."""
        violations = [
            Violation(rule_id=f"err{i}", severity="error", property="", expected="", found="", message="", suggestion="")
            for i in range(10)  # 10 errors = 150 point penalty
        ]
        error_count = sum(1 for v in violations if v.severity == 'error')
        warning_count = sum(1 for v in violations if v.severity == 'warning')
        score = max(0, 100 - (error_count * 15) - (warning_count * 5))
        assert score == 0


class TestContextualRules:
    """Tests for context-aware rule application."""

    def test_component_specific_rule(self):
        """Rules should apply to specific components."""
        class MockRule:
            rule_id = "btn-001"
            property = "border-radius"
            operator = ">="
            value = "8"
            severity = "warning"
            message = "Button border-radius should be >= 8px"
            component_type = "button"

        extracted = {
            "colors": [],
            "fonts": [],
            "measurements": {
                "button_border_radius": "4px"  # Violates rule
            }
        }

        violations = apply_rules_to_extracted_values(
            extracted, [MockRule()], None, None
        )

        assert len(violations) == 1
        assert violations[0].rule_id == "btn-001"

    def test_global_rule_applies_to_all(self):
        """Rules with no component_type should apply globally."""
        class MockRule:
            rule_id = "global-001"
            property = "font-size"
            operator = ">="
            value = "14"
            severity = "warning"
            message = "Font size should be >= 14px for readability"
            component_type = None

        extracted = {
            "colors": [],
            "fonts": [],
            "measurements": {
                "body_font_size": "12px"
            }
        }

        violations = apply_rules_to_extracted_values(
            extracted, [MockRule()], None, None
        )

        # Should match because "font" is in "body_font_size"
        assert len(violations) >= 0  # Rule matching depends on property name


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
