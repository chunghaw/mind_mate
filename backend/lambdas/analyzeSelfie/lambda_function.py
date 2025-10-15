import json, os, base64, uuid, datetime
import boto3

s3 = boto3.client('s3')
rek = boto3.client('rekognition')
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('TABLE_NAME', 'EmoCompanion'))
BUCKET = os.environ.get('BUCKET', 'mindmate-uploads')

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

def detect_environment_context(bucket, key):
    """Detect indoor/outdoor, weather conditions, and scene context"""
    try:
        # Detect labels (objects, scenes, activities)
        labels_response = rek.detect_labels(
            Image={"S3Object": {"Bucket": bucket, "Name": key}},
            MaxLabels=20,
            MinConfidence=70
        )
        
        labels = [l['Name'] for l in labels_response.get('Labels', [])]
        
        # Determine indoor/outdoor
        outdoor_indicators = ['Sky', 'Cloud', 'Outdoors', 'Nature', 'Tree', 'Grass', 'Sun', 'Mountain', 'Beach', 'Park']
        indoor_indicators = ['Indoors', 'Room', 'Furniture', 'Wall', 'Ceiling', 'Floor', 'Office', 'Home']
        
        outdoor_score = sum(1 for l in labels if l in outdoor_indicators)
        indoor_score = sum(1 for l in labels if l in indoor_indicators)
        
        location = 'outdoor' if outdoor_score > indoor_score else 'indoor'
        
        # Detect weather conditions (if outdoor)
        weather = 'unknown'
        if location == 'outdoor':
            if 'Sun' in labels or 'Sunny' in labels:
                weather = 'sunny'
            elif 'Cloud' in labels or 'Overcast' in labels:
                weather = 'cloudy'
            elif 'Rain' in labels or 'Storm' in labels:
                weather = 'rainy'
            elif 'Snow' in labels:
                weather = 'snowy'
        
        # Detect activity context
        activity_context = []
        activity_keywords = {
            'work': ['Office', 'Computer', 'Desk', 'Meeting'],
            'exercise': ['Gym', 'Sports', 'Running', 'Yoga'],
            'social': ['Restaurant', 'Party', 'People', 'Group'],
            'relaxation': ['Bed', 'Couch', 'Reading', 'Nature'],
            'commute': ['Car', 'Bus', 'Train', 'Transportation']
        }
        
        for activity, keywords in activity_keywords.items():
            if any(k in labels for k in keywords):
                activity_context.append(activity)
        
        return {
            'location': location,
            'weather': weather,
            'labels': labels[:10],  # Top 10 labels
            'activity_context': activity_context
        }
    except Exception as e:
        print(f"Error detecting environment: {e}")
        return {'location': 'unknown', 'weather': 'unknown', 'labels': [], 'activity_context': []}

def generate_contextual_response(emotions, environment, personality='gentle'):
    """Generate empathetic response with activity suggestions based on full context"""
    try:
        top_emotion = emotions[0]['Type'] if emotions else 'CALM'
        confidence = emotions[0]['Confidence'] if emotions else 0
        
        prompt = f"""You are an empathetic AI companion. Respond to your friend based on their current state.

Context:
- Detected emotion: {top_emotion} ({confidence:.0f}% confidence)
- Location: {environment['location']}
- Weather: {environment['weather']}
- Scene: {', '.join(environment['labels'][:5])}
- Activity context: {', '.join(environment['activity_context']) if environment['activity_context'] else 'general'}
- Personality: {personality}

Provide:
1. A warm, empathetic message (2-3 sentences)
2. 2-3 specific activity suggestions that fit their current context and environment

Format as JSON:
{{
  "message": "Your empathetic response here...",
  "activities": [
    {{"activity": "...", "duration": "...", "reason": "..."}},
    {{"activity": "...", "duration": "...", "reason": "..."}}
  ]
}}

Make suggestions practical for their current location and weather."""

        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 600,
                "messages": [{
                    "role": "user",
                    "content": prompt
                }]
            })
        )
        
        result = json.loads(response['body'].read())
        response_text = result['content'][0]['text']
        
        # Extract JSON
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        
        return {
            "message": "I'm here with you. How can I support you right now?",
            "activities": []
        }
    except Exception as e:
        print(f"Error generating response: {e}")
        return {
            "message": "I'm here with you. How can I support you right now?",
            "activities": []
        }

def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}")) if isinstance(event.get("body"), str) else (event.get("body") or {})
        user_id = body.get("userId", "demo-user")
        img_b64 = body["imageBase64"]
        
        # Strip data URL prefix if present
        if "," in img_b64:
            img_b64 = img_b64.split(",", 1)[1]
        img_bytes = base64.b64decode(img_b64)

        ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        key = f"selfies/{user_id}/{ts}-{uuid.uuid4().hex}.jpg"
        s3.put_object(Bucket=BUCKET, Key=key, Body=img_bytes, ContentType="image/jpeg")

        # Detect emotions
        faces = rek.detect_faces(Image={"S3Object": {"Bucket": BUCKET, "Name": key}}, Attributes=["ALL"])
        emotions = []
        if faces.get("FaceDetails"):
            emotions = sorted(faces["FaceDetails"][0].get("Emotions", []), key=lambda e: e["Confidence"], reverse=True)[:3]

        # Detect environment context
        environment = detect_environment_context(BUCKET, key)
        
        # Get user personality
        personality = 'gentle'
        try:
            profile_response = table.get_item(Key={'PK': f'USER#{user_id}', 'SK': 'PROFILE'})
            if 'Item' in profile_response:
                personality = profile_response['Item'].get('personality', 'gentle')
        except:
            pass
        
        # Generate contextual response
        ai_response = generate_contextual_response(emotions, environment, personality)

        # Store analysis with full context
        table.put_item(Item={
            "PK": f"USER#{user_id}",
            "SK": f"SELFIE#{ts}",
            "type": "SELFIE",
            "userId": user_id,
            "s3Key": key,
            "emotions": [{"Type": e["Type"], "Confidence": round(e["Confidence"], 2)} for e in emotions],
            "environment": environment,
            "aiResponse": ai_response,
            "ts": ts
        })
        
        return _resp(200, {
            "ok": True,
            "s3Key": key,
            "emotions": emotions,
            "environment": environment,
            "response": ai_response
        })
    except Exception as e:
        return _resp(500, {"error": str(e)})
