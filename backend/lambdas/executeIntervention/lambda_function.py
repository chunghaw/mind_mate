import json
import os
import boto3
from datetime import datetime, timedelta
from decimal import Decimal

# AWS Clients
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
bedrock_agent = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

# Environment variables
INTERVENTIONS_TABLE = os.environ.get('INTERVENTIONS_TABLE', 'MindMate-Interventions')
CHAT_HISTORY_TABLE = os.environ.get('CHAT_HISTORY_TABLE', 'EmoCompanion')
USERS_TABLE = os.environ.get('USERS_TABLE', 'EmoCompanion')
MOOD_LOGS_TABLE = os.environ.get('MOOD_LOGS_TABLE', 'EmoCompanion')
BEDROCK_AGENT_ID = os.environ.get('BEDROCK_AGENT_ID', '8W0ULUYHAE')
BEDROCK_AGENT_ALIAS_ID = os.environ.get('BEDROCK_AGENT_ALIAS_ID', 'TSTALIASID')
ALERT_SNS_TOPIC = os.environ.get('ML_ALERTS_SNS_TOPIC', '')

# DynamoDB tables
interventions_table = dynamodb.Table(INTERVENTIONS_TABLE)
chat_table = dynamodb.Table(CHAT_HISTORY_TABLE)
users_table = dynamodb.Table(USERS_TABLE)
mood_table = dynamodb.Table(MOOD_LOGS_TABLE)


def get_user_profile(user_id):
    """Get user profile information"""
    try:
        response = users_table.get_item(Key={'PK': f"USER#{user_id}", 'SK': 'PROFILE'})
        if 'Item' in response:
            return response['Item']
        return {'userId': user_id, 'name': 'there'}
    except Exception as e:
        print(f"Error getting user profile: {e}")
        return {'userId': user_id, 'name': 'there'}


def get_recent_moods(user_id, days=7):
    """Get recent mood logs"""
    try:
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat() + 'Z'
        
        response = mood_table.query(
            KeyConditionExpression='PK = :pk AND SK > :cutoff',
            ExpressionAttributeValues={
                ':pk': f"USER#{user_id}",
                ':cutoff': f"MOOD#{cutoff}"
            },
            ScanIndexForward=False,
            Limit=days
        )
        
        moods = [float(item.get('mood', 5)) for item in response.get('Items', [])]
        return moods if moods else [5.0]
    except Exception as e:
        print(f"Error getting recent moods: {e}")
        return [5.0]


def get_recent_chats(user_id, days=3):
    """Get recent chat messages"""
    try:
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat() + 'Z'
        
        response = chat_table.query(
            KeyConditionExpression='PK = :pk AND SK > :cutoff',
            ExpressionAttributeValues={
                ':pk': f"USER#{user_id}",
                ':cutoff': f"CHAT#{cutoff}"
            },
            ScanIndexForward=False,
            Limit=20
        )
        
        messages = [item.get('message', '') for item in response.get('Items', []) 
                   if item.get('sender') == 'user']
        return messages
    except Exception as e:
        print(f"Error getting recent chats: {e}")
        return []


def get_last_intervention(user_id):
    """Get the most recent intervention for user"""
    try:
        response = interventions_table.query(
            IndexName='UserInterventionsIndex',
            KeyConditionExpression='userId = :uid',
            ExpressionAttributeValues={':uid': user_id},
            ScanIndexForward=False,
            Limit=1
        )
        
        items = response.get('Items', [])
        return items[0] if items else None
    except Exception as e:
        print(f"Error getting last intervention: {e}")
        return None


def should_send_intervention(user_id, risk_level):
    """Check if intervention should be sent based on frequency rules"""
    last_intervention = get_last_intervention(user_id)
    
    if not last_intervention:
        return True  # First intervention
    
    last_timestamp = datetime.fromisoformat(last_intervention['timestamp'].replace('Z', '+00:00'))
    hours_since_last = (datetime.utcnow().replace(tzinfo=last_timestamp.tzinfo) - last_timestamp).total_seconds() / 3600
    
    # Minimum hours between interventions by risk level
    min_hours = {
        'minimal': 999,  # Don't send
        'low': 168,      # 1 week
        'moderate': 72,  # 3 days
        'high': 24,      # 1 day
        'critical': 6    # 6 hours
    }
    
    required_gap = min_hours.get(risk_level, 24)
    
    # If user responded to last intervention, wait longer
    if last_intervention.get('userResponded'):
        required_gap *= 2
    
    return hours_since_last >= required_gap


