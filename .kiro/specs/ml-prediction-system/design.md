# Design Document - ML Prediction System

## Overview

The ML Prediction System implements a serverless machine learning pipeline on AWS to predict mental health crisis risk 3-7 days in advance. The system uses Lambda for feature extraction and inference, SageMaker for model training, DynamoDB for data storage, and EventBridge for orchestration. The architecture prioritizes scalability, cost-efficiency, and real-time responsiveness.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     ML Prediction System                         │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐         ┌──────────────────┐
│  EventBridge     │────────▶│  Risk Assessment │
│  (Daily 6AM UTC) │         │  Orchestrator    │
└──────────────────┘         └────────┬─────────┘
                                      │
                                      ▼
                            ┌──────────────────┐
                            │ Calculate Risk   │◀────── Models (S3)
                            │ Score Lambda     │
                            └────────┬─────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
          ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
          │   Extract   │  │   Extract   │  │   Extract   │
          │    Mood     │  │ Behavioral  │  │  Sentiment  │
          │  Features   │  │  Features   │  │  Features   │
          └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
                 │                │                 │
                 └────────────────┼─────────────────┘
                                  ▼
                         ┌─────────────────┐
                         │   DynamoDB      │
                         │  Risk Scores    │
                         └────────┬────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    ▼                           ▼
          ┌──────────────────┐        ┌──────────────────┐
          │  Intervention    │        │  Bedrock Claude  │
          │  Trigger Lambda  │───────▶│  (Personalized   │
          └──────────────────┘        │   Messages)      │
                                      └──────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     Training Pipeline                            │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐         ┌──────────────────┐
│  EventBridge     │────────▶│  Training Data   │
│  (Monthly)       │         │  Preparation     │
└──────────────────┘         └────────┬─────────┘
                                      │
                                      ▼
                            ┌──────────────────┐
                            │  Upload to S3    │
                            │  (train.csv)     │
                            └────────┬─────────┘
                                     │
                                     ▼
                            ┌──────────────────┐
                            │   SageMaker      │
                            │   Training Job   │
                            └────────┬─────────┘
                                     │
                                     ▼
                            ┌──────────────────┐
                            │  Save Models     │
                            │  to S3           │
                            └──────────────────┘
```

## Components and Interfaces

### 1. Feature Extraction Lambdas

#### extractMoodFeatures
```python
# Input
{
    "userId": "user123",
    "days": 30
}

# Output
{
    "mood_trend_7day": -0.15,
    "mood_mean_7day": 5.2,
    "mood_std_7day": 1.8,
    "mood_volatility": 1.2,
    "consecutive_low_days": 2,
    "low_mood_frequency": 0.28,
    "missing_days_7day": 1
}
```

**Implementation:**
- Query DynamoDB MoodLogs table for user's last 30 days
- Calculate statistical features using numpy
- Handle missing data with median imputation
- Return feature dictionary

#### extractBehavioralFeatures
```python
# Input
{
    "userId": "user123",
    "days": 30
}

# Output
{
    "daily_checkin_frequency": 0.85,
    "avg_session_duration": 180,
    "engagement_decline": -0.05,
    "activity_completion_rate": 0.72,
    "negative_word_frequency": 0.15,
    "late_night_usage": 3
}
```

**Implementation:**
- Query DynamoDB Interactions and ActivityCompletions tables
- Calculate engagement metrics
- Analyze message content for patterns
- Return feature dictionary

#### extractSentimentFeatures
```python
# Input
{
    "userId": "user123",
    "days": 30
}

# Output
{
    "sentiment_trend_7day": -0.08,
    "negative_sentiment_frequency": 0.35,
    "avg_negative_score": 0.42,
    "sentiment_volatility": 0.18,
    "despair_keywords": 2,
    "hopelessness_score": 0.25
}
```

**Implementation:**
- Query DynamoDB Messages table
- Call AWS Comprehend DetectSentiment API for each message
- Aggregate sentiment scores
- Detect crisis keywords
- Return feature dictionary

### 2. Risk Scoring Lambda

#### calculateRiskScore
```python
# Input
{
    "userId": "user123"
}

# Output
{
    "statusCode": 200,
    "riskScore": 0.68,
    "riskLevel": "high",
    "timestamp": "2025-10-19T10:30:00Z",
    "features": {...},
    "interventionTriggered": true
}
```

**Implementation:**
```python
import boto3
import joblib
import numpy as np
from datetime import datetime

