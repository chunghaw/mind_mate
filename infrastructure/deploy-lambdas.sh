#!/bin/bash
# Deploy Lambda functions to AWS
# Usage: ./deploy-lambdas.sh <TABLE_NAME> <BUCKET_NAME> <SENDER_EMAIL> <RECIPIENT_EMAIL>

set -e

TABLE_NAME=${1:-EmoCompanion}
BUCKET_NAME=${2:-mindmate-uploads}
SENDER_EMAIL=${3:-noreply@example.com}
RECIPIENT_EMAIL=${4:-user@example.com}
ROLE_NAME="MindMateLambdaRole"

echo "🚀 Deploying Mind Mate Lambda functions..."
echo "Table: $TABLE_NAME"
echo "Bucket: $BUCKET_NAME"
echo ""

# Get role ARN
ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text)
echo "Using role: $ROLE_ARN"
echo ""

# Function to deploy a Lambda
deploy_lambda() {
    local FUNCTION_NAME=$1
    local HANDLER=${2:-lambda_function.lambda_handler}
    local TIMEOUT=${3:-10}
    local MEMORY=${4:-256}
    
    echo "📦 Deploying $FUNCTION_NAME..."
    
    cd "../backend/lambdas/$FUNCTION_NAME"
    
    # Create deployment package
    zip -q -r function.zip .
    
    # Check if function exists
    if aws lambda get-function --function-name "$FUNCTION_NAME" 2>/dev/null; then
        # Update existing function
        aws lambda update-function-code \
            --function-name "$FUNCTION_NAME" \
            --zip-file fileb://function.zip \
            --no-cli-pager > /dev/null
        
        aws lambda update-function-configuration \
            --function-name "$FUNCTION_NAME" \
            --timeout $TIMEOUT \
            --memory-size $MEMORY \
            --environment "Variables={TABLE_NAME=$TABLE_NAME,BUCKET=$BUCKET_NAME,SENDER_EMAIL=$SENDER_EMAIL,RECIPIENT_EMAIL=$RECIPIENT_EMAIL}" \
            --no-cli-pager > /dev/null
        
        echo "✅ Updated $FUNCTION_NAME"
    else
        # Create new function
        aws lambda create-function \
            --function-name "$FUNCTION_NAME" \
            --runtime python3.12 \
            --role "$ROLE_ARN" \
            --handler "$HANDLER" \
            --zip-file fileb://function.zip \
            --timeout $TIMEOUT \
            --memory-size $MEMORY \
            --environment "Variables={TABLE_NAME=$TABLE_NAME,BUCKET=$BUCKET_NAME,SENDER_EMAIL=$SENDER_EMAIL,RECIPIENT_EMAIL=$RECIPIENT_EMAIL}" \
            --no-cli-pager > /dev/null
        
        echo "✅ Created $FUNCTION_NAME"
    fi
    
    rm function.zip
    cd - > /dev/null
}

# Deploy all functions
deploy_lambda "logMood"
deploy_lambda "analyzeSelfie"
deploy_lambda "analyzeScene"
deploy_lambda "generateAvatar"
deploy_lambda "dailyRecap" "lambda_function.lambda_handler" 30
deploy_lambda "riskScan" "lambda_function.lambda_handler" 30
deploy_lambda "getProfile"
deploy_lambda "updateProfile"
deploy_lambda "getStats" "lambda_function.lambda_handler" 15

echo ""
echo "🎉 All Lambda functions deployed successfully!"
echo ""
echo "Next steps:"
echo "1. Set up API Gateway routes in AWS Console"
echo "2. Verify SES email addresses"
echo "3. Create EventBridge rules for dailyRecap and riskScan"
echo "4. Deploy frontend to Amplify"
