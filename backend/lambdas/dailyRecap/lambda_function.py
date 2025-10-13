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
    
    # Get yesterday's data
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    yesterday_str = yesterday.isoformat()
    
    # Query moods from yesterday
    response = table.query(
        KeyConditionExpression=Key('PK').eq(f'USER#{user_id}') & Key('SK').begins_with('MOOD#'),
        ScanIndexForward=False,
        Limit=10
    )
    
    moods = [item for item in response.get('Items', []) if item.get('ts', '').startswith(yesterday_str)]
    
    # Query selfies/emotions
    selfie_response = table.query(
        KeyConditionExpression=Key('PK').eq(f'USER#{user_id}') & Key('SK').begins_with('SELFIE#'),
        ScanIndexForward=False,
        Limit=5
    )
    selfies = [item for item in selfie_response.get('Items', []) if item.get('ts', '').startswith(yesterday_str)]
    
    # Build context for Bedrock
    mood_summary = f"Logged {len(moods)} mood entries. " if moods else "No mood entries. "
    if moods:
        avg_mood = sum(m['mood'] for m in moods) / len(moods)
        mood_summary += f"Average mood: {avg_mood:.1f}/10. "
    
    emotion_summary = ""
    if selfies:
        all_emotions = []
        for s in selfies:
            all_emotions.extend([e['Type'] for e in s.get('emotions', [])])
        emotion_summary = f"Detected emotions: {', '.join(set(all_emotions))}. "
    
    # Get user personality
    try:
        profile_response = table.get_item(Key={'PK': f'USER#{user_id}', 'SK': 'PROFILE'})
        personality = profile_response.get('Item', {}).get('personality', 'gentle')
    except:
        personality = 'gentle'
    
    # Personality-based system prompts
    PERSONALITY_PROMPTS = {
        'gentle': "You are a gentle, nurturing AI companion. Use soft, supportive language with warmth and care. Be like a comforting friend who always sees the best in people.",
        'playful': "You are an energetic, fun-loving AI companion. Use playful, upbeat language with enthusiasm and joy. Be like an encouraging cheerleader who makes everything feel lighter.",
        'focused': "You are a calm, centered AI companion. Use clear, direct language with wisdom and clarity. Be like a mindful guide who helps people find their center.",
        'sensitive': "You are an empathetic, understanding AI companion. Use warm, validating language with deep compassion. Be like a caring listener who truly understands feelings."
    }
    
    system_prompt = PERSONALITY_PROMPTS.get(personality, PERSONALITY_PROMPTS['gentle'])
    
    # Call Bedrock for empathetic recap
    prompt = f"""{system_prompt}

Given the user's data from {yesterday_str}:
{mood_summary}
{emotion_summary}

Write a warm, encouraging daily recap (max 150 words) that:
- Reflects their emotional trend kindly
- Acknowledges any challenges
- Suggests 2 practical coping strategies
Keep tone friendly and supportive, not clinical."""

    try:
        bedrock_response = bedrock.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 300,
                "messages": [{"role": "user", "content": prompt}]
            })
        )
        
        response_body = json.loads(bedrock_response['body'].read())
        recap_text = response_body['content'][0]['text']
    except Exception as e:
        recap_text = f"Daily recap for {yesterday_str}: Keep going! Try a 2-min breathing break and a 10-min walk. (Bedrock error: {str(e)})"
    
    # Send email
    try:
        ses.send_email(
            Source=SENDER,
            Destination={"ToAddresses": [RECIPIENT]},
            Message={
                "Subject": {"Data": f"🐾 Your Mind Mate Daily Recap - {yesterday_str}"},
                "Body": {"Text": {"Data": recap_text}}
            }
        )
    except Exception as e:
        print(f"SES error: {e}")
    
    # Store recap
    table.put_item(Item={
        "PK": f"USER#{user_id}",
        "SK": f"RECAP#{yesterday_str}",
        "type": "RECAP",
        "userId": user_id,
        "date": yesterday_str,
        "text": recap_text,
        "sentAt": datetime.datetime.utcnow().isoformat(),
        "ts": datetime.datetime.utcnow().isoformat()
    })
    
    return {"ok": True, "recap": recap_text}
