import json
import os
import boto3
import joblib
import numpy as np
from datetime import datetime, timedelta
from decimal import Decimal

# AWS Clients
lambda_client = boto3.client('lambda')
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
risk_table = dynamodb.Table(os.environ.get('RISK_ASSESSMENTS_TABLE', 'MindMate-RiskAssessments'))
chat_table = dynamodb.Table(os.environ.get('CHAT_HISTORY_TABLE', 'EmoCompanion'))

# Model cache
_models_cache = {}

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

def load_ml_models():
    """Load trained ML models from S3"""
    global _models_cache
    
    if 'rf_model' in _models_cache and 'gb_model' in _models_cache:
        return _models_cache['rf_model'], _models_cache['gb_model']
    
    try:
        bucket = os.environ.get('MODEL_BUCKET', 'mindmate-ml-models')
        
        # Download models from S3
        rf_path = '/tmp/rf_model.pkl'
        gb_path = '/tmp/gb_model.pkl'
        
        s3_client.download_file(bucket, 'models/rf_model.pkl', rf_path)
        s3_client.download_file(bucket, 'models/gb_model.pkl', gb_path)
        
        # Load models
        rf_model = joblib.load(rf_path)
        gb_model = joblib.load(gb_path)
        
        # Cache models
        _models_cache['rf_model'] = rf_model
        _models_cache['gb_model'] = gb_model
        
        print("✅ ML models loaded successfully")
        return rf_model, gb_model
        
    except Exception as e:
        print(f"❌ Error loading ML models: {e}")
        return None, None

def extract_all_features(user_id):
    """Extract all ML features by calling feature extraction lambdas"""
    try:
        features = {}
        
        # Extract mood features
        mood_response = lambda_client.invoke(
            FunctionName='mindmate-extractMoodFeatures',
            InvocationType='RequestResponse',
            Payload=json.dumps({'userId': user_id, 'days': 30})
        )
        mood_data = json.loads(mood_response['Payload'].read())
        if mood_data.get('statusCode') == 200:
            mood_features = json.loads(mood_data['body'])
            features.update(mood_features)
        
        # Extract sentiment features
        sentiment_response = lambda_client.invoke(
            FunctionName='mindmate-extractSentimentFeatures',
            InvocationType='RequestResponse',
            Payload=json.dumps({'userId': user_id, 'days': 30})
        )
        sentiment_data = json.loads(sentiment_response['Payload'].read())
        if sentiment_data.get('statusCode') == 200:
            sentiment_features = json.loads(sentiment_data['body'])
            features.update(sentiment_features)
        
        # Extract behavioral features
        behavioral_response = lambda_client.invoke(
            FunctionName='mindmate-extractBehavioralFeatures',
            InvocationType='RequestResponse',
            Payload=json.dumps({'userId': user_id, 'days': 30})
        )
        behavioral_data = json.loads(behavioral_response['Payload'].read())
        if behavioral_data.get('statusCode') == 200:
            behavioral_features = json.loads(behavioral_data['body'])
            features.update(behavioral_features)
        
        print(f"✅ Extracted {len(features)} ML features")
        return features
        
    except Exception as e:
        print(f"❌ Error extracting features: {e}")
        return {}

