import json
import os
import boto3
from datetime import datetime
from decimal import Decimal
import uuid

# AWS Clients
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb')
interventions_table = dynamodb.Table(os.environ.get('INTERVENTIONS_TABLE', 'MindMate-Interventions'))
main_table = dynamodb.Table(os.environ.get('TABLE_NAME', 'EmoCompanion'))

def _resp(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(body, default=str)
    }

def get_user_profile(user_id):
    """Get user profile from DynamoDB"""
    try:
        response = main_table.get_item(
            Key={'PK': f'USER#{user_id}', 'SK': 'PROFILE'}
        )
        profile = response.get('Item', {})
        return {
            'petName': profile.get('petName', 'Mind Mate'),
            'personality': profile.get('personality', 'gentle'),
            'userName': profile.get('userName', 'friend')
        }
    except Exception as e:
        print(f"Error getting profile: {e}")
        return {
            'petName': 'Mind Mate',
            'personality': 'gentle',
            'userName': 'friend'
        }

def get_mood_trend(user_id, days=7):
    """Get recent mood trend"""
    try:
        from boto3.dynamodb.conditions import Key
        from datetime import timedelta
        
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        response = main_table.query(
            KeyConditionExpression=Key('PK').eq(f'USER#{user_id}') & Key('SK').begins_with('MOOD#'),
            ScanIndexForward=False,
            Limit=days * 3  # Allow multiple entries per day
        )
        
        moods = [item.get('mood', 5) for item in response.get('Items', [])]
        
        if moods:
            avg = sum(moods) / len(moods)
            return f"averaging {avg:.1f}/10 over {len(moods)} check-ins"
        return "limited data available"
        
    except Exception as e:
        print(f"Error getting mood trend: {e}")
        return "data unavailable"

def generate_proactive_message(user_id, risk_level, risk_factors, profile):
    """Generate personalized proactive message using Bedrock Claude"""
    try:
        mood_trend = get_mood_trend(user_id, days=7)
        
        personality_traits = {
            'gentle': 'warm, nurturing, and deeply caring',
            'playful': 'upbeat, encouraging, and optimistic',
            'focused': 'calm, centered, and mindfully supportive',
            'sensitive': 'deeply empathetic and emotionally attuned'
        }
        
        trait = personality_traits.get(profile['personality'], 'caring and supportive')
        
        # Build context about risk factors
        risk_context = "\n".join([f"- {factor}" for factor in risk_factors[:3]])
        
        prompt = f"""You are {profile['petName']}, an AI companion with a {trait} personality.

You've noticed some concerning patterns for {profile['userName']}:
{risk_context}

Recent mood trend: {mood_trend}
Risk level: {risk_level}

Generate a caring, proactive check-in message that:
1. Shows you've noticed they might be struggling (without being alarming)
2. Expresses genuine care and concern
3. Offers specific, actionable support
4. Suggests 2-3 helpful activities they could try
5. Reminds them they're not alone and help is available

Keep it warm, conversational, and under 100 words. Don't be clinical or mention "risk" or "assessment". Just be a caring friend who's noticed something and wants to help.

If risk level is critical, gently mention crisis resources (988 Suicide & Crisis Lifeline, Crisis Text Line: text HOME to 741741) as available 24/7 support."""

        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 300,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
            })
        )
        
        result = json.loads(response['body'].read())
        message = result['content'][0]['text']
        return message
        
    except Exception as e:
        print(f"Error generating message: {e}")
        # Fallback message
        if risk_level == 'critical':
            return f"Hey {profile['userName']}, I've been thinking about you and I'm here if you need to talk. Remember, you're not alone - the 988 Lifeline is available 24/7 if you need immediate support. I care about you. 💚"
        else:
            return f"Hey {profile['userName']}, I've noticed you might be going through a tough time. I'm here for you, and I'd love to help. Want to try a calming activity together? 💚"

