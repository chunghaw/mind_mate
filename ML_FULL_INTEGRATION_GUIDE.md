# Mind Mate ML System - Full Integration Guide

## 🎯 Overview

This guide walks you through integrating the ML Prediction System into your existing Mind Mate app, covering both backend Lambda functions and frontend UI components.

## 📋 Prerequisites

- ✅ Existing Mind Mate app deployed
- ✅ ML infrastructure stack deployed (DynamoDB tables, S3 buckets, IAM roles)
- ✅ Feature extraction Lambdas deployed (tasks 1-6 complete)
- ✅ AWS CLI configured
- ✅ API Gateway set up

## 🏗️ Architecture

The integration adds two main components:

### Backend
1. **calculateRiskScore** - Calculates risk scores using extracted features
2. **executeIntervention** - Triggers proactive support for at-risk users
3. **getRiskScore** - Retrieves latest risk assessment

### Frontend
1. **ML Wellness Widget** - Displays real-time wellness status
2. **Auto-refresh** - Updates every 5 minutes
3. **Intervention Alerts** - Notifies users of proactive check-ins

## 🚀 Step-by-Step Integration

### Step 1: Deploy Backend Lambdas

Deploy the new ML integration Lambda functions:

```bash
# Make script executable (if not already)
chmod +x infrastructure/deploy-ml-lambdas.sh

# Deploy Lambdas
./infrastructure/deploy-ml-lambdas.sh
```

This deploys:
- `calculateRiskScore` - Main risk assessment function
- `executeIntervention` - Intervention execution function

**Expected Output**:
```
🚀 Deploying ML Integration Lambda Functions...
📦 Deploying calculateRiskScore...
  ✅ calculateRiskScore deployed
📦 Deploying executeIntervention...
  ✅ executeIntervention deployed
✅ All ML Integration Lambdas deployed successfully!
```

### Step 2: Add API Gateway Routes

Add the new endpoints to your API Gateway:

```bash
# Make script executable (if not already)
chmod +x infrastructure/add-ml-routes.sh

# Add routes
./infrastructure/add-ml-routes.sh
```

This creates:
- `POST /calculate-risk` - Trigger risk assessment
- `GET /risk-score` - Get latest risk score

**Expected Output**:
```
🔧 Adding ML routes to API Gateway...
📍 Found API Gateway: abc123xyz
Creating /calculate-risk endpoint...
  ✅ /calculate-risk endpoint created
Creating /risk-score endpoint...
  ✅ /risk-score endpoint created
🚀 Deploying API changes...
✅ ML routes added successfully!
```

### Step 3: Test Backend Integration

Test the new endpoints:

```bash
# Get your API URL
API_URL="https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/prod"

# Test risk calculation
curl -X POST "$API_URL/calculate-risk" \
  -H "Content-Type: application/json" \
  -d '{"userId":"demo-user"}'

# Expected response:
# {
#   "ok": true,
#   "riskScore": 0.35,
#   "riskLevel": "moderate",
#   "riskFactors": [...],
#   "timestamp": "2025-10-19T10:30:00Z",
#   "interventionTriggered": false
# }

# Test risk retrieval
curl "$API_URL/risk-score?userId=demo-user"

# Expected response:
# {
#   "ok": true,
#   "riskScore": 0.35,
#   "riskLevel": "moderate",
#   "lastAssessment": "2025-10-19T10:30:00Z"
# }
```

### Step 4: Integrate Frontend Widget

#### Option A: Automatic Integration (Recommended)

Use the integration script to automatically add the widget:

```bash
# Make script executable
chmod +x scripts/integrate-ml-widget.sh

# Run integration
./scripts/integrate-ml-widget.sh
```

This creates `frontend/mind-mate-ml.html` with the widget integrated.

#### Option B: Manual Integration

Add the widget manually to your HTML file:

1. **Add CSS** (in `<head>`):
```html
<link rel="stylesheet" href="ml-wellness-widget.css">
```

2. **Add JavaScript** (before `</body>`):
```html
<script src="ml-wellness-widget.js"></script>
```

3. **Add Widget Container** (after header):
```html
<!-- ML Wellness Widget -->
<div id="ml-wellness-widget"></div>
```

4. **Initialize Widget** (in your JavaScript):
```javascript
window.onload = () => {
    initMLWidget(API, USER_ID);
    // ... your other initialization code
};
```

### Step 5: Deploy Frontend

Deploy the updated frontend to your hosting service:

```bash
# If using S3/CloudFront
aws s3 cp frontend/mind-mate-ml.html s3://your-bucket/index.html
aws s3 cp frontend/ml-wellness-widget.js s3://your-bucket/
aws s3 cp frontend/ml-wellness-widget.css s3://your-bucket/

# If using Amplify
# Push to your Git repository and Amplify will auto-deploy
```

### Step 6: Verify Integration

1. **Open the app** in your browser
2. **Log a mood** to generate data
3. **Check the wellness widget** - should show "No Data" initially
4. **Trigger assessment**:
   ```bash
   curl -X POST "$API_URL/calculate-risk" \
     -H "Content-Type: application/json" \
     -d '{"userId":"YOUR_USER_ID"}'
   ```
5. **Refresh the page** - widget should now show risk level
6. **Wait 5 minutes** - widget should auto-refresh

## 🎨 Widget Customization

### Change Colors

Edit `frontend/ml-wellness-widget.css`:

```css
/* Customize risk level colors */
.status-minimal {
    background: #your-color;
    color: #your-text-color;
}
```

### Change Refresh Interval

Edit `frontend/ml-wellness-widget.js`:

```javascript
// Change from 5 minutes to 10 minutes
this.checkInterval = setInterval(() => {
    this.loadRiskScore();
}, 10 * 60 * 1000);  // 10 minutes
```

### Customize Messages

Edit the `getRiskConfig()` method in `ml-wellness-widget.js`:

```javascript
minimal: {
    icon: '😊',
    title: 'Your Custom Title',
    message: 'Your custom message',
    class: 'status-minimal'
}
```

## 🔍 Monitoring & Debugging

### Check Lambda Logs

```bash
# View calculateRiskScore logs
aws logs tail /aws/lambda/calculateRiskScore --follow

# View executeIntervention logs
aws logs tail /aws/lambda/executeIntervention --follow
```

### Check DynamoDB Data

```bash
# Query risk assessments
aws dynamodb query \
  --table-name MindMate-RiskAssessments \
  --key-condition-expression "userId = :uid" \
  --expression-attribute-values '{":uid":{"S":"demo-user"}}'

# Query interventions
aws dynamodb scan \
  --table-name MindMate-Interventions \
  --limit 10
```

### Browser Console

Open browser DevTools and check:
- Network tab for API calls
- Console tab for JavaScript errors
- Look for `mlWidget` object

## 🐛 Troubleshooting

### Widget Not Showing

**Problem**: Widget container is empty

**Solutions**:
1. Check browser console for errors
2. Verify `ml-wellness-widget.js` is loaded
3. Ensure `initMLWidget()` is called
4. Check API URL is correct

### "No Data" Message

**Problem**: Widget shows "No Data" or "Unknown"

**Solutions**:
1. User needs to log moods first
2. Trigger manual assessment: `POST /calculate-risk`
3. Check Lambda logs for errors
4. Verify feature extraction Lambdas are working

### Risk Score Not Updating

**Problem**: Widget shows old data

**Solutions**:
1. Check auto-refresh is working (5 min interval)
2. Manually refresh: click 🔄 button
3. Verify `GET /risk-score` endpoint works
4. Check CORS headers in API Gateway

### Intervention Not Triggering

**Problem**: High risk but no intervention

**Solutions**:
1. Check `executeIntervention` Lambda logs
2. Verify Bedrock permissions
3. Check DynamoDB Interventions table
4. Ensure risk level is "high" or "critical"

## 📊 Testing Scenarios

### Test Low Risk

```bash
# Log several good moods
for i in {1..5}; do
  curl -X POST "$API_URL/mood" \
    -H "Content-Type: application/json" \
    -d '{"userId":"test-user","mood":8,"notes":"Feeling good"}'
  sleep 1
done

# Calculate risk
curl -X POST "$API_URL/calculate-risk" \
  -H "Content-Type: application/json" \
  -d '{"userId":"test-user"}'
```

### Test High Risk

```bash
# Log several low moods
for i in {1..5}; do
  curl -X POST "$API_URL/mood" \
    -H "Content-Type: application/json" \
    -d '{"userId":"test-user","mood":3,"notes":"Struggling today"}'
  sleep 1
done

# Calculate risk
curl -X POST "$API_URL/calculate-risk" \
  -H "Content-Type: application/json" \
  -d '{"userId":"test-user"}'

# Should trigger intervention
```

## 📈 Next Steps

### Immediate
- ✅ Backend Lambdas deployed
- ✅ API routes added
- ✅ Frontend widget integrated
- ✅ Basic testing complete

### Short Term (1-2 weeks)
- [ ] Set up automated daily assessments (EventBridge)
- [ ] Add push notifications for critical risk
- [ ] Create admin dashboard for monitoring
- [ ] Implement user opt-out mechanism

### Long Term (1-3 months)
- [ ] Train ML models with real data
- [ ] Replace rule-based scoring with ML predictions
- [ ] Implement model monitoring & retraining
- [ ] Add advanced analytics

## 📚 Additional Resources

- [ML System Design](docs/ML_INTEGRATION_COMPLETE.md)
- [API Reference](docs/API_REFERENCE.md)
- [Feature Extraction Guide](docs/ML_SETUP_GUIDE.md)
- [Training Data Guide](docs/TRAINING_DATA_GUIDE.md)

## 🆘 Support

If you encounter issues:

1. **Check Logs**: CloudWatch logs for all Lambdas
2. **Review Docs**: This guide and linked documentation
3. **Test Endpoints**: Use curl to test each endpoint
4. **Browser DevTools**: Check console and network tabs

## ✅ Integration Checklist

- [ ] ML infrastructure deployed
- [ ] Feature extraction Lambdas working
- [ ] calculateRiskScore Lambda deployed
- [ ] executeIntervention Lambda deployed
- [ ] API Gateway routes added
- [ ] Backend endpoints tested
- [ ] Frontend widget files added
- [ ] Widget initialized in app
- [ ] Frontend deployed
- [ ] End-to-end testing complete
- [ ] Monitoring set up
- [ ] Documentation reviewed

---

**Congratulations!** 🎉 Your Mind Mate app now has ML-powered proactive mental health monitoring!

**Last Updated**: October 19, 2025
**Version**: 1.0.0
