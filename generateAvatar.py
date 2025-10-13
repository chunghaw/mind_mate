import os
import json
import base64
import uuid
import boto3

"""
Lambda: generateAvatar
Purpose:
- Generate a personalized pet avatar using Amazon Titan Image on Bedrock
- Store PNG/JPEG to S3 and return a public (or signed) URL

Env vars required:
- BUCKET             (S3 bucket to store images)
- MODEL_ID           (Bedrock model id, e.g., "amazon.titan-image-generator-v1" or "amazon.titan-image-generator-v2:0")
- PUBLIC_URL_PREFIX  (optional; if you're using CloudFront/static site; otherwise return s3 key)
"""

s3 = boto3.client('s3')
bedrock = boto3.client('bedrock-runtime', region_name=os.getenv('AWS_REGION', 'us-east-1'))

BUCKET = os.environ['BUCKET']
MODEL_ID = os.getenv('MODEL_ID', 'amazon.titan-image-generator-v1')
PUBLIC_URL_PREFIX = os.getenv('PUBLIC_URL_PREFIX', '')

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
    body = json.loads(event.get("body", "{}")) if isinstance(event.get("body"), str) else (event.get("body") or {})
    user_id = body.get("userId", "demo-user")
    prompt = body.get("prompt", "cute shiba inu companion in cozy watercolor style, gentle smile, soft lighting, warm color palette")
    width = int(body.get("width", 768))
    height = int(body.get("height", 768))

    request = {
        "taskType": "TEXT_IMAGE",
        "textToImageParams": {"text": prompt},
        "imageGenerationConfig": {
            "numberOfImages": 1,
            "quality": "standard",
            "cfgScale": 8.0,
            "height": height,
            "width": width,
            "seed": 0
        }
    }

    resp = bedrock.invoke_model(
        modelId=MODEL_ID,
        accept="application/json",
        contentType="application/json",
        body=json.dumps(request)
    )
    payload = json.loads(resp['body'].read())
    try:
        b64img = payload["images"][0]["data"]
    except Exception as e:
        return _resp(500, {"ok": False, "error": f"Model response format unexpected: {str(e)}", "raw": payload})

    img_bytes = base64.b64decode(b64img)
    key = f"avatars/{user_id}/{uuid.uuid4().hex}.png"
    s3.put_object(Bucket=BUCKET, Key=key, Body=img_bytes, ContentType="image/png")

    out = {"ok": True, "s3Key": key}
    if PUBLIC_URL_PREFIX:
        out["url"] = PUBLIC_URL_PREFIX.rstrip("/") + "/" + key
    return _resp(200, out)
