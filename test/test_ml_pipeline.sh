#!/bin/bash
# test_ml_pipeline.sh - Test complete ML pipeline

set -e

USER_ID="${1:-ml-test-user-$(date +%s)}"

echo "=========================================="
echo "Testing ML Pipeline"
echo "=========================================="
echo "User ID: $USER_ID"
echo ""

# Step 1: Generate synthetic data
echo "Step 1: Generate Test Data"
echo "--------------------------"
echo "Creating 30 days of mood logs..."

for day in {1..30}; do
  # Simulate declining mood pattern
  mood=$((8 - day / 5))
  mood=$((mood < 2 ? 2 : mood))
  
  aws lambda invoke \
    --function-name logMood \
    --payload "{\"body\":\"{\\\"userId\\\":\\\"$USER_ID\\\",\\\"mood\\\":$mood,\\\"notes\\\":\\\"Day $day\\\"}\"}" \
    /dev/null 2>&1
  
  if [ $((day % 10)) -eq 0 ]; then
    echo "  $day days logged..."
  fi
done
echo "✓ 30 days of data created"
echo ""

# Step 2: Extract mood features
echo "Step 2: Extract Mood Features"
echo "------------------------------"
aws lambda invoke \
  --function-name extractMoodFeatures \
  --payload "{\"userId\":\"$USER_ID\",\"days\":30}" \
  mood_features.json > /dev/null

echo "Mood Features:"
cat mood_features.json | jq '{
  mood_mean_7day,
  mood_trend_7day,
  consecutive_low_days,
  mood_volatility
}'
echo ""

# Step 3: Extract behavioral features
echo "Step 3: Extract Behavioral Features"
echo "------------------------------------"
aws lambda invoke \
  --function-name extractBehavioralFeatures \
  --payload "{\"userId\":\"$USER_ID\",\"days\":30}" \
  behavioral_features.json > /dev/null

echo "Behavioral Features:"
cat behavioral_features.json | jq '{
  checkin_frequency,
  engagement_score,
  days_since_last_checkin
}'
echo ""

# Step 4: Extract sentiment features
echo "Step 4: Extract Sentiment Features"
echo "-----------------------------------"
aws lambda invoke \
  --function-name extractSentimentFeatures \
  --payload "{\"userId\":\"$USER_ID\",\"days\":30}" \
  sentiment_features.json > /dev/null

echo "Sentiment Features:"
cat sentiment_features.json | jq '{
  positive_sentiment_frequency,
  negative_sentiment_frequency,
  crisis_keywords_present
}'
echo ""

# Step 5: Calculate risk score
echo "Step 5: Calculate Risk Score"
echo "----------------------------"
aws lambda invoke \
  --function-name calculateRiskScore \
  --payload "{\"userId\":\"$USER_ID\"}" \
  risk_score.json > /dev/null

echo "Risk Assessment:"
cat risk_score.json | jq '{
  risk_score,
  risk_level,
  mood_risk,
  behavioral_risk,
  sentiment_risk,
  recommendations
}'
echo ""

# Step 6: Verify feature storage
echo "Step 6: Verify Feature Storage"
echo "-------------------------------"
FEATURE_COUNT=$(aws dynamodb query \
  --table-name MoodFeatures \
  --key-condition-expression "userId = :uid" \
  --expression-attribute-values "{\":uid\":{\"S\":\"$USER_ID\"}}" \
  --select COUNT \
  --output text \
  --query 'Count' 2>/dev/null || echo "0")

echo "Features stored in DynamoDB: $FEATURE_COUNT"
echo ""

echo "=========================================="
echo "✓ ML Pipeline Test Complete"
echo "=========================================="

# Cleanup
rm -f mood_features.json behavioral_features.json sentiment_features.json risk_score.json
