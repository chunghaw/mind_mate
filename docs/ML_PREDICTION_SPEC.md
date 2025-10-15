# ML Prediction System - Technical Specification

## 🧠 Overview

Predictive mental health modeling to identify risk patterns 3-7 days before crisis points. Uses SageMaker for custom risk prediction with mood trends, sentiment analysis, and behavioral patterns.

## 🏗️ Architecture

```
Daily Data Collection
    ↓
Feature Engineering Pipeline
    ↓
SageMaker Training Pipeline
    ↓
Real-time Risk Scoring
    ↓
Early Warning System
    ↓
Proactive Interventions
```

## 📊 Feature Engineering

### **1. Mood Features**
```python
# Lambda: extractMoodFeatures

import numpy as np
from datetime import datetime, timedelta

def extract_mood_features(user_id, days=30):
    moods = get_user_moods(user_id, days)
    
    features = {
        # Trend features
        'mood_trend_7day': calculate_trend(moods[-7:]),
        'mood_trend_14day': calculate_trend(moods[-14:]),
        'mood_trend_30day': calculate_trend(moods[-30:]),
        
        # Statistical features
        'mood_mean_7day': np.mean([m['mood'] for m in moods[-7:]]),
        'mood_std_7day': np.std([m['mood'] for m in moods[-7:]]),
        'mood_variance_7day': np.var([m['mood'] for m in moods[-7:]]),
        'mood_min_7day': np.min([m['mood'] for m in moods[-7:]]),
        'mood_max_7day': np.max([m['mood'] for m in moods[-7:]]),
        
        # Pattern features
        'mood_volatility': calculate_volatility(moods),
        'consecutive_low_days': count_consecutive_low(moods, threshold=4),
        'consecutive_high_days': count_consecutive_high(moods, threshold=7),
        'mood_decline_rate': calculate_decline_rate(moods),
        
        # Frequency features
        'low_mood_frequency': len([m for m in moods[-7:] if m['mood'] <= 3]) / 7,
        'high_mood_frequency': len([m for m in moods[-7:] if m['mood'] >= 8]) / 7,
        'missing_days_7day': 7 - len(moods[-7:]),
        
        # Temporal features
        'weekend_mood_diff': calculate_weekend_difference(moods),
        'morning_vs_evening': calculate_time_difference(moods),
    }
    
    return features

def calculate_trend(moods):
    if len(moods) < 2:
        return 0
    
    x = np.arange(len(moods))
    y = [m['mood'] for m in moods]
    slope, _ = np.polyfit(x, y, 1)
    return slope

def calculate_volatility(moods):
    if len(moods) < 2:
        return 0
    
    mood_values = [m['mood'] for m in moods]
    daily_changes = [abs(mood_values[i] - mood_values[i-1]) for i in range(1, len(mood_values))]
    return np.mean(daily_changes)
```

### **2. Behavioral Features**
```python
def extract_behavioral_features(user_id, days=30):
    interactions = get_user_interactions(user_id, days)
    completions = get_activity_completions(user_id, days)
    
    features = {
        # Engagement features
        'daily_checkin_frequency': len(interactions) / days,
        'avg_session_duration': np.mean([i['duration'] for i in interactions]),
        'response_time_trend': calculate_response_time_trend(interactions),
        'engagement_decline': calculate_engagement_decline(interactions),
        
        # Activity features
        'activity_completion_rate': len([c for c in completions if c['completed']]) / max(len(completions), 1),
        'helpful_activity_rate': len([c for c in completions if c['helpful']]) / max(len(completions), 1),
        'activity_diversity': len(set([c['category'] for c in completions])),
        'preferred_activity_types': get_preferred_categories(completions),
        
        # Communication features
        'avg_message_length': np.mean([len(i['message']) for i in interactions if i.get('message')]),
        'negative_word_frequency': calculate_negative_words(interactions),
        'help_seeking_frequency': calculate_help_seeking(interactions),
        'crisis_keywords': detect_crisis_keywords(interactions),
        
        # Temporal patterns
        'late_night_usage': count_late_night_interactions(interactions),
        'weekend_usage_change': calculate_weekend_usage_change(interactions),
        'usage_consistency': calculate_usage_consistency(interactions),
    }
    
    return features
```