s3 = boto3.client('s3')
lambda_client = boto3.client('lambda')
dynamodb = boto3.resource('dynamodb')

# Global model cache
rf_model = None
gb_model = None

def lambda_handler(event, context):
    global rf_model, gb_model
    
    # Load models if not cached
    if rf_model is None:
        rf_model = load_model_from_s3('models/rf_model.pkl')
        gb_model = load_model_from_s3('models/gb_model.pkl')
    
    user_id = event['userId']
    
    # Extract all features in parallel
    features = extract_all_features(user_id)
    
    # Prepare feature vector
    feature_vector = prepare_feature_vector(features)
    
    # Get ensemble predictions
    rf_prob = rf_model.predict_proba([feature_vector])[0][1]
    gb_prob = gb_model.predict_proba([feature_vector])[0][1]
    risk_score = (rf_prob + gb_prob) / 2
    
    # Classify risk level
    risk_level = classify_risk_level(risk_score)
    
    # Store assessment
    store_risk_assessment(user_id, risk_score, risk_level, features)
    
    # Trigger interventions if needed
    intervention_triggered = False
    if risk_level in ['high', 'critical']:
        trigger_intervention(user_id, risk_level, risk_score)
        intervention_triggered = True
    
    return {
        'statusCode': 200,
        'riskScore': float(risk_score),
        'riskLevel': risk_level,
        'timestamp': datetime.utcnow().isoformat(),
        'interventionTriggered': intervention_triggered
    }

def extract_all_features(user_id):
    # Invoke feature extraction Lambdas in parallel
    mood_response = lambda_client.invoke(
        FunctionName='extractMoodFeatures',
        InvocationType='RequestResponse',
        Payload=json.dumps({'userId': user_id, 'days': 30})
    )
    
    behavioral_response = lambda_client.invoke(
        FunctionName='extractBehavioralFeatures',
        InvocationType='RequestResponse',
        Payload=json.dumps({'userId': user_id, 'days': 30})
    )
    
    sentiment_response = lambda_client.invoke(
        FunctionName='extractSentimentFeatures',
        InvocationType='RequestResponse',
        Payload=json.dumps({'userId': user_id, 'days': 30})
    )
    
    # Combine features
    features = {
        **json.loads(mood_response['Payload'].read()),
        **json.loads(behavioral_response['Payload'].read()),
        **json.loads(sentiment_response['Payload'].read())
    }
    
    return features

def classify_risk_level(risk_score):
    if risk_score >= 0.8:
        return 'critical'
    elif risk_score >= 0.6:
        return 'high'
    elif risk_score >= 0.4:
        return 'moderate'
    elif risk_score >= 0.2:
        return 'low'
    else:
        return 'minimal'
```

### 3. Training Pipeline

#### prepareTrainingData
```python
# Input (EventBridge scheduled)
{}

# Output
{
    "statusCode": 200,
    "s3TrainingPath": "s3://bucket/training/train.csv",
    "s3ValidationPath": "s3://bucket/training/validation.csv",
    "totalSamples": 5000,
    "positiveClass": 450,
    "negativeClass": 4550
}
```

**Implementation:**
```python
def lambda_handler(event, context):
    # Get users with sufficient history
    users = get_users_with_history(min_days=60)
    
    dataset = []
    for user in users:
        # Extract features
        features = extract_all_features(user['userId'])
        
        # Get label (crisis in next 7 days?)
        label = check_crisis_occurred(user['userId'], days_ahead=7)
        
        dataset.append({
            **features,
            'label': label
        })
    
    # Split train/validation
    train_df, val_df = train_test_split(dataset, test_size=0.2, stratify=labels)
    
    # Upload to S3
    train_path = upload_to_s3(train_df, 'training/train.csv')
    val_path = upload_to_s3(val_df, 'training/validation.csv')
    
    return {
        'statusCode': 200,
        's3TrainingPath': train_path,
        's3ValidationPath': val_path,
        'totalSamples': len(dataset),
        'positiveClass': sum(labels),
        'negativeClass': len(labels) - sum(labels)
    }
```

#### triggerModelTraining
```python
# Input
{
    "s3TrainingPath": "s3://bucket/training/train.csv",
    "s3ValidationPath": "s3://bucket/training/validation.csv"
}

