import json, os
import boto3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('TABLE_NAME', 'EmoCompanion'))

# Helper to convert Decimal to int/float
def decimal_default(obj):
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    raise TypeError

def _resp(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,PUT"
        },
        "body": json.dumps(body, default=decimal_default)
    }

def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}")) if isinstance(event.get("body"), str) else (event.get("body") or {})
        user_id = body.get("userId", "demo-user")
        personality = body.get("personality")
        pet_name = body.get("petName")
        
        if not personality and not pet_name:
            return _resp(400, {"error": "personality or petName required"})
        
        # Get existing profile or create new
        try:
            response = table.get_item(Key={'PK': f'USER#{user_id}', 'SK': 'PROFILE'})
            profile = response.get('Item', {})
            if not profile:
                profile = {}
        except:
            profile = {}
        
        # Ensure required keys
        profile['PK'] = f'USER#{user_id}'
        profile['SK'] = 'PROFILE'
        profile['type'] = 'PROFILE'
        profile['userId'] = user_id
        
        # Update fields
        if personality:
            profile['personality'] = personality
        if pet_name:
            profile['petName'] = pet_name
        
        # Save profile
        table.put_item(Item=profile)
        
        return _resp(200, {
            "ok": True,
            "profile": {
                "personality": profile.get('personality'),
                "petName": profile.get('petName')
            }
        })
        
    except Exception as e:
        return _resp(500, {"error": str(e)})
