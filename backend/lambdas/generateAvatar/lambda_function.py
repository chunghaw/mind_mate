import json, os, base64, uuid
import boto3

s3 = boto3.client('s3')
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
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
        pet_description = body.get("description", "a friendly golden retriever puppy with big eyes")
        
        # Generate avatar using Titan Image
        prompt = f"A cute cartoon-style AI pet avatar: {pet_description}. Friendly, warm, approachable style. Digital art."
        
        bedrock_body = {
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {
                "text": prompt
            },
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "quality": "standard",
                "height": 512,
                "width": 512,
                "cfgScale": 8.0
            }
        }
        
        response = bedrock.invoke_model(
            modelId='amazon.titan-image-generator-v1',
            body=json.dumps(bedrock_body)
        )
        
        response_body = json.loads(response['body'].read())
        image_b64 = response_body['images'][0]
        image_bytes = base64.b64decode(image_b64)
        
        # Save to S3
        key = f"avatars/{user_id}/{uuid.uuid4().hex}.png"
        s3.put_object(Bucket=BUCKET, Key=key, Body=image_bytes, ContentType="image/png")
        
        avatar_url = f"https://{BUCKET}.s3.amazonaws.com/{key}"
        
        # Update user profile
        table.put_item(Item={
            "PK": f"USER#{user_id}",
            "SK": "PROFILE",
            "type": "PROFILE",
            "userId": user_id,
            "petAvatarUrl": avatar_url,
            "petDescription": pet_description,
            "updatedAt": boto3.dynamodb.types.Decimal(str(context.request_time_epoch))
        })
        
        return _resp(200, {"ok": True, "avatarUrl": avatar_url, "s3Key": key})
    except Exception as e:
        return _resp(500, {"error": str(e)})