# Output
{
    "statusCode": 200,
    "trainingJobName": "mindmate-risk-model-20251019",
    "trainingJobArn": "arn:aws:sagemaker:..."
}
```

**Implementation:**
```python
import sagemaker
from sagemaker.sklearn.estimator import SKLearn

def lambda_handler(event, context):
    # Configure SageMaker estimator
    sklearn_estimator = SKLearn(
        entry_point='train.py',
        source_dir='training_scripts/',
        role=os.environ['SAGEMAKER_ROLE'],
        instance_type='ml.m5.xlarge',
        instance_count=1,
        framework_version='1.0-1',
        py_version='py3',
        hyperparameters={
            'n_estimators': 200,
            'max_depth': 10,
            'min_samples_split': 5,
            'class_weight': 'balanced'
        }
    )
    
    # Start training
    sklearn_estimator.fit({
        'train': event['s3TrainingPath'],
        'validation': event['s3ValidationPath']
    })
    
    return {
        'statusCode': 200,
        'trainingJobName': sklearn_estimator.latest_training_job.name,
        'trainingJobArn': sklearn_estimator.latest_training_job.describe()['TrainingJobArn']
    }
```

### 4. Intervention System

#### executeIntervention
```python
# Input
{
    "userId": "user123",
    "riskLevel": "high",
    "riskScore": 0.68
}

# Output
{
    "statusCode": 200,
    "interventionsSent": ["proactive_checkin", "coping_activities"],
    "messageGenerated": true
}
```

**Implementation:**
```python
def lambda_handler(event, context):
    user_id = event['userId']
    risk_level = event['riskLevel']
    risk_score = event['riskScore']
    
    interventions_sent = []
    
    if risk_level == 'critical':
        send_crisis_resources(user_id)
        interventions_sent.append('crisis_resources')
        
        send_push_notification(user_id, {
            'title': 'Help is available 24/7',
            'body': 'You don\'t have to face this alone. Tap for resources.',
            'priority': 'high'
        })
        interventions_sent.append('push_notification')
    
    if risk_level in ['high', 'critical']:
        # Generate personalized message
        message = generate_proactive_message(user_id, risk_level)
        create_priority_chat_message(user_id, message)
        interventions_sent.append('proactive_checkin')
        
        # Suggest coping activities
        suggest_coping_activities(user_id, risk_score)
        interventions_sent.append('coping_activities')
    
    # Log intervention
    log_intervention(user_id, risk_level, risk_score, interventions_sent)
    
    return {
        'statusCode': 200,
        'interventionsSent': interventions_sent,
        'messageGenerated': True
    }

def generate_proactive_message(user_id, risk_level):
    bedrock = boto3.client('bedrock-runtime')
    
    profile = get_user_profile(user_id)
    history = get_recent_conversations(user_id, days=7)
    mood_trend = get_mood_trend(user_id, days=7)
    
    prompt = f"""You are {profile['petName']}, an empathetic AI companion with a {profile['personality']} personality.

Based on recent patterns, generate a caring, proactive check-in message for {profile['userName']}.

Risk Level: {risk_level}
Recent Mood Trend: {mood_trend}
Recent Context: {summarize_history(history)}

Generate a warm, non-alarming message that:
1. Shows you've noticed they might be struggling
2. References specific recent context
3. Offers specific support
4. Suggests 2-3 helpful activities
5. Reminds them they're not alone

Keep it natural and conversational (under 100 words), not clinical."""
    
    response = bedrock.invoke_model(
        modelId='anthropic.claude-3-sonnet-20240229',
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 300,
            "messages": [{"role": "user", "content": prompt}]
        })
    )
    
    message = json.loads(response['body'].read())['content'][0]['text']
    return message
