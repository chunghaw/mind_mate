#!/bin/bash
# Test Mind Mate API endpoints
# Usage: ./test-api.sh <API_GATEWAY_URL>

API_URL=${1:-"https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com"}

echo "🧪 Testing Mind Mate API"
echo "API URL: $API_URL"
echo ""

# Test 1: Log mood
echo "1️⃣ Testing POST /mood..."
curl -X POST "$API_URL/mood" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "test-user",
    "mood": 8,
    "tags": ["happy", "productive"],
    "notes": "Had a great day at work!"
  }' \
  -w "\nStatus: %{http_code}\n\n"

sleep 1

# Test 2: Log another mood (for trend analysis)
echo "2️⃣ Logging multiple moods for testing..."
for mood in 7 6 5 4 3; do
  curl -s -X POST "$API_URL/mood" \
    -H "Content-Type: application/json" \
    -d "{\"userId\":\"test-user\",\"mood\":$mood,\"tags\":[\"work\"],\"notes\":\"Day $mood\"}" \
    > /dev/null
  echo "Logged mood: $mood"
  sleep 0.5
done
echo ""

# Test 3: Analyze selfie (requires base64 image)
echo "3️⃣ Testing POST /selfie..."
echo "Note: This requires a base64-encoded image. Skipping for now."
echo "To test manually, use the web interface or provide a base64 image."
echo ""

# Test 4: Generate avatar
echo "4️⃣ Testing POST /avatar..."
curl -X POST "$API_URL/avatar" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "test-user",
    "description": "a friendly golden retriever puppy with big brown eyes"
  }' \
  -w "\nStatus: %{http_code}\n\n"

echo ""
echo "✅ API tests complete!"
echo ""
echo "Next steps:"
echo "- Check DynamoDB table 'EmoCompanion' for stored data"
echo "- Test Lambda functions directly via AWS Console"
echo "- Open the web app and test the full user flow"
