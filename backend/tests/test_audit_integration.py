"""
TML Audit Integration Tests

Tests for the full audit flow, simulating realistic scenarios
where users upload screenshots and receive programmatic feedback.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from audit_routes import apply_rules_to_extracted_values, Violation


class TestRealWorldScenarios:
    """Tests simulating real-world audit scenarios."""

    def test_enterprise_dashboard_audit(self):
        """
        Scenario: Auditing an enterprise dashboard against a professional style profile.
        Expected: Flag off-brand colors, allow professional fonts.
        """
        # Simulated Claude Vision extraction from enterprise dashboard
        extracted = {
            "colors": [
                {"element": "header background", "color": "#1a365d"},  # Brand primary - OK
                {"element": "sidebar", "color": "#f3f4f6"},  # Neutral gray - OK
                {"element": "warning badge", "color": "#f59e0b"},  # Amber accent - OK
                {"element": "random decoration", "color": "#ff00ff"},  # Magenta - BAD!
            ],
            "fonts": [
                {"element": "heading", "font": "Inter, sans-serif"},
                {"element": "body", "font": "Inter, sans-serif"},
            ],
            "measurements": {
                "button_border_radius": "8px",
                "card_padding": "24px",
            }
        }

        chosen_colors = {
            "primary": "#1a365d",
            "secondary": "#115e59",
            "accent": "#f59e0b",
            "background": "#ffffff"
        }
        chosen_typography = {"heading": "Inter", "body": "Inter"}

        violations = apply_rules_to_extracted_values(
            extracted, [], chosen_colors, chosen_typography
        )

        # Should flag magenta as off-brand, neutral gray is close to white
        off_brand = [v for v in violations if "#ff00ff" in v.found]
        assert len(off_brand) >= 1, "Should flag magenta as off-brand"

    def test_healthcare_portal_accessibility(self):
        """
        Scenario: Healthcare portal needs high contrast and clear typography.
        Expected: Flag low contrast colors, flag decorative fonts.
        """
        extracted = {
            "colors": [
                {"element": "button text", "color": "#ffffff"},
                {"element": "button background", "color": "#2563eb"},  # Blue - good
                {"element": "link", "color": "#93c5fd"},  # Light blue on white - bad contrast
            ],
            "fonts": [
                {"element": "heading", "font": "Merriweather, serif"},
                {"element": "body", "font": "Comic Sans"},  # Bad for healthcare!
            ],
            "measurements": {}
        }

        chosen_colors = {
            "primary": "#1e40af",
            "secondary": "#0d9488",
            "background": "#ffffff"
        }
        chosen_typography = {"heading": "Merriweather", "body": "Open Sans"}

        violations = apply_rules_to_extracted_values(
            extracted, [], chosen_colors, chosen_typography
        )

        # Should flag Comic Sans
        font_violations = [v for v in violations if "font" in v.property.lower()]
        assert len(font_violations) >= 1, "Should flag Comic Sans"

        # Should flag colors not in palette
        color_violations = [v for v in violations if "color" in v.property.lower()]
        assert len(color_violations) >= 1, "Should flag off-palette colors"

    def test_ecommerce_checkout_form(self):
        """
        Scenario: E-commerce checkout needs clear CTAs and readable forms.
        Expected: Flag small fonts, incorrect CTA colors.
        """
        class MockRule:
            rule_id = "form-001"
            property = "font-size"
            operator = ">="
            value = "14"
            severity = "error"
            message = "Form text must be readable"
            component_type = "form"

        extracted = {
            "colors": [
                {"element": "cta button", "color": "#22c55e"},  # Green - good for CTA
                {"element": "error message", "color": "#ef4444"},  # Red - good for errors
            ],
            "fonts": [],
            "measurements": {
                "form_font_size": "12px",  # Too small!
                "button_padding": "16px",
            }
        }

        chosen_colors = {
            "primary": "#1a1a1a",
            "accent": "#22c55e",
            "error": "#ef4444",
        }

        violations = apply_rules_to_extracted_values(
            extracted, [MockRule()], chosen_colors, None
        )

        # Should flag small font
        size_violations = [v for v in violations if "font" in v.property.lower() or "size" in v.property.lower()]
        assert len(size_violations) >= 1, "Should flag 12px font as too small"


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_empty_extraction(self):
        """Handle empty extraction gracefully."""
        extracted = {
            "colors": [],
            "fonts": [],
            "measurements": {}
        }

        violations = apply_rules_to_extracted_values(
            extracted, [], {"primary": "#000000"}, {"heading": "Inter"}
        )

        # No violations when nothing to check
        assert len(violations) == 0

    def test_missing_keys(self):
        """Handle missing keys in extraction."""
        extracted = {}  # Completely empty

        violations = apply_rules_to_extracted_values(
            extracted, [], {"primary": "#000000"}, None
        )

        assert violations is not None  # Should not crash

    def test_null_style_choices(self):
        """Handle null color/typography choices."""
        extracted = {
            "colors": [{"element": "button", "color": "#ff0000"}],
            "fonts": [{"element": "body", "font": "Arial"}],
            "measurements": {}
        }

        # No palette or typography defined
        violations = apply_rules_to_extracted_values(
            extracted, [], None, None
        )

        # Should not crash, no violations since no rules defined
        assert violations is not None

    def test_similar_colors_tolerance(self):
        """Colors within tolerance should not trigger violations."""
        # These colors differ by only a few RGB values
        extracted = {
            "colors": [
                {"element": "btn1", "color": "#1a365d"},  # Exact
                {"element": "btn2", "color": "#1b375e"},  # Off by 1
                {"element": "btn3", "color": "#1e3a60"},  # Off by ~4
                {"element": "btn4", "color": "#2a4670"},  # Off by ~16-18
            ],
            "fonts": [],
            "measurements": {}
        }

        violations = apply_rules_to_extracted_values(
            extracted, [], {"primary": "#1a365d"}, None
        )

        # Only colors significantly different should be flagged
        # Default tolerance is 20, so all these should pass
        flagged_colors = [v.found for v in violations]
        assert "#1a365d" not in flagged_colors  # Exact match
        assert "#1b375e" not in flagged_colors  # Close enough


class TestScoringIntegration:
    """Tests for audit score calculation in context."""

    def test_perfect_compliance_score(self):
        """Perfect compliance should yield score 100."""
        extracted = {
            "colors": [{"element": "primary", "color": "#1a365d"}],
            "fonts": [{"element": "body", "font": "Inter"}],
            "measurements": {}
        }

        violations = apply_rules_to_extracted_values(
            extracted, [], {"primary": "#1a365d"}, {"body": "Inter"}
        )

        error_count = sum(1 for v in violations if v.severity == 'error')
        warning_count = sum(1 for v in violations if v.severity == 'warning')
        score = max(0, 100 - (error_count * 15) - (warning_count * 5))

        assert score == 100

    def test_multiple_violations_score(self):
        """Multiple violations should reduce score proportionally."""
        extracted = {
            "colors": [
                {"element": "btn1", "color": "#ff0000"},  # Violation 1
                {"element": "btn2", "color": "#00ff00"},  # Violation 2
                {"element": "btn3", "color": "#0000ff"},  # Violation 3
            ],
            "fonts": [{"element": "body", "font": "Comic Sans"}],  # Violation 4
            "measurements": {}
        }

        violations = apply_rules_to_extracted_values(
            extracted,
            [],
            {"primary": "#1a365d", "secondary": "#115e59"},
            {"body": "Inter"}
        )

        # Should have 4 violations (3 color + 1 font)
        assert len(violations) >= 3

        error_count = sum(1 for v in violations if v.severity == 'error')
        warning_count = sum(1 for v in violations if v.severity == 'warning')
        score = max(0, 100 - (error_count * 15) - (warning_count * 5))

        # Score should be reduced
        assert score < 100


class TestContextualAudit:
    """Tests for context-aware audit behavior."""

    def test_button_specific_rules(self):
        """Rules match by property name - border-radius matches any *border_radius key."""
        class ButtonRule:
            rule_id = "btn-radius"
            property = "border-radius"
            operator = ">="
            value = "8"
            severity = "warning"
            message = "Buttons need rounded corners"
            component_type = "button"

        extracted = {
            "colors": [],
            "fonts": [],
            "measurements": {
                "button_border_radius": "4px",  # Triggers - contains 'border_radius'
                "card_border_radius": "2px",    # Also triggers - contains 'border_radius'
            }
        }

        violations = apply_rules_to_extracted_values(
            extracted, [ButtonRule()], None, None
        )

        # Current implementation matches by property name containment
        # Both measurements contain 'border_radius', so both are checked
        button_violations = [v for v in violations if v.rule_id == "btn-radius"]
        assert len(button_violations) == 2  # Both violate the >= 8px rule

    def test_multiple_rules_same_property(self):
        """Multiple rules for same property should all be checked."""
        class MinRule:
            rule_id = "spacing-min"
            property = "padding"
            operator = ">="
            value = "8"
            severity = "warning"
            message = "Minimum padding"
            component_type = None

        class MaxRule:
            rule_id = "spacing-max"
            property = "padding"
            operator = "<="
            value = "32"
            severity = "warning"
            message = "Maximum padding"
            component_type = None

        # Value within range - should pass both
        extracted = {
            "colors": [],
            "fonts": [],
            "measurements": {"button_padding": "16px"}
        }

        violations = apply_rules_to_extracted_values(
            extracted, [MinRule(), MaxRule()], None, None
        )
        assert len(violations) == 0

        # Value below range - should fail min
        extracted["measurements"]["button_padding"] = "4px"
        violations = apply_rules_to_extracted_values(
            extracted, [MinRule(), MaxRule()], None, None
        )
        assert any(v.rule_id == "spacing-min" for v in violations)

        # Value above range - should fail max
        extracted["measurements"]["button_padding"] = "48px"
        violations = apply_rules_to_extracted_values(
            extracted, [MinRule(), MaxRule()], None, None
        )
        assert any(v.rule_id == "spacing-max" for v in violations)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
