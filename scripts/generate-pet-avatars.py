#!/usr/bin/env python3
"""
Generate 4 pet avatars using Amazon Bedrock Titan Image Generator
Run this script to create personality-based pet images
"""

import boto3
import json
import base64
import os
from datetime import datetime

# Initialize clients
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
s3 = boto3.client('s3')

# Configuration
BUCKET_NAME = os.environ.get('BUCKET', 'mindmate-uploads')  # Replace with your bucket
OUTPUT_DIR = 'pet-avatars'

# Pet personality definitions
PERSONALITIES = {
    'gentle': {
        'name': 'Gentle Guardian',
        'emoji': '🐶',
        'prompt': 'A cute cartoon-style friendly dog companion with soft blue colors, gentle expression, warm kind eyes, supportive and nurturing personality, simple clean background, digital art, kawaii style, pastel colors'
    },
    'playful': {
        'name': 'Playful Pal',
        'emoji': '🐱',
        'prompt': 'A cute cartoon-style playful cat companion with warm yellow and orange colors, energetic happy expression, bright sparkling eyes, fun-loving personality, simple clean background, digital art, kawaii style, vibrant colors'
    },
    'focused': {
        'name': 'Focused Friend',
        'emoji': '🐉',
        'prompt': 'A cute cartoon-style calm dragon companion with purple and lavender colors, centered peaceful expression, wise gentle eyes, focused meditative personality, simple clean background, digital art, kawaii style, serene colors'
    },
    'sensitive': {
        'name': 'Sensitive Soul',
        'emoji': '🦊',
        'prompt': 'A cute cartoon-style empathetic fox companion with warm orange and peach colors, understanding caring expression, kind compassionate eyes, sensitive gentle personality, simple clean background, digital art, kawaii style, soft colors'
    }
}

def generate_avatar(personality_key, personality_data):
    """Generate a single avatar using Bedrock Titan Image"""
    print(f"\n🎨 Generating {personality_data['name']} {personality_data['emoji']}...")
    
    # Prepare Bedrock request
    request_body = {
        "taskType": "TEXT_IMAGE",
        "textToImageParams": {
            "text": personality_data['prompt']
        },
        "imageGenerationConfig": {
            "numberOfImages": 1,
            "quality": "standard",
            "height": 512,
            "width": 512,
            "cfgScale": 8.0,
            "seed": 42  # For consistency
        }
    }
    
    try:
        # Call Bedrock
        response = bedrock.invoke_model(
            modelId='amazon.titan-image-generator-v1',
            body=json.dumps(request_body)
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        image_b64 = response_body['images'][0]
        image_bytes = base64.b64decode(image_b64)
        
        # Save locally
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        local_path = f"{OUTPUT_DIR}/{personality_key}.png"
        with open(local_path, 'wb') as f:
            f.write(image_bytes)
        print(f"✅ Saved locally: {local_path}")
        
        # Upload to S3
        s3_key = f"avatars/{personality_key}.png"
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=image_bytes,
            ContentType='image/png'
        )
        s3_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{s3_key}"
        print(f"✅ Uploaded to S3: {s3_url}")
        
        return {
            'personality': personality_key,
            'name': personality_data['name'],
            'emoji': personality_data['emoji'],
            'local_path': local_path,
            's3_url': s3_url
        }
        
    except Exception as e:
        print(f"❌ Error generating {personality_key}: {str(e)}")
        return None

def main():
    print("🐾 Mind Mate - Pet Avatar Generator")
    print("=" * 50)
    print(f"Bucket: {BUCKET_NAME}")
    print(f"Output: {OUTPUT_DIR}/")
    print("=" * 50)
    
    results = []
    
    # Generate all 4 avatars
    for key, data in PERSONALITIES.items():
        result = generate_avatar(key, data)
        if result:
            results.append(result)
    
    # Summary
    print("\n" + "=" * 50)
    print("🎉 Generation Complete!")
    print("=" * 50)
    
    for result in results:
        print(f"\n{result['emoji']} {result['name']}")
        print(f"  Local: {result['local_path']}")
        print(f"  S3: {result['s3_url']}")
    
    # Save manifest
    manifest_path = f"{OUTPUT_DIR}/manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n📄 Manifest saved: {manifest_path}")
    
    # Generate CSS snippet
    print("\n📝 CSS for frontend:")
    print("```css")
    for result in results:
        print(f".pet-avatar.{result['personality']} {{")
        print(f"  background-image: url('{result['s3_url']}');")
        print(f"}}")
    print("```")

if __name__ == "__main__":
    main()
