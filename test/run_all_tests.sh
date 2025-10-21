#!/bin/bash
# run_all_tests.sh - Comprehensive test suite for Mind Mate

set -e

# Configuration
API_URL="${API_URL:-https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com}"
TEST_USER="test-$(date +%s)"
PASSED=0
FAILED=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Mind Mate - Automated Test Suite"
echo "=========================================="
echo "Test User: $TEST_USER"
echo "API URL: $API_URL"
echo ""

# Helper functions
pass() {
  echo -e "${GREEN}✓ PASS${NC} $1"
  ((PASSED++))
}

fail() {
  echo -e "${RED}✗ FAIL${NC} $1"
  ((FAILED++))
}

warn() {
  echo -e "${YELLOW}⚠ WARN${NC} $1"
}

# Test 1: Lambda Functions
echo "Test 1: Lambda Functions"
echo "------------------------"

test_lambda() {
  local FUNCTION=$1
  local PAYLOAD=$2
  
  echo -n "  Testing $FUNCTION... "
  if aws lambda invoke \
    --function-name "$FUNCTION" \
    --payload "$PAYLOAD" \
    response.json > /dev/null 2>&1; then
    pass ""
  else
    fail ""
  fi
}

test_lambda "logMood" "{\"body\":\"{\\\"userId\\\":\\\"$TEST_USER\\\",\\\"mood\\\":7}\"}"
test_lambda "chat" "{\"body\":\"{\\\"userId\\\":\\\"$TEST_USER\\\",\\\"message\\\":\\\"Hello\\\"}\"}"
test_lambda "getChatHistory" "{\"userId\":\"$TEST_USER\"}"
test_lambda "calculateRiskScore" "{\"userId\":\"$TEST_USER\"}"

echo ""

# Test 2: API Endpoints
echo "Test 2: API Endpoints"
echo "---------------------"

test_api() {
  local ENDPOINT=$1
  local METHOD=$2
  local DATA=$3
  
  echo -n "  Testing $METHOD $ENDPOINT... "
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    -X "$METHOD" "$API_URL$ENDPOINT" \
    -H "Content-Type: application/json" \
    -d "$DATA")
  
  if [ "$HTTP_CODE" = "200" ]; then
    pass "(HTTP $HTTP_CODE)"
  else
    fail "(HTTP $HTTP_CODE)"
  fi
}

test_api "/mood" "POST" "{\"userId\":\"$TEST_USER\",\"mood\":7,\"notes\":\"Test\"}"
test_api "/chat" "POST" "{\"userId\":\"$TEST_USER\",\"message\":\"Test message\"}"

echo ""

# Test 3: Data Persistence
echo "Test 3: Data Persistence"
echo "------------------------"

echo -n "  Checking DynamoDB... "
sleep 2  # Wait for data to be written
ITEM_COUNT=$(aws dynamodb query \
  --table-name EmoCompanion \
  --key-condition-expression "PK = :pk" \
  --expression-attribute-values "{\":pk\":{\"S\":\"USER#$TEST_USER\"}}" \
  --select COUNT \
  --output text \
  --query 'Count' 2>/dev/null || echo "0")

if [ "$ITEM_COUNT" -gt 0 ]; then
  pass "($ITEM_COUNT items)"
else
  fail "(no items found)"
fi

echo ""

# Test 4: ML Pipeline
echo "Test 4: ML Pipeline"
echo "-------------------"

# Create test data
echo "  Creating test data (7 days)..."
for i in {1..7}; do
  aws lambda invoke \
    --function-name logMood \
    --payload "{\"body\":\"{\\\"userId\\\":\\\"$TEST_USER\\\",\\\"mood\\\":$((5 + RANDOM % 3))}\"}" \
    /dev/null 2>&1
  sleep 1
done

echo -n "  Extracting mood features... "
if aws lambda invoke \
  --function-name extractMoodFeatures \
  --payload "{\"userId\":\"$TEST_USER\",\"days\":7}" \
  features.json > /dev/null 2>&1; then
  pass ""
else
  fail ""
fi

echo -n "  Extracting behavioral features... "
if aws lambda invoke \
  --function-name extractBehavioralFeatures \
  --payload "{\"userId\":\"$TEST_USER\",\"days\":7}" \
  behavioral.json > /dev/null 2>&1; then
  pass ""
else
  fail ""
fi

echo -n "  Calculating risk score... "
if aws lambda invoke \
  --function-name calculateRiskScore \
  --payload "{\"userId\":\"$TEST_USER\"}" \
  risk.json > /dev/null 2>&1; then
  RISK_LEVEL=$(cat risk.json | jq -r '.risk_level' 2>/dev/null || echo "UNKNOWN")
  pass "(Risk: $RISK_LEVEL)"
else
  fail ""
fi

echo ""

# Test 5: Performance
echo "Test 5: Performance"
echo "-------------------"

echo -n "  API response time... "
START=$(date +%s%N)
curl -s -X POST "$API_URL/mood" \
  -H "Content-Type: application/json" \
  -d "{\"userId\":\"$TEST_USER\",\"mood\":7}" > /dev/null 2>&1
END=$(date +%s%N)
DURATION=$(( (END - START) / 1000000 ))

if [ "$DURATION" -lt 3000 ]; then
  pass "(${DURATION}ms)"
elif [ "$DURATION" -lt 5000 ]; then
  warn "(${DURATION}ms - acceptable)"
else
  fail "(${DURATION}ms - too slow)"
fi

echo ""

# Cleanup
echo "Cleanup"
echo "-------"
echo "  Removing test files..."
rm -f response.json features.json behavioral.json risk.json

echo ""
echo "=========================================="
echo "Test Suite Complete"
echo "=========================================="
echo -e "Results: ${GREEN}$PASSED passed${NC}, ${RED}$FAILED failed${NC}"
echo "=========================================="

# Exit with error if any tests failed
if [ "$FAILED" -gt 0 ]; then
  exit 1
fi