def prepare_feature_vector(features):
    """Prepare feature vector for ML model prediction"""
    # Define expected feature order (should match training data)
    expected_features = [
        # Mood features
        'mood_trend_7day', 'mood_trend_14day', 'mood_trend_30day',
        'mood_mean_7day', 'mood_mean_14day', 'mood_mean_30day',
        'mood_std_7day', 'mood_std_14day', 'mood_std_30day',
        'mood_variance_7day', 'mood_min_7day', 'mood_max_7day',
        'mood_volatility', 'consecutive_low_days', 'consecutive_high_days',
        'mood_decline_rate', 'low_mood_frequency', 'high_mood_frequency',
        'missing_days_7day', 'weekend_mood_diff', 'total_mood_entries',
        
        # Sentiment features
        'sentiment_trend_7day', 'sentiment_trend_30day',
        'negative_sentiment_frequency', 'positive_sentiment_frequency',
        'neutral_sentiment_frequency', 'mixed_sentiment_frequency',
        'avg_negative_score', 'avg_positive_score', 'avg_neutral_score',
        'sentiment_volatility', 'despair_keywords', 'isolation_keywords',
        'hopelessness_score', 'crisis_keywords', 'total_messages_analyzed',
        
        # Behavioral features
        'daily_checkin_frequency', 'avg_session_duration', 'engagement_trend',
        'response_time_trend', 'activity_completion_rate', 'selfie_frequency',
        'avg_message_length', 'negative_word_frequency', 'help_seeking_frequency',
        'late_night_usage', 'weekend_usage_change', 'usage_consistency',
        'total_interactions', 'mood_logs_count', 'selfies_count'
    ]
    
    # Create feature vector with defaults for missing features
    feature_vector = []
    for feature_name in expected_features:
        value = features.get(feature_name, 0.0)
        # Handle any remaining Decimal objects
        if isinstance(value, Decimal):
            value = float(value)
        feature_vector.append(value)
    
    return np.array(feature_vector).reshape(1, -1)

def get_risk_factors_from_features(features):
    """Extract interpretable risk factors from ML features"""
    risk_factors = []
    
    try:
        # PRIORITIZE CHAT-BASED ANALYSIS
        total_messages = features.get('total_messages_analyzed', 0)
        total_moods = features.get('total_mood_entries', 0)
        
        # Crisis indicators from chat
        if features.get('crisis_keywords', 0) > 0:
            risk_factors.append(f"Crisis language detected in messages ({features['crisis_keywords']} instances)")
        
        if features.get('despair_keywords', 0) > 0:
            risk_factors.append(f"Expressions of despair detected ({features['despair_keywords']} instances)")
        
        if features.get('isolation_keywords', 0) > 0:
            risk_factors.append(f"Expressions of loneliness and isolation ({features['isolation_keywords']} instances)")
        
        # Sentiment analysis from chat (AWS Comprehend)
        negative_freq = features.get('negative_sentiment_frequency', 0)
        if negative_freq > 0.7:
            risk_factors.append(f"High negative sentiment in communications ({negative_freq*100:.0f}% of messages)")
        elif negative_freq > 0.5:
            risk_factors.append(f"Elevated negative sentiment detected ({negative_freq*100:.0f}% of messages)")
        
        hopelessness = features.get('hopelessness_score', 0)
        if hopelessness > 0.7:
            risk_factors.append(f"Strong expressions of hopelessness (score: {hopelessness:.2f})")
        elif hopelessness > 0.5:
            risk_factors.append(f"Expressions of hopelessness detected (score: {hopelessness:.2f})")
        
        # Help-seeking behavior from chat
        help_seeking = features.get('help_seeking_frequency', 0)
        if help_seeking > 0.4:
            risk_factors.append(f"Frequent help-seeking behavior ({help_seeking*100:.0f}% of messages)")
        
        # Mood patterns (if available)
        if total_moods > 0:
            if features.get('mood_trend_7day', 0) < -0.2:
                trend = features['mood_trend_7day']
                risk_factors.append(f"Declining mood trend over past week ({trend:.3f} slope)")
            
            if features.get('consecutive_low_days', 0) >= 3:
                days = features['consecutive_low_days']
                risk_factors.append(f"Extended low mood period ({days} consecutive days)")
            
            if features.get('mood_mean_7day', 5) < 3.5:
                mean_mood = features['mood_mean_7day']
                risk_factors.append(f"Consistently low mood ratings (average: {mean_mood:.1f}/10)")
        
        # Behavioral changes
        if features.get('engagement_trend', 0) < -0.1:
            risk_factors.append("Declining engagement with mental health tracking")
        
        if features.get('late_night_usage', 0) > 3:
            risk_factors.append(f"Increased late-night activity ({features['late_night_usage']} sessions)")
        
        # Data context
        if total_messages > 0 and total_moods == 0:
            risk_factors.append("Analysis based on chat messages (no mood logs available)")
        elif total_messages == 0 and total_moods > 0:
            risk_factors.append("Analysis based on mood logs (no chat messages available)")
        elif total_messages == 0 and total_moods == 0:
            risk_factors.append("Limited interaction data available for analysis")
        
        # If no specific risk factors found but we have concerning chat
        if not risk_factors and total_messages > 0:
            if negative_freq > 0.3 or hopelessness > 0.3:
                risk_factors.append("Concerning patterns detected in recent communications")
        
        return risk_factors if risk_factors else ["No significant risk factors detected"]
        
    except Exception as e:
        print(f"Error extracting risk factors: {e}")
        return ["Error analyzing risk factors"]

