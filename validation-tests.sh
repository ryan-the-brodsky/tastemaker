#!/bin/bash
# TasteMaker Validation Tests

set -e

BASE_URL="http://localhost:8000"
TOKEN=""
SESSION_ID=""
COMP_ID=""

echo "=== TasteMaker Validation Tests ==="

# 1. Health check
echo "1. Health check..."
HEALTH=$(curl -sf ${BASE_URL}/health 2>/dev/null || echo '{"status":"fail"}')
if echo "$HEALTH" | grep -q "ok"; then
    echo "   PASS"
else
    echo "   FAIL - Backend not running"
    exit 1
fi

# 2. Register user
echo "2. Register user..."
REGISTER_RESP=$(curl -sf -X POST ${BASE_URL}/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@tastemaker.dev","password":"testpass123","first_name":"Test","last_name":"User"}' 2>/dev/null || echo '{}')
TOKEN=$(echo $REGISTER_RESP | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
if [ -n "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
    echo "   PASS"
else
    # Try login in case user already exists
    echo "   User may exist, trying login..."
fi

# 3. Login
echo "3. Login..."
LOGIN_RESP=$(curl -sf -X POST ${BASE_URL}/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@tastemaker.dev","password":"testpass123"}' 2>/dev/null || echo '{}')
TOKEN=$(echo $LOGIN_RESP | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
if [ -n "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
    echo "   PASS"
else
    echo "   FAIL - Could not authenticate"
    exit 1
fi

# 4. Create session
echo "4. Create session..."
SESSION_RESP=$(curl -sf -X POST ${BASE_URL}/api/sessions \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Profile"}' 2>/dev/null || echo '{}')
SESSION_ID=$(echo $SESSION_RESP | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
if [ -n "$SESSION_ID" ] && [ "$SESSION_ID" != "null" ]; then
    echo "   PASS (session_id: $SESSION_ID)"
else
    echo "   FAIL - Could not create session"
    exit 1
fi

# 5. Get comparison
echo "5. Get comparison..."
COMP_RESP=$(curl -sf -X GET "${BASE_URL}/api/sessions/${SESSION_ID}/comparison" \
  -H "Authorization: Bearer ${TOKEN}" 2>/dev/null || echo '{}')
COMP_ID=$(echo $COMP_RESP | grep -o '"comparison_id":[0-9]*' | cut -d':' -f2)
if [ -n "$COMP_ID" ] && [ "$COMP_ID" != "null" ]; then
    echo "   PASS (comparison_id: $COMP_ID)"
else
    echo "   FAIL - Could not get comparison"
    exit 1
fi

# 6. Submit choice
echo "6. Submit choice..."
CHOICE_RESP=$(curl -sf -X POST "${BASE_URL}/api/sessions/${SESSION_ID}/comparison/${COMP_ID}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"choice":"a","decision_time_ms":2000}' 2>/dev/null || echo '{}')
if echo "$CHOICE_RESP" | grep -q "comparison_count"; then
    echo "   PASS"
else
    echo "   FAIL - Could not submit choice"
    exit 1
fi

# 7. Add stated rule
echo "7. Add stated rule..."
RULE_RESP=$(curl -sf -X POST "${BASE_URL}/api/sessions/${SESSION_ID}/rules" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"statement":"never use gradients"}' 2>/dev/null || echo '{}')
if echo "$RULE_RESP" | grep -q "rule_id"; then
    echo "   PASS"
else
    echo "   FAIL - Could not add rule"
    exit 1
fi

# 8. Get rules
echo "8. Get rules..."
RULES_RESP=$(curl -sf -X GET "${BASE_URL}/api/sessions/${SESSION_ID}/rules" \
  -H "Authorization: Bearer ${TOKEN}" 2>/dev/null || echo '[]')
RULE_COUNT=$(echo "$RULES_RESP" | grep -o '"rule_id"' | wc -l)
if [ "$RULE_COUNT" -gt 0 ]; then
    echo "   PASS (${RULE_COUNT} rules)"
else
    echo "   FAIL - No rules found"
    exit 1
fi

echo ""
echo "=== All Backend Validation Tests Passed! ==="
