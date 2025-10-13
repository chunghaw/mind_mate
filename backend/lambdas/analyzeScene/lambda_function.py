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
        
        if "," in img_b64:
            img_b64 = img_b64.split(",", 1)[1]
        img_bytes = base64.b64decode(img_b64)

        ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        key = f"scenes/{user_id}/{ts}-{uuid.uuid4().hex}.jpg"
        s3.put_object(Bucket=BUCKET, Key=key, Body=img_bytes, ContentType="image/jpeg")

        # Detect scene labels
        labels_resp = rek.detect_labels(Image={"S3Object": {"Bucket": BUCKET, "Name": key}}, MaxLabels=10)
        labels = sorted(labels_resp.get("Labels", []), key=lambda l: l["Confidence"], reverse=True)[:5]

        table.put_item(Item={
            "PK": f"USER#{user_id}",
            "SK": f"SCENE#{ts}",
            "type": "SCENE",
            "userId": user_id,
            "s3Key": key,
            "labels": [{"Name": l["Name"], "Confidence": round(l["Confidence"], 2)} for l in labels],
            "ts": ts
        })
        
        return _resp(200, {"ok": True, "s3Key": key, "topLabels": labels})
    except Exception as e:
        return _resp(500, {"error": str(e)})