### **3. Sentiment Features**
```python
def extract_sentiment_features(user_id, days=30):
    messages = get_user_messages(user_id, days)
    
    # Use Comprehend for sentiment analysis
    comprehend = boto3.client('comprehend')
    
    sentiments = []
    for message in messages:
        try:
            response = comprehend.detect_sentiment(
                Text=message['text'],
                LanguageCode='en'
            )
            sentiments.append({
                'sentiment': response['Sentiment'],
                'scores': response['SentimentScore'],
                'timestamp': message['timestamp']
            })
        except Exception as e:
            continue
    
    features = {
        # Sentiment trends
        'sentiment_trend_7day': calculate_sentiment_trend(sentiments[-7:]),
        'negative_sentiment_frequency': len([s for s in sentiments if s['sentiment'] == 'NEGATIVE']) / len(sentiments),
        'positive_sentiment_frequency': len([s for s in sentiments if s['sentiment'] == 'POSITIVE']) / len(sentiments),
        
        # Sentiment scores
        'avg_negative_score': np.mean([s['scores']['Negative'] for s in sentiments]),
        'avg_positive_score': np.mean([s['scores']['Positive'] for s in sentiments]),
        'sentiment_volatility': calculate_sentiment_volatility(sentiments),
        
        # Crisis indicators
        'despair_keywords': count_despair_keywords(messages),
        'isolation_keywords': count_isolation_keywords(messages),
        'hopelessness_score': calculate_hopelessness_score(messages),
    }
    
    return features
```

### **4. Contextual Features**
```python
def extract_contextual_features(user_id, days=30):
    profile = get_user_profile(user_id)
    external_data = get_external_context(user_id, days)
    
    features = {
        # User demographics
        'user_age_group': profile.get('ageGroup', 'unknown'),
        'user_timezone': profile.get('timezone', 'UTC'),
        'days_since_signup': (datetime.now() - profile['createdAt']).days,
        
        # Seasonal patterns
        'season': get_current_season(),
        'daylight_hours': get_daylight_hours(profile.get('location')),
        'weather_pattern': get_weather_pattern(profile.get('location'), days),
        
        # Social context
        'social_interaction_frequency': calculate_social_interactions(user_id, days),
        'support_network_size': len(profile.get('emergencyContacts', [])),
        
        # Life events
        'recent_life_events': detect_life_events(user_id, days),
        'stress_triggers': identify_stress_triggers(user_id, days),
    }
    
    return features
```

## 🤖 SageMaker Model Training

### **1. Training Pipeline**
```python
# Lambda: triggerModelTraining

import sagemaker
from sagemaker.sklearn.estimator import SKLearn
from sagemaker.tuner import HyperparameterTuner

def lambda_handler(event, context):
    # Prepare training data
    training_data = prepare_training_dataset()
    
    # Upload to S3
    s3_input_train = upload_to_s3(training_data, 'training')
    s3_input_validation = upload_to_s3(training_data, 'validation')
    
    # Configure SageMaker estimator
    sklearn_estimator = SKLearn(
        entry_point='train.py',
        role=get_sagemaker_role(),
        instance_type='ml.m5.xlarge',
        framework_version='1.0-1',
        hyperparameters={
            'n_estimators': 200,
            'max_depth': 10,
            'min_samples_split': 5,
            'class_weight': 'balanced'
        }
    )
    
    # Start training
    sklearn_estimator.fit({
        'train': s3_input_train,
        'validation': s3_input_validation
    })
    
    return {
        'statusCode': 200,
        'trainingJobName': sklearn_estimator.latest_training_job.name
    }

def prepare_training_dataset():
    # Get all users with sufficient history
    users = get_users_with_history(min_days=60)
    
    dataset = []
    for user in users:
        # Extract features
        mood_features = extract_mood_features(user['userId'])
        behavioral_features = extract_behavioral_features(user['userId'])
        sentiment_features = extract_sentiment_features(user['userId'])
        contextual_features = extract_contextual_features(user['userId'])
        
        # Combine features
        features = {
            **mood_features,
            **behavioral_features,
            **sentiment_features,
            **contextual_features
        }
        
        # Get label (did user experience crisis in next 7 days?)
        label = check_crisis_occurred(user['userId'], days_ahead=7)
        
        dataset.append({
            'features': features,
            'label': label,
            'userId': user['userId']
        })
    
    return dataset
```

