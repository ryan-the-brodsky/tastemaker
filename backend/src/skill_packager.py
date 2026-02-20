"""
Skill packager for generating Agent Skills packages.
Creates downloadable ZIP files with SKILL.md and supporting files.
"""
import json
import os
import zipfile
import tempfile
from datetime import datetime
from typing import Dict, List, Any

from baseline_rules import get_baseline_rules, WCAG_RULES, NIELSEN_RULES


def generate_skill_package(
    session_name: str,
    username: str,
    rules: List[dict],
    include_baseline: bool = True,
    session_id: str = None,
    chosen_colors: dict = None,
    chosen_typography: dict = None
) -> str:
    """
    Generate a complete Agent Skills package as a ZIP file.

    Args:
        session_name: Name of the extraction session
        username: Username for package naming
        rules: List of extracted/stated rules
        include_baseline: Whether to include WCAG/Nielsen baseline rules
        session_id: Optional session ID for including mockup PNGs

    Returns:
        Path to generated ZIP file
    """
    # Create temp directory for package
    temp_dir = tempfile.mkdtemp()
    # Use session name (project name) for folder, not username
    safe_session_name = "".join(c if c.isalnum() or c in "- " else "" for c in session_name)
    package_name = f"tastemaker-{safe_session_name}".lower().replace(" ", "-")
    package_dir = os.path.join(temp_dir, package_name)
    os.makedirs(package_dir)
    os.makedirs(os.path.join(package_dir, "references"))
    os.makedirs(os.path.join(package_dir, "scripts"))
    os.makedirs(os.path.join(package_dir, "assets", "mockups"), exist_ok=True)

    # Generate files
    _generate_skill_md(package_dir, session_name, username, rules)
    _generate_rules_json(package_dir, rules, include_baseline)
    _generate_baseline_md(package_dir)
    _generate_component_docs(package_dir, rules)
    _generate_audit_script(package_dir)

    # Include mockup PNGs if available
    if session_id:
        _include_mockup_pngs(package_dir, session_id)

    # Generate palette.json if color/typography data available
    _generate_palette_json(package_dir, session_name, chosen_colors, chosen_typography)

    # Create ZIP
    zip_path = os.path.join(temp_dir, f"{package_name}.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, temp_dir)
                zf.write(file_path, arc_name)

    return zip_path


def _include_mockup_pngs(package_dir: str, session_id: str):
    """Include mockup PNGs in the package if they exist."""
    import shutil

    try:
        from mockup_generator import get_mockup_paths
        mockup_paths = get_mockup_paths(session_id)

        mockups_dest = os.path.join(package_dir, "assets", "mockups")

        for mockup_type, source_path in mockup_paths.items():
            if os.path.exists(source_path):
                dest_path = os.path.join(mockups_dest, f"{mockup_type}.png")
                shutil.copy2(source_path, dest_path)

    except ImportError:
        # mockup_generator not available
        pass
    except Exception as e:
        print(f"Warning: Could not include mockups: {e}")


def _generate_palette_json(package_dir: str, session_name: str, chosen_colors: dict = None, chosen_typography: dict = None):
    """Generate palette.json with structured color and typography data."""
    if not chosen_colors:
        return

    from color_utils import calculate_derived_colors

    # Colors may be nested under 'colors' key or flat on the object
    colors = chosen_colors.get('colors', {})
    if not colors:
        # Flat structure: {primary, secondary, accent, accentSoft, background, name, ...}
        color_keys = ('primary', 'secondary', 'accent', 'accentSoft', 'background')
        colors = {k: chosen_colors[k] for k in color_keys if k in chosen_colors}
    palette_name = chosen_colors.get('name', 'custom')
    palette_category = chosen_colors.get('category', 'custom')

    derived = calculate_derived_colors(colors) if all(
        k in colors for k in ('primary', 'secondary', 'accent', 'background')
    ) else {}

    palette_data = {
        "version": "1.0",
        "generated": datetime.now().isoformat(),
        "session": session_name,
        "palette": {
            "name": palette_name,
            "category": palette_category,
            "colors": colors,
            "derived": derived,
        },
    }

    if chosen_typography:
        palette_data["typography"] = {
            "heading": chosen_typography.get('heading', ''),
            "body": chosen_typography.get('body', ''),
            "style": chosen_typography.get('style', ''),
            "category": chosen_typography.get('category', ''),
        }

    with open(os.path.join(package_dir, "palette.json"), "w") as f:
        json.dump(palette_data, f, indent=2)


def _generate_skill_md(package_dir: str, session_name: str, username: str, rules: List[dict]):
    """Generate the main SKILL.md file."""
    # Get the folder name for the setup instructions
    safe_session_name = "".join(c if c.isalnum() or c in "- " else "" for c in session_name)
    folder_name = f"tastemaker-{safe_session_name}".lower().replace(" ", "-")

    content = f"""# TasteMaker Style Guide: {session_name}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Author:** {username}

---

## Quick Setup

To use this skill with Claude Code or other AI coding tools:

### Option 1: Project Root (Recommended)
```bash
# Copy this folder to your project root
cp -r {folder_name}/ /path/to/your/project/

# Add to your project's CLAUDE.md:
echo "\\n## Style Guide\\nSee ./{folder_name}/SKILL.md for UI/UX preferences." >> CLAUDE.md
```

### Option 2: Claude Code Skills Directory
```bash
# Copy to Claude Code's skills directory
cp -r {folder_name}/ ~/.claude/skills/
```

### How Claude Will Use This
When you ask Claude to build UI components, it will:
1. Reference the rules in `references/rules.json` for specific property values
2. Follow the component guidelines in `references/*.md` files
3. Respect the accessibility baseline in `references/baseline.md`
4. Use your preferred color palette, typography, and spacing

**Example prompt after setup:**
> "Build a signup form following my TasteMaker style preferences"

---

## Overview

This Agent Skill provides style rules and preferences extracted through TasteMaker's
A/B comparison process. Use these guidelines when making UI/UX decisions.

## Quick Reference

### Key Preferences

"""
    # Group rules by source and component
    extracted = [r for r in rules if r.get("source") == "extracted"]
    stated = [r for r in rules if r.get("source") == "stated"]

    if extracted:
        content += "#### Extracted Preferences (from A/B comparisons)\n\n"
        # Group by component for readability
        by_component: Dict[str, List[dict]] = {}
        for rule in extracted:
            comp = rule.get("component_type", "general")
            by_component.setdefault(comp, []).append(rule)

        component_labels = {
            "button": "Button", "input": "Input", "card": "Card",
            "typography": "Typography", "navigation": "Navigation",
            "form": "Form", "modal": "Modal", "feedback": "Feedback",
            "table": "Table", "badge": "Badge", "tabs": "Tabs",
            "toggle": "Toggle",
        }

        for comp, comp_rules in by_component.items():
            label = component_labels.get(comp, comp.title())
            content += f"**{label}**\n"
            for rule in comp_rules:
                confidence = rule.get("confidence", 0)
                content += f"- `{rule.get('property')}`: {rule.get('value', '')} "
                content += f"({confidence:.0%})\n"
            content += "\n"

    if stated:
        content += "#### Stated Preferences (explicit rules)\n\n"
        for rule in stated:
            content += f"- {rule.get('message', rule.get('property'))}\n"
        content += "\n"

    content += """## How to Use

1. **Reference these rules** when implementing UI components
2. **Check rules.json** for programmatic access to all rules
3. **Review component-specific files** in the `references/` directory
4. **Run audit.py** to check your code against these rules (v1.5)

## Reference Files

See the `references/` folder for detailed guidelines:

### Global & Baseline
- `global.md` - Rules that apply to all components
- `baseline.md` - WCAG accessibility & Nielsen usability rules
- `rules.json` - Machine-readable rule set for programmatic access

### Component-Specific
- `buttons.md` - Button styling rules
- `inputs.md` - Form input rules
- `cards.md` - Card component rules
- `typography.md` - Typography rules
- `navigation.md` - Navigation patterns
- `forms.md` - Form layout rules
- `feedback.md` - Feedback/notification rules
- `modals.md` - Modal/dialog rules
- `tables.md` - Table component rules
- `badges.md` - Badge component rules
- `tabs.md` - Tabs component rules
- `toggles.md` - Toggle/switch component rules

---

*Generated by TasteMaker*
"""
    with open(os.path.join(package_dir, "SKILL.md"), "w") as f:
        f.write(content)


def _generate_rules_json(package_dir: str, rules: List[dict], include_baseline: bool):
    """Generate the rules.json file."""
    all_rules = []
    seen_ids = set()

    # Add user rules (deduplicate by rule ID)
    for rule in rules:
        rule_id = rule.get("rule_id", "")
        if rule_id in seen_ids:
            continue
        seen_ids.add(rule_id)
        all_rules.append({
            "id": rule_id,
            "component": rule.get("component_type"),
            "property": rule.get("property", ""),
            "operator": rule.get("operator", "="),
            "value": json.loads(rule.get("value", "null")) if isinstance(rule.get("value"), str) else rule.get("value"),
            "severity": rule.get("severity", "warning"),
            "confidence": rule.get("confidence"),
            "source": rule.get("source", "extracted"),
            "message": rule.get("message", "")
        })

    # Add baseline rules if requested
    if include_baseline:
        for rule in get_baseline_rules():
            all_rules.append({
                "id": rule["id"],
                "component": rule.get("component_type"),
                "property": rule["property"],
                "operator": rule["operator"],
                "value": rule["value"],
                "severity": rule["severity"],
                "confidence": 1.0,
                "source": "baseline",
                "message": rule["message"]
            })

    output = {
        "version": "1.0",
        "generated": datetime.now().isoformat(),
        "rules": all_rules
    }

    with open(os.path.join(package_dir, "references", "rules.json"), "w") as f:
        json.dump(output, f, indent=2)


def _generate_baseline_md(package_dir: str):
    """Generate the baseline.md file."""
    content = """# Accessibility & Usability Baseline

This file contains baseline rules for WCAG accessibility and Nielsen usability heuristics.
These rules apply to all components unless explicitly overridden.

## WCAG Accessibility Rules

"""
    for rule in WCAG_RULES:
        content += f"### {rule['id']}: {rule['property']}\n"
        content += f"- **Requirement:** {rule['operator']} {rule['value']}\n"
        content += f"- **Severity:** {rule['severity']}\n"
        content += f"- **Message:** {rule['message']}\n\n"

    content += """## Nielsen Usability Heuristics

"""
    for rule in NIELSEN_RULES:
        content += f"### {rule['id']}: {rule['property']}\n"
        content += f"- **Requirement:** {rule['operator']} {rule['value']}\n"
        content += f"- **Severity:** {rule['severity']}\n"
        content += f"- **Message:** {rule['message']}\n\n"

    with open(os.path.join(package_dir, "references", "baseline.md"), "w") as f:
        f.write(content)


def _generate_component_docs(package_dir: str, rules: List[dict]):
    """Generate component-specific documentation files."""
    components = {
        "button": "buttons.md",
        "input": "inputs.md",
        "card": "cards.md",
        "typography": "typography.md",
        "navigation": "navigation.md",
        "form": "forms.md",
        "feedback": "feedback.md",
        "modal": "modals.md",
        "table": "tables.md",
        "badge": "badges.md",
        "tabs": "tabs.md",
        "toggle": "toggles.md",
    }

    # Group rules by component - only include rules specific to each component
    component_rules = {comp: [] for comp in components}
    global_rules = []

    for rule in rules:
        comp = rule.get("component_type")
        if comp and comp in component_rules:
            component_rules[comp].append(rule)
        else:
            global_rules.append(rule)

    # Generate component-specific files (without global rules repeated)
    for component, filename in components.items():
        rules_for_comp = component_rules.get(component, [])

        content = f"# {component.title()} Component Guidelines\n\n"
        content += f"Style rules specific to {component} components.\n\n"

        if rules_for_comp:
            content += "## Component-Specific Rules\n\n"
            for rule in rules_for_comp:
                content += f"### {rule.get('rule_id', 'Rule')}\n"
                content += f"- **Property:** {rule.get('property')}\n"
                content += f"- **Requirement:** {rule.get('operator')} `{rule.get('value')}`\n"
                content += f"- **Severity:** {rule.get('severity')}\n"
                if rule.get('confidence'):
                    content += f"- **Confidence:** {rule.get('confidence'):.0%}\n"
                if rule.get('message'):
                    content += f"- **Note:** {rule.get('message')}\n"
                content += "\n"
        else:
            content += "*No component-specific rules extracted.*\n\n"

        content += "---\n\n"
        content += "**Note:** Also apply global rules from `rules.json` and baseline rules from `baseline.md`.\n"

        with open(os.path.join(package_dir, "references", filename), "w") as f:
            f.write(content)

    # Always generate global.md (referenced in SKILL.md)
    content = "# Global Style Rules\n\n"
    content += "These rules apply to all components unless overridden by component-specific rules.\n\n"
    if global_rules:
        content += "## Rules\n\n"
        for rule in global_rules:
            content += f"### {rule.get('rule_id', 'Rule')}\n"
            content += f"- **Property:** {rule.get('property')}\n"
            content += f"- **Requirement:** {rule.get('operator')} `{rule.get('value')}`\n"
            content += f"- **Severity:** {rule.get('severity')}\n"
            if rule.get('confidence'):
                content += f"- **Confidence:** {rule.get('confidence'):.0%}\n"
            if rule.get('message'):
                content += f"- **Note:** {rule.get('message')}\n"
            content += "\n"
    else:
        content += "*No global rules extracted. All rules are component-specific.*\n\n"
        content += "See `baseline.md` for WCAG and Nielsen baseline rules that apply globally.\n"

    with open(os.path.join(package_dir, "references", "global.md"), "w") as f:
        f.write(content)


def _generate_audit_script(package_dir: str):
    """Generate functional audit script."""
    content = '''#!/usr/bin/env python3
"""
TasteMaker Style Audit Script v1.5

Analyzes files or screenshots against your extracted style rules.

Usage:
    python audit.py --screenshot <path>   Analyze a screenshot image
    python audit.py --url <url>           Analyze a live URL (requires browser)
    python audit.py --css <path>          Analyze CSS/SCSS files
    python audit.py --help                Show this help message

Examples:
    python audit.py --screenshot ./my-app.png
    python audit.py --css ./src/styles/
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Any

# Color codes for terminal output
class Colors:
    RED = '\\033[91m'
    YELLOW = '\\033[93m'
    GREEN = '\\033[92m'
    BLUE = '\\033[94m'
    RESET = '\\033[0m'
    BOLD = '\\033[1m'


def load_rules() -> Dict[str, Any]:
    """Load rules from rules.json."""
    script_dir = Path(__file__).parent
    rules_path = script_dir.parent / "references" / "rules.json"

    if not rules_path.exists():
        print(f"{Colors.RED}Error: rules.json not found at {rules_path}{Colors.RESET}")
        sys.exit(1)

    with open(rules_path) as f:
        return json.load(f)


def parse_css_value(value: str) -> tuple:
    """Parse a CSS value into (number, unit)."""
    match = re.match(r'^([\\d.]+)(px|rem|em|%)?$', str(value).strip())
    if match:
        return float(match.group(1)), match.group(2) or ''
    return value, ''


def check_rule(rule: Dict, actual_value: Any) -> Dict:
    """Check if an actual value satisfies a rule."""
    expected = rule.get('value')
    operator = rule.get('operator', '=')

    # Parse values for numeric comparison
    actual_num, actual_unit = parse_css_value(actual_value)
    expected_num, expected_unit = parse_css_value(expected)

    passed = False

    if operator == '=' or operator == '==':
        passed = str(actual_value) == str(expected)
    elif operator == '!=':
        passed = str(actual_value) != str(expected)
    elif operator == '>=' and isinstance(actual_num, (int, float)) and isinstance(expected_num, (int, float)):
        passed = actual_num >= expected_num
    elif operator == '<=' and isinstance(actual_num, (int, float)) and isinstance(expected_num, (int, float)):
        passed = actual_num <= expected_num
    elif operator == '>' and isinstance(actual_num, (int, float)) and isinstance(expected_num, (int, float)):
        passed = actual_num > expected_num
    elif operator == '<' and isinstance(actual_num, (int, float)) and isinstance(expected_num, (int, float)):
        passed = actual_num < expected_num
    elif operator == 'contains':
        passed = str(expected).lower() in str(actual_value).lower()
    elif operator == 'not_contains':
        passed = str(expected).lower() not in str(actual_value).lower()

    return {
        'rule_id': rule.get('id'),
        'property': rule.get('property'),
        'expected': f"{operator} {expected}",
        'actual': actual_value,
        'passed': passed,
        'severity': rule.get('severity', 'warning'),
        'message': rule.get('message', '')
    }


def extract_css_properties(css_content: str) -> Dict[str, List[str]]:
    """Extract CSS property values from CSS content."""
    properties = {}

    # Find all property: value pairs
    pattern = r'([a-z-]+)\\s*:\\s*([^;]+);'
    matches = re.findall(pattern, css_content, re.IGNORECASE)

    for prop, value in matches:
        prop = prop.strip().lower()
        value = value.strip()
        if prop not in properties:
            properties[prop] = []
        properties[prop].append(value)

    return properties


def audit_css_files(path: str, rules: List[Dict]) -> List[Dict]:
    """Audit CSS/SCSS files against rules."""
    violations = []
    path = Path(path)

    if path.is_file():
        files = [path]
    else:
        files = list(path.glob('**/*.css')) + list(path.glob('**/*.scss'))

    for file_path in files:
        with open(file_path) as f:
            content = f.read()

        properties = extract_css_properties(content)

        for rule in rules:
            prop = rule.get('property', '').replace('_', '-')
            if prop in properties:
                for value in properties[prop]:
                    result = check_rule(rule, value)
                    if not result['passed']:
                        result['file'] = str(file_path)
                        violations.append(result)

    return violations


def audit_screenshot(image_path: str, rules: List[Dict]) -> List[Dict]:
    """
    Audit a screenshot against rules.
    Note: Full image analysis requires Claude Vision API.
    This provides basic file validation.
    """
    if not os.path.exists(image_path):
        print(f"{Colors.RED}Error: Image not found: {image_path}{Colors.RESET}")
        return []

    print(f"\\n{Colors.BLUE}Screenshot Analysis{Colors.RESET}")
    print("-" * 40)
    print(f"Image: {image_path}")
    print(f"Rules to check: {len(rules)}")
    print()
    print(f"{Colors.YELLOW}Note: Full screenshot analysis requires the TasteMaker web app")
    print(f"or Claude Vision API integration.{Colors.RESET}")
    print()
    print("To analyze this screenshot with full AI-powered detection:")
    print("1. Use the TasteMaker web app audit feature")
    print("2. Upload your screenshot")
    print("3. Select your style profile")
    print()

    return []


def audit_url(url: str, rules: List[Dict]) -> List[Dict]:
    """
    Audit a live URL against rules.
    Note: Full URL analysis requires headless browser.
    """
    print(f"\\n{Colors.BLUE}URL Analysis{Colors.RESET}")
    print("-" * 40)
    print(f"URL: {url}")
    print(f"Rules to check: {len(rules)}")
    print()
    print(f"{Colors.YELLOW}Note: Full URL analysis requires headless browser integration.{Colors.RESET}")
    print()
    print("To analyze this URL:")
    print("1. Take a screenshot of the page")
    print("2. Run: python audit.py --screenshot screenshot.png")
    print()

    return []


def print_violations(violations: List[Dict]):
    """Print violations in a formatted way."""
    if not violations:
        print(f"\\n{Colors.GREEN}No violations found!{Colors.RESET}")
        return

    errors = [v for v in violations if v['severity'] == 'error']
    warnings = [v for v in violations if v['severity'] == 'warning']
    infos = [v for v in violations if v['severity'] == 'info']

    print(f"\\n{Colors.BOLD}Audit Results{Colors.RESET}")
    print("=" * 50)

    if errors:
        print(f"\\n{Colors.RED}Errors ({len(errors)}){Colors.RESET}")
        for v in errors:
            print(f"  [{v['rule_id']}] {v['property']}")
            print(f"    Expected: {v['expected']}")
            print(f"    Found: {v['actual']}")
            if v.get('file'):
                print(f"    File: {v['file']}")
            if v['message']:
                print(f"    {v['message']}")

    if warnings:
        print(f"\\n{Colors.YELLOW}Warnings ({len(warnings)}){Colors.RESET}")
        for v in warnings:
            print(f"  [{v['rule_id']}] {v['property']}")
            print(f"    Expected: {v['expected']}, Found: {v['actual']}")

    if infos:
        print(f"\\n{Colors.BLUE}Info ({len(infos)}){Colors.RESET}")
        for v in infos:
            print(f"  [{v['rule_id']}] {v['message']}")

    total = len(violations)
    print(f"\\n{Colors.BOLD}Summary:{Colors.RESET} {total} violation(s) found")
    print(f"  {Colors.RED}{len(errors)} error(s){Colors.RESET}")
    print(f"  {Colors.YELLOW}{len(warnings)} warning(s){Colors.RESET}")
    print(f"  {Colors.BLUE}{len(infos)} info(s){Colors.RESET}")


def main():
    parser = argparse.ArgumentParser(
        description='TasteMaker Style Audit Script v1.5',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --screenshot ./app-screenshot.png
  %(prog)s --css ./src/styles/
  %(prog)s --url https://myapp.com
        """
    )
    parser.add_argument('--screenshot', help='Path to screenshot image')
    parser.add_argument('--url', help='URL to audit')
    parser.add_argument('--css', help='Path to CSS/SCSS files or directory')
    parser.add_argument('--json', action='store_true', help='Output results as JSON')

    args = parser.parse_args()

    if not any([args.screenshot, args.url, args.css]):
        parser.print_help()
        print(f"\\n{Colors.YELLOW}Tip: Use --screenshot, --url, or --css to specify what to audit{Colors.RESET}")
        sys.exit(0)

    # Load rules
    data = load_rules()
    rules = data.get('rules', [])
    print(f"{Colors.GREEN}Loaded {len(rules)} style rules{Colors.RESET}")

    violations = []

    if args.screenshot:
        violations = audit_screenshot(args.screenshot, rules)
    elif args.url:
        violations = audit_url(args.url, rules)
    elif args.css:
        violations = audit_css_files(args.css, rules)

    if args.json:
        print(json.dumps(violations, indent=2))
    else:
        print_violations(violations)

    # Exit with error code if violations found
    sys.exit(1 if violations else 0)


if __name__ == "__main__":
    main()
'''
    with open(os.path.join(package_dir, "scripts", "audit.py"), "w") as f:
        f.write(content)


def get_skill_preview(rules: List[dict], session_id: str = None) -> dict:
    """
    Generate a preview of what the skill package will contain.
    """
    extracted = [r for r in rules if r.get("source") == "extracted"]
    stated = [r for r in rules if r.get("source") == "stated"]
    baseline_count = len(get_baseline_rules())

    # Get component coverage
    components_covered = set()
    for rule in rules:
        if rule.get("component_type"):
            components_covered.add(rule["component_type"])

    files_included = [
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
        "references/tables.md",
        "references/badges.md",
        "references/tabs.md",
        "references/toggles.md",
        "scripts/audit.py"
    ]

    # Check for mockups
    mockups_available = []
    if session_id:
        try:
            from mockup_generator import get_mockup_paths
            mockup_paths = get_mockup_paths(session_id)
            for mockup_type in mockup_paths:
                files_included.append(f"assets/mockups/{mockup_type}.png")
                mockups_available.append(mockup_type)
        except ImportError:
            pass

    return {
        "total_rules": len(rules) + baseline_count,
        "extracted_rules": len(extracted),
        "stated_rules": len(stated),
        "baseline_rules": baseline_count,
        "components_covered": list(components_covered),
        "files_included": files_included,
        "mockups_available": mockups_available
    }
