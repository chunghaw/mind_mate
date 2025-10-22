# ML Pipeline Explained: From Training Data to Web App

This document explains the complete machine learning pipeline for Mind Mate's risk prediction system.

---

## 🎯 Overview

The ML system predicts mental health crisis risk 3-7 days in advance by analyzing user behavior patterns. Here's the complete flow:

```
User Activity → Feature Extraction → ML Model → Risk Score → Intervention
     ↓                                    ↑
  DynamoDB                          SageMaker Training
```

---

## 📊 Part 1: Training Data

### What is the Training Data?

The training data is a CSV file with **49 features + 1 label** per sample. Each row represents a user's state over a period of time.

**File**: `sagemaker/example_training_data.csv`  
**Samples**: 10 synthetic examples (in production, you'd have thousands)  
**Purpose**: Teach the model to recognize patterns that precede mental health crises

### Training Data Structure

```csv
sample_id, [49 features], label
sample_000001, -0.15, 0.05, ..., 0
sample_000002, 0.05, -0.08, ..., 1
```

**Label**:
- `0` = No crisis occurred in next 7 days (healthy)
- `1` = Crisis occurred in next 7 days (at-risk)

### The 49 Features (Grouped by Category)

#### 1. Mood Features (21 features)
Extracted from daily mood logs (1-10 scale):

- **Trends**: `mood_trend_7day`, `mood_trend_14day`, `mood_trend_30day`
  - Example: `-0.25` means mood declining by 0.25 points per day
  - Negative trends = worsening mood

- **Averages**: `mood_mean_7day`, `mood_mean_14day`, `mood_mean_30day`
  - Example: `3.5` = average mood of 3.5/10 (low)
  - Lower values = worse mood

- **Volatility**: `mood_std_7day`, `mood_variance_7day`, `mood_volatility`
  - Example: `2.1` = high mood swings
  - Higher values = unstable mood

- **Extremes**: `mood_min_7day`, `mood_max_7day`, `consecutive_low_days`
  - Example: `consecutive_low_days=5` = 5 days in a row with mood < 4
  - More consecutive low days = higher risk

- **Patterns**: `low_mood_frequency`, `high_mood_frequency`, `weekend_mood_diff`
  - Example: `low_mood_frequency=0.71` = 71% of days had low mood
  - Higher frequency = higher risk

#### 2. Behavioral Features (15 features)
Extracted from app usage patterns:

- **Engagement**: `daily_checkin_frequency`, `avg_session_duration`, `engagement_trend`
  - Example: `daily_checkin_frequency=0.4` = only checking in 40% of days
  - Declining engagement = warning sign

- **Activity**: `activity_completion_rate`, `selfie_frequency`, `total_interactions`
  - Example: `activity_completion_rate=0.25` = only completing 25% of suggested activities
  - Lower completion = disengagement

- **Timing**: `late_night_usage`, `weekend_usage_change`
  - Example: `late_night_usage=12` = 12 sessions after midnight
  - Increased late-night usage = sleep disruption

- **Consistency**: `usage_consistency`, `response_time_trend`
  - Example: `usage_consistency=3.2` = erratic usage patterns
  - Higher inconsistency = instability

#### 3. Sentiment Features (13 features)
Extracted from chat messages using AWS Comprehend:

- **Trends**: `sentiment_trend_7day`, `sentiment_trend_30day`
  - Example: `0.18` = sentiment improving
  - Negative trends = worsening emotional state

- **Distribution**: `negative_sentiment_frequency`, `positive_sentiment_frequency`
  - Example: `negative_sentiment_frequency=0.75` = 75% of messages are negative
  - Higher negative frequency = higher risk

- **Scores**: `avg_negative_score`, `avg_positive_score`, `sentiment_volatility`
  - Example: `avg_negative_score=0.82` = very negative messages
  - Higher negative scores = higher risk

- **Keywords**: `despair_keywords`, `isolation_keywords`, `hopelessness_score`, `crisis_keywords`
  - Example: `crisis_keywords=2` = mentioned "suicide" or "end it" 2 times
  - Any crisis keywords = immediate high risk

### Example Training Samples

**Sample 1: Healthy User (label=0)**
```
mood_trend_7day: 0.12 (improving)
mood_mean_7day: 7.5 (good mood)
consecutive_low_days: 0 (no bad days)
negative_sentiment_frequency: 0.15 (mostly positive)
crisis_keywords: 0 (no crisis language)
→ Prediction: Low risk
```

**Sample 2: At-Risk User (label=1)**
```
mood_trend_7day: -0.32 (rapidly declining)
mood_mean_7day: 1.8 (very low mood)
consecutive_low_days: 6 (week of bad days)
negative_sentiment_frequency: 0.75 (mostly negative)
crisis_keywords: 2 (mentioned crisis language)
→ Prediction: High risk
```

---

## 🤖 Part 2: Model Training

### How Training Works

The training script (`train_simple.py`) does the following:

#### Step 1: Load Data
```python
df = pd.read_csv('example_training_data.csv')
# 10 samples with 49 features + 1 label
```

#### Step 2: Split Data (80/20)
```python
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2)
# Training: 8 samples
# Validation: 2 samples
```

#### Step 3: Train Two Models

**Random Forest**:
- Creates 200 decision trees
- Each tree learns different patterns
- Example: "If mood_trend < -0.2 AND consecutive_low_days > 4 → High Risk"
- Votes from all trees are averaged

**Gradient Boosting**:
- Creates 200 sequential trees
- Each tree corrects errors from previous trees
- Example: "Previous trees missed users with high late_night_usage → focus on that"
- More accurate but slower

#### Step 4: Ensemble Prediction
```python
rf_prediction = 0.65  # Random Forest says 65% risk
gb_prediction = 0.75  # Gradient Boosting says 75% risk
final_risk = (0.65 + 0.75) / 2 = 0.70  # 70% risk
```

#### Step 5: Evaluate Performance
```
AUC: 0.85 (85% accurate at distinguishing risk levels)
Recall: 0.80 (catches 80% of at-risk users)
Precision: 0.75 (75% of high-risk predictions are correct)
```

#### Step 6: Save Models
```
s3://mindmate-ml-models-{account}/models/{job-name}/output/
├── rf_model.pkl (Random Forest)
├── gb_model.pkl (Gradient Boosting)
├── feature_importance.csv (which features matter most)
└── metrics.json (performance stats)
```

### What Makes a Good Model?

**Target Metrics**:
- **AUC > 0.80**: Model can distinguish risk levels well
- **Recall > 0.75**: Catches most at-risk users (minimize false negatives)
- **Precision > 0.70**: Doesn't over-alert (minimize false positives)

**Why Recall Matters Most**:
- False Negative = Missing someone in crisis (BAD!)
- False Positive = Extra check-in for healthy user (OK)
- Better to be cautious in mental health

---

## 🔄 Part 3: Feature Extraction (Real-Time)

When a user interacts with the app, we extract the same 49 features:

### Lambda Functions

#### `extractMoodFeatures`
```javascript
// User logs mood daily
logMood(userId, mood=3, timestamp)

// Lambda calculates features
{
  mood_trend_7day: -0.25,  // Declining
  mood_mean_7day: 3.5,     // Low average
  consecutive_low_days: 4   // 4 bad days in a row
}
```

#### `extractBehavioralFeatures`
```javascript
// User interacts with app
chat(userId, message)
completeActivity(userId, activityId)

// Lambda calculates features
{
  daily_checkin_frequency: 0.6,  // Checking in 60% of days
  late_night_usage: 8,           // 8 late-night sessions
  engagement_trend: -0.15        // Declining engagement
}
```

#### `extractSentimentFeatures`
```javascript
// User sends chat message
message = "I feel hopeless and alone"

// AWS Comprehend analyzes sentiment
{
  sentiment: "NEGATIVE",
  negative_score: 0.85,
  despair_keywords: 1,      // "hopeless"
  isolation_keywords: 1     // "alone"
}
```

### Feature Storage

Features are stored in DynamoDB:
```json
{
  "userId": "user-123",
  "timestamp": "2025-10-22T10:00:00Z",
  "features": {
    "mood_trend_7day": -0.25,
    "mood_mean_7day": 3.5,
    // ... all 49 features
  }
}
```

---

## 🎯 Part 4: Risk Prediction (Real-Time)

### Lambda: `calculateRiskScore`

This Lambda runs daily for each user:

#### Step 1: Load Models from S3
```python
rf_model = joblib.load('s3://models/rf_model.pkl')
gb_model = joblib.load('s3://models/gb_model.pkl')
```

#### Step 2: Get User Features
```python
features = get_user_features(userId)
# Returns array of 49 values in correct order
feature_vector = [
  -0.25,  # mood_trend_7day
  3.5,    # mood_mean_7day
  # ... 47 more features
]
```

#### Step 3: Make Prediction
```python
rf_prob = rf_model.predict_proba([feature_vector])[0][1]  # 0.68
gb_prob = gb_model.predict_proba([feature_vector])[0][1]  # 0.72
risk_score = (rf_prob + gb_prob) / 2  # 0.70 (70% risk)
```

#### Step 4: Determine Risk Level
```python
if risk_score >= 0.7:
    risk_level = "high"      # Immediate intervention
elif risk_score >= 0.4:
    risk_level = "medium"    # Increased monitoring
else:
    risk_level = "low"       # Normal support
```

#### Step 5: Save to DynamoDB
```json
{
  "userId": "user-123",
  "timestamp": "2025-10-22T10:00:00Z",
  "riskScore": 0.70,
  "riskLevel": "high",
  "features": { /* 49 features */ },
  "interventionTriggered": true
}
```

---

## 🌐 Part 5: Web App Integration

### Frontend Display

The ML wellness widget shows risk information:

```javascript
// frontend/ml-wellness-widget.js

async function loadRiskScore(userId) {
  const response = await fetch(`/risk/calculate`, {
    method: 'POST',
    body: JSON.stringify({ userId })
  });
  
  const data = await response.json();
  // {
  //   riskScore: 0.70,
  //   riskLevel: "high",
  //   riskFactors: ["Declining mood trend", "High negative sentiment"],
  //   recommendation: "Consider reaching out to support"
  // }
  
  displayRiskScore(data);
}
```

### Visual Display

```html
<!-- High Risk -->
<div class="risk-indicator high">
  <div class="risk-score">70%</div>
  <div class="risk-level">High Risk</div>
  <div class="risk-factors">
    • Mood declining for 7 days
    • 75% negative sentiment
    • Increased late-night usage
  </div>
  <button>Get Support Now</button>
</div>

<!-- Low Risk -->
<div class="risk-indicator low">
  <div class="risk-score">25%</div>
  <div class="risk-level">Low Risk</div>
  <div class="message">You're doing great! Keep it up.</div>
</div>
```

---

## 🔄 Part 6: Automated Interventions

When high risk is detected:

### Lambda: `executeIntervention`

```python
if risk_level == "high":
    # Generate personalized message using Bedrock
    message = generate_intervention_message(userId, risk_factors)
    
    # Send via Bedrock Agent
    send_proactive_message(userId, message)
    
    # Log intervention
    log_intervention(userId, risk_score, message)
```

### Example Intervention

```
Hi Sarah,

I've noticed you've been having a tough week. Your mood has been 
lower than usual, and you've mentioned feeling isolated in our chats.

I'm here for you. Would you like to:
• Talk about what's been bothering you?
• Try a guided breathing exercise?
• Connect with a crisis counselor?

You don't have to go through this alone. 💙
```

---

## 📈 Part 7: Continuous Improvement

### Monthly Retraining

EventBridge triggers retraining monthly:

```python
# Lambda: prepareTrainingData

# 1. Collect new data from past month
users = get_all_users()
training_samples = []

for user in users:
    # Get features from 30 days ago
    features = get_features(user, date=30_days_ago)
    
    # Check if crisis occurred in next 7 days
    crisis_occurred = check_crisis(user, date=23_days_ago)
    
    training_samples.append({
        **features,
        'label': 1 if crisis_occurred else 0
    })

# 2. Upload to S3
save_to_s3(training_samples, 'training-data/monthly.csv')

# 3. Trigger SageMaker training
start_training_job('monthly-retrain')
```

### Model Monitoring

Track model performance over time:

```python
# Compare predictions vs actual outcomes
predictions = get_predictions(last_month)
actuals = get_actual_outcomes(last_month)

auc = calculate_auc(predictions, actuals)
recall = calculate_recall(predictions, actuals)

if auc < 0.75:
    alert_admin("Model performance degraded - retrain needed")
```

---

## 🎬 Complete Flow Example

### Day 1: User Logs Mood
```
User: Logs mood = 3/10
→ extractMoodFeatures: mood_mean_7day = 3.5
→ Stored in DynamoDB
```

### Day 2: User Chats
```
User: "I feel hopeless"
→ extractSentimentFeatures: negative_score = 0.85, despair_keywords = 1
→ Stored in DynamoDB
```

### Day 3: Daily Risk Assessment (6 AM)
```
EventBridge triggers calculateRiskScore
→ Load models from S3
→ Get all 49 features for user
→ Predict: risk_score = 0.72 (high)
→ Save to DynamoDB
→ Trigger intervention
```

### Day 3: Intervention Sent (6:05 AM)
```
executeIntervention
→ Generate personalized message
→ Send via Bedrock Agent
→ User receives proactive check-in
```

### Day 3: User Opens App (10 AM)
```
Frontend loads
→ Fetch risk score from API
→ Display: "High Risk - 72%"
→ Show risk factors
→ Offer support resources
```

### Month End: Retrain Models
```
EventBridge triggers prepareTrainingData
→ Collect 1000 new samples from past month
→ Upload to S3
→ Start SageMaker training
→ New models deployed
→ Improved accuracy
```

---

## 💡 Key Takeaways

1. **Training Data**: Historical patterns of users who did/didn't experience crises
2. **Features**: 49 metrics extracted from mood logs, behavior, and chat sentiment
3. **Models**: Ensemble of Random Forest + Gradient Boosting for robust predictions
4. **Real-Time**: Features extracted continuously, risk calculated daily
5. **Interventions**: Automated proactive support when high risk detected
6. **Continuous**: Models retrained monthly with new data for improvement

---

## 🔍 Current Status

**Training**: In progress (5-10 minutes)  
**Models**: Will be saved to S3 when complete  
**Integration**: Lambda functions ready to use models  
**Frontend**: Widget ready to display risk scores  

**Next Steps**:
1. Wait for training to complete
2. Copy models to 'latest' folder in S3
3. Update Lambda environment variables
4. Test end-to-end with real user data
5. Deploy to production

---

## 📚 Related Documents

- [ML Prediction Spec](./ML_PREDICTION_SPEC.md) - Full technical specification
- [ML Setup Guide](./ML_SETUP_GUIDE.md) - Deployment instructions
- [Training Data Guide](./TRAINING_DATA_GUIDE.md) - How to prepare training data
- [SageMaker Quick Deploy](../SAGEMAKER_QUICK_DEPLOY.md) - Quick start guide