def gather_intervention_context(user_id, risk_level, risk_factors):
    """Gather context for personalized intervention message"""
    user = get_user_profile(user_id)
    name = user.get('name', 'there')
    
    # Get recent moods
    recent_moods = get_recent_moods(user_id, days=7)
    mood_avg = sum(recent_moods) / len(recent_moods) if recent_moods else 5.0
    
    # Get recent chat messages
    recent_chats = get_recent_chats(user_id, days=3)
    
    # Extract themes from risk factors
    themes = []
    for factor in risk_factors:
        if 'mood' in factor.lower() or 'declining' in factor.lower():
            themes.append('mood_decline')
        if 'isolated' in factor.lower() or 'isolation' in factor.lower():
            themes.append('isolation')
        if 'negative' in factor.lower() or 'sentiment' in factor.lower():
            themes.append('negative_sentiment')
        if 'late' in factor.lower() or 'night' in factor.lower():
            themes.append('sleep_disruption')
        if 'crisis' in factor.lower() or 'hopeless' in factor.lower():
            themes.append('crisis_language')
    
    # Get previous interventions count
    last_intervention = get_last_intervention(user_id)
    
    return {
        'name': name,
        'risk_level': risk_level,
        'risk_factors': risk_factors,
        'mood_avg': round(mood_avg, 1),
        'mood_count': len(recent_moods),
        'chat_count': len(recent_chats),
        'themes': list(set(themes)),
        'has_previous_intervention': last_intervention is not None,
        'previous_responded': last_intervention.get('userResponded', False) if last_intervention else False
    }


def generate_intervention_message(context):
    """Generate personalized intervention message using Bedrock Claude"""
    
    # Build prompt based on risk level
    risk_level = context['risk_level']
    name = context['name']
    risk_factors = context['risk_factors']
    mood_avg = context['mood_avg']
    themes = context['themes']
    
    # Customize prompt by risk level
    if risk_level == 'critical':
        urgency = "URGENT - This user may be in crisis"
        tone = "urgent but compassionate, include crisis resources"
        actions = "Strongly encourage calling 988 or texting HOME to 741741"
    elif risk_level == 'high':
        urgency = "HIGH PRIORITY - This user needs immediate support"
        tone = "concerned and supportive, offer concrete help"
        actions = "Offer to talk, provide coping strategies, mention crisis resources"
    elif risk_level == 'moderate':
        urgency = "MODERATE - This user could use a check-in"
        tone = "caring and gentle, offer support"
        actions = "Ask how they're feeling, offer activities or conversation"
    else:  # low
        urgency = "LOW - This is a positive check-in"
        tone = "warm and encouraging"
        actions = "Acknowledge their consistency, offer continued support"
    
    prompt = f"""You are Mind Mate, a compassionate mental health support AI. Generate a caring, personalized intervention message.

Context:
- User name: {name}
- Risk level: {risk_level} ({urgency})
- Risk factors: {', '.join(risk_factors)}
- Recent mood average: {mood_avg}/10
- Themes detected: {', '.join(themes) if themes else 'general concern'}

Guidelines:
1. Use a {tone} tone
2. Address them by name naturally
3. Reference specific concerns from risk factors
4. {actions}
5. Keep message concise (2-3 short paragraphs)
6. End with supportive emoji (💙 or similar)
7. Be authentic and human, not robotic

Generate ONLY the message text, no additional commentary:"""

    try:
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 400,
                'messages': [{
                    'role': 'user',
                    'content': prompt
                }],
                'temperature': 0.7
            })
        )
        
        result = json.loads(response['body'].read())
        message = result['content'][0]['text'].strip()
        
        # Add crisis resources for high/critical risk
        if risk_level in ['high', 'critical']:
            message += "\n\n🆘 Crisis Resources:\n"
            message += "• Call 988 (Suicide & Crisis Lifeline)\n"
            message += "• Text HOME to 741741 (Crisis Text Line)\n"
            message += "• Call 911 if in immediate danger"
        
        return message
        
    except Exception as e:
        print(f"Error generating message with Bedrock: {e}")
        # Fallback message
        return f"Hi {name}, I've noticed some concerning patterns and wanted to check in. How are you feeling today? I'm here to support you. 💙"


def send_via_bedrock_agent(user_id, message):
    """Send intervention message via Bedrock Agent"""
    try:
        session_id = f"{user_id}-intervention-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        # Note: Bedrock Agent doesn't support proactive messages directly
        # Instead, we store the message in chat history so it appears when user opens app
        
        # Store in chat history (EmoCompanion table uses PK/SK structure)
        timestamp = datetime.utcnow().isoformat() + 'Z'
        chat_table.put_item(Item={
            'PK': f"USER#{user_id}",
            'SK': f"CHAT#{timestamp}",
            'userId': user_id,
            'timestamp': timestamp,
            'message': message,
            'sender': 'agent',
            'messageType': 'intervention',
            'sessionId': session_id,
            'agentId': BEDROCK_AGENT_ID
        })
        
        print(f"Intervention message stored in chat history for {user_id}")
        return session_id
        
    except Exception as e:
        print(f"Error sending via Bedrock Agent: {e}")
        raise