def calculate_risk_score(user_id):
    """Calculate risk score using trained ML models"""
    try:
        print(f"🧠 Calculating ML-based risk score for user: {user_id}")
        
        # Extract all ML features
        features = extract_all_features(user_id)
        
        if not features:
            print("⚠️ No features extracted, using fallback scoring")
            return {
                'riskScore': 0.0,
                'riskLevel': 'minimal',
                'riskFactors': ['Insufficient data for ML prediction'],
                'features': {},
                'confidence': 0,
                'method': 'fallback'
            }
        
        # Try to load and use ML models
        rf_model, gb_model = load_ml_models()
        
        if rf_model is not None and gb_model is not None:
            # Use ML models for prediction
            feature_vector = prepare_feature_vector(features)
            
            # Get predictions from both models
            rf_prob = rf_model.predict_proba(feature_vector)[0][1]
            gb_prob = gb_model.predict_proba(feature_vector)[0][1]
            
            # Ensemble prediction (average)
            risk_score = float((rf_prob + gb_prob) / 2)
            
            # Get interpretable risk factors
            risk_factors = get_risk_factors_from_features(features)
            
            # Calculate confidence based on model agreement
            model_agreement = 1.0 - abs(rf_prob - gb_prob)
            confidence = int(70 + (model_agreement * 25))  # 70-95% confidence
            
            method = 'ml_ensemble'
            
        else:
            # Fallback to rule-based scoring if models unavailable
            print("⚠️ ML models unavailable, using rule-based fallback")
            risk_score = calculate_rule_based_risk(features)
            risk_factors = get_risk_factors_from_features(features)
            confidence = 60  # Lower confidence for rule-based
            method = 'rule_based'
        
        # Determine risk level
        if risk_score >= 0.8:
            risk_level = 'critical'
        elif risk_score >= 0.6:
            risk_level = 'high'
        elif risk_score >= 0.4:
            risk_level = 'moderate'
        elif risk_score >= 0.2:
            risk_level = 'low'
        else:
            risk_level = 'minimal'
        
        print(f"✅ Risk assessment complete: {risk_level} ({risk_score:.3f}) via {method}")
        
        return {
            'riskScore': risk_score,
            'riskLevel': risk_level,
            'riskFactors': risk_factors,
            'features': features,
            'confidence': confidence,
            'method': method
        }
        
    except Exception as e:
        print(f"❌ Error calculating risk: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'riskScore': 0.0,
            'riskLevel': 'minimal',
            'riskFactors': ['Error in risk calculation'],
            'features': {},
            'confidence': 0,
            'method': 'error'
        }

