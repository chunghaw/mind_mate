# Deploy ML Integration - Step-by-Step Checklist

## 📋 Pre-Deployment Checklist

- [ ] ML infrastructure stack deployed (DynamoDB tables, S3, IAM roles)
- [ ] Feature extraction Lambdas deployed (tasks 1-6)
- [ ] Existing Mind Mate app is working
- [ ] AWS CLI configured with correct credentials
- [ ] API Gateway exists and is accessible
- [ ] `.env` file has all required variables

## 🚀 Deployment Steps

### Step 1: Verify Prerequisites

```bash
# Check AWS credentials
aws sts get-caller-identity

# Check if ML tables exist
aws dynamodb describe-table --table-name MindMate-RiskAssessments
aws dynamodb describe-table --table-name MindMate-Interventions

# Check if feature extraction Lambdas exist
aws lambda get-function --function-name extractMoodFeatures
aws lambda get-function --function-name extractBehavioralFeatures
aws lambda get-function --function-name extractSentimentFeatures
```

**Status**: [ ] Complete

---

### Step 2: Deploy Backend Lambdas

```bash
# Deploy calculateRiskScore and executeIntervention
./infrastructure/deploy-ml-lambdas.sh
```

**Expected Output**:
```
🚀 Deploying ML Integration Lambda Functions...
📦 Deploying calculateRiskScore...
  ✅ calculateRiskScore deployed
📦 Deploying executeIntervention...
  ✅ executeIntervention deployed
✅ All ML Integration Lambdas deployed successfully!
```

**Verify**:
```bash
# Check Lambda functions exist
aws lambda get-function --function-name calculateRiskScore
aws lambda get-function --function-name executeIntervention
```

**Status**: [ ] Complete

---

### Step 3: Add API Gateway Routes

```bash
# Add /calculate-risk and /risk-score endpoints
./infrastructure/add-ml-routes.sh
```

**Expected Output**:
```
🔧 Adding ML routes to API Gateway...
📍 Found API Gateway: abc123xyz
Creating /calculate-risk endpoint...
  ✅ /calculate-risk endpoint created
Creating /risk-score endpoint...
  ✅ /risk-score endpoint created
✅ ML routes added successfully!
```

**Verify**:
```bash
# Get API URL
API_URL=$(aws apigateway get-rest-apis --query "items[?name=='MindMateAPI'].id" --output text)
echo "https://${API_URL}.execute-api.us-east-1.amazonaws.com/prod"
```

**Status**: [ ] Complete

---

### Step 4: Test Backend Integration

```bash
# Set your API URL
export API_URL="https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/prod"

# Test 1: Log some moods first
curl -X POST "$API_URL/mood" \
  -H "Content-Type: application/json" \
  -d '{"userId":"test-user","mood":7,"notes":"Testing"}'

# Test 2: Calculate risk
curl -X POST "$API_URL/calculate-risk" \
  -H "Content-Type: application/json" \
  -d '{"userId":"test-user"}'

# Test 3: Get risk score
curl "$API_URL/risk-score?userId=test-user"
```

**Expected Results**:
- Test 1: `{"ok": true, ...}`
- Test 2: `{"ok": true, "riskScore": 0.XX, "riskLevel": "...", ...}`
- Test 3: `{"ok": true, "riskScore": 0.XX, "riskLevel": "...", ...}`

**Status**: [ ] Complete

---

### Step 5: Integrate Frontend Widget

#### Option A: Automatic (Recommended)

```bash
# Run integration script
./scripts/integrate-ml-widget.sh
```

**Expected Output**:
```
🔧 Integrating ML Wellness Widget into Frontend...
📄 Creating frontend/mind-mate-ml.html...
✅ ML widget integrated successfully!
```

**Status**: [ ] Complete

#### Option B: Manual

1. Add to `<head>`:
```html
<link rel="stylesheet" href="ml-wellness-widget.css">
```

2. Add before `</body>`:
```html
<script src="ml-wellness-widget.js"></script>
```

3. Add after header:
```html
<div id="ml-wellness-widget"></div>
```

4. Add to `window.onload`:
```javascript
initMLWidget(API, USER_ID);
```

**Status**: [ ] Complete

---

### Step 6: Test Frontend Locally

```bash
# If you have a local server
cd frontend
python3 -m http.server 8000

# Open in browser
open http://localhost:8000/mind-mate-ml.html
```

**Verify**:
- [ ] Page loads without errors
- [ ] ML wellness widget appears
- [ ] Widget shows "No Data" or risk level
- [ ] Refresh button works
- [ ] No console errors

**Status**: [ ] Complete

---

### Step 7: Deploy Frontend

#### For S3/CloudFront:

