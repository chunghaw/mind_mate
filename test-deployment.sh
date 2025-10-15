#!/bin/bash

API_URL="https://h8iyzk1h3k.execute-api.us-east-1.amazonaws.com"
USER_ID="demo-user-$(date +%s)"

echo "🧪 Testing Mind Mate Deployment"
echo "================================"
echo ""

# Test 1: Get Profile
echo "1️⃣ Testing GET /profile..."
curl -s "${API_URL}/profile?userId=${USER_ID}" | jq '.'
echo ""

# Test 2: Update Profile
echo "2️⃣ Testing POST /profile..."
curl -s -X POST "${API_URL}/profile" \
  -H "Content-Type: application/json" \
  -d "{\"userId\":\"${USER_ID}\",\"personality\":\"playful\",\"petName\":\"Buddy\"}" | jq '.'
echo ""

# Test 3: Log Mood
echo "3️⃣ Testing POST /mood..."
curl -s -X POST "${API_URL}/mood" \
  -H "Content-Type: application/json" \
  -d "{\"userId\":\"${USER_ID}\",\"mood\":8,\"note\":\"Feeling great!\",\"tags\":[\"happy\",\"energetic\"]}" | jq '.'
echo ""

# Test 4: Get Stats
echo "4️⃣ Testing GET /stats..."
curl -s "${API_URL}/stats?userId=${USER_ID}" | jq '.'
echo ""

echo "✅ All tests complete!"