def calculate_rule_based_risk(features):
    """Fallback rule-based risk calculation when ML models unavailable"""
    try:
        risk_score = 0.0
        
        # Crisis indicators (highest weight) - PRIORITIZE CHAT ANALYSIS
        crisis_keywords = features.get('crisis_keywords', 0)
        despair_keywords = features.get('despair_keywords', 0)
        isolation_keywords = features.get('isolation_keywords', 0)
        
        # Strong weight for crisis language in chat
        if crisis_keywords > 0:
            risk_score += min(crisis_keywords * 0.3, 0.8)
        
        if despair_keywords > 0:
            risk_score += min(despair_keywords * 0.2, 0.6)
            
        if isolation_keywords > 0:
            risk_score += min(isolation_keywords * 0.15, 0.4)
        
        # Sentiment analysis from chat (AWS Comprehend)
        negative_sentiment_freq = features.get('negative_sentiment_frequency', 0)
        hopelessness_score = features.get('hopelessness_score', 0)
        
        if negative_sentiment_freq > 0.8:
            risk_score += 0.3
        elif negative_sentiment_freq > 0.6:
            risk_score += 0.2
        elif negative_sentiment_freq > 0.4:
            risk_score += 0.1
        
        if hopelessness_score > 0.8:
            risk_score += 0.3
        elif hopelessness_score > 0.6:
            risk_score += 0.2
        elif hopelessness_score > 0.4:
            risk_score += 0.1
        
        # Mood indicators (secondary to chat analysis)
        mood_mean_7day = features.get('mood_mean_7day', 5.0)
        consecutive_low_days = features.get('consecutive_low_days', 0)
        mood_trend_7day = features.get('mood_trend_7day', 0)
        
        # Only add mood risk if we have mood data
        if features.get('total_mood_entries', 0) > 0:
            if mood_mean_7day < 3.0:
                risk_score += 0.2
            elif mood_mean_7day < 4.0:
                risk_score += 0.1
            
            if consecutive_low_days >= 3:
                risk_score += 0.15
            
            if mood_trend_7day < -0.3:
                risk_score += 0.15
        
        # Behavioral indicators from chat patterns
        total_messages = features.get('total_messages_analyzed', 0)
        help_seeking_freq = features.get('help_seeking_frequency', 0)
        
        # If we have chat messages, analyze patterns
        if total_messages > 0:
            if help_seeking_freq > 0.5:
                risk_score += 0.1
            
            # Boost risk if we have concerning chat but no mood logs
            if features.get('total_mood_entries', 0) == 0 and (crisis_keywords > 0 or despair_keywords > 0):
                risk_score += 0.2  # Boost for concerning chat without mood tracking
        
        # Cap at 1.0
        return min(risk_score, 1.0)
        
    except Exception as e:
        print(f"Error in rule-based calculation: {e}")
        return 0.0

def store_risk_assessment(user_id, risk_data):
    """Store risk assessment in DynamoDB"""
    try:
        timestamp = datetime.utcnow().isoformat() + 'Z'
        
        item = {
            'userId': user_id,
            'timestamp': timestamp,
            'riskScore': Decimal(str(round(risk_data['riskScore'], 4))),
            'riskLevel': risk_data['riskLevel'],
            'riskFactors': risk_data['riskFactors'],
            'features': {k: Decimal(str(v)) if isinstance(v, (int, float)) else v 
                        for k, v in risk_data['features'].items()},
            'confidence': Decimal(str(risk_data['confidence'])),
            'interventionsTriggered': [],
            'ttl': int((datetime.utcnow().timestamp() + 90 * 24 * 3600))  # 90 days
        }
        
        risk_table.put_item(Item=item)
        return timestamp
    except Exception as e:
        print(f"Error storing risk assessment: {e}")
        return None

def trigger_intervention(user_id, risk_level, risk_score, risk_factors):
    """Trigger intervention Lambda if risk is high or critical"""
    try:
        if risk_level in ['high', 'critical']:
            lambda_client.invoke(
                FunctionName='mindmate-executeIntervention',
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
        
        print(f"Calculating risk for user: {user_id}")
        
        # Calculate risk score
        risk_data = calculate_risk_score(user_id)
        
        # Store assessment
        timestamp = store_risk_assessment(user_id, risk_data)
        
        # Trigger interventions if needed
        intervention_triggered = trigger_intervention(
            user_id, 
            risk_data['riskLevel'], 
            risk_data['riskScore'], 
            risk_data['riskFactors']
        )
        
        print(f"Risk assessment complete: {risk_data['riskLevel']} ({risk_data['riskScore']:.2f})")
        
        return _resp(200, {
            'ok': True,
            'riskScore': risk_data['riskScore'],
            'riskLevel': risk_data['riskLevel'],
            'riskFactors': risk_data['riskFactors'],
            'features': risk_data['features'],
            'confidence': risk_data['confidence'],
            'timestamp': timestamp,
            'interventionTriggered': intervention_triggered,
            'message': f'Risk assessment complete: {risk_data["riskLevel"]} risk level'
        })
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return _resp(500, {'error': str(e)})