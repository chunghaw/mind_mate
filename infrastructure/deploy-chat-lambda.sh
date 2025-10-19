#!/bin/bash

# Deploy Chat Lambda Function
# This script deploys the conversational AI chat Lambda

set -e

echo "🚀 Deploying Chat Lambda Function..."

# Configuration
FUNCTION_NAME="mindmate-chat"
REGION="us-east-1"
ROLE_ARN="arn:aws:iam::403745271636:role/MindMate-MLLambdaRole"
TABLE_NAME="EmoCompanion"

# Create deployment package
echo "📦 Creating deployment package..."
cd backend/lambdas/chat
zip -r ../../../chat-lambda.zip lambda_function.py
cd ../../..

# Check if function exists
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION 2>/dev/null; then
    echo "♻️  Updating existing function..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://chat-lambda.zip \
        --region $REGION
    
    aws lambda update-function-configuration \
        --function-name $FUNCTION_NAME \
        --runtime python3.11 \
        --handler lambda_function.lambda_handler \
        --timeout 30 \
        --memory-size 512 \
        --environment "Variables={TABLE_NAME=$TABLE_NAME}" \
        --region $REGION
else
    echo "✨ Creating new function..."
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime python3.11 \
        --role $ROLE_ARN \
        --handler lambda_function.lambda_handler \
        --zip-file fileb://chat-lambda.zip \
        --timeout 30 \
        --memory-size 512 \
        --environment "Variables={TABLE_NAME=$TABLE_NAME}" \
        --region $REGION
fi

# Create function URL
echo "🔗 Creating/updating function URL..."
aws lambda create-function-url-config \
    --function-name $FUNCTION_NAME \
    --auth-type NONE \
    --cors "AllowOrigins=*,AllowMethods=POST,AllowHeaders=*" \
    --region $REGION 2>/dev/null || \
aws lambda update-function-url-config \
    --function-name $FUNCTION_NAME \
    --auth-type NONE \
    --cors "AllowOrigins=*,AllowMethods=POST,AllowHeaders=*" \
    --region $REGION

# Add resource-based policy for function URL
aws lambda add-permission \
    --function-name $FUNCTION_NAME \
    --statement-id FunctionURLAllowPublicAccess \
    --action lambda:InvokeFunctionUrl \
    --principal "*" \
    --function-url-auth-type NONE \
    --region $REGION 2>/dev/null || echo "Permission already exists"

# Get function URL
FUNCTION_URL=$(aws lambda get-function-url-config \
    --function-name $FUNCTION_NAME \
    --region $REGION \
    --query 'FunctionUrl' \
    --output text)

echo ""
echo "✅ Chat Lambda deployed successfully!"
echo "📍 Function URL: $FUNCTION_URL"
echo ""
echo "🧪 Test with:"
echo "curl -X POST $FUNCTION_URL \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"userId\":\"test-user\",\"message\":\"Hello, how are you?\",\"context\":{\"wellnessScore\":7.5,\"riskLevel\":\"LOW\"}}'"
echo ""

# Cleanup
rm -f chat-lambda.zip

echo "🎉 Deployment complete!"
