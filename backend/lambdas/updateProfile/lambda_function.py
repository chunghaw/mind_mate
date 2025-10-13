import json, os
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('TABLE_NAME', 'EmoCompanion'))

def _resp(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,PUT"
        },
        "body": json.dumps(body)
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
        except:
            profile = {
                'PK': f'USER#{user_id}',
                'SK': 'PROFILE',
                'type': 'PROFILE',
                'userId': user_id,
                'coins': 0
            }
        
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
                "petName": profile.get('petName'),
                "coins": profile.get('coins', 0)
            }
        })
        
    except Exception as e:
        return _resp(500, {"error": str(e)})
