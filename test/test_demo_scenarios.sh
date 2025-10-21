#!/bin/bash
# test_demo_scenarios.sh - Test predefined demo scenarios

set -e

echo "=========================================="
echo "Mind Mate - Demo Scenarios Test"
echo "=========================================="
echo ""

# Scenario 1: Stable User (Low Risk)
echo "Scenario 1: Stable User (Low Risk)"
echo "==================================="
USER_ID="demo-stable-$(date +%s)"

echo "Creating stable mood pattern..."
for day in {1..7}; do
  mood=$((7 + RANDOM % 2))
  aws lambda invoke \
    --function-name logMood \
    --payload "{\"body\":\"{\\\"userId\\\":\\\"$USER_ID\\\",\\\"mood\\\":$mood,\\\"notes\\\":\\\"Feeling good today\\\"}\"}" \
    /dev/null 2>&1
  sleep 1
done

echo "Calculating risk..."
aws lambda invoke \
  --function-name calculateRiskScore \
  --payload "{\"userId\":\"$USER_ID\"}" \
  stable_risk.json > /dev/null

echo "Results:"
cat stable_risk.json | jq '{risk_level, risk_score, mood_risk}'
echo ""

# Scenario 2: Declining User (Moderate Risk)
echo "Scenario 2: Declining User (Moderate Risk)"
echo "==========================================="
USER_ID="demo-declining-$(date +%s)"

echo "Creating declining mood pattern..."
for day in {7..1}; do
  aws lambda invoke \
    --function-name logMood \
    --payload "{\"body\":\"{\\\"userId\\\":\\\"$USER_ID\\\",\\\"mood\\\":$day,\\\"notes\\\":\\\"Feeling stressed\\\"}\"}" \
    /dev/null 2>&1
  sleep 1
done

echo "Calculating risk..."
aws lambda invoke \
  --function-name calculateRiskScore \
  --payload "{\"userId\":\"$USER_ID\"}" \
  declining_risk.json > /dev/null

echo "Results:"
cat declining_risk.json | jq '{risk_level, risk_score, mood_risk, mood_trend_7day}'
echo ""

# Scenario 3: Crisis User (Critical Risk)
echo "Scenario 3: Crisis User (Critical Risk)"
echo "========================================"
USER_ID="demo-crisis-$(date +%s)"

echo "Creating crisis mood pattern..."
for day in {1..7}; do
  aws lambda invoke \
    --function-name logMood \
    --payload "{\"body\":\"{\\\"userId\\\":\\\"$USER_ID\\\",\\\"mood\\\":2,\\\"notes\\\":\\\"Feeling hopeless and alone\\\"}\"}" \
    /dev/null 2>&1
  sleep 1
done

echo "Calculating risk..."
aws lambda invoke \
  --function-name calculateRiskScore \
  --payload "{\"userId\":\"$USER_ID\"}" \
  crisis_risk.json > /dev/null

echo "Results:"
cat crisis_risk.json | jq '{risk_level, risk_score, crisis_keywords_present, recommendations}'
echo ""

# Scenario 4: Volatile User (Unpredictable Risk)
echo "Scenario 4: Volatile User (Unpredictable Risk)"
echo "==============================================="
USER_ID="demo-volatile-$(date +%s)"

echo "Creating volatile mood pattern..."
moods=(8 3 7 2 9 4 6)
for i in {0..6}; do
  aws lambda invoke \
    --function-name logMood \
    --payload "{\"body\":\"{\\\"userId\\\":\\\"$USER_ID\\\",\\\"mood\\\":${moods[$i]},\\\"notes\\\":\\\"Mood swings today\\\"}\"}" \
    /dev/null 2>&1
  sleep 1
done

echo "Calculating risk..."
aws lambda invoke \
  --function-name calculateRiskScore \
  --payload "{\"userId\":\"$USER_ID\"}" \
  volatile_risk.json > /dev/null

echo "Results:"
cat volatile_risk.json | jq '{risk_level, risk_score, mood_volatility}'
echo ""

echo "=========================================="
echo "✓ All Demo Scenarios Complete"
echo "=========================================="
echo ""
echo "Summary:"
echo "--------"
echo "Stable User:    $(cat stable_risk.json | jq -r '.risk_level')"
echo "Declining User: $(cat declining_risk.json | jq -r '.risk_level')"
echo "Crisis User:    $(cat crisis_risk.json | jq -r '.risk_level')"
echo "Volatile User:  $(cat volatile_risk.json | jq -r '.risk_level')"

# Cleanup
rm -f stable_risk.json declining_risk.json crisis_risk.json volatile_risk.json
