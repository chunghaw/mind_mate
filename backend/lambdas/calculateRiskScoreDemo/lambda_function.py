import json
import os
from datetime import datetime
from decimal import Decimal
import boto3

dynamodb = boto3.resource('dynamodb')
lambda_client = boto3.client('lambda')
risk_table = dynamodb.Table(os.environ.get('RISK_ASSESSMENTS_TABLE', 'MindMate-RiskAssessments'))

def lambda_handler(event, context):
    """
    Demo risk scoring Lambda - calculates risk based on features
    For hackathon: Uses simple rule-based scoring until ML model is trained
    """
    try:
        user_id = event.get('userId')
        
        if not user_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'userId is required'})
            }
        
        # Extract features from all 3 Lambdas
        print(f"Extracting features for {user_id}...")
        
        payload = json.dumps({'userId': user_id, 'days': 30})
        
        # Mood features
        mood_response = lambda_client.invoke(
            FunctionName='mindmate-extractMoodFeatures',
            InvocationType='RequestResponse',
            Payload=payload
        )
        mood_result = json.loads(mood_response['Payload'].read())
        mood_features = json.loads(mood_result.get('body', '{}'))
        
        # Behavioral features
        behavioral_response = lambda_client.invoke(
            FunctionName='mindmate-extractBehavioralFeatures',
            InvocationType='RequestResponse',
            Payload=payload
        )
        behavioral_result = json.loads(behavioral_response['Payload'].read())
        behavioral_features = json.loads(behavioral_result.get('body', '{}'))
        
        # Sentiment features
        sentiment_response = lambda_client.invoke(
            FunctionName='mindmate-extractSentimentFeatures',
            InvocationType='RequestResponse',
            Payload=payload
        )
        sentiment_result = json.loads(sentiment_response['Payload'].read())
        sentiment_features = json.loads(sentiment_result.get('body', '{}'))
        
        # Calculate risk score using rule-based system (until ML model is trained)
        risk_score = calculate_rule_based_risk(mood_features, behavioral_features, sentiment_features)
        risk_level = classify_risk_level(risk_score)
        
        # Store risk assessment
        timestamp = datetime.utcnow().isoformat() + 'Z'
        risk_table.put_item(Item={
            'userId': user_id,
            'timestamp': timestamp,
            'riskScore': Decimal(str(risk_score)),
            'riskLevel': risk_level,
            'features': {
                'mood_mean_7day': Decimal(str(mood_features.get('mood_mean_7day', 5))),
                'consecutive_low_days': mood_features.get('consecutive_low_days', 0),
                'negative_sentiment_frequency': Decimal(str(sentiment_features.get('negative_sentiment_frequency', 0))),
                'despair_keywords': sentiment_features.get('despair_keywords', 0),
                'crisis_keywords': sentiment_features.get('crisis_keywords', 0)
            },
            'interventionsTriggered': [] if risk_level in ['minimal', 'low'] else ['proactive_checkin']
        })
        
        print(f"Risk assessment complete: {user_id} = {risk_level} ({risk_score:.2f})")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'userId': user_id,
                'riskScore': risk_score,
                'riskLevel': risk_level,
                'timestamp': timestamp,
                'features': {
                    # Mood features
                    'mood_mean_7day': mood_features.get('mood_mean_7day', 5),
                    'mood_trend_7day': mood_features.get('mood_trend_7day', 0),
                    'mood_volatility': mood_features.get('mood_volatility', 0),
                    'consecutive_low_days': mood_features.get('consecutive_low_days', 0),
                    
                    # Behavioral features
                    'daily_checkin_frequency': behavioral_features.get('daily_checkin_frequency', 0),
                    'platform_engagement_score': behavioral_features.get('platform_engagement_score', 0),
                    'circadian_disruption': behavioral_features.get('circadian_disruption', 0),
                    'task_completion_rate': behavioral_features.get('task_completion_rate', 0),
                    
                    # Sentiment features
                    'positive_sentiment': sentiment_features.get('positive_sentiment_frequency', 0),
                    'negative_sentiment_frequency': sentiment_features.get('negative_sentiment_frequency', 0),
                    'crisis_keywords': sentiment_features.get('crisis_keywords', 0),
                    'hopelessness_score': sentiment_features.get('hopelessness_score', 0)
                }
            })
        }
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def calculate_rule_based_risk(mood_features, behavioral_features, sentiment_features):
    """
    Calculate risk score using rule-based system
    Returns score 0-1 (0 = no risk, 1 = critical risk)
    """
    risk_score = 0.0
    
    # Mood indicators (40% weight)
    mood_mean = mood_features.get('mood_mean_7day', 5)
    if mood_mean <= 3:
        risk_score += 0.25
    elif mood_mean <= 4:
        risk_score += 0.15
    elif mood_mean <= 5:
        risk_score += 0.05
    
    consecutive_low = mood_features.get('consecutive_low_days', 0)
    if consecutive_low >= 5:
        risk_score += 0.15
    elif consecutive_low >= 3:
        risk_score += 0.10
    elif consecutive_low >= 2:
        risk_score += 0.05
    
    # Sentiment indicators (30% weight)
    negative_freq = sentiment_features.get('negative_sentiment_frequency', 0)
    if negative_freq >= 0.6:
        risk_score += 0.15
    elif negative_freq >= 0.4:
        risk_score += 0.10
    elif negative_freq >= 0.3:
        risk_score += 0.05
    
    despair_keywords = sentiment_features.get('despair_keywords', 0)
    if despair_keywords >= 5:
        risk_score += 0.10
    elif despair_keywords >= 3:
        risk_score += 0.05
    
    crisis_keywords = sentiment_features.get('crisis_keywords', 0)
    if crisis_keywords > 0:
        risk_score += 0.30  # Critical indicator
    
    # Behavioral indicators (30% weight)
    engagement_trend = behavioral_features.get('engagement_trend', 0)
    if engagement_trend < -0.1:
        risk_score += 0.10
    elif engagement_trend < -0.05:
        risk_score += 0.05
    
    late_night_usage = behavioral_features.get('late_night_usage', 0)
    if late_night_usage >= 10:
        risk_score += 0.10
    elif late_night_usage >= 5:
        risk_score += 0.05
    
    help_seeking = behavioral_features.get('help_seeking_frequency', 0)
    if help_seeking >= 0.2:
        risk_score += 0.10
    elif help_seeking >= 0.1:
        risk_score += 0.05
    
    return min(1.0, risk_score)


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
