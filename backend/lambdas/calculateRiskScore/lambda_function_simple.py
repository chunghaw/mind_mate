import json
import os
import boto3
from datetime import datetime, timedelta
from decimal import Decimal

# AWS Clients
lambda_client = boto3.client('lambda')
dynamodb = boto3.resource('dynamodb')
risk_table = dynamodb.Table(os.environ.get('RISK_ASSESSMENTS_TABLE', 'MindMate-RiskAssessments'))
chat_table = dynamodb.Table(os.environ.get('CHAT_HISTORY_TABLE', 'EmoCompanion'))

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

def extract_basic_features(user_id):
    """Extract basic features without calling other Lambdas"""
    try:
        features = {}
        
        # Get recent chat messages
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        try:
            chat_response = chat_table.query(
                KeyConditionExpression='PK = :pk AND SK BETWEEN :start AND :end',
                ExpressionAttributeValues={
                    ':pk': f'USER#{user_id}',
                    ':start': f'CHAT#{start_date.isoformat()}',
                    ':end': f'CHAT#{end_date.isoformat()}Z'
                },
                Limit=50
            )
            
            messages = chat_response.get('Items', [])
            total_messages = len(messages)
            
            # Analyze message content for sentiment
            negative_count = 0
            crisis_count = 0
            hopelessness_count = 0
            
            crisis_words = ['hopeless', 'pointless', 'give up', 'end it', 'worthless', 'no point']
            negative_words = ['sad', 'depressed', 'anxious', 'worried', 'overwhelmed', 'tired', 'stressed']
            hopelessness_words = ['hopeless', 'no hope', 'pointless', 'worthless', 'give up']
            
            for item in messages:
                user_msg = item.get('userMessage', '').lower()
                if user_msg:
                    # Count crisis indicators
                    for word in crisis_words:
                        if word in user_msg:
                            crisis_count += 1
                    
                    # Count negative sentiment
                    for word in negative_words:
                        if word in user_msg:
                            negative_count += 1
                    
                    # Count hopelessness
                    for word in hopelessness_words:
                        if word in user_msg:
                            hopelessness_count += 1
            
            # Calculate frequencies
            features['total_messages_analyzed'] = total_messages
            features['negative_sentiment_frequency'] = negative_count / max(total_messages, 1)
            features['crisis_keywords'] = crisis_count
            features['hopelessness_score'] = hopelessness_count / max(total_messages, 1)
            features['isolation_keywords'] = 0  # Basic implementation
            
        except Exception as e:
            print(f"Error analyzing chat: {e}")
            features.update({
                'total_messages_analyzed': 0,
                'negative_sentiment_frequency': 0.0,
                'crisis_keywords': 0,
                'hopelessness_score': 0.0,
                'isolation_keywords': 0
            })
        
        # Get mood data
        try:
            mood_response = chat_table.query(
                KeyConditionExpression='PK = :pk AND begins_with(SK, :mood)',
                ExpressionAttributeValues={
                    ':pk': f'USER#{user_id}',
                    ':mood': 'MOOD#'
                },
                Limit=30,
                ScanIndexForward=False  # Most recent first
            )
            
            mood_entries = mood_response.get('Items', [])
            total_moods = len(mood_entries)
            
            if total_moods > 0:
                moods = [float(item.get('mood', 5)) for item in mood_entries]
                avg_mood = sum(moods) / len(moods)
                
                # Count consecutive low days
                consecutive_low = 0
                for mood in moods:
                    if mood <= 4:
                        consecutive_low += 1
                    else:
                        break
                
                # Calculate trend (simple)
                if len(moods) >= 7:
                    recent_avg = sum(moods[:7]) / 7
                    older_avg = sum(moods[7:14]) / min(7, len(moods[7:14])) if len(moods) > 7 else recent_avg
                    trend = recent_avg - older_avg
                else:
                    trend = 0.0
                
                features.update({
                    'mood_mean_7day': avg_mood,
                    'mood_trend_7day': trend,
                    'consecutive_low_days': consecutive_low,
                    'total_mood_entries': total_moods
                })
            else:
                features.update({
                    'mood_mean_7day': 7.0,  # Neutral for new users
                    'mood_trend_7day': 0.0,
                    'consecutive_low_days': 0,
                    'total_mood_entries': 0
                })
                
        except Exception as e:
            print(f"Error analyzing mood: {e}")
            features.update({
                'mood_mean_7day': 7.0,
                'mood_trend_7day': 0.0,
                'consecutive_low_days': 0,
                'total_mood_entries': 0
            })
        
        # Basic behavioral features
        features.update({
            'daily_checkin_frequency': min(total_moods / 30.0, 1.0),
            'engagement_decline': 0.0,
            'late_night_usage_frequency': 0,
            'help_seeking_frequency': 0.0
        })
        
        return features
        
    except Exception as e:
        print(f"Error extracting features: {e}")
        return {
            'mood_mean_7day': 7.0,
            'mood_trend_7day': 0.0,
            'consecutive_low_days': 0,
            'negative_sentiment_frequency': 0.0,
            'crisis_keywords': 0,
            'hopelessness_score': 0.0,
            'total_mood_entries': 0,
            'total_messages_analyzed': 0
        }

