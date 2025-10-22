#!/bin/bash

# Add test chat data using AWS CLI
TEST_USER_ID="test-user-with-data"
TABLE_NAME="EmoCompanion"

echo "🧪 Adding test chat data for user: $TEST_USER_ID"

# Function to add a chat message
add_chat_message() {
    local user_message="$1"
    local ai_response="$2"
    local hours_ago="$3"
    
    # Calculate timestamp (hours ago)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        timestamp=$(date -u -v-${hours_ago}H +"%Y-%m-%dT%H:%M:%S.000Z")
    else
        # Linux
        timestamp=$(date -u -d "${hours_ago} hours ago" +"%Y-%m-%dT%H:%M:%S.000Z")
    fi
    
    echo "Adding message: '$user_message' (${hours_ago}h ago)"
    
    aws dynamodb put-item \
        --table-name "$TABLE_NAME" \
        --item "{
            \"PK\": {\"S\": \"USER#${TEST_USER_ID}\"},
            \"SK\": {\"S\": \"CHAT#${timestamp}\"},
            \"type\": {\"S\": \"CHAT\"},
            \"userId\": {\"S\": \"${TEST_USER_ID}\"},
            \"userMessage\": {\"S\": \"${user_message}\"},
            \"aiResponse\": {\"S\": \"${ai_response}\"},
            \"sessionId\": {\"S\": \"${TEST_USER_ID}-test\"},
            \"timestamp\": {\"S\": \"${timestamp}\"},
            \"source\": {\"S\": \"test-data\"}
        }" > /dev/null
    
    if [ $? -eq 0 ]; then
        echo "✅ Added successfully"
    else
        echo "❌ Failed to add"
    fi
}

# Add test messages with concerning content
add_chat_message "I feel hopeless today" "I hear that you're feeling hopeless right now. That sounds really difficult." 48
add_chat_message "I don't see the point in anything anymore" "It sounds like you're going through a really tough time. Your feelings are valid." 36
add_chat_message "Sometimes I wish I could just disappear" "I'm concerned about you. It sounds like you're in a lot of pain right now." 24
add_chat_message "wanna die" "I'm very worried about you. Please know that you're not alone and there is help available." 12
add_chat_message "it sucks to be alive" "I understand this is an incredibly difficult time for you. Your life has value." 6

echo ""
echo "🔍 Testing risk calculation for user: $TEST_USER_ID"

# Test the risk calculation
response=$(curl -s -X POST "https://h8iyzk1h3k.execute-api.us-east-1.amazonaws.com/calculate-risk" \
    -H "Content-Type: application/json" \
    -d "{\"userId\": \"$TEST_USER_ID\"}" \
    -w "HTTP_STATUS:%{http_code}")

http_status=$(echo "$response" | grep -o "HTTP_STATUS:[0-9]*" | cut -d: -f2)
response_body=$(echo "$response" | sed 's/HTTP_STATUS:[0-9]*$//')

echo "HTTP Status: $http_status"
echo "Response:"
echo "$response_body" | jq . 2>/dev/null || echo "$response_body"

echo ""
echo "🏁 Test completed for user: $TEST_USER_ID"
echo "You can now use this user ID in the frontend to test the ML system"