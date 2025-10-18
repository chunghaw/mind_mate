import json
import boto3
import base64
import os
from datetime import datetime

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
s3 = boto3.client('s3')

BUCKET_NAME = 'mindmate-avatars-403745271636'

# Guardrails: Safe, gentle, mental health companion prompts
PERSONALITY_PROMPTS = {
    'gentle': 'A cute, friendly dog companion with warm, gentle eyes, soft fur, cartoon style, safe for mental health app, comforting and nurturing appearance',
    'playful': 'A cheerful, energetic cat companion with bright eyes, playful expression, cartoon style, safe for mental health app, fun and uplifting appearance',
    'focused': 'A wise, calm dragon companion with serene expression, gentle features, cartoon style, safe for mental health app, mindful and centered appearance',
    'sensitive': 'A kind, empathetic fox companion with understanding eyes, soft features, cartoon style, safe for mental health app, compassionate and validating appearance'
}

# Negative prompts for safety
NEGATIVE_PROMPT = 'scary, aggressive, violent, dark, disturbing, inappropriate, realistic, photorealistic, horror'

def lambda_handler(event, context):
    """
    Generate custom pet avatar using Bedrock Titan Image
    with guardrails for mental health companion appropriateness
    """
    try:
        print(f"Event: {json.dumps(event)}")
        
        # Get userId from request
        try:
            user_id = event['requestContext']['authorizer']['jwt']['claims']['sub']
        except (KeyError, TypeError):
            body = json.loads(event['body'])
            user_id = body.get('userId')
            if not user_id:
                return _resp(401, {'error': 'Unauthorized'})
        
        # Parse request
        body = json.loads(event['body'])
        personality = body.get('personality', 'gentle')
        custom_description = body.get('description', '')
        
        # Build prompt with guardrails
        base_prompt = PERSONALITY_PROMPTS.get(personality, PERSONALITY_PROMPTS['gentle'])
        
        # If user provides custom description, sanitize and append
        if custom_description:
            # Remove potentially harmful keywords
            harmful_keywords = ['scary', 'violent', 'aggressive', 'dark', 'horror', 'disturbing']
            sanitized = custom_description.lower()
            for keyword in harmful_keywords:
                if keyword in sanitized:
                    return _resp(400, {'error': 'Please use gentle, positive descriptions for your companion'})
            
            prompt = f"{base_prompt}, {custom_description}, gentle mental health companion"
        else:
            prompt = f"{base_prompt}, gentle mental health companion"
        
        print(f"Generating avatar with prompt: {prompt}")
        
        # Call Bedrock Titan Image
        request_body = {
            "textToImageParams": {
                "text": prompt,
                "negativeText": NEGATIVE_PROMPT
            },
            "taskType": "TEXT_IMAGE",
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "quality": "standard",
                "height": 512,
                "width": 512,
                "cfgScale": 8.0,
                "seed": int(datetime.now().timestamp())
            }
        }
        
        response = bedrock.invoke_model(
            modelId='amazon.titan-image-generator-v1',
            body=json.dumps(request_body)
        )
        
        response_body = json.loads(response['body'].read())
        
        # Get generated image
        image_base64 = response_body['images'][0]
        image_bytes = base64.b64decode(image_base64)
        
        # Save to S3
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"avatars/{user_id}_{timestamp}.png"
        
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=filename,
            Body=image_bytes,
            ContentType='image/png'
        )
        
        # Generate public URL
        avatar_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{filename}"
        
        print(f"Avatar generated: {avatar_url}")
        
        return _resp(200, {
            'ok': True,
            'avatarUrl': avatar_url,
            'message': 'Avatar generated successfully'
        })
        
    except Exception as e:
        print(f'Error generating avatar: {e}')
        return _resp(500, {'error': str(e)})

def _resp(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'POST,OPTIONS'
        },
        'body': json.dumps(body)
    }
