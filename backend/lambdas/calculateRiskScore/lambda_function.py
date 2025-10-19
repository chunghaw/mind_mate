import json
import os
import boto3
from datetime import datetime
from decimal import Decimal

# AWS Clients
lambda_client = boto3.client('lambda')
dynamodb = boto3.resource('dynamodb')
risk_table = dynamodb.Table(os.environ.get('RISK_ASSESSMENTS_TABLE', 'MindMate-RiskAssessments'))

def decimal_to_float(obj):
    """Convert DynamoDB Decimal to float"""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: decimal_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [decimal_to_float(i) for i in obj]
    return obj

def _resp(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST"
        },
        "body": json.dumps(body, default=str)
    }

def extract_all_features(user_id):
    """Extract features by invoking feature extraction Lambdas in parallel"""
    try:
        # Invoke mood features
        mood_response = lambda_client.invoke(
            FunctionName='mindmate-extractMoodFeatures',
            InvocationType='RequestResponse',
            Payload=json.dumps({'userId': user_id, 'days': 30})
        )
        mood_features = json.loads(mood_response['Payload'].read())
        
        # Invoke behavioral features
        behavioral_response = lambda_client.invoke(
            FunctionName='mindmate-extractBehavioralFeatures',
            InvocationType='RequestResponse',
            Payload=json.dumps({'userId': user_id, 'days': 30})
        )
        behavioral_features = json.loads(behavioral_response['Payload'].read())
        
        # Invoke sentiment features
        sentiment_response = lambda_client.invoke(
            FunctionName='mindmate-extractSentimentFeatures',
            InvocationType='RequestResponse',
            Payload=json.dumps({'userId': user_id, 'days': 30})
        )
        sentiment_features = json.loads(sentiment_response['Payload'].read())
        
        # Combine all features
        all_features = {
            **mood_features,
            **behavioral_features,
            **sentiment_features
        }
        
        return all_features
        
    except Exception as e:
        print(f"Error extracting features: {e}")
        return {}

def calculate_rule_based_risk(features):
    """
    Calculate risk score using rule-based approach
    This is used when ML models are not available
    """
    risk_score = 0.0
    risk_factors = []
    
    # Mood-based risk factors
    mood_mean_7day = features.get('mood_mean_7day', 5.0)
    mood_trend_7day = features.get('mood_trend_7day', 0.0)
    consecutive_low_days = features.get('consecutive_low_days', 0)
    low_mood_frequency = features.get('low_mood_frequency', 0.0)
    
    # Very low average mood (< 4)
    if mood_mean_7day < 4:
        risk_score += 0.25
        risk_factors.append(f"Low average mood ({mood_mean_7day:.1f}/10)")
    
    # Declining mood trend
    if mood_trend_7day < -0.2:
        risk_score += 0.20
        risk_factors.append(f"Declining mood trend ({mood_trend_7day:.2f})")
    
    # Consecutive low mood days
    if consecutive_low_days >= 3:
        risk_score += 0.25
        risk_factors.append(f"{consecutive_low_days} consecutive low mood days")
    
    # High frequency of low moods
    if low_mood_frequency > 0.5:
        risk_score += 0.15
        risk_factors.append(f"High frequency of low moods ({low_mood_frequency:.0%})")
    
    # Behavioral risk factors
    engagement_decline = features.get('engagement_decline', 0.0)
    daily_checkin_frequency = features.get('daily_checkin_frequency', 1.0)
    late_night_usage = features.get('late_night_usage', 0)
    
    # Declining engagement
    if engagement_decline < -0.3:
        risk_score += 0.15
        risk_factors.append("Declining engagement")
    
    # Low check-in frequency
    if daily_checkin_frequency < 0.3:
        risk_score += 0.10
        risk_factors.append("Low check-in frequency")
    
    # Frequent late-night usage
    if late_night_usage >= 5:
        risk_score += 0.10
        risk_factors.append(f"Frequent late-night usage ({late_night_usage} times)")
    
    # Sentiment risk factors
    sentiment_trend_7day = features.get('sentiment_trend_7day', 0.0)
    negative_sentiment_frequency = features.get('negative_sentiment_frequency', 0.0)
    despair_keywords = features.get('despair_keywords', 0)
    hopelessness_score = features.get('hopelessness_score', 0.0)
    
    # Declining sentiment
    if sentiment_trend_7day < -0.15:
        risk_score += 0.15
        risk_factors.append("Declining sentiment")
    
    # High negative sentiment
    if negative_sentiment_frequency > 0.6:
        risk_score += 0.20
        risk_factors.append(f"High negative sentiment ({negative_sentiment_frequency:.0%})")
    
    # Crisis keywords detected
    if despair_keywords >= 2:
        risk_score += 0.30
        risk_factors.append(f"Crisis keywords detected ({despair_keywords})")
    
    # High hopelessness score
    if hopelessness_score > 0.3:
        risk_score += 0.25
        risk_factors.append(f"High hopelessness indicators")
    
    # Cap at 1.0
    risk_score = min(risk_score, 1.0)
    
    return risk_score, risk_factors

