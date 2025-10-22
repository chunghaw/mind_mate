#!/bin/bash

echo "🧠 Testing ML Integration for Risk Calculation"
echo "=============================================="

# Test user ID
USER_ID="test-user-123"
API_BASE="https://h8iyzk1h3k.execute-api.us-east-1.amazonaws.com"

echo ""
echo "1. Testing Mood Feature Extraction..."
echo "------------------------------------"
curl -s -X POST "${API_BASE}/extract-mood-features" \
  -H "Content-Type: application/json" \
  -d "{\"userId\": \"${USER_ID}\"}" | jq '.'

echo ""
echo "2. Testing Sentiment Feature Extraction..."
echo "-----------------------------------------"
curl -s -X POST "${API_BASE}/extract-sentiment-features" \
  -H "Content-Type: application/json" \
  -d "{\"userId\": \"${USER_ID}\"}" | jq '.'

echo ""
echo "3. Testing Behavioral Feature Extraction..."
echo "------------------------------------------"
curl -s -X POST "${API_BASE}/extract-behavioral-features" \
  -H "Content-Type: application/json" \
  -d "{\"userId\": \"${USER_ID}\"}" | jq '.'

echo ""
echo "4. Testing ML-Powered Risk Calculation..."
echo "----------------------------------------"
curl -s -X POST "${API_BASE}/calculate-risk" \
  -H "Content-Type: application/json" \
  -d "{\"userId\": \"${USER_ID}\"}" | jq '.'

echo ""
echo "✅ ML Integration Test Complete!"
echo ""
echo "Expected behavior:"
echo "- Feature extraction should return numerical features"
echo "- Risk calculation should use 'ml_ensemble' or 'rule_based' method"
echo "- Wellness score should be calculated from real ML features"
echo "- Risk factors should be interpretable and specific"