### **2. Training Script**
```python
# train.py (uploaded to SageMaker)

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import cross_val_score
from sklearn.metrics import precision_recall_curve, roc_auc_score
import joblib
import argparse
import os

def train_model(args):
    # Load training data
    train_df = pd.read_csv(os.path.join(args.train, 'train.csv'))
    val_df = pd.read_csv(os.path.join(args.validation, 'validation.csv'))
    
    # Separate features and labels
    X_train = train_df.drop(['label', 'userId'], axis=1)
    y_train = train_df['label']
    X_val = val_df.drop(['label', 'userId'], axis=1)
    y_val = val_df['label']
    
    # Handle missing values
    X_train = X_train.fillna(X_train.median())
    X_val = X_val.fillna(X_train.median())
    
    # Train ensemble model
    rf_model = RandomForestClassifier(
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
        min_samples_split=args.min_samples_split,
        class_weight=args.class_weight,
        random_state=42
    )
    
    gb_model = GradientBoostingClassifier(
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
        learning_rate=0.1,
        random_state=42
    )
    
    # Train models
    rf_model.fit(X_train, y_train)
    gb_model.fit(X_train, y_train)
    
    # Ensemble predictions
    rf_pred = rf_model.predict_proba(X_val)[:, 1]
    gb_pred = gb_model.predict_proba(X_val)[:, 1]
    ensemble_pred = (rf_pred + gb_pred) / 2
    
    # Evaluate
    auc_score = roc_auc_score(y_val, ensemble_pred)
    print(f'Validation AUC: {auc_score}')
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': X_train.columns,
        'importance': rf_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print('Top 10 features:')
    print(feature_importance.head(10))
    
    # Save models
    joblib.dump(rf_model, os.path.join(args.model_dir, 'rf_model.pkl'))
    joblib.dump(gb_model, os.path.join(args.model_dir, 'gb_model.pkl'))
    joblib.dump(feature_importance, os.path.join(args.model_dir, 'feature_importance.pkl'))
    
    return auc_score

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--n_estimators', type=int, default=200)
    parser.add_argument('--max_depth', type=int, default=10)
    parser.add_argument('--min_samples_split', type=int, default=5)
    parser.add_argument('--class_weight', type=str, default='balanced')
    parser.add_argument('--train', type=str, default=os.environ.get('SM_CHANNEL_TRAIN'))
    parser.add_argument('--validation', type=str, default=os.environ.get('SM_CHANNEL_VALIDATION'))
    parser.add_argument('--model_dir', type=str, default=os.environ.get('SM_MODEL_DIR'))
    
    args = parser.parse_args()
    train_model(args)
```

## 🎯 Real-time Risk Scoring

### **1. Daily Risk Assessment**
```python
# Lambda: calculateRiskScore

import boto3
import joblib
import numpy as np

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Load models from S3 (cached)
rf_model = None
gb_model = None

def lambda_handler(event, context):
    global rf_model, gb_model
    
    # Load models if not cached
    if rf_model is None:
        rf_model = load_model_from_s3('rf_model.pkl')
        gb_model = load_model_from_s3('gb_model.pkl')
    
    user_id = event['userId']
    
    # Extract current features
    features = extract_all_features(user_id)
    
    # Prepare feature vector
    feature_vector = prepare_feature_vector(features)
    
    # Get predictions
    rf_prob = rf_model.predict_proba([feature_vector])[0][1]
    gb_prob = gb_model.predict_proba([feature_vector])[0][1]
    risk_score = (rf_prob + gb_prob) / 2
    
    # Classify risk level
    risk_level = classify_risk_level(risk_score)
    
    # Store risk assessment
    store_risk_assessment(user_id, risk_score, risk_level, features)
    
    # Trigger interventions if needed
    if risk_level in ['high', 'critical']:
        trigger_intervention(user_id, risk_level, risk_score)
    
    return {
        'statusCode': 200,
        'riskScore': float(risk_score),
        'riskLevel': risk_level,
        'timestamp': datetime.utcnow().isoformat()
    }

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

def trigger_intervention(user_id, risk_level, risk_score):
    interventions = {
        'critical': [
            'immediate_check_in',
            'crisis_resources',
            'emergency_contact_notification',
            'professional_referral'
        ],
        'high': [
            'daily_check_in',
            'mood_tracking_reminder',
            'coping_activities',
            'support_resources'
        ]
    }
    
    for intervention in interventions.get(risk_level, []):
        execute_intervention(user_id, intervention, risk_score)
```

