import json
import os
import boto3
from datetime import datetime, timedelta
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('TABLE_NAME', 'EmoCompanion'))

def decimal_to_float(obj):
    """Convert Decimal to float for JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: decimal_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [decimal_to_float(i) for i in obj]
    return obj

def lambda_handler(event, context):
    """
    Retrieve chat history for a user from DynamoDB
    Returns last 30 days of conversations
    """
    
    # Enable CORS
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
    }
    
    try:
        # Parse request
        if event.get('httpMethod') == 'OPTIONS':
            return {'statusCode': 200, 'headers': headers, 'body': ''}
        
        # Get userId from query params or body
        user_id = None
        if event.get('queryStringParameters'):
            user_id = event['queryStringParameters'].get('userId')
        elif event.get('body'):
            body = json.loads(event['body']) if isinstance(event['body'], str) else event
            user_id = body.get('userId')
        
        if not user_id:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'userId is required'})
            }
        
        # Query last 30 days of chat messages
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        response = table.query(
            KeyConditionExpression='PK = :pk AND SK BETWEEN :start AND :end',
            ExpressionAttributeValues={
                ':pk': f'USER#{user_id}',
                ':start': f'CHAT#{start_date.isoformat()}',
                ':end': f'CHAT#{end_date.isoformat()}Z'
            },
            ScanIndexForward=True,  # Oldest first
            Limit=100  # Last 100 messages
        )
        
        # Format messages for frontend
        messages = []
        for item in response.get('Items', []):
            if item.get('type') == 'CHAT':
                # Add user message
                if item.get('userMessage'):
                    messages.append({
                        'type': 'user',
                        'text': item['userMessage'],
                        'timestamp': item.get('timestamp', item.get('ts'))
                    })
                
                # Add AI response
                if item.get('aiResponse'):
                    messages.append({
                        'type': 'companion',
                        'text': item['aiResponse'],
                        'timestamp': item.get('timestamp', item.get('ts'))
                    })
        
        # Convert Decimals to floats
        messages = decimal_to_float(messages)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'messages': messages,
                'count': len(messages),
                'userId': user_id
            })
        }
        
    except Exception as e:
        print(f"Error retrieving chat history: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': str(e),
                'messages': []
            })
        }
