import json, os, datetime
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
            "Access-Control-Allow-Methods": "OPTIONS,POST"
        },
        "body": json.dumps(body)
    }

def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}")) if isinstance(event.get("body"), str) else (event.get("body") or {})
        user_id = body.get("userId", "demo-user")
        mood = int(body["mood"])  # 1–10
        tags = body.get("tags", [])
        notes = body.get("notes", "")
        ts = datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"

        item = {
            "PK": f"USER#{user_id}",
            "SK": f"MOOD#{ts}",
            "type": "MOOD",
            "userId": user_id,
            "mood": mood,
            "tags": tags,
            "notes": notes,
            "ts": ts
        }
        table.put_item(Item=item)
        
        # Award coins (10-20 based on mood entry completeness)
        coins_earned = 10
        if notes:
            coins_earned += 5
        if tags:
            coins_earned += 5
        
        # Update user coins
        try:
            table.update_item(
                Key={'PK': f'USER#{user_id}', 'SK': 'PROFILE'},
                UpdateExpression='ADD coins :coins',
                ExpressionAttributeValues={':coins': coins_earned}
            )
        except:
            # Profile doesn't exist, create it
            table.put_item(Item={
                'PK': f'USER#{user_id}',
                'SK': 'PROFILE',
                'type': 'PROFILE',
                'userId': user_id,
                'coins': coins_earned,
                'personality': 'gentle'
            })
        
        return _resp(200, {"ok": True, "ts": ts, "mood": mood, "coinsEarned": coins_earned})
    except Exception as e:
        return _resp(500, {"error": str(e)})