### **2. EventBridge Scheduled Assessment**
```yaml
# CloudFormation
DailyRiskAssessmentRule:
  Type: AWS::Events::Rule
  Properties:
    Description: "Trigger daily risk assessment for all users"
    ScheduleExpression: "cron(0 6 * * ? *)"  # 6 AM UTC daily
    State: ENABLED
    Targets:
      - Arn: !GetAtt RiskAssessmentOrchestrator.Arn
        Id: "RiskAssessmentTarget"

RiskAssessmentOrchestrator:
  Type: AWS::Lambda::Function
  Properties:
    FunctionName: riskAssessmentOrchestrator
    Runtime: python3.11
    Handler: index.lambda_handler
    Code:
      ZipFile: |
        import boto3
        
        lambda_client = boto3.client('lambda')
        dynamodb = boto3.resource('dynamodb')
        
        def lambda_handler(event, context):
            # Get all active users
            users = get_active_users()
            
            # Trigger risk assessment for each user
            for user in users:
                lambda_client.invoke(
                    FunctionName='calculateRiskScore',
                    InvocationType='Event',
                    Payload=json.dumps({'userId': user['userId']})
                )
            
            return {'statusCode': 200, 'usersProcessed': len(users)}
```

## 🚨 Early Warning System

### **1. Intervention Triggers**
```python
# Lambda: executeIntervention

def execute_intervention(user_id, intervention_type, risk_score):
    interventions = {
        'immediate_check_in': send_immediate_check_in,
        'crisis_resources': provide_crisis_resources,
        'emergency_contact_notification': notify_emergency_contacts,
        'professional_referral': suggest_professional_help,
        'daily_check_in': schedule_daily_check_in,
        'mood_tracking_reminder': send_mood_reminder,
        'coping_activities': suggest_coping_activities,
        'support_resources': provide_support_resources
    }
    
    intervention_func = interventions.get(intervention_type)
    if intervention_func:
        intervention_func(user_id, risk_score)
        log_intervention(user_id, intervention_type, risk_score)

def send_immediate_check_in(user_id, risk_score):
    # Send push notification
    sns = boto3.client('sns')
    
    message = {
        'type': 'urgent_check_in',
        'title': 'Your companion is here for you',
        'body': 'I noticed you might be going through a tough time. Want to talk?',
        'priority': 'high',
        'data': {
            'action': 'open_chat',
            'riskScore': risk_score
        }
    }
    
    send_push_notification(user_id, message)
    
    # Create in-app message
    create_priority_message(user_id, {
        'message': "Hey, I've been thinking about you. How are you really doing?",
        'tone': 'concerned',
        'suggestedActivities': ['breathing', 'journaling', 'crisis_hotline']
    })

def provide_crisis_resources(user_id, risk_score):
    resources = {
        'crisis_hotlines': [
            {'name': '988 Suicide & Crisis Lifeline', 'number': '988'},
            {'name': 'Crisis Text Line', 'number': 'Text HOME to 741741'}
        ],
        'emergency': '911',
        'online_resources': [
            'https://suicidepreventionlifeline.org',
            'https://www.crisistextline.org'
        ]
    }
    
    store_priority_resources(user_id, resources)
    send_push_notification(user_id, {
        'type': 'crisis_resources',
        'title': 'Help is available 24/7',
        'body': 'You don\'t have to face this alone. Tap to see resources.',
        'data': resources
    })
```

