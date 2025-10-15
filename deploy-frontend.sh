#!/bin/bash

# Mind Mate Frontend Deployment Script
# Deploys frontend to S3 static website hosting

set -e

BUCKET_NAME="mindmate-frontend-403745271636"
REGION="us-east-1"
FRONTEND_FILE="frontend/app-v2.html"

echo "🚀 Mind Mate Frontend Deployment"
echo "================================"
echo ""

# Check if bucket exists
echo "📦 Checking if bucket exists..."
if aws s3 ls "s3://${BUCKET_NAME}" 2>&1 | grep -q 'NoSuchBucket'; then
    echo "Creating bucket ${BUCKET_NAME}..."
    aws s3 mb "s3://${BUCKET_NAME}" --region ${REGION}
    
    # Enable static website hosting
    echo "🌐 Enabling static website hosting..."
    aws s3 website "s3://${BUCKET_NAME}" \
        --index-document index.html \
        --error-document index.html
    
    # Set bucket policy for public read
    echo "🔓 Setting public read policy..."
    cat > /tmp/bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::${BUCKET_NAME}/*"
        }
    ]
}
EOF
    aws s3api put-bucket-policy \
        --bucket ${BUCKET_NAME} \
        --policy file:///tmp/bucket-policy.json
    
    rm /tmp/bucket-policy.json
else
    echo "✅ Bucket already exists"
fi

# Upload frontend file
echo ""
echo "📤 Uploading frontend..."
aws s3 cp ${FRONTEND_FILE} "s3://${BUCKET_NAME}/index.html" \
    --content-type "text/html" \
    --cache-control "max-age=300"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Website URL:"
echo "http://${BUCKET_NAME}.s3-website-${REGION}.amazonaws.com"
echo ""
echo "📝 Note: It may take a few seconds for the website to be available."
echo ""
