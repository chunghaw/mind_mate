import json, os, datetime
import boto3

dynamodb = boto3.resource('dynamodb')
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
table = dynamodb.Table(os.environ.get('TABLE_NAME', 'EmoCompanion'))

def _resp(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST"
        },
        "body": json.dumps(body)
    }

def get_activity_suggestions(mood, notes, tags, personality='gentle'):
    """Generate contextual activity suggestions using Claude"""
    try:
        prompt = f"""You are an empathetic AI companion helping someone with their mental wellness.

User's current state:
- Mood level: {mood}/10
- Notes: {notes if notes else 'None provided'}
- Tags: {', '.join(tags) if tags else 'None'}
- Personality preference: {personality}

Based on their mood and context, suggest 2-3 specific, actionable activities they can do right now (each taking 2-10 minutes).

Format as JSON array:
[
  {{"activity": "Take 5 deep breaths", "duration": "2 min", "reason": "Helps calm anxiety"}},
  {{"activity": "...", "duration": "...", "reason": "..."}}
]

Keep suggestions practical, specific, and encouraging."""

        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 500,
                "messages": [{
                    "role": "user",
                    "content": prompt
                }]
            })
        )
        
        result = json.loads(response['body'].read())
        suggestions_text = result['content'][0]['text']
        
        # Extract JSON from response
        import re
        json_match = re.search(r'\[.*\]', suggestions_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return []
    except Exception as e:
        print(f"Error generating suggestions: {e}")
        # Fallback suggestions
        if mood <= 4:
            return [
                {"activity": "Take 5 deep breaths", "duration": "2 min", "reason": "Helps calm your mind"},
                {"activity": "Step outside for fresh air", "duration": "5 min", "reason": "Nature can lift your mood"}
            ]
        elif mood <= 7:
            return [
                {"activity": "Listen to uplifting music", "duration": "5 min", "reason": "Music can shift your energy"},
                {"activity": "Write down 3 things you're grateful for", "duration": "3 min", "reason": "Gratitude builds positivity"}
            ]
        else:
            return [
                {"activity": "Share your joy with someone", "duration": "5 min", "reason": "Spreading happiness multiplies it"},
                {"activity": "Do a quick stretch", "duration": "3 min", "reason": "Movement celebrates your good mood"}
            ]

def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}")) if isinstance(event.get("body"), str) else (event.get("body") or {})
        user_id = body.get("userId", "demo-user")
        mood = int(body["mood"])  # 1–10
        tags = body.get("tags", [])
        notes = body.get("notes", "")
        ts = datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"
        
        # Get user personality
        personality = 'gentle'
        try:
            profile_response = table.get_item(Key={'PK': f'USER#{user_id}', 'SK': 'PROFILE'})
            if 'Item' in profile_response:
                personality = profile_response['Item'].get('personality', 'gentle')
        except:
            pass

        # Generate activity suggestions
        suggestions = get_activity_suggestions(mood, notes, tags, personality)

        item = {
            "PK": f"USER#{user_id}",
            "SK": f"MOOD#{ts}",
            "type": "MOOD",
            "userId": user_id,
            "mood": mood,
            "tags": tags,
            "notes": notes,
            "suggestions": suggestions,
            "ts": ts
        }
        table.put_item(Item=item)
        
        return _resp(200, {
            "ok": True,
            "ts": ts,
            "mood": mood,
            "suggestions": suggestions
        })
    except Exception as e:
        return _resp(500, {"error": str(e)})
