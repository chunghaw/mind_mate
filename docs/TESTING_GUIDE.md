# Mind Mate - Testing Guide

## Overview

This guide covers comprehensive testing procedures for the Mind Mate application, including unit tests, integration tests, end-to-end tests, and manual testing workflows.

---

## Table of Contents

1. [Quick Test Commands](#quick-test-commands)
2. [Backend Testing](#backend-testing)
3. [Frontend Testing](#frontend-testing)
4. [Integration Testing](#integration-testing)
5. [ML Pipeline Testing](#ml-pipeline-testing)
6. [Authentication Testing](#authentication-testing)
7. [Performance Testing](#performance-testing)
8. [Security Testing](#security-testing)
9. [Demo Scenarios](#demo-scenarios)

---

## Quick Test Commands

### Test All Lambda Functions
```bash
# Test mood logging
aws lambda invoke \
  --function-name logMood \
  --payload '{"body":"{\"userId\":\"test-user\",\"mood\":7,\"tags\":[\"happy\"],\"notes\":\"Great day!\"}"}' \
  response.json && cat response.json

# Test chat
aws lambda invoke \
  --function-name chat \
  --payload '{"body":"{\"userId\":\"test-user\",\"message\":\"Hello!\"}"}' \
  response.json && cat response.json

# Test risk calculation
aws lambda invoke \
  --function-name calculateRiskScore \
  --payload '{"userId":"test-user"}' \
  response.json && cat response.json
```

### Test API Endpoints
```bash
# Set your API Gateway URL
API_URL="https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com"

# Test mood endpoint
curl -X POST "$API_URL/mood" \
  -H "Content-Type: application/json" \
  -d '{"userId":"test-user","mood":7,"tags":["happy"],"notes":"Testing"}'

# Test chat endpoint
curl -X POST "$API_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{"userId":"test-user","message":"How are you?"}'

# Test risk score endpoint
curl -X GET "$API_URL/risk-score?userId=test-user"
```

---

## Backend Testing

### 1. Lambda Function Testing

#### Test logMood Function
```bash
# Test payload
cat > test_mood.json << EOF
{
  "body": "{\"userId\":\"test-user\",\"mood\":7,\"tags\":[\"happy\",\"productive\"],\"notes\":\"Had a great day at work!\"}"
}
EOF

# Invoke function
aws lambda invoke \
  --function-name logMood \
  --payload file://test_mood.json \
  response.json

# Check response
cat response.json

# Verify in DynamoDB
aws dynamodb query \
  --table-name EmoCompanion \
  --key-condition-expression "PK = :pk" \
  --expression-attribute-values '{":pk":{"S":"USER#test-user"}}' \
  --limit 5
```

#### Test chat Function (Bedrock Integration)
```bash
# Test payload
cat > test_chat.json << EOF
{
  "body": "{\"userId\":\"test-user\",\"message\":\"I'm feeling anxious today\"}"
}
EOF

# Invoke function
aws lambda invoke \
  --function-name chat \
  --payload file://test_chat.json \
  response.json

# Check response (should contain AI reply)
cat response.json | jq '.body' | jq -r '.reply'
```

#### Test calculateRiskScore Function
```bash
# First, create test data (7 days of mood logs)
for i in {1..7}; do
  aws lambda invoke \
    --function-name logMood \
    --payload "{\"body\":\"{\\\"userId\\\":\\\"test-user\\\",\\\"mood\\\":$((3 + RANDOM % 3)),\\\"notes\\\":\\\"Day $i\\\"}\"}" \
    /dev/null
  sleep 1
done

# Calculate risk score
aws lambda invoke \
  --function-name calculateRiskScore \
  --payload '{"userId":"test-user"}' \
  response.json

# Check risk assessment
cat response.json | jq '.'
```

#### Test ML Feature Extraction Functions
```bash
# Test mood feature extraction
aws lambda invoke \
  --function-name extractMoodFeatures \
  --payload '{"userId":"test-user","days":30}' \
  response.json && cat response.json

# Test behavioral feature extraction
aws lambda invoke \
  --function-name extractBehavioralFeatures \
  --payload '{"userId":"test-user","days":30}' \
  response.json && cat response.json

# Test sentiment feature extraction
aws lambda invoke \
  --function-name extractSentimentFeatures \
  --payload '{"userId":"test-user","days":30}' \
  response.json && cat response.json
```

### 2. DynamoDB Testing

#### Verify Data Storage
```bash
# Check user profile
aws dynamodb get-item \
  --table-name EmoCompanion \
  --key '{"PK":{"S":"USER#test-user"},"SK":{"S":"PROFILE"}}'

# Scan recent mood logs
aws dynamodb query \
  --table-name EmoCompanion \
  --key-condition-expression "PK = :pk AND begins_with(SK, :sk)" \
  --expression-attribute-values '{":pk":{"S":"USER#test-user"},":sk":{"S":"MOOD#"}}' \
  --scan-index-forward false \
  --limit 10

# Check ML features table
aws dynamodb scan \
  --table-name MoodFeatures \
  --limit 5
```

### 3. CloudWatch Logs Testing

#### Monitor Lambda Execution
```bash
# Tail logs in real-time
aws logs tail /aws/lambda/logMood --follow

# Get recent errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/chat \
  --filter-pattern "ERROR" \
  --start-time $(date -u -d '1 hour ago' +%s)000

# Check execution metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=chat \
  --start-time $(date -u -d '1 day ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Sum
```

---

## Frontend Testing

### 1. Authentication Flow Testing

#### Manual Test Steps
1. Open `check-auth.html` in browser
2. Verify localStorage status
3. Test authentication states:
   - Not authenticated
   - Demo mode
   - Authenticated with Cognito

#### Automated Test Script
```javascript
// Run in browser console on check-auth.html

// Test 1: Clear auth
localStorage.clear();
console.assert(!localStorage.getItem('mindmate_token'), 'Auth should be cleared');

// Test 2: Set demo mode
localStorage.setItem('mindmate_token', 'demo-token');
localStorage.setItem('mindmate_onboardingComplete', 'true');
localStorage.setItem('mindmate_userId', 'demo-user');
console.assert(localStorage.getItem('mindmate_token') === 'demo-token', 'Demo mode set');

// Test 3: Verify redirect
window.location.href = '/mind-mate-hackathon.html';
```

### 2. UI Component Testing

#### Dashboard Widget Tests
```javascript
// Run in browser console on mind-mate-hackathon.html

// Test 1: Risk score display
const testRiskData = {
  risk_score: 0.65,
  risk_level: 'HIGH',
  mood_risk: 0.7,
  behavioral_risk: 0.6,
  sentiment_risk: 0.65
};

// Manually trigger widget update
if (window.updateMLWidget) {
  window.updateMLWidget(testRiskData);
  console.log('✓ Widget updated with test data');
}

// Test 2: Chart rendering
const chartCanvas = document.querySelector('#riskChart');
console.assert(chartCanvas !== null, 'Chart canvas exists');

// Test 3: Tab switching
document.querySelector('[data-tab="dashboard"]').click();
console.assert(document.querySelector('#dashboard').style.display !== 'none', 'Dashboard visible');

document.querySelector('[data-tab="chat"]').click();
console.assert(document.querySelector('#chat').style.display !== 'none', 'Chat visible');
```

### 3. API Integration Testing

#### Test Frontend API Calls
```javascript
// Run in browser console

// Test 1: Log mood
fetch('https://YOUR_API_URL/mood', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    userId: 'test-user',
    mood: 7,
    tags: ['happy'],
    notes: 'Testing from frontend'
  })
})
.then(r => r.json())
.then(data => console.log('Mood logged:', data))
.catch(err => console.error('Error:', err));

// Test 2: Send chat message
fetch('https://YOUR_API_URL/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    userId: 'test-user',
    message: 'Hello, how can you help me?'
  })
})
.then(r => r.json())
.then(data => console.log('Chat response:', data))
.catch(err => console.error('Error:', err));
```

---

## Integration Testing

### 1. End-to-End User Flow

#### Complete User Journey Test
```bash
#!/bin/bash
# test_user_journey.sh

API_URL="https://YOUR_API_URL"
USER_ID="e2e-test-$(date +%s)"

echo "Testing complete user journey for $USER_ID"

# Step 1: User signs up (simulated)
echo "1. User signup..."
# In real test, use Cognito API

# Step 2: Log first mood
echo "2. Logging mood..."
curl -X POST "$API_URL/mood" \
  -H "Content-Type: application/json" \
  -d "{\"userId\":\"$USER_ID\",\"mood\":7,\"notes\":\"First day\"}"

# Step 3: Send chat message
echo "3. Sending chat message..."
curl -X POST "$API_URL/chat" \
  -H "Content-Type: application/json" \
  -d "{\"userId\":\"$USER_ID\",\"message\":\"Hello!\"}"

# Step 4: Log multiple moods over time
echo "4. Logging 7 days of moods..."
for day in {1..7}; do
  mood=$((4 + RANDOM % 4))
  curl -s -X POST "$API_URL/mood" \
    -H "Content-Type: application/json" \
    -d "{\"userId\":\"$USER_ID\",\"mood\":$mood,\"notes\":\"Day $day\"}"
  sleep 1
done

# Step 5: Calculate risk score
echo "5. Calculating risk score..."
curl -X GET "$API_URL/risk-score?userId=$USER_ID"

echo "✓ User journey test complete"
```

### 2. ML Pipeline Integration Test

#### Test Complete ML Flow
```bash
#!/bin/bash
# test_ml_pipeline.sh

USER_ID="ml-test-user"

echo "Testing ML pipeline for $USER_ID"

# Step 1: Generate synthetic data
echo "1. Generating test data..."
python3 scripts/generate-synthetic-data.py

# Step 2: Extract mood features
echo "2. Extracting mood features..."
aws lambda invoke \
  --function-name extractMoodFeatures \
  --payload "{\"userId\":\"$USER_ID\",\"days\":30}" \
  mood_features.json

# Step 3: Extract behavioral features
echo "3. Extracting behavioral features..."
aws lambda invoke \
  --function-name extractBehavioralFeatures \
  --payload "{\"userId\":\"$USER_ID\",\"days\":30}" \
  behavioral_features.json

# Step 4: Extract sentiment features
echo "4. Extracting sentiment features..."
aws lambda invoke \
  --function-name extractSentimentFeatures \
  --payload "{\"userId\":\"$USER_ID\",\"days\":30}" \
  sentiment_features.json

# Step 5: Calculate risk score
echo "5. Calculating risk score..."
aws lambda invoke \
  --function-name calculateRiskScore \
  --payload "{\"userId\":\"$USER_ID\"}" \
  risk_score.json

# Step 6: Verify results
echo "6. Verifying results..."
cat risk_score.json | jq '.'

echo "✓ ML pipeline test complete"
```

---

## ML Pipeline Testing

### 1. Feature Extraction Testing

#### Test Mood Features
```bash
# Create test data with known patterns
USER_ID="feature-test-user"

# Log 7 days of declining mood
for i in {7..1}; do
  aws lambda invoke \
    --function-name logMood \
    --payload "{\"body\":\"{\\\"userId\\\":\\\"$USER_ID\\\",\\\"mood\\\":$i,\\\"notes\\\":\\\"Day $i\\\"}\"}" \
    /dev/null
  sleep 1
done

# Extract features
aws lambda invoke \
  --function-name extractMoodFeatures \
  --payload "{\"userId\":\"$USER_ID\",\"days\":7}" \
  features.json

# Verify expected patterns
cat features.json | jq '.mood_trend_7day' # Should be negative
cat features.json | jq '.mood_mean_7day'  # Should be ~4
```

#### Test Behavioral Features
```bash
# Test with varying engagement patterns
USER_ID="behavioral-test-user"

# High engagement period
for i in {1..5}; do
  aws lambda invoke \
    --function-name logMood \
    --payload "{\"body\":\"{\\\"userId\\\":\\\"$USER_ID\\\",\\\"mood\\\":7}\"}" \
    /dev/null
  sleep 1
done

# Low engagement period (skip days)
sleep 5

# Extract features
aws lambda invoke \
  --function-name extractBehavioralFeatures \
  --payload "{\"userId\":\"$USER_ID\",\"days\":7}" \
  features.json

cat features.json | jq '.checkin_frequency'
```

### 2. Risk Score Validation

#### Test Risk Levels
```bash
# Test MINIMAL risk (stable, high mood)
test_risk_level() {
  local USER_ID=$1
  local MOOD_PATTERN=$2
  
  echo "Testing $MOOD_PATTERN pattern..."
  
  # Log moods based on pattern
  case $MOOD_PATTERN in
    "stable")
      for i in {1..7}; do
        aws lambda invoke --function-name logMood \
          --payload "{\"body\":\"{\\\"userId\\\":\\\"$USER_ID\\\",\\\"mood\\\":8}\"}" /dev/null
      done
      ;;
    "declining")
      for i in {7..1}; do
        aws lambda invoke --function-name logMood \
          --payload "{\"body\":\"{\\\"userId\\\":\\\"$USER_ID\\\",\\\"mood\\\":$i}\"}" /dev/null
      done
      ;;
    "crisis")
      for i in {1..7}; do
        aws lambda invoke --function-name logMood \
          --payload "{\"body\":\"{\\\"userId\\\":\\\"$USER_ID\\\",\\\"mood\\\":2,\\\"notes\\\":\\\"feeling hopeless\\\"}\"}" /dev/null
      done
      ;;
  esac
  
  # Calculate risk
  aws lambda invoke \
    --function-name calculateRiskScore \
    --payload "{\"userId\":\"$USER_ID\"}" \
    risk.json
  
  cat risk.json | jq '.risk_level'
}

# Run tests
test_risk_level "stable-user" "stable"     # Expected: MINIMAL
test_risk_level "declining-user" "declining" # Expected: MODERATE/HIGH
test_risk_level "crisis-user" "crisis"     # Expected: CRITICAL
```

### 3. SageMaker Model Testing (Optional)

#### Test Model Training
```bash
# Prepare training data
aws lambda invoke \
  --function-name prepareTrainingData \
  --payload '{"days":90}' \
  training_data.json

# Check S3 for training data
aws s3 ls s3://YOUR_BUCKET/training-data/

# Start training job (see SAGEMAKER_QUICK_DEPLOY.md)
aws sagemaker create-training-job \
  --cli-input-json file://training-job.json

# Monitor training
aws sagemaker describe-training-job \
  --training-job-name mindmate-training-$(date +%Y%m%d)
```

#### Test Model Predictions
```bash
# After model is trained and deployed
aws lambda invoke \
  --function-name calculateRiskScore \
  --payload '{"userId":"test-user","use_ml_model":true}' \
  ml_prediction.json

# Compare rule-based vs ML predictions
cat ml_prediction.json | jq '.ml_risk_score, .rule_based_risk_score'
```

---

## Authentication Testing

### 1. Cognito Integration Testing

#### Test User Registration
```bash
# Sign up new user
aws cognito-idp sign-up \
  --client-id YOUR_CLIENT_ID \
  --username test@example.com \
  --password TestPass123! \
  --user-attributes Name=email,Value=test@example.com

# Confirm user (admin)
aws cognito-idp admin-confirm-sign-up \
  --user-pool-id YOUR_USER_POOL_ID \
  --username test@example.com
```

#### Test User Login
```bash
# Initiate auth
aws cognito-idp initiate-auth \
  --client-id YOUR_CLIENT_ID \
  --auth-flow USER_PASSWORD_AUTH \
  --auth-parameters USERNAME=test@example.com,PASSWORD=TestPass123!

# Extract token from response
TOKEN=$(aws cognito-idp initiate-auth ... | jq -r '.AuthenticationResult.IdToken')

# Test authenticated API call
curl -X POST "https://YOUR_API_URL/mood" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"userId":"test@example.com","mood":7}'
```

### 2. Google OAuth Testing

#### Manual Test Steps
1. Open `onboarding.html` in browser
2. Click "Continue with Google"
3. Complete Google sign-in
4. Verify redirect to personality assessment
5. Complete onboarding
6. Verify redirect to main app
7. Check localStorage for tokens

---

## Performance Testing

### 1. Load Testing

#### Test API Endpoints Under Load
```bash
# Install Apache Bench
# brew install httpd (macOS)

# Test mood logging endpoint
ab -n 1000 -c 10 -p mood_payload.json -T application/json \
  https://YOUR_API_URL/mood

# Test chat endpoint
ab -n 100 -c 5 -p chat_payload.json -T application/json \
  https://YOUR_API_URL/chat
```

#### Lambda Concurrency Testing
```bash
# Test concurrent Lambda invocations
for i in {1..50}; do
  aws lambda invoke \
    --function-name calculateRiskScore \
    --payload "{\"userId\":\"user-$i\"}" \
    response_$i.json &
done

wait
echo "All concurrent invocations complete"

# Check for errors
grep -l "errorMessage" response_*.json
```

### 2. Response Time Testing

#### Measure API Latency
```bash
# Test endpoint response times
test_latency() {
  local ENDPOINT=$1
  local PAYLOAD=$2
  
  for i in {1..10}; do
    START=$(date +%s%N)
    curl -s -X POST "$ENDPOINT" \
      -H "Content-Type: application/json" \
      -d "$PAYLOAD" > /dev/null
    END=$(date +%s%N)
    
    DURATION=$(( (END - START) / 1000000 ))
    echo "Request $i: ${DURATION}ms"
  done
}

test_latency "https://YOUR_API_URL/mood" '{"userId":"test","mood":7}'
test_latency "https://YOUR_API_URL/chat" '{"userId":"test","message":"Hi"}'
```

### 3. Database Performance Testing

#### Test DynamoDB Query Performance
```bash
# Measure query latency
for i in {1..100}; do
  START=$(date +%s%N)
  aws dynamodb query \
    --table-name EmoCompanion \
    --key-condition-expression "PK = :pk" \
    --expression-attribute-values '{":pk":{"S":"USER#test-user"}}' \
    > /dev/null
  END=$(date +%s%N)
  
  DURATION=$(( (END - START) / 1000000 ))
  echo "$DURATION" >> query_times.txt
done

# Calculate average
awk '{ sum += $1; n++ } END { print "Average: " sum/n "ms" }' query_times.txt
```

---

## Security Testing

### 1. Authentication Security

#### Test Unauthorized Access
```bash
# Test without token (should fail)
curl -X POST "https://YOUR_API_URL/mood" \
  -H "Content-Type: application/json" \
  -d '{"userId":"test","mood":7}'

# Test with invalid token (should fail)
curl -X POST "https://YOUR_API_URL/mood" \
  -H "Authorization: Bearer invalid-token" \
  -H "Content-Type: application/json" \
  -d '{"userId":"test","mood":7}'
```

### 2. Input Validation Testing

#### Test Malicious Inputs
```bash
# Test SQL injection attempt
curl -X POST "https://YOUR_API_URL/mood" \
  -H "Content-Type: application/json" \
  -d '{"userId":"test OR 1=1","mood":7}'

# Test XSS attempt
curl -X POST "https://YOUR_API_URL/mood" \
  -H "Content-Type: application/json" \
  -d '{"userId":"<script>alert(1)</script>","mood":7}'

# Test oversized payload
curl -X POST "https://YOUR_API_URL/chat" \
  -H "Content-Type: application/json" \
  -d "{\"userId\":\"test\",\"message\":\"$(python3 -c 'print("A"*100000)')\"}"
```

### 3. Rate Limiting Testing

#### Test API Throttling
```bash
# Send rapid requests
for i in {1..1000}; do
  curl -s -X POST "https://YOUR_API_URL/mood" \
    -H "Content-Type: application/json" \
    -d '{"userId":"test","mood":7}' &
done

wait
# Check for 429 Too Many Requests responses
```

---

## Demo Scenarios

### Scenario 1: Stable User (Low Risk)

#### Setup
```bash
USER_ID="demo-stable-user"

# Log 7 days of consistently good mood
for day in {1..7}; do
  aws lambda invoke \
    --function-name logMood \
    --payload "{\"body\":\"{\\\"userId\\\":\\\"$USER_ID\\\",\\\"mood\\\":$((7 + RANDOM % 2)),\\\"notes\\\":\\\"Feeling good today\\\"}\"}" \
    /dev/null
  sleep 1
done

# Send positive chat messages
aws lambda invoke \
  --function-name chat \
  --payload "{\"body\":\"{\\\"userId\\\":\\\"$USER_ID\\\",\\\"message\\\":\\\"I had a great day at work!\\\"}\"}" \
  /dev/null
```

#### Expected Results
- Risk Level: MINIMAL or LOW
- Risk Score: 0.0 - 0.3
- Mood Trend: Stable or positive
- Recommendations: Continue current practices

### Scenario 2: Declining User (Moderate Risk)

#### Setup
```bash
USER_ID="demo-declining-user"

# Log 7 days of declining mood
for day in {7..1}; do
  aws lambda invoke \
    --function-name logMood \
    --payload "{\"body\":\"{\\\"userId\\\":\\\"$USER_ID\\\",\\\"mood\\\":$day,\\\"notes\\\":\\\"Feeling stressed\\\"}\"}" \
    /dev/null
  sleep 1
done

# Send concerning chat messages
aws lambda invoke \
  --function-name chat \
  --payload "{\"body\":\"{\\\"userId\\\":\\\"$USER_ID\\\",\\\"message\\\":\\\"I'm feeling overwhelmed lately\\\"}\"}" \
  /dev/null
```

#### Expected Results
- Risk Level: MODERATE or HIGH
- Risk Score: 0.4 - 0.7
- Mood Trend: Negative
- Recommendations: Coping strategies, professional resources

### Scenario 3: Crisis User (Critical Risk)

#### Setup
```bash
USER_ID="demo-crisis-user"

# Log 7 days of very low mood with crisis keywords
for day in {1..7}; do
  aws lambda invoke \
    --function-name logMood \
    --payload "{\"body\":\"{\\\"userId\\\":\\\"$USER_ID\\\",\\\"mood\\\":2,\\\"notes\\\":\\\"Feeling hopeless and alone\\\"}\"}" \
    /dev/null
  sleep 1
done

# Send crisis-level chat messages
aws lambda invoke \
  --function-name chat \
  --payload "{\"body\":\"{\\\"userId\\\":\\\"$USER_ID\\\",\\\"message\\\":\\\"I can't cope anymore, everything feels pointless\\\"}\"}" \
  /dev/null
```

#### Expected Results
- Risk Level: CRITICAL
- Risk Score: 0.8 - 1.0
- Crisis Keywords Detected: Yes
- Recommendations: Immediate crisis resources (988, crisis text line)

### Scenario 4: Volatile User (Unpredictable Risk)

#### Setup
```bash
USER_ID="demo-volatile-user"

# Log 7 days of erratic mood swings
moods=(8 3 7 2 9 4 6)
for day in {0..6}; do
  aws lambda invoke \
    --function-name logMood \
    --payload "{\"body\":\"{\\\"userId\\\":\\\"$USER_ID\\\",\\\"mood\\\":${moods[$day]},\\\"notes\\\":\\\"Mood swings today\\\"}\"}" \
    /dev/null
  sleep 1
done
```

#### Expected Results
- Risk Level: MODERATE
- High Volatility Score
- Recommendations: Mood stabilization strategies

---

## Automated Test Suite

### Create Complete Test Suite

```bash
#!/bin/bash
# run_all_tests.sh - Comprehensive test suite

set -e

API_URL="https://YOUR_API_URL"
TEST_USER="test-$(date +%s)"

echo "=========================================="
echo "Mind Mate - Automated Test Suite"
echo "=========================================="
echo "Test User: $TEST_USER"
echo ""

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
    echo "✓ PASS"
    return 0
  else
    echo "✗ FAIL"
    return 1
  fi
}

test_lambda "logMood" "{\"body\":\"{\\\"userId\\\":\\\"$TEST_USER\\\",\\\"mood\\\":7}\"}"
test_lambda "chat" "{\"body\":\"{\\\"userId\\\":\\\"$TEST_USER\\\",\\\"message\\\":\\\"Hello\\\"}\"}"
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
    echo "✓ PASS (HTTP $HTTP_CODE)"
    return 0
  else
    echo "✗ FAIL (HTTP $HTTP_CODE)"
    return 1
  fi
}

test_api "/mood" "POST" "{\"userId\":\"$TEST_USER\",\"mood\":7}"
test_api "/chat" "POST" "{\"userId\":\"$TEST_USER\",\"message\":\"Test\"}"

echo ""

# Test 3: Data Persistence
echo "Test 3: Data Persistence"
echo "------------------------"

echo -n "  Checking DynamoDB... "
ITEM_COUNT=$(aws dynamodb query \
  --table-name EmoCompanion \
  --key-condition-expression "PK = :pk" \
  --expression-attribute-values "{\":pk\":{\"S\":\"USER#$TEST_USER\"}}" \
  --select COUNT \
  --output text \
  --query 'Count')

if [ "$ITEM_COUNT" -gt 0 ]; then
  echo "✓ PASS ($ITEM_COUNT items)"
else
  echo "✗ FAIL (no items found)"
fi

echo ""

# Test 4: ML Pipeline
echo "Test 4: ML Pipeline"
echo "-------------------"

# Create test data
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
  echo "✓ PASS"
else
  echo "✗ FAIL"
fi

echo -n "  Calculating risk score... "
if aws lambda invoke \
  --function-name calculateRiskScore \
  --payload "{\"userId\":\"$TEST_USER\"}" \
  risk.json > /dev/null 2>&1; then
  RISK_LEVEL=$(cat risk.json | jq -r '.risk_level')
  echo "✓ PASS (Risk: $RISK_LEVEL)"
else
  echo "✗ FAIL"
fi

echo ""

# Test 5: Performance
echo "Test 5: Performance"
echo "-------------------"

echo -n "  API response time... "
START=$(date +%s%N)
curl -s -X POST "$API_URL/mood" \
  -H "Content-Type: application/json" \
  -d "{\"userId\":\"$TEST_USER\",\"mood\":7}" > /dev/null
END=$(date +%s%N)
DURATION=$(( (END - START) / 1000000 ))

if [ "$DURATION" -lt 3000 ]; then
  echo "✓ PASS (${DURATION}ms)"
else
  echo "⚠ SLOW (${DURATION}ms)"
fi

echo ""

# Cleanup
echo "Cleanup"
echo "-------"
echo "  Removing test data..."
rm -f response.json features.json risk.json

echo ""
echo "=========================================="
echo "Test Suite Complete"
echo "=========================================="
```

### Run Test Suite
```bash
chmod +x run_all_tests.sh
./run_all_tests.sh
```

---

## Monitoring & Debugging

### 1. Real-Time Monitoring

#### Watch Lambda Logs
```bash
# Monitor all Lambda functions
watch -n 2 'aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=chat \
  --start-time $(date -u -d "5 minutes ago" +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Sum'
```

#### Monitor API Gateway
```bash
# Check API request count
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name Count \
  --dimensions Name=ApiId,Value=YOUR_API_ID \
  --start-time $(date -u -d "1 hour ago" +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

### 2. Error Tracking

#### Find Recent Errors
```bash
# Search for errors in last hour
for FUNCTION in logMood chat calculateRiskScore; do
  echo "Checking $FUNCTION..."
  aws logs filter-log-events \
    --log-group-name "/aws/lambda/$FUNCTION" \
    --filter-pattern "ERROR" \
    --start-time $(date -u -d "1 hour ago" +%s)000 \
    --query 'events[*].message' \
    --output text
done
```

### 3. Performance Metrics

#### Lambda Performance Dashboard
```bash
# Get Lambda duration metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=calculateRiskScore \
  --start-time $(date -u -d "1 day ago" +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Average,Maximum
```

---

## Troubleshooting Test Failures

### Common Issues

#### Lambda Timeout
```bash
# Increase timeout
aws lambda update-function-configuration \
  --function-name calculateRiskScore \
  --timeout 30
```

#### DynamoDB Throttling
```bash
# Check for throttling
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name UserErrors \
  --dimensions Name=TableName,Value=EmoCompanion \
  --start-time $(date -u -d "1 hour ago" +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

#### Bedrock Errors
```bash
# Check Bedrock model access
aws bedrock list-foundation-models \
  --query 'modelSummaries[?contains(modelId, `claude`)].modelId'

# Test Bedrock directly
aws bedrock-runtime invoke-model \
  --model-id anthropic.claude-3-haiku-20240307-v1:0 \
  --body '{"anthropic_version":"bedrock-2023-05-31","max_tokens":100,"messages":[{"role":"user","content":"Hello"}]}' \
  response.json
```

---

## Test Data Cleanup

### Remove Test Data
```bash
#!/bin/bash
# cleanup_test_data.sh

echo "Cleaning up test data..."

# Remove test users from DynamoDB
for USER in test-user demo-user e2e-test-*; do
  echo "Removing $USER..."
  aws dynamodb query \
    --table-name EmoCompanion \
    --key-condition-expression "PK = :pk" \
    --expression-attribute-values "{\":pk\":{\"S\":\"USER#$USER\"}}" \
    --projection-expression "PK,SK" \
    --output json | \
  jq -r '.Items[] | "\(.PK.S) \(.SK.S)"' | \
  while read PK SK; do
    aws dynamodb delete-item \
      --table-name EmoCompanion \
      --key "{\"PK\":{\"S\":\"$PK\"},\"SK\":{\"S\":\"$SK\"}}"
  done
done

# Remove test files from S3
aws s3 rm s3://YOUR_BUCKET/test/ --recursive

echo "✓ Cleanup complete"
```

---

## Continuous Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Test Mind Mate

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Configure AWS
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Test Lambda Functions
        run: |
          ./run_all_tests.sh
      
      - name: Upload Test Results
        uses: actions/upload-artifact@v2
        with:
          name: test-results
          path: test-results/
```

---

## Summary

This testing guide covers:

✅ **Backend Testing**: Lambda functions, DynamoDB, CloudWatch  
✅ **Frontend Testing**: UI components, authentication, API integration  
✅ **Integration Testing**: End-to-end user flows, ML pipeline  
✅ **ML Testing**: Feature extraction, risk scoring, model validation  
✅ **Performance Testing**: Load testing, latency measurement  
✅ **Security Testing**: Authentication, input validation, rate limiting  
✅ **Demo Scenarios**: Pre-configured test cases for demonstrations  

For additional help, see:
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues and solutions
- [API_REFERENCE.md](API_REFERENCE.md) - API endpoint documentation
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Deployment verification

---

**Last Updated**: October 2025  
**Maintained By**: Mind Mate Team
