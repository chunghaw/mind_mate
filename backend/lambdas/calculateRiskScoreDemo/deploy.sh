#!/bin/bash

# Deploy calculateRiskScoreDemo Lambda function

set -e

FUNCTION_NAME="mindmate-calculateRiskScoreDemo"
REGION=${AWS_REGION:-us-east-1}
LAMBDA_DIR="backend/lambdas/calculateRiskScoreDemo"

echo "📦 Deploying $FUNCTION_NAME..."

# Get environment variables
source .env 2>/dev/null || true

RISK_ASSESSMENTS_TABLE=${RISK_ASSESSMENTS_TABLE}
ML_LAMBDA_ROLE_ARN=${ML_LAMBDA_ROLE_ARN}

if [ -z "$ML_LAMBDA_ROLE_ARN" ]; then
    echo "❌ ML_LAMBDA_ROLE_ARN not found in .env"
    exit 1
fi

# Create deployment package
echo "📦 Creating deployment package..."
cd $LAMBDA_DIR
zip function.zip lambda_function.py -q
cd ../../..

echo "🚀 Deploying to AWS..."

# Check if function exists
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION >/dev/null 2>&1; then
    echo "♻️  Updating existing function..."
    
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://$LAMBDA_DIR/function.zip \
        --region $REGION \
        --no-cli-pager
    
    aws lambda update-function-configuration \
        --function-name $FUNCTION_NAME \
        --environment "Variables={RISK_ASSESSMENTS_TABLE=$RISK_ASSESSMENTS_TABLE}" \
        --timeout 120 \
        --memory-size 512 \
        --region $REGION \
        --no-cli-pager
    
    echo "✅ Function updated!"
else
    echo "🆕 Creating new function..."
    
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime python3.11 \
        --role $ML_LAMBDA_ROLE_ARN \
        --handler lambda_function.lambda_handler \
        --zip-file fileb://$LAMBDA_DIR/function.zip \
        --timeout 120 \
        --memory-size 512 \
        --environment "Variables={RISK_ASSESSMENTS_TABLE=$RISK_ASSESSMENTS_TABLE}" \
        --region $REGION \
        --no-cli-pager
    
    echo "✅ Function created!"
fi

# Clean up
rm $LAMBDA_DIR/function.zip

echo "🎉 Deployment complete!"
