#!/bin/bash

# Add demo data for Mind Mate presentation
# Creates realistic mood logs for the past 7 days

set -e

echo "📊 Adding demo data for Mind Mate..."

# Get API Gateway URL from environment or use default
API_URL="${API_GATEWAY_URL:-https://your-api-gateway-url.execute-api.us-east-1.amazonaws.com}"
USER_ID="${DEMO_USER_ID:-demo-user}"

echo "API URL: $API_URL"
echo "User ID: $USER_ID"

# Add mood logs for the past 7 days
echo ""
echo "Adding mood logs..."

# Day 7 (oldest) - Good mood
curl -X POST "$API_URL/mood" \
  -H "Content-Type: application/json" \
  -d "{
    \"userId\": \"$USER_ID\",
    \"mood\": 7,
    \"tags\": [\"productive\", \"energetic\"],
    \"notes\": \"Had a great day at work, feeling accomplished\"
  }" 2>/dev/null && echo "✅ Day 7: Mood 7"

sleep 1

# Day 6 - Good mood
curl -X POST "$API_URL/mood" \
  -H "Content-Type: application/json" \
  -d "{
    \"userId\": \"$USER_ID\",
    \"mood\": 8,
    \"tags\": [\"happy\", \"social\"],
    \"notes\": \"Spent time with friends, feeling connected\"
  }" 2>/dev/null && echo "✅ Day 6: Mood 8"

sleep 1

# Day 5 - Slight decline
curl -X POST "$API_URL/mood" \
  -H "Content-Type: application/json" \
  -d "{
    \"userId\": \"$USER_ID\",
    \"mood\": 6,
    \"tags\": [\"tired\", \"work\"],
    \"notes\": \"Long day, a bit tired but okay\"
  }" 2>/dev/null && echo "✅ Day 5: Mood 6"

sleep 1

# Day 4 - More decline
curl -X POST "$API_URL/mood" \
  -H "Content-Type: application/json" \
  -d "{
    \"userId\": \"$USER_ID\",
    \"mood\": 5,
    \"tags\": [\"stressed\", \"overwhelmed\"],
    \"notes\": \"Feeling a bit overwhelmed with deadlines\"
  }" 2>/dev/null && echo "✅ Day 4: Mood 5"

sleep 1

# Day 3 - Low mood
curl -X POST "$API_URL/mood" \
  -H "Content-Type: application/json" \
  -d "{
    \"userId\": \"$USER_ID\",
    \"mood\": 4,
    \"tags\": [\"anxious\", \"tired\"],
    \"notes\": \"Having trouble sleeping, feeling anxious\"
  }" 2>/dev/null && echo "✅ Day 3: Mood 4"

sleep 1

# Day 2 - Recovery starting
curl -X POST "$API_URL/mood" \
  -H "Content-Type: application/json" \
  -d "{
    \"userId\": \"$USER_ID\",
    \"mood\": 5,
    \"tags\": [\"hopeful\", \"trying\"],
    \"notes\": \"Trying some coping strategies, feeling a bit better\"
  }" 2>/dev/null && echo "✅ Day 2: Mood 5"

sleep 1

# Day 1 (today) - Improving
curl -X POST "$API_URL/mood" \
  -H "Content-Type: application/json" \
  -d "{
    \"userId\": \"$USER_ID\",
    \"mood\": 6,
    \"tags\": [\"calm\", \"optimistic\"],
    \"notes\": \"Feeling more balanced today, taking things one step at a time\"
  }" 2>/dev/null && echo "✅ Day 1: Mood 6"

echo ""
echo "✅ Demo data added successfully!"
echo ""
echo "This creates a realistic pattern showing:"
echo "- Initial good mood (7-8)"
echo "- Gradual decline (6-5-4)"
echo "- Recovery starting (5-6)"
echo ""
echo "Perfect for demonstrating:"
echo "- Mood trend analysis"
echo "- Risk detection (caught the decline)"
echo "- Pattern recognition"
echo "- Recovery tracking"
