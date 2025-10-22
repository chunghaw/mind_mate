import json
import os
import boto3
from datetime import datetime

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('TABLE_NAME', 'EmoCompanion'))

def lambda_handler(event, context):
    """
    Conversational AI chat using AWS Bedrock Claude
    Provides empathetic, context-aware responses
    """
    try:
        # Parse request
        body = json.loads(event.get('body', '{}')) if isinstance(event.get('body'), str) else event
        
        user_id = body.get('userId', 'demo-user')
        message = body.get('message', '')
        image_data = body.get('image')
        history = body.get('history', [])
        user_context = body.get('context', {})
        
        if not message and not image_data:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'error': 'message or image is required'})
            }
        
        # Build system prompt with wellness context
        wellness_score = user_context.get('wellnessScore', 7.5)
        risk_level = user_context.get('riskLevel', 'LOW')
        
        system_prompt = f"""You are "Your Gentle Guardian", a compassionate AI mental health companion.

CRITICAL RULES:
- NEVER use asterisks (*) or stage directions in your responses
- NEVER write things like "*responds warmly*", "*speaks gently*", "*nods*", etc.
- Respond DIRECTLY in plain conversational text only
- Maintain conversation context - reference what the user previously shared
- Keep responses natural and conversational (2-3 sentences)
- Be empathetic, warm, and non-judgmental
- Offer practical suggestions when asked "what should I do?"
- Never provide medical advice or diagnosis

IMAGE ANALYSIS:
- If the user shares an image, analyze their facial expression, body language, and environment
- Comment on what you observe in a caring, supportive way
- Ask follow-up questions about how they're feeling
- Provide emotional support based on what you see

Current user context:
- Wellness Score: {wellness_score}/10
- Risk Level: {risk_level}

Read the conversation history carefully and respond naturally to continue the discussion.

REMEMBER: No asterisks or stage directions - just speak directly to the user."""

        # Build conversation messages
        messages = []
        
        # Add conversation history (last 10 messages)
        for msg in history[-10:]:
            messages.append({
                'role': msg.get('role', 'user'),
                'content': msg.get('content', '')
            })
        
        # Add current message (with image support)
        if image_data:
            # Handle image message
            content = []
            if message:
                content.append({
                    "type": "text",
                    "text": message
                })
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": image_data.get('type', 'image/jpeg'),
                    "data": image_data['data']
                }
            })
            messages.append({
                'role': 'user',
                'content': content
            })
        else:
            # Text-only message
            messages.append({
                'role': 'user',
                'content': message
            })
        
        # Ensure first message is from user (Claude requirement)
        if messages and messages[0].get('role') != 'user':
            # Remove leading assistant messages
            while messages and messages[0].get('role') == 'assistant':
                messages.pop(0)
        
        # Call Bedrock Claude
        bedrock_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 300,
            "system": system_prompt,
            "messages": messages,
            "temperature": 0.7
        }
        
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            body=json.dumps(bedrock_body)
        )
        
        response_body = json.loads(response['body'].read())
        ai_response = response_body['content'][0]['text']
        
        # Store conversation in DynamoDB
        timestamp = datetime.utcnow().isoformat() + 'Z'
        try:
            from decimal import Decimal
            table.put_item(Item={
                'PK': f'USER#{user_id}',
                'SK': f'CHAT#{timestamp}',
                'type': 'CHAT',
                'userId': user_id,
                'userMessage': message,
                'aiResponse': ai_response,
                'wellnessScore': Decimal(str(wellness_score)),
                'riskLevel': risk_level,
                'timestamp': timestamp,
                'ts': timestamp
            })
        except Exception as db_error:
            print(f"DynamoDB error (non-critical): {db_error}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': 'https://main.d3pktquxaop3su.amplifyapp.com',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            'body': json.dumps({
                'response': ai_response,
                'timestamp': timestamp
            })
        }
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': 'https://main.d3pktquxaop3su.amplifyapp.com',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }
