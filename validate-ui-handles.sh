#!/bin/bash
# Validate Agent Handles in Frontend

echo "=== Validating Agent Handles ==="

# Get script directory and use relative path
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_SRC="${SCRIPT_DIR}/frontend/src"
PASS_COUNT=0
FAIL_COUNT=0

check_handle() {
    local handle=$1
    local description=$2
    if grep -r "agent-handle=\"${handle}\"" "$FRONTEND_SRC" > /dev/null 2>&1; then
        echo "PASS: $description ($handle)"
        ((PASS_COUNT++))
    else
        echo "FAIL: $description ($handle)"
        ((FAIL_COUNT++))
    fi
}

# Landing page
check_handle "landing-hero-button-getstarted" "Get Started button"
check_handle "landing-hero-button-login" "Login button"

# Auth pages
check_handle "auth-login-input-email" "Login email input"
check_handle "auth-login-input-password" "Login password input"
check_handle "auth-login-button-submit" "Login submit button"
check_handle "auth-register-input-email" "Register email input"
check_handle "auth-register-input-password" "Register password input"
check_handle "auth-register-input-confirmpassword" "Register confirm password"
check_handle "auth-register-input-firstname" "Register first name"
check_handle "auth-register-input-lastname" "Register last name"
check_handle "auth-register-button-submit" "Register submit button"

# Dashboard
check_handle "dashboard-sessions-button-create" "Create session button"

# Extraction flow
check_handle "extraction-comparison-option-a" "Option A"
check_handle "extraction-comparison-option-b" "Option B"
check_handle "extraction-comparison-button-nopreference" "No preference button"
check_handle "extraction-progress-indicator" "Progress indicator"

# Rule review
check_handle "review-rules-input-newrule" "New rule input"
check_handle "review-rules-button-addrule" "Add rule button"
check_handle "review-rules-button-generate" "Generate skill button"

# Skill download
check_handle "skill-download-button-zip" "Download button"
check_handle "skill-preview-content" "Preview content"

echo ""
echo "=== Handle Validation Complete ==="
echo "Passed: $PASS_COUNT"
echo "Failed: $FAIL_COUNT"

if [ $FAIL_COUNT -gt 0 ]; then
    exit 1
fi
