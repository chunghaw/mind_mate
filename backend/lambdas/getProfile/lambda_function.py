import json, os
import boto3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('TABLE_NAME', 'EmoCompanion'))

def _resp(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "OPTIONS,GET"
        },
        "body": json.dumps(body, default=str)
    }

def lambda_handler(event, context):
    try:
        user_id = event.get('queryStringParameters', {}).get('userId', 'demo-user') if event.get('queryStringParameters') else 'demo-user'
        
        # Get profile
        response = table.get_item(Key={'PK': f'USER#{user_id}', 'SK': 'PROFILE'})
        profile = response.get('Item')
        
        if not profile:
            # Create default profile
            profile = {
                'PK': f'USER#{user_id}',
                'SK': 'PROFILE',
                'type': 'PROFILE',
                'userId': user_id,
                'coins': 0,
                'personality': 'gentle',
                'petName': 'Mind Mate'
            }
            table.put_item(Item=profile)
        
        return _resp(200, {
            "ok": True,
            "profile": {
                "personality": profile.get('personality', 'gentle'),
                "petName": profile.get('petName', 'Mind Mate'),
                "coins": int(profile.get('coins', 0)) if isinstance(profile.get('coins'), Decimal) else profile.get('coins', 0)
            }
        })
        
    except Exception as e:
        return _resp(500, {"error": str(e)})
