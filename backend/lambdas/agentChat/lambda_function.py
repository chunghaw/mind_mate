import json
import os
import boto3
from datetime import datetime

# Initialize Bedrock Agent Runtime client
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('TABLE_NAME', 'EmoCompanion'))

# Agent configuration
AGENT_ID = os.environ.get('AGENT_ID', '8W0ULUYHAE')
AGENT_ALIAS_ID = os.environ.get('AGENT_ALIAS_ID', 'I84EATXKU5')

def lambda_handler(event, context):
    """
    Bedrock Agent chat handler
    Uses AWS Bedrock Agents for orchestrated AI conversations
    """
    try:
        # Parse request
        body = json.loads(event.get('body', '{}')) if isinstance(event.get('body'), str) else event
        
        user_id = body.get('userId', 'demo-user')
        message = body.get('message', '')
        session_id = body.get('sessionId', f"{user_id}-{datetime.utcnow().strftime('%Y%m%d')}")
        
        if not message:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST'
                },
                'body': json.dumps({'error': 'message is required'})
            }
        
        print(f"Agent chat request - User: {user_id}, Session: {session_id}")
        
        # Invoke Bedrock Agent
        response = bedrock_agent_runtime.invoke_agent(
            agentId=AGENT_ID,
            agentAliasId=AGENT_ALIAS_ID,
            sessionId=session_id,
            inputText=message
        )
        
        # Process streaming response
        agent_response = ""
        event_stream = response.get('completion', [])
        
        for event in event_stream:
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    agent_response += chunk['bytes'].decode('utf-8')
        
        print(f"Agent response length: {len(agent_response)}")
        
        # Store conversation in DynamoDB
        timestamp = datetime.utcnow().isoformat() + 'Z'
        try:
            table.put_item(Item={
                'PK': f'USER#{user_id}',
                'SK': f'CHAT#{timestamp}',
                'type': 'CHAT',
                'userId': user_id,
                'userMessage': message,
                'aiResponse': agent_response,
                'sessionId': session_id,
                'agentId': AGENT_ID,
                'timestamp': timestamp,
                'source': 'bedrock-agent'
            })
        except Exception as e:
            print(f"Error storing chat: {e}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({
                'response': agent_response,
                'sessionId': session_id,
                'agentId': AGENT_ID,
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
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({
                'error': str(e),
                'message': 'Failed to invoke Bedrock Agent'
            })
        }
