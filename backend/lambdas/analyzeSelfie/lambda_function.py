import json, os, base64, uuid, datetime
import boto3

s3 = boto3.client('s3')
rek = boto3.client('rekognition')
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

        # Store derived scores only (privacy-friendly)
        table.put_item(Item={
            "PK": f"USER#{user_id}",
            "SK": f"SELFIE#{ts}",
            "type": "SELFIE",
            "userId": user_id,
            "s3Key": key,
            "emotions": [{"Type": e["Type"], "Confidence": round(e["Confidence"], 2)} for e in emotions],
            "ts": ts
        })
        
        # Award coins for selfie analysis
        coins_earned = 15
        try:
            table.update_item(
                Key={'PK': f'USER#{user_id}', 'SK': 'PROFILE'},
                UpdateExpression='ADD coins :coins',
                ExpressionAttributeValues={':coins': coins_earned}
            )
        except:
            table.put_item(Item={
                'PK': f'USER#{user_id}',
                'SK': 'PROFILE',
                'type': 'PROFILE',
                'userId': user_id,
                'coins': coins_earned,
                'personality': 'gentle'
            })
        
        return _resp(200, {"ok": True, "s3Key": key, "topEmotions": emotions, "coinsEarned": coins_earned})
    except Exception as e:
        return _resp(500, {"error": str(e)})
