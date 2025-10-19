# ML System Integration Guide

## Overview

This guide explains how the ML Prediction System is integrated into the Mind Mate app, covering both backend and frontend components.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Mind Mate App                             │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │   Mood     │  │   Selfie   │  │   Stats    │            │
│  │   Logging  │  │  Analysis  │  │  Dashboard │            │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘            │
│        │               │               │                     │
│        └───────────────┼───────────────┘                     │
│                        │                                     │
│                        ▼                                     │
│              ┌──────────────────┐                           │
│              │  ML Wellness     │                           │
│              │  Widget          │                           │
│              └────────┬─────────┘                           │
└───────────────────────┼─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  ML Backend System                           │
│                                                              │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │ calculateRiskScore│────────▶│ Feature          │         │
│  │ Lambda            │         │ Extraction       │         │
│  └────────┬─────────┘         │ Lambdas          │         │
│           │                    └──────────────────┘         │
│           │                                                  │
│           ▼                                                  │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │ Risk Assessment  │────────▶│ executeIntervention│        │
│  │ Storage          │         │ Lambda            │         │
│  └──────────────────┘         └──────────────────┘         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Backend Components

### 1. calculateRiskScore Lambda

**Purpose**: Calculate risk scores for users based on extracted features

**Location**: `backend/lambdas/calculateRiskScore/lambda_function.py`

**Key Features**:
- Invokes feature extraction Lambdas in parallel
- Calculates rule-based risk score (ML models coming soon)
- Classifies risk into 5 levels: minimal, low, moderate, high, critical
- Stores assessment in DynamoDB
- Triggers interventions for high/critical risk

**API Endpoint**: `POST /calculate-risk`

**Request**:
```json
{
  "userId": "user123"
}
```

**Response**:
```json
{
  "ok": true,
  "riskScore": 0.68,
  "riskLevel": "high",
  "riskFactors": [
    "Low average mood (3.5/10)",
    "Declining mood trend (-0.25)",
    "High negative sentiment (65%)"
  ],
  "timestamp": "2025-10-19T10:30:00Z",
  "interventionTriggered": true
}
```

### 2. executeIntervention Lambda

**Purpose**: Execute proactive interventions for at-risk users

**Location**: `backend/lambdas/executeIntervention/lambda_function.py`

**Key Features**:
- Generates personalized messages using Bedrock Claude
- Creates priority chat messages
- Suggests coping activities based on risk level
- Logs all interventions for tracking
- Includes crisis resources for critical risk

**Triggered By**: calculateRiskScore Lambda (async)

**Intervention Types**:
- **High Risk**: Proactive check-in + coping activities
- **Critical Risk**: Crisis resources + immediate support

### 3. getRiskScore Lambda

**Purpose**: Retrieve latest risk assessment for a user

**Location**: `backend/lambdas/getRiskScore/lambda_function.py`

**API Endpoint**: `GET /risk-score?userId=user123`

**Response**:
```json
{
  "ok": true,
  "riskScore": 0.68,
  "riskLevel": "high",
  "lastAssessment": "2025-10-19T10:30:00Z",
  "interventionTriggered": true
}
```

## Frontend Components

### 1. ML Wellness Widget

**Purpose**: Display real-time wellness status in the app

**Location**: `frontend/ml-wellness-widget.js`

**Features**:
- Auto-refreshes every 5 minutes
- Shows risk level with color-coded status
- Displays time since last assessment
- Alerts user when interventions are triggered
- Manual refresh button

**Integration**:
```html
<!-- Add to HTML -->
<link rel="stylesheet" href="ml-wellness-widget.css">
<script src="ml-wellness-widget.js"></script>

<!-- Add widget container -->
<div id="ml-wellness-widget"></div>

<!-- Initialize -->
<script>
  initMLWidget(API_URL, USER_ID);
</script>
```

### 2. Widget Styles

**Location**: `frontend/ml-wellness-widget.css`

