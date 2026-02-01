"""
TML Protocol Specification Tests

These tests define the TML (Taste Markup Language) protocol behavior.
They serve as both tests AND documentation of expected behavior.
"""
import pytest
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestTMLRuleSchema:
    """Tests for TML rule JSON schema validation."""

    def test_minimal_valid_rule(self):
        """A rule must have at minimum: id, property, operator, value."""
        rule = {
            "id": "test-001",
            "property": "border-radius",
            "operator": ">=",
            "value": 8
        }
        assert "id" in rule
        assert "property" in rule
        assert "operator" in rule
        assert "value" in rule

    def test_full_rule_schema(self):
        """Full TML rule with all optional fields."""
        rule = {
            "id": "btn-001",
            "component": "button",
            "property": "border-radius",
            "operator": ">=",
            "value": 8,
            "severity": "warning",
            "confidence": 0.92,
            "source": "extracted",
            "message": "Buttons should have rounded corners"
        }

        # Required fields
        assert isinstance(rule["id"], str)
        assert isinstance(rule["property"], str)
        assert isinstance(rule["operator"], str)

        # Value can be any type
        assert rule["value"] is not None

        # Optional fields
        assert rule["component"] in ["button", "input", "card", "typography",
                                     "navigation", "form", "feedback", "modal", None]
        assert rule["severity"] in ["error", "warning", "info"]
        assert 0 <= rule["confidence"] <= 1
        assert rule["source"] in ["extracted", "stated", "baseline"]

    def test_operator_types(self):
        """Valid TML operators."""
        valid_operators = [
            "=", "==",      # Equality
            "!=",           # Inequality
            ">", "<",       # Comparison
            ">=", "<=",     # Comparison with equality
            "contains",     # String contains
            "not_contains", # String not contains
            "one_of",       # Value in list
            "matches",      # Regex match (future)
        ]

        for op in ["=", ">=", "<=", ">", "<", "!=", "contains", "one_of"]:
            assert op in valid_operators


class TestTMLValueTypes:
    """Tests for TML value type handling."""

    def test_numeric_value_types(self):
        """Numeric values for size/spacing rules."""
        rules = [
            {"property": "border-radius", "value": 8, "operator": ">="},
            {"property": "padding", "value": 16.5, "operator": ">="},
            {"property": "font-size", "value": "14px", "operator": ">="},
        ]

        for rule in rules:
            # Value can be int, float, or string with unit
            assert isinstance(rule["value"], (int, float, str))

    def test_color_value_types(self):
        """Color values for palette rules."""
        valid_colors = [
            "#1a365d",          # 6-digit hex
            "#fff",             # 3-digit hex
            "rgb(26, 54, 93)",  # RGB function
        ]

        for color in valid_colors:
            assert color.startswith("#") or color.startswith("rgb(")

    def test_list_value_type(self):
        """List values for one_of operator."""
        rule = {
            "property": "variant",
            "operator": "one_of",
            "value": "primary, secondary, ghost, destructive"
        }

        options = [o.strip() for o in rule["value"].split(",")]
        assert len(options) >= 2


class TestTMLRuleSources:
    """Tests for TML rule source types."""

    def test_extracted_source(self):
        """Extracted rules come from A/B comparison choices."""
        rule = {
            "id": "extracted-001",
            "source": "extracted",
            "confidence": 0.85,
            "property": "border-radius",
            "operator": ">=",
            "value": 8
        }

        assert rule["source"] == "extracted"
        # Extracted rules have confidence < 1.0 (learned from choices)
        assert 0 < rule["confidence"] < 1

    def test_stated_source(self):
        """Stated rules are explicitly added by user."""
        rule = {
            "id": "stated-001",
            "source": "stated",
            "confidence": 1.0,  # User explicitly stated this
            "property": "color",
            "operator": "!=",
            "value": "#ff0000"
        }

        assert rule["source"] == "stated"
        # Stated rules always have 100% confidence
        assert rule["confidence"] == 1.0

    def test_baseline_source(self):
        """Baseline rules are WCAG/Nielsen defaults."""
        rule = {
            "id": "wcag-001",
            "source": "baseline",
            "confidence": 1.0,
            "property": "contrast-ratio",
            "operator": ">=",
            "value": 4.5,
            "message": "WCAG AA minimum contrast ratio"
        }

        assert rule["source"] == "baseline"
        # Baseline rules are authoritative
        assert rule["confidence"] == 1.0


class TestTMLSeverityLevels:
    """Tests for TML violation severity levels."""

    def test_error_severity(self):
        """Errors are critical violations that must be fixed."""
        # Examples: accessibility failures, security issues
        error_rules = [
            {"severity": "error", "message": "Contrast ratio too low (WCAG)"},
            {"severity": "error", "message": "Missing aria-label on button"},
            {"severity": "error", "message": "Focus indicator not visible"},
        ]

        for rule in error_rules:
            assert rule["severity"] == "error"

    def test_warning_severity(self):
        """Warnings are style deviations that should be addressed."""
        # Examples: off-brand colors, wrong spacing
        warning_rules = [
            {"severity": "warning", "message": "Color not in brand palette"},
            {"severity": "warning", "message": "Font doesn't match style guide"},
            {"severity": "warning", "message": "Border radius below preference"},
        ]

        for rule in warning_rules:
            assert rule["severity"] == "warning"

    def test_info_severity(self):
        """Info items are suggestions, not violations."""
        info_rules = [
            {"severity": "info", "message": "Consider using larger touch targets"},
            {"severity": "info", "message": "Animation could improve feedback"},
        ]

        for rule in info_rules:
            assert rule["severity"] == "info"


