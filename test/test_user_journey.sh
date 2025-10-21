#!/bin/bash
# test_user_journey.sh - End-to-end user journey test

set -e

API_URL="${API_URL:-https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com}"
USER_ID="e2e-test-$(date +%s)"

echo "=========================================="
echo "Testing Complete User Journey"
echo "=========================================="
echo "User ID: $USER_ID"
echo ""

# Step 1: User onboarding (simulated)
echo "Step 1: User Onboarding"
echo "-----------------------"
echo "✓ User signs up (simulated)"
echo "✓ Completes personality assessment"
echo ""

# Step 2: First mood log
echo "Step 2: First Mood Log"
echo "----------------------"
curl -s -X POST "$API_URL/mood" \
  -H "Content-Type: application/json" \
  -d "{\"userId\":\"$USER_ID\",\"mood\":7,\"tags\":[\"happy\"],\"notes\":\"First day with Mind Mate!\"}" | jq '.'
echo ""

# Step 3: Chat interaction
echo "Step 3: Chat Interaction"
echo "------------------------"
curl -s -X POST "$API_URL/chat" \
  -H "Content-Type: application/json" \
  -d "{\"userId\":\"$USER_ID\",\"message\":\"Hello! I'm new here.\"}" | jq '.reply'
echo ""

# Step 4: Multiple mood logs over time
echo "Step 4: Logging 7 Days of Moods"
echo "--------------------------------"
for day in {1..7}; do
  mood=$((5 + RANDOM % 4))
  echo "Day $day: Mood $mood"
  curl -s -X POST "$API_URL/mood" \
    -H "Content-Type: application/json" \
    -d "{\"userId\":\"$USER_ID\",\"mood\":$mood,\"notes\":\"Day $day\"}" > /dev/null
  sleep 1
done
echo ""

# Step 5: Check chat history
echo "Step 5: Retrieve Chat History"
echo "------------------------------"
aws lambda invoke \
  --function-name getChatHistory \
  --payload "{\"userId\":\"$USER_ID\"}" \
  history.json > /dev/null
cat history.json | jq '.messages | length'
echo ""

# Step 6: Calculate risk score
echo "Step 6: Risk Assessment"
echo "-----------------------"
curl -s -X GET "$API_URL/risk-score?userId=$USER_ID" | jq '.'
echo ""

echo "=========================================="
echo "✓ User Journey Test Complete"
echo "=========================================="

# Cleanup
rm -f history.json