def calculate_rule_based_risk(features):
    """Simple rule-based risk calculation"""
    try:
        risk_score = 0.0
        
        # Crisis indicators (highest weight)
        crisis_keywords = features.get('crisis_keywords', 0)
        if crisis_keywords > 0:
            risk_score += min(crisis_keywords * 0.3, 0.8)
        
        # Sentiment analysis
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
        
        # Mood indicators
        mood_mean_7day = features.get('mood_mean_7day', 7.0)
        consecutive_low_days = features.get('consecutive_low_days', 0)
        mood_trend_7day = features.get('mood_trend_7day', 0)
        
        if features.get('total_mood_entries', 0) > 0:
            if mood_mean_7day < 3.0:
                risk_score += 0.2
            elif mood_mean_7day < 4.0:
                risk_score += 0.1
            
            if consecutive_low_days >= 3:
                risk_score += 0.15
            
            if mood_trend_7day < -0.3:
                risk_score += 0.15
        
        # Cap at 1.0
        return min(risk_score, 1.0)
        
    except Exception as e:
        print(f"Error in rule-based calculation: {e}")
        return 0.0

def get_risk_factors_from_features(features):
    """Extract interpretable risk factors"""
    risk_factors = []
    
    try:
        total_messages = features.get('total_messages_analyzed', 0)
        total_moods = features.get('total_mood_entries', 0)
        
        # Crisis indicators
        if features.get('crisis_keywords', 0) > 0:
            risk_factors.append(f"Crisis language detected in messages ({features['crisis_keywords']} instances)")
        
        # Sentiment analysis
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
        
        # Mood patterns
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
        
        # Data context
        if total_messages == 0 and total_moods == 0:
            risk_factors.append("New user - building baseline analysis")
        elif total_messages == 0:
            risk_factors.append("Analysis based on mood logs only")
        elif total_moods == 0:
            risk_factors.append("Analysis based on chat messages only")
        
        return risk_factors if risk_factors else ["No significant risk factors detected - healthy baseline"]
        
    except Exception as e:
        print(f"Error extracting risk factors: {e}")
        return ["Error analyzing risk factors"]

def calculate_risk_score(user_id):
    """Calculate risk score using rule-based analysis"""
    try:
        print(f"🧠 Calculating risk score for user: {user_id}")
        
        # Extract features
        features = extract_basic_features(user_id)
        
        if not features:
            print("⚠️ No features extracted, using minimal risk")
            return {
                'riskScore': 0.0,
                'riskLevel': 'minimal',
                'riskFactors': ['New user - insufficient data for analysis'],
                'features': {},
                'confidence': 50,
                'method': 'new_user'
            }
        
        # Calculate risk using rule-based approach
        risk_score = calculate_rule_based_risk(features)
        risk_factors = get_risk_factors_from_features(features)
        
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
        
        # Calculate confidence based on data availability
        total_data_points = features.get('total_messages_analyzed', 0) + features.get('total_mood_entries', 0)
        if total_data_points >= 10:
            confidence = 85
        elif total_data_points >= 5:
            confidence = 70
        elif total_data_points >= 1:
            confidence = 60
        else:
            confidence = 40
        
        print(f"✅ Risk assessment complete: {risk_level} ({risk_score:.3f}) - rule-based analysis")
        
        return {
            'riskScore': risk_score,
            'riskLevel': risk_level,
            'riskFactors': risk_factors,
            'features': features,
            'confidence': confidence,
            'method': 'rule_based'
        }
        
    except Exception as e:
        print(f"❌ Error calculating risk: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'riskScore': 0.0,
            'riskLevel': 'minimal',
            'riskFactors': ['Error in risk calculation - defaulting to safe baseline'],
            'features': {},
            'confidence': 0,
            'method': 'error'
        }

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
            'method': risk_data['method'],
            'ttl': int((datetime.utcnow().timestamp() + 90 * 24 * 3600))  # 90 days
        }
        
        risk_table.put_item(Item=item)
        return timestamp
    except Exception as e:
        print(f"Error storing risk assessment: {e}")
        return None

def lambda_handler(event, context):
    """Calculate risk score for a user"""
    try:
        # Handle CORS preflight
        if event.get('httpMethod') == 'OPTIONS':
            return _resp(200, {})
        
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
        
        print(f"Risk assessment complete: {risk_data['riskLevel']} ({risk_data['riskScore']:.2f})")
        
        return _resp(200, {
            'ok': True,
            'riskScore': risk_data['riskScore'],
            'riskLevel': risk_data['riskLevel'],
            'riskFactors': risk_data['riskFactors'],
            'features': risk_data['features'],
            'confidence': risk_data['confidence'],
            'method': risk_data['method'],
            'timestamp': timestamp,
            'message': f'Risk assessment complete: {risk_data["riskLevel"]} risk level'
        })
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return _resp(500, {'error': str(e)})