def log_intervention(user_id, risk_level, risk_score, risk_factors, message, session_id):
    """Log intervention in DynamoDB"""
    try:
        intervention_id = f"{user_id}-{datetime.utcnow().isoformat()}"
        timestamp = datetime.utcnow().isoformat() + 'Z'
        
        interventions_table.put_item(Item={
            'interventionId': intervention_id,
            'userId': user_id,
            'timestamp': timestamp,
            'riskLevel': risk_level,
            'riskScore': Decimal(str(round(risk_score, 4))),
            'riskFactors': risk_factors,
            'interventionType': get_intervention_type(risk_level),
            'messageGenerated': message,
            'sessionId': session_id,
            'userResponded': False,
            'responseTimestamp': None,
            'responseEngagement': None,
            'ttl': int((datetime.utcnow().timestamp() + 90 * 24 * 3600))  # 90 days
        })
        
        print(f"Intervention logged: {intervention_id}")
        return intervention_id
        
    except Exception as e:
        print(f"Error logging intervention: {e}")
        raise


def get_intervention_type(risk_level):
    """Map risk level to intervention type"""
    mapping = {
        'minimal': 'none',
        'low': 'encouragement',
        'moderate': 'check_in',
        'high': 'proactive_support',
        'critical': 'crisis_intervention'
    }
    return mapping.get(risk_level, 'check_in')


def alert_admin_if_critical(user_id, risk_level, risk_score):
    """Send SNS alert to admin for critical risk"""
    if risk_level == 'critical' and ALERT_SNS_TOPIC:
        try:
            sns.publish(
                TopicArn=ALERT_SNS_TOPIC,
                Subject=f'CRITICAL: User {user_id} at high crisis risk',
                Message=f"""CRITICAL ALERT

User ID: {user_id}
Risk Level: {risk_level}
Risk Score: {risk_score}
Timestamp: {datetime.utcnow().isoformat()}

Intervention has been sent. Please monitor this user closely.

This is an automated alert from Mind Mate ML Prediction System.
"""
            )
            print(f"Admin alert sent for critical risk: {user_id}")
        except Exception as e:
            print(f"Error sending admin alert: {e}")


def lambda_handler(event, context):
    """Execute intervention for high-risk user"""
    try:
        print(f"Intervention triggered with event: {json.dumps(event)}")
        
        # Parse event
        user_id = event.get('userId')
        risk_level = event.get('riskLevel')
        risk_score = event.get('riskScore', 0.0)
        risk_factors = event.get('riskFactors', [])
        
        if not user_id or not risk_level:
            return {
                'ok': False,
                'error': 'Missing required parameters: userId, riskLevel'
            }
        
        print(f"Processing intervention for {user_id} - {risk_level} risk ({risk_score})")
        
        # Check frequency rules
        if not should_send_intervention(user_id, risk_level):
            print(f"Skipping intervention - too soon since last one")
            return {
                'ok': True,
                'sent': False,
                'reason': 'frequency_limit',
                'message': 'Intervention skipped due to frequency rules'
            }
        
        # Gather context
        print("Gathering intervention context...")
        intervention_context = gather_intervention_context(user_id, risk_level, risk_factors)
        
        # Generate personalized message
        print("Generating personalized message with Bedrock...")
        message = generate_intervention_message(intervention_context)
        print(f"Generated message: {message[:100]}...")
        
        # Send via Bedrock Agent (store in chat history)
        print("Sending intervention message...")
        session_id = send_via_bedrock_agent(user_id, message)
        
        # Log intervention
        print("Logging intervention...")
        intervention_id = log_intervention(
            user_id, risk_level, risk_score, risk_factors, message, session_id
        )
        
        # Alert admin if critical
        if risk_level == 'critical':
            print("Alerting admin for critical risk...")
            alert_admin_if_critical(user_id, risk_level, risk_score)
        
        print(f"Intervention complete: {intervention_id}")
        
        return {
            'ok': True,
            'sent': True,
            'interventionId': intervention_id,
            'sessionId': session_id,
            'riskLevel': risk_level,
            'message': 'Intervention sent successfully'
        }
        
    except Exception as e:
        print(f"Error executing intervention: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'ok': False,
            'error': str(e),
            'message': 'Failed to execute intervention'
        }
