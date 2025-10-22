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

def get_recent_chat_messages(user_id, days=7):
    """Get recent chat messages directly from DynamoDB"""
    try:
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat() + 'Z'
        
        response = chat_table.query(
            KeyConditionExpression='PK = :pk AND SK > :cutoff',
            ExpressionAttributeValues={
                ':pk': f"USER#{user_id}",
                ':cutoff': f"CHAT#{cutoff}"
            },
            ScanIndexForward=False,
            Limit=50
        )
        
        messages = []
        for item in response.get('Items', []):
            if item.get('sender') == 'user' and item.get('message'):
                messages.append(item['message'])
        
        return messages
    except Exception as e:
        print(f"Error getting chat messages: {e}")
        return []

def analyze_crisis_keywords(messages):
    """Analyze messages for crisis keywords"""
    crisis_keywords = [
        'suicide', 'kill myself', 'end it all', 'want to die', 'feel like dying',
        'hopeless', 'worthless', 'no point', 'give up', 'can\'t go on',
        'end my life', 'better off dead', 'commit suicide', 'kill me'
    ]
    
    crisis_count = 0
    negative_sentiment = 0
    total_messages = len(messages)
    
    if total_messages == 0:
        return 0, []
    
    detected_factors = []
    
    for message in messages:
        message_lower = message.lower()
        
        # Check for crisis keywords
        for keyword in crisis_keywords:
            if keyword in message_lower:
                crisis_count += 1
                if keyword not in [f.split('(')[0].strip() for f in detected_factors]:
                    detected_factors.append(f"Crisis keywords detected ({keyword})")
                break
        
        # Simple negative sentiment detection
        negative_words = ['sad', 'depressed', 'angry', 'hate', 'terrible', 'awful', 'bad', 'worst']
        if any(word in message_lower for word in negative_words):
            negative_sentiment += 1
    
    # Calculate risk factors
    if crisis_count > 0:
        detected_factors.append(f"Crisis language detected ({crisis_count} messages)")
    
    if negative_sentiment > total_messages * 0.6:
        detected_factors.append(f"High negative sentiment ({negative_sentiment}/{total_messages} messages)")
    
    if total_messages < 3:
        detected_factors.append("Limited recent communication")
    
    return crisis_count, detected_factors

def calculate_risk_score(user_id):
    """Calculate risk score based on available data"""
    try:
        # Get recent chat messages
        messages = get_recent_chat_messages(user_id, days=7)
        
        # Analyze for crisis keywords and sentiment
        crisis_count, risk_factors = analyze_crisis_keywords(messages)
        
        # Calculate base risk score
        risk_score = 0.0
        
        # Crisis keywords are the highest risk factor
        if crisis_count > 0:
            risk_score += min(crisis_count * 0.3, 0.8)  # Max 0.8 from crisis keywords
        
        # Add risk based on number of risk factors
        risk_score += len(risk_factors) * 0.1
        
        # Cap at 1.0
        risk_score = min(risk_score, 1.0)
        
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
        
        # Create features object for compatibility
        features = {
            'total_messages_analyzed': len(messages),
            'crisis_keywords': crisis_count,
            'risk_factors_detected': len(risk_factors),
            'analysis_period_days': 7
        }
        
        return {
            'riskScore': risk_score,
            'riskLevel': risk_level,
            'riskFactors': risk_factors,
            'features': features,
            'confidence': 85 if crisis_count > 0 else 70  # Higher confidence if crisis keywords detected
        }
        
    except Exception as e:
        print(f"Error calculating risk: {e}")
        return {
            'riskScore': 0.0,
            'riskLevel': 'minimal',
            'riskFactors': ['Error in risk calculation'],
            'features': {},
            'confidence': 0
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