### **2. Proactive Messaging**
```python
def generate_proactive_message(user_id, risk_level, risk_factors):
    # Use Bedrock to generate personalized intervention message
    bedrock = boto3.client('bedrock-runtime')
    
    profile = get_user_profile(user_id)
    history = get_recent_conversations(user_id, days=7)
    
    prompt = f"""
    You are an empathetic AI companion. Based on the user's recent patterns, 
    generate a caring, proactive check-in message.
    
    Risk Level: {risk_level}
    Key Concerns: {', '.join(risk_factors)}
    User Personality: {profile['personality']}
    Recent Context: {summarize_history(history)}
    
    Generate a warm, non-alarming message that:
    1. Shows you've noticed they might be struggling
    2. Offers specific support
    3. Suggests helpful activities
    4. Reminds them they're not alone
    
    Keep it natural and conversational, not clinical.
    """
    
    response = bedrock.invoke_model(
        modelId='anthropic.claude-3-sonnet-20240229',
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 200,
            "messages": [{"role": "user", "content": prompt}]
        })
    )
    
    message = json.loads(response['body'].read())['content'][0]['text']
    return message
```

## 📈 Model Monitoring & Retraining

### **1. Performance Tracking**
```python
# Lambda: monitorModelPerformance

def lambda_handler(event, context):
    # Get recent predictions
    predictions = get_recent_predictions(days=30)
    
    # Get actual outcomes
    actuals = get_actual_outcomes(days=30)
    
    # Calculate metrics
    metrics = calculate_performance_metrics(predictions, actuals)
    
    # Store metrics
    store_metrics(metrics)
    
    # Check if retraining needed
    if should_retrain(metrics):
        trigger_model_retraining()
    
    return metrics

def calculate_performance_metrics(predictions, actuals):
    from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
    
    y_true = [a['actual'] for a in actuals]
    y_pred = [p['predicted'] for p in predictions]
    y_prob = [p['probability'] for p in predictions]
    
    return {
        'precision': precision_score(y_true, y_pred),
        'recall': recall_score(y_true, y_pred),
        'f1_score': f1_score(y_true, y_pred),
        'auc': roc_auc_score(y_true, y_prob),
        'false_positive_rate': calculate_fpr(y_true, y_pred),
        'false_negative_rate': calculate_fnr(y_true, y_pred)
    }

def should_retrain(metrics):
    # Retrain if performance degrades
    thresholds = {
        'auc': 0.75,
        'recall': 0.70,  # Prioritize catching true positives
        'precision': 0.60
    }
    
    return any(metrics[k] < v for k, v in thresholds.items())
```

### **2. Automated Retraining**
```yaml
# CloudFormation
ModelRetrainingRule:
  Type: AWS::Events::Rule
  Properties:
    Description: "Retrain model monthly"
    ScheduleExpression: "cron(0 0 1 * ? *)"  # 1st of each month
    State: ENABLED
    Targets:
      - Arn: !GetAtt TriggerModelTraining.Arn
        Id: "RetrainingTarget"
```

## 🔒 Privacy & Ethics

### **1. Data Protection**
- All features anonymized before training
- No PII in training data
- Encrypted at rest and in transit
- User can opt-out of ML predictions

### **2. Ethical Considerations**
- **False positives acceptable**: Better to check in unnecessarily than miss someone in need
- **Transparency**: Users informed about risk monitoring
- **Human oversight**: Critical alerts reviewed by support team
- **No automated decisions**: Predictions inform, don't dictate

### **3. Bias Mitigation**
- Balanced training data across demographics
- Regular fairness audits
- Multiple validation sets
- Continuous monitoring for disparate impact

## 📊 Expected Performance

### **Target Metrics**
- **AUC**: > 0.80
- **Recall**: > 0.75 (catch 75% of actual crises)
- **Precision**: > 0.60 (60% of alerts are true positives)
- **Lead time**: 3-7 days before crisis
- **False positive rate**: < 40%

### **Cost Estimates**
- **SageMaker training**: ~$50/month (monthly retraining)
- **Real-time inference**: ~$100/month (10K users)
- **Feature extraction**: ~$30/month
- **Total**: ~$180/month for 10K users

---

**Status**: Specification complete ✅
**Complexity**: Very High (ML pipeline + real-time scoring)
**Timeline**: 4-6 weeks for full implementation
**Priority**: Phase 3 (after core features proven)
**Dependencies**: Requires 60+ days of user data for training