```

## Data Models

### RiskAssessments Table (DynamoDB)
```
{
    "userId": "user123",                    // Partition Key
    "timestamp": "2025-10-19T10:30:00Z",   // Sort Key
    "riskScore": 0.68,
    "riskLevel": "high",
    "features": {
        "mood_trend_7day": -0.15,
        "mood_mean_7day": 5.2,
        // ... all features
    },
    "interventionsTriggered": ["proactive_checkin", "coping_activities"],
    "ttl": 1729420800                      // 90 days retention
}
```

### TrainingJobs Table (DynamoDB)
```
{
    "jobId": "mindmate-risk-model-20251019",  // Partition Key
    "status": "Completed",
    "startTime": "2025-10-19T08:00:00Z",
    "endTime": "2025-10-19T08:45:00Z",
    "metrics": {
        "auc": 0.82,
        "precision": 0.65,
        "recall": 0.78,
        "f1": 0.71
    },
    "modelS3Path": "s3://bucket/models/rf_model.pkl",
    "featureImportance": [
        {"feature": "mood_trend_7day", "importance": 0.15},
        {"feature": "consecutive_low_days", "importance": 0.12}
    ]
}
```

### Interventions Table (DynamoDB)
```
{
    "interventionId": "uuid",               // Partition Key
    "userId": "user123",
    "timestamp": "2025-10-19T10:30:00Z",
    "riskLevel": "high",
    "riskScore": 0.68,
    "interventionType": "proactive_checkin",
    "messageGenerated": "Hey Sarah, I've noticed...",
    "userResponse": "Thanks, I needed this",
    "responseTimestamp": "2025-10-19T11:15:00Z",
    "effectiveness": "helpful"
}
```

## Error Handling

### Feature Extraction Failures
- **Scenario**: User has insufficient data
- **Handling**: Return partial features with defaults for missing values
- **Logging**: Log warning with user ID and missing data types

### Model Loading Failures
- **Scenario**: S3 model file is corrupted or missing
- **Handling**: Retry 3 times, then use fallback rule-based scoring
- **Alerting**: Send SNS alert to administrators

### Comprehend API Failures
- **Scenario**: Rate limit or service error
- **Handling**: Skip sentiment analysis, use text-based keyword detection
- **Logging**: Log error and continue with available features

### Training Data Insufficient
- **Scenario**: Less than 100 users with 60+ days of data
- **Handling**: Skip training, keep using existing models
- **Alerting**: Send notification to administrators

## Testing Strategy

### Unit Tests
- Test feature extraction functions with mock data
- Test risk classification logic
- Test intervention trigger conditions
- Test model loading and caching

### Integration Tests
- Test end-to-end risk assessment flow
- Test training pipeline with sample data
- Test intervention delivery
- Test DynamoDB read/write operations

### Performance Tests
- Load test with 10,000 concurrent risk assessments
- Measure Lambda cold start times
- Test model inference latency
- Verify DynamoDB throughput

### Validation Tests
- Validate model predictions against historical data
- Test false positive/negative rates
- Verify intervention effectiveness
- Test privacy and data anonymization

## Deployment Strategy

### Phase 1: Infrastructure Setup
1. Create DynamoDB tables
2. Deploy feature extraction Lambdas
3. Set up S3 buckets for models and training data
4. Configure IAM roles and permissions

### Phase 2: Training Pipeline
1. Deploy training data preparation Lambda
2. Create SageMaker training script
3. Run initial training with historical data
4. Validate model performance

### Phase 3: Risk Scoring
1. Deploy risk scoring Lambda
2. Deploy intervention Lambda
3. Set up EventBridge rules for daily assessment
4. Test with small user subset

### Phase 4: Monitoring
1. Set up CloudWatch dashboards
2. Configure SNS alerts
3. Deploy model monitoring Lambda
4. Enable automated retraining

## Cost Optimization

### Lambda Optimization
- Use 1024MB memory for feature extraction (balance speed/cost)
- Cache models in Lambda memory (reduce S3 calls)
- Use asynchronous invocation for non-critical paths

### SageMaker Optimization
- Use ml.m5.xlarge (sufficient for 10K users)
- Train monthly instead of weekly
- Use spot instances for training (70% cost savings)

### DynamoDB Optimization
- Use on-demand pricing for RiskAssessments table
- Enable TTL for 90-day retention
- Use GSI only where necessary

### Estimated Monthly Costs (10K users)
- Lambda: $50 (feature extraction + inference)
- SageMaker: $30 (monthly training with spot instances)
- DynamoDB: $40 (on-demand with TTL)
- Comprehend: $30 (sentiment analysis)
- S3: $5 (model storage)
- **Total: ~$155/month**

## Security Considerations

### Data Protection
- Encrypt all data at rest using KMS
- Use TLS for all data in transit
- Anonymize PII before training
- Implement least-privilege IAM policies

### Privacy
- Allow users to opt-out of ML predictions
- Never show raw risk scores to users
- Provide transparency about data usage
- Implement data retention policies (90 days)

### Compliance
- Log all risk assessments for audit
- Implement human oversight for critical alerts
- Provide data export capabilities
- Support data deletion requests