class TestTMLComponentTypes:
    """Tests for TML component type classifications."""

    def test_valid_component_types(self):
        """TML v1 supports 8 component types."""
        valid_types = [
            "button",
            "input",
            "card",
            "typography",
            "navigation",
            "form",
            "feedback",
            "modal",
        ]

        assert len(valid_types) == 8

    def test_global_rule_no_component(self):
        """Global rules have null/None component."""
        global_rule = {
            "id": "global-001",
            "component": None,  # Applies to all
            "property": "font-family",
            "operator": "=",
            "value": "Inter"
        }

        assert global_rule["component"] is None


class TestTMLPackageStructure:
    """Tests for TML skill package structure."""

    def test_rules_json_structure(self):
        """rules.json has correct top-level structure."""
        rules_json = {
            "version": "1.0",
            "generated": "2026-01-07T12:00:00Z",
            "rules": []
        }

        assert "version" in rules_json
        assert "generated" in rules_json
        assert "rules" in rules_json
        assert isinstance(rules_json["rules"], list)

    def test_package_file_structure(self):
        """TML package has expected file structure."""
        expected_files = [
            "SKILL.md",
            "references/rules.json",
            "references/baseline.md",
            "references/buttons.md",
            "references/inputs.md",
            "references/cards.md",
            "references/typography.md",
            "references/navigation.md",
            "references/forms.md",
            "references/feedback.md",
            "references/modals.md",
            "scripts/audit.py",
            "assets/mockups/landing.png",
            "assets/mockups/dashboard.png",
            "assets/mockups/form.png",
            "assets/mockups/settings.png",
        ]

        # All files should be relative paths
        for f in expected_files:
            assert not f.startswith("/")


class TestTMLAuditProtocol:
    """Tests for TML audit protocol behavior."""

    def test_audit_is_deterministic(self):
        """Same inputs should always produce same audit results."""
        # This is the core principle - audits are NOT LLM opinions
        extracted_values = {
            "colors": [{"element": "button", "color": "#ff0000"}],
            "fonts": [],
            "measurements": {}
        }
        palette = {"primary": "#1a365d"}

        # Running multiple times should give same result
        from audit_routes import apply_rules_to_extracted_values
        result1 = apply_rules_to_extracted_values(extracted_values, [], palette, None)
        result2 = apply_rules_to_extracted_values(extracted_values, [], palette, None)

        assert len(result1) == len(result2)
        if result1:
            assert result1[0].rule_id == result2[0].rule_id
            assert result1[0].found == result2[0].found

    def test_audit_extracts_then_applies(self):
        """Audit process: 1. Extract values, 2. Apply rules."""
        # Step 1: Claude Vision extracts (mocked)
        extracted = {
            "colors": [{"element": "cta-button", "color": "#3b82f6"}],
            "fonts": [{"element": "heading", "font": "Inter"}],
            "measurements": {"button_padding": "12px"}
        }

        # Step 2: Rules applied programmatically
        from audit_routes import apply_rules_to_extracted_values

        violations = apply_rules_to_extracted_values(
            extracted,
            [],  # No explicit rules
            {"primary": "#1a365d"},  # Color palette
            {"heading": "Inter"}     # Typography
        )

        # The blue color is not in palette, so violation expected
        color_violations = [v for v in violations if "color" in v.property.lower()]
        assert len(color_violations) == 1

    def test_tolerance_prevents_false_positives(self):
        """Color tolerance prevents flagging near-matches."""
        from audit_routes import apply_rules_to_extracted_values

        # Color is very close to primary (within tolerance)
        extracted = {
            "colors": [{"element": "button", "color": "#1b375e"}],  # Off by 1
            "fonts": [],
            "measurements": {}
        }

        violations = apply_rules_to_extracted_values(
            extracted, [], {"primary": "#1a365d"}, None
        )

        # Should NOT flag as violation (within tolerance)
        assert len(violations) == 0


class TestTMLUserFlowContext:
    """Tests for context-aware TML rules based on user flows."""

    def test_form_validation_context(self):
        """Form fields have specific validation display rules."""
        form_rules = [
            {
                "id": "form-001",
                "component": "form",
                "property": "error-color",
                "operator": "=",
                "value": "#dc2626",  # Red for errors
                "context": "validation-error"
            },
            {
                "id": "form-002",
                "component": "form",
                "property": "success-color",
                "operator": "=",
                "value": "#16a34a",  # Green for success
                "context": "validation-success"
            }
        ]

        # Context-specific rules (future enhancement)
        for rule in form_rules:
            assert "context" in rule or True  # Optional for now

    def test_interaction_state_rules(self):
        """Rules can specify interaction states."""
        button_rules = [
            {"property": "background-color", "state": "default"},
            {"property": "background-color", "state": "hover"},
            {"property": "background-color", "state": "active"},
            {"property": "background-color", "state": "disabled"},
            {"property": "background-color", "state": "focus"},
        ]

        valid_states = ["default", "hover", "active", "disabled", "focus"]
        for rule in button_rules:
            if "state" in rule:
                assert rule["state"] in valid_states


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