def create_chat_message(user_id, message):
    """Create a priority chat message in DynamoDB"""
    try:
        timestamp = datetime.utcnow().isoformat() + 'Z'
        
        item = {
            'PK': f'USER#{user_id}',
            'SK': f'MESSAGE#{timestamp}',
            'type': 'PROACTIVE_CHECKIN',
            'message': message,
            'timestamp': timestamp,
            'priority': 'high',
            'read': False
        }
        
        main_table.put_item(Item=item)
        return True
    except Exception as e:
        print(f"Error creating chat message: {e}")
        return False

def suggest_coping_activities(risk_level):
    """Suggest coping activities based on risk level"""
    if risk_level == 'critical':
        return [
            {
                'activity': 'Deep Breathing Exercise',
                'duration': '5 minutes',
                'description': 'Try the 4-7-8 breathing technique to calm your nervous system'
            },
            {
                'activity': 'Reach Out to Someone',
                'duration': '10 minutes',
                'description': 'Call or text a trusted friend or family member'
            },
            {
                'activity': 'Crisis Support',
                'duration': 'As needed',
                'description': '988 Lifeline or Crisis Text Line (text HOME to 741741) - available 24/7'
            }
        ]
    elif risk_level == 'high':
        return [
            {
                'activity': 'Guided Meditation',
                'duration': '10 minutes',
                'description': 'Try a calming meditation to center yourself'
            },
            {
                'activity': 'Gentle Walk',
                'duration': '15 minutes',
                'description': 'Get some fresh air and gentle movement'
            },
            {
                'activity': 'Journaling',
                'duration': '10 minutes',
                'description': 'Write down your thoughts and feelings'
            }
        ]
    else:
        return []

def log_intervention(user_id, risk_level, risk_score, risk_factors, interventions_sent, message):
    """Log intervention details to DynamoDB"""
    try:
        intervention_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat() + 'Z'
        
        item = {
            'interventionId': intervention_id,
            'userId': user_id,
            'timestamp': timestamp,
            'riskLevel': risk_level,
            'riskScore': Decimal(str(round(risk_score, 4))),
            'riskFactors': risk_factors,
            'interventionTypes': interventions_sent,
            'messageGenerated': message,
            'ttl': int((datetime.utcnow().timestamp() + 90 * 24 * 3600))  # 90 days
        }
        
        interventions_table.put_item(Item=item)
        return intervention_id
        
    except Exception as e:
        print(f"Error logging intervention: {e}")
        return None

def lambda_handler(event, context):
    """Execute interventions based on risk level"""
    try:
        # Parse event
        user_id = event.get('userId')
        risk_level = event.get('riskLevel')
        risk_score = event.get('riskScore', 0.0)
        risk_factors = event.get('riskFactors', [])
        
        if not user_id or not risk_level:
            return _resp(400, {'error': 'userId and riskLevel are required'})
        
        interventions_sent = []
        
        # Get user profile
        profile = get_user_profile(user_id)
        
        # Generate personalized message
        print(f"Generating proactive message for {user_id} (risk: {risk_level})")
        message = generate_proactive_message(user_id, risk_level, risk_factors, profile)
        
        # Create priority chat message
        if create_chat_message(user_id, message):
            interventions_sent.append('proactive_checkin')
        
        # Get coping activities
        activities = suggest_coping_activities(risk_level)
        if activities:
            # Store activities as a message
            activities_text = "\n\n".join([
                f"**{a['activity']}** ({a['duration']})\n{a['description']}"
                for a in activities
            ])
            create_chat_message(user_id, f"Here are some activities that might help:\n\n{activities_text}")
            interventions_sent.append('coping_activities')
        
        # Log intervention
        intervention_id = log_intervention(
            user_id, risk_level, risk_score, risk_factors, 
            interventions_sent, message
        )
        
        print(f"Intervention complete: {intervention_id}")
        
        return _resp(200, {
            'ok': True,
            'interventionId': intervention_id,
            'interventionsSent': interventions_sent,
            'messageGenerated': True,
            'message': 'Intervention executed successfully'
        })
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return _resp(500, {'error': str(e)})