def classify_risk_level(risk_score):
    """Classify risk score into levels"""
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

def store_risk_assessment(user_id, risk_score, risk_level, features, risk_factors):
    """Store risk assessment in DynamoDB"""
    timestamp = datetime.utcnow().isoformat() + 'Z'
    
    item = {
        'userId': user_id,
        'timestamp': timestamp,
        'riskScore': Decimal(str(round(risk_score, 4))),
        'riskLevel': risk_level,
        'riskFactors': risk_factors,
        'features': {k: Decimal(str(v)) if isinstance(v, float) else v for k, v in features.items()},
        'interventionsTriggered': [],
        'ttl': int((datetime.utcnow().timestamp() + 90 * 24 * 3600))  # 90 days
    }
    
    risk_table.put_item(Item=item)
    return timestamp

def trigger_intervention(user_id, risk_level, risk_score, risk_factors):
    """Trigger intervention Lambda if risk is high or critical"""
    try:
        lambda_client.invoke(
            FunctionName='executeIntervention',
            InvocationType='Event',  # Async
            Payload=json.dumps({
                'userId': user_id,
                'riskLevel': risk_level,
                'riskScore': risk_score,
                'riskFactors': risk_factors
            })
        )
        return True
    except Exception as e:
        print(f"Error triggering intervention: {e}")
        return False

def lambda_handler(event, context):
    """Calculate risk score for a user"""
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        user_id = body.get('userId')
        
        if not user_id:
            return _resp(400, {'error': 'userId is required'})
        
        # Extract all features
        print(f"Extracting features for user: {user_id}")
        features = extract_all_features(user_id)
        
        if not features:
            return _resp(500, {'error': 'Failed to extract features'})
        
        # Calculate risk score using rule-based approach
        # TODO: Replace with ML model predictions when models are trained
        print(f"Calculating risk score...")
        risk_score, risk_factors = calculate_rule_based_risk(features)
        
        # Classify risk level
        risk_level = classify_risk_level(risk_score)
        
        # Store assessment
        print(f"Storing risk assessment: {risk_level} ({risk_score:.2f})")
        timestamp = store_risk_assessment(user_id, risk_score, risk_level, features, risk_factors)
        
        # Trigger interventions if needed
        intervention_triggered = False
        if risk_level in ['high', 'critical']:
            print(f"Triggering intervention for {risk_level} risk")
            intervention_triggered = trigger_intervention(user_id, risk_level, risk_score, risk_factors)
        
        return _resp(200, {
            'ok': True,
            'riskScore': float(risk_score),
            'riskLevel': risk_level,
            'riskFactors': risk_factors,
            'timestamp': timestamp,
            'interventionTriggered': intervention_triggered,
            'message': f'Risk assessment complete: {risk_level} risk level'
        })
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return _resp(500, {'error': str(e)})
