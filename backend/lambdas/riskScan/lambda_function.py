import os, json, datetime
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('TABLE_NAME', 'EmoCompanion'))
ses = boto3.client('ses')
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

SENDER = os.environ.get('SENDER_EMAIL', 'noreply@example.com')
RECIPIENT = os.environ.get('RECIPIENT_EMAIL', 'user@example.com')

def lambda_handler(event, context):
    user_id = event.get("userId", "demo-user")
    
    # Get last 7 days of mood data
    today = datetime.date.today()
    seven_days_ago = today - datetime.timedelta(days=7)
    
    response = table.query(
        KeyConditionExpression=Key('PK').eq(f'USER#{user_id}') & Key('SK').begins_with('MOOD#'),
        ScanIndexForward=False,
        Limit=50
    )
    
    recent_moods = [
        item for item in response.get('Items', []) 
        if item.get('ts', '') >= seven_days_ago.isoformat()
    ]
    
    if len(recent_moods) < 3:
        return {"ok": True, "risk": False, "reason": "Insufficient data"}
    
    # Calculate metrics
    moods = [m['mood'] for m in recent_moods]
    avg_mood = sum(moods) / len(moods)
    
    # Simple slope calculation (first half vs second half)
    mid = len(moods) // 2
    first_half_avg = sum(moods[:mid]) / mid if mid > 0 else avg_mood
    second_half_avg = sum(moods[mid:]) / (len(moods) - mid) if len(moods) > mid else avg_mood
    slope = second_half_avg - first_half_avg
    
    # Risk detection
    risk_detected = False
    risk_reason = ""
    
    if avg_mood <= 4.0:
        risk_detected = True
        risk_reason = f"Low average mood ({avg_mood:.1f}/10) over 7 days"
    elif slope < -1.5:
        risk_detected = True
        risk_reason = f"Declining mood trend (slope: {slope:.1f})"
    
    if not risk_detected:
        return {"ok": True, "risk": False, "avgMood": avg_mood, "slope": slope}
    
    # Get user personality
    try:
        profile_response = table.get_item(Key={'PK': f'USER#{user_id}', 'SK': 'PROFILE'})
        personality = profile_response.get('Item', {}).get('personality', 'gentle')
    except:
        personality = 'gentle'
    
    # Personality-based system prompts
    PERSONALITY_PROMPTS = {
        'gentle': "You are a gentle, nurturing AI companion. Use soft, supportive language with extra warmth during difficult times. Be like a comforting presence who offers unconditional support.",
        'playful': "You are an energetic, caring AI companion. Use encouraging, hopeful language while staying sensitive to their struggles. Be like a loyal friend who brings light even in dark moments.",
        'focused': "You are a calm, wise AI companion. Use clear, grounding language with practical wisdom. Be like a steady anchor who helps people find stability.",
        'sensitive': "You are a deeply empathetic AI companion. Use validating, understanding language with profound compassion. Be like a safe space where all feelings are welcome."
    }
    
    system_prompt = PERSONALITY_PROMPTS.get(personality, PERSONALITY_PROMPTS['gentle'])
    
    # Generate empathetic prevention message
    prompt = f"""{system_prompt}

The user has shown concerning patterns:
- 7-day average mood: {avg_mood:.1f}/10
- Trend: {risk_reason}

Write a gentle, supportive message (max 200 words) that:
- Acknowledges they might be going through a tough time
- Encourages them without being pushy
- Suggests 2-3 evidence-based self-care actions
- Reminds them professional help is available if needed
Keep tone warm, non-judgmental, and hopeful."""

    try:
        bedrock_response = bedrock.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 400,
                "messages": [{"role": "user", "content": prompt}]
            })
        )
        
        response_body = json.loads(bedrock_response['body'].read())
        prevention_text = response_body['content'][0]['text']
    except Exception as e:
        prevention_text = f"We've noticed you might be having a tough week. Remember to take breaks, connect with someone you trust, and consider reaching out to a mental health professional if you need support. You're not alone. 💙"
    
    # Send prevention email
    try:
        ses.send_email(
            Source=SENDER,
            Destination={"ToAddresses": [RECIPIENT]},
            Message={
                "Subject": {"Data": "🐾 Mind Mate Check-In - We're Here for You"},
                "Body": {"Text": {"Data": prevention_text}}
            }
        )
    except Exception as e:
        print(f"SES error: {e}")
    
    # Store risk alert
    table.put_item(Item={
        "PK": f"USER#{user_id}",
        "SK": f"RISK#{today.isoformat()}",
        "type": "RISK",
        "userId": user_id,
        "date": today.isoformat(),
        "avgMood": round(avg_mood, 2),
        "slope": round(slope, 2),
        "reason": risk_reason,
        "preventionText": prevention_text,
        "sentAt": datetime.datetime.utcnow().isoformat(),
        "ts": datetime.datetime.utcnow().isoformat()
    })
    
    return {
        "ok": True, 
        "risk": True, 
        "reason": risk_reason,
        "avgMood": avg_mood,
        "slope": slope
    }
