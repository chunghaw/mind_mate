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
        history = body.get('history', [])
        user_context = body.get('context', {})
        
        if not message:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'message is required'})
            }
        
        # Build system prompt with wellness context
        wellness_score = user_context.get('wellnessScore', 7.5)
        risk_level = user_context.get('riskLevel', 'LOW')
        
        system_prompt = f"""You are a compassionate AI mental health companion named "Your Gentle Guardian". 

Your role:
- Provide empathetic, supportive responses
- Be warm, understanding, and non-judgmental
- Keep responses concise (2-3 sentences)
- Validate feelings and offer gentle encouragement
- Suggest practical coping strategies when appropriate
- Never provide medical advice or diagnosis

Current user context:
- Wellness Score: {wellness_score}/10
- Risk Level: {risk_level}

Respond naturally and supportively to the user's message."""

        # Build conversation messages
        messages = []
        
        # Add conversation history (last 10 messages)
        for msg in history[-10:]:
            messages.append({
                'role': msg.get('role', 'user'),
                'content': msg.get('content', '')
            })
        
        # Add current message
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
            table.put_item(Item={
                'PK': f'USER#{user_id}',
                'SK': f'CHAT#{timestamp}',
                'type': 'CHAT',
                'userId': user_id,
                'userMessage': message,
                'aiResponse': ai_response,
                'wellnessScore': wellness_score,
                'riskLevel': risk_level,
                'timestamp': timestamp,
                'ts': timestamp
            })
        except Exception as db_error:
            print(f"DynamoDB error (non-critical): {db_error}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
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
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': str(e),
                'response': "I'm here to listen. How can I support you today?"
            })
        }