**Risk Level Colors**:
- **Minimal**: Green (#dcfce7) - "Doing Great"
- **Low**: Blue (#dbeafe) - "Doing Well"
- **Moderate**: Yellow (#fef3c7) - "Check In"
- **High**: Orange (#fed7aa) - "Need Support"
- **Critical**: Red (#fecaca) - "Reach Out"

## Integration Steps

### Step 1: Deploy Backend

```bash
# Deploy ML integration Lambdas
./infrastructure/deploy-ml-lambdas.sh

# Add API Gateway routes
./infrastructure/add-ml-routes.sh
```

### Step 2: Update Frontend

Add the ML wellness widget to your main app file:

```html
<!DOCTYPE html>
<html>
<head>
    <!-- Existing styles -->
    <link rel="stylesheet" href="ml-wellness-widget.css">
</head>
<body>
    <div class="container">
        <!-- Existing header -->
        
        <!-- Add ML Wellness Widget -->
        <div id="ml-wellness-widget"></div>
        
        <!-- Existing navigation and content -->
    </div>
    
    <!-- Existing scripts -->
    <script src="ml-wellness-widget.js"></script>
    <script>
        const API = "YOUR_API_URL";
        const USER_ID = "YOUR_USER_ID";
        
        // Initialize ML widget
        window.onload = () => {
            initMLWidget(API, USER_ID);
            // ... other initialization
        };
    </script>
</body>
</html>
```

### Step 3: Test Integration

```bash
# Test risk calculation
curl -X POST "$API_URL/calculate-risk" \
  -H "Content-Type: application/json" \
  -d '{"userId":"demo-user"}'

# Test risk retrieval
curl "$API_URL/risk-score?userId=demo-user"
```

## Data Flow

### 1. User Logs Mood
```
User → logMood Lambda → DynamoDB (MoodLogs)
```

### 2. Risk Assessment Triggered
```
calculateRiskScore → extractMoodFeatures
                  → extractBehavioralFeatures  
                  → extractSentimentFeatures
                  → Calculate Risk Score
                  → Store in DynamoDB
                  → (if high/critical) → executeIntervention
```

### 3. Intervention Execution
```
executeIntervention → Get User Profile
                   → Generate Message (Bedrock)
                   → Create Chat Message
                   → Suggest Activities
                   → Log Intervention
```

### 4. Frontend Display
```
ML Widget → GET /risk-score → Display Status
         → Auto-refresh every 5 min
         → Show alerts if intervention triggered
```

## Environment Variables

Add to `.env`:
```bash
# ML System
RISK_ASSESSMENTS_TABLE=MindMate-RiskAssessments
INTERVENTIONS_TABLE=MindMate-Interventions
ML_MODELS_BUCKET=mindmate-ml-models-ACCOUNT_ID
ML_LAMBDA_ROLE_ARN=arn:aws:iam::ACCOUNT_ID:role/MindMate-MLLambdaRole
```

## Monitoring

### CloudWatch Metrics
- Risk assessment execution count
- Risk level distribution
- Intervention trigger rate
- Feature extraction latency

### CloudWatch Logs
- `/aws/lambda/calculateRiskScore`
- `/aws/lambda/executeIntervention`
- `/aws/lambda/getRiskScore`

## Future Enhancements

### Phase 1 (Current)
- ✅ Rule-based risk scoring
- ✅ Feature extraction pipeline
- ✅ Intervention system
- ✅ Frontend widget

### Phase 2 (Next)
- [ ] ML model training (SageMaker)
- [ ] Model-based predictions
- [ ] Automated daily assessments
- [ ] Model monitoring & retraining

### Phase 3 (Future)
- [ ] Push notifications
- [ ] Email alerts
- [ ] Advanced analytics dashboard
- [ ] Personalized intervention strategies

## Troubleshooting

### Widget Not Loading
- Check API URL is correct
- Verify CORS is enabled on API Gateway
- Check browser console for errors

### Risk Score Not Updating
- Ensure user has logged moods recently
- Check Lambda execution logs
- Verify DynamoDB tables exist

### Interventions Not Triggering
- Check executeIntervention Lambda logs
- Verify Bedrock access permissions
- Check DynamoDB write permissions

## API Reference

### POST /calculate-risk
Trigger a new risk assessment for a user.

### GET /risk-score
Get the latest risk assessment for a user.

### POST /mood
Log a mood entry (existing endpoint, triggers feature extraction).

## Security Considerations

- All API endpoints use HTTPS
- DynamoDB data encrypted at rest (KMS)
- Lambda functions use least-privilege IAM roles
- User data anonymized in training datasets
- 90-day TTL on risk assessments

## Cost Estimates

**Per 1000 users/day**:
- Lambda executions: ~$2
- DynamoDB: ~$3
- Bedrock (interventions): ~$1
- **Total: ~$6/day or $180/month**

## Support

For issues or questions:
1. Check CloudWatch logs
2. Review this integration guide
3. Consult main ML system documentation
4. Contact development team

---

**Last Updated**: October 19, 2025
**Version**: 1.0.0
