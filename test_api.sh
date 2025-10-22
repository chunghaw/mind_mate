#!/bin/bash

API_BASE="https://h8iyzk1h3k.execute-api.us-east-1.amazonaws.com"
TEST_USER_ID="test-user-$(date +%s)"

echo "🧪 Testing Mind Mate API with User ID: $TEST_USER_ID"
echo ""

# Step 1: Send concerning messages
echo "📝 Step 1: Sending concerning messages..."

MESSAGES=(
    "I feel hopeless today"
    "I don't see the point in anything anymore"
    "Sometimes I wish I could just disappear"
)

for message in "${MESSAGES[@]}"; do
    echo "Sending: '$message'"
    
    response=$(curl -s -X POST "$API_BASE/agent-chat" \
        -H "Content-Type: application/json" \
        -d "{\"userId\": \"$TEST_USER_ID\", \"message\": \"$message\", \"sessionId\": \"$TEST_USER_ID-test\"}" \
        -w "HTTP_STATUS:%{http_code}")
    
    http_status=$(echo "$response" | grep -o "HTTP_STATUS:[0-9]*" | cut -d: -f2)
    response_body=$(echo "$response" | sed 's/HTTP_STATUS:[0-9]*$//')
    
    if [ "$http_status" = "200" ]; then
        echo "✅ Message sent successfully"
    else
        echo "❌ Failed to send message (HTTP $http_status)"
        echo "Response: $response_body"
    fi
    
    sleep 1
done

echo ""
echo "🔍 Step 2: Calculating risk score..."

risk_response=$(curl -s -X POST "$API_BASE/calculate-risk" \
    -H "Content-Type: application/json" \
    -d "{\"userId\": \"$TEST_USER_ID\"}" \
    -w "HTTP_STATUS:%{http_code}")

http_status=$(echo "$risk_response" | grep -o "HTTP_STATUS:[0-9]*" | cut -d: -f2)
response_body=$(echo "$risk_response" | sed 's/HTTP_STATUS:[0-9]*$//')

echo "HTTP Status: $http_status"
echo "Response:"
echo "$response_body" | jq . 2>/dev/null || echo "$response_body"

echo ""
echo "🏁 Test completed for user: $TEST_USER_ID"