```bash
# Get your bucket name
BUCKET_NAME="your-frontend-bucket"

# Upload files
aws s3 cp frontend/mind-mate-ml.html s3://$BUCKET_NAME/index.html
aws s3 cp frontend/ml-wellness-widget.js s3://$BUCKET_NAME/
aws s3 cp frontend/ml-wellness-widget.css s3://$BUCKET_NAME/

# Invalidate CloudFront cache (if using)
DISTRIBUTION_ID="your-distribution-id"
aws cloudfront create-invalidation \
  --distribution-id $DISTRIBUTION_ID \
  --paths "/*"
```

#### For Amplify:

```bash
# Commit and push to Git
git add frontend/mind-mate-ml.html
git add frontend/ml-wellness-widget.*
git commit -m "Add ML wellness widget integration"
git push origin main

# Amplify will auto-deploy
```

**Status**: [ ] Complete

---

### Step 8: End-to-End Testing

```bash
# 1. Open your deployed app
open https://your-app-url.com

# 2. Log in or use demo mode

# 3. Log a few moods
# (Use the app UI)

# 4. Trigger risk assessment
curl -X POST "$API_URL/calculate-risk" \
  -H "Content-Type: application/json" \
  -d '{"userId":"YOUR_USER_ID"}'

# 5. Refresh the page
# Widget should show risk level

# 6. Wait 5 minutes
# Widget should auto-refresh
```

**Verify**:
- [ ] Can log moods
- [ ] Widget shows after assessment
- [ ] Risk level is displayed correctly
- [ ] Colors match risk level
- [ ] Auto-refresh works
- [ ] Manual refresh works
- [ ] No errors in console

**Status**: [ ] Complete

---

### Step 9: Monitor & Verify

```bash
# Check Lambda logs
aws logs tail /aws/lambda/calculateRiskScore --follow

# Check DynamoDB data
aws dynamodb scan --table-name MindMate-RiskAssessments --limit 5

# Check interventions
aws dynamodb scan --table-name MindMate-Interventions --limit 5
```

**Verify**:
- [ ] Logs show successful executions
- [ ] Risk assessments are being stored
- [ ] Interventions are triggered for high risk
- [ ] No error messages in logs

**Status**: [ ] Complete

---

### Step 10: Set Up Monitoring (Optional)

```bash
# Create CloudWatch dashboard
aws cloudwatch put-dashboard \
  --dashboard-name MindMate-ML-Dashboard \
  --dashboard-body file://infrastructure/ml-dashboard.json

# Set up alarms
aws cloudwatch put-metric-alarm \
  --alarm-name ml-lambda-errors \
  --alarm-description "Alert on ML Lambda errors" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold
```

**Status**: [ ] Complete

---

## ✅ Post-Deployment Checklist

- [ ] Backend Lambdas deployed and working
- [ ] API Gateway routes accessible
- [ ] Frontend widget integrated
- [ ] Frontend deployed to hosting
- [ ] End-to-end testing passed
- [ ] Monitoring set up
- [ ] Documentation reviewed
- [ ] Team notified of new features

## 🎯 Success Criteria

Your integration is successful when:

1. ✅ Users can log moods
2. ✅ Risk assessments are calculated
3. ✅ Widget displays risk levels
4. ✅ High-risk users receive interventions
5. ✅ Widget auto-refreshes every 5 minutes
6. ✅ No errors in CloudWatch logs
7. ✅ Data is stored in DynamoDB

## 🐛 Troubleshooting

### Issue: Widget not showing

**Solution**:
```bash
# Check browser console
# Verify API URL is correct
# Check CORS settings
./infrastructure/add-ml-routes.sh
```

### Issue: Risk score always "No Data"

**Solution**:
```bash
# Ensure user has logged moods
# Trigger manual assessment
curl -X POST "$API_URL/calculate-risk" \
  -d '{"userId":"YOUR_USER_ID"}'
```

### Issue: Intervention not triggering

**Solution**:
```bash
# Check Lambda logs
aws logs tail /aws/lambda/executeIntervention --follow

# Verify Bedrock permissions
aws iam get-role-policy \
  --role-name MindMate-MLLambdaRole \
  --policy-name BedrockAccess
```

## 📊 Metrics to Monitor

After deployment, monitor:

- **Lambda Invocations**: calculateRiskScore, executeIntervention
- **API Gateway Requests**: /calculate-risk, /risk-score
- **DynamoDB Operations**: RiskAssessments writes, Interventions writes
- **Error Rates**: Lambda errors, API Gateway 4xx/5xx
- **Latency**: Risk calculation time, API response time

## 🎉 Deployment Complete!

Once all checkboxes are marked:

1. Your ML system is live
2. Users are being monitored proactively
3. At-risk users receive timely support
4. Wellness status is visible in real-time

## 📚 Next Steps

- [ ] Review analytics after 1 week
- [ ] Gather user feedback
- [ ] Plan ML model training
- [ ] Consider automated daily assessments
- [ ] Add push notifications

---

**Deployment Date**: _______________
**Deployed By**: _______________
**Status**: [ ] Complete

**Notes**:
_______________________________________
_______________________________________
_______________________________________
