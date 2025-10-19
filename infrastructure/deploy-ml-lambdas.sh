#!/bin/bash

# Deploy ML-related Lambda functions
# This script deploys the new ML integration Lambdas

set -e

echo "🚀 Deploying ML Integration Lambda Functions..."

# Get environment variables
source .env

REGION=${Region:-us-east-1}
ML_LAMBDA_ROLE_ARN=${ML_LAMBDA_ROLE_ARN}

if [ -z "$ML_LAMBDA_ROLE_ARN" ]; then
    echo "❌ Error: ML_LAMBDA_ROLE_ARN not set in .env"
    exit 1
fi

# Function to deploy a Lambda
deploy_lambda() {
    local FUNCTION_NAME=$1
    local LAMBDA_DIR="backend/lambdas/$FUNCTION_NAME"
    
    echo "📦 Deploying $FUNCTION_NAME..."
    
    # Create deployment package
    cd "$LAMBDA_DIR"
    
    # Check if requirements.txt exists
    if [ -f "requirements.txt" ]; then
        echo "  Installing dependencies..."
        pip install -r requirements.txt -t . --quiet
    fi
    
    # Create zip
    zip -r "../${FUNCTION_NAME}.zip" . -x "*.pyc" -x "__pycache__/*" -x "*.md" > /dev/null
    
    cd ../../..
    
    # Check if function exists
    if aws lambda get-function --function-name "$FUNCTION_NAME" --region "$REGION" 2>/dev/null; then
        echo "  Updating existing function..."
        aws lambda update-function-code \
            --function-name "$FUNCTION_NAME" \
            --zip-file "fileb://backend/lambdas/${FUNCTION_NAME}.zip" \
            --region "$REGION" > /dev/null
    else
        echo "  Creating new function..."
        aws lambda create-function \
            --function-name "$FUNCTION_NAME" \
            --runtime python3.11 \
            --role "$ML_LAMBDA_ROLE_ARN" \
            --handler lambda_function.lambda_handler \
            --zip-file "fileb://backend/lambdas/${FUNCTION_NAME}.zip" \
            --timeout 60 \
            --memory-size 512 \
            --environment "Variables={
                TABLE_NAME=EmoCompanion,
                RISK_ASSESSMENTS_TABLE=${RISK_ASSESSMENTS_TABLE},
                INTERVENTIONS_TABLE=${INTERVENTIONS_TABLE},
                ML_MODELS_BUCKET=${ML_MODELS_BUCKET}
            }" \
            --region "$REGION" > /dev/null
    fi
    
    # Clean up
    rm "backend/lambdas/${FUNCTION_NAME}.zip"
    
    echo "  ✅ $FUNCTION_NAME deployed"
}

# Deploy new ML integration Lambdas
deploy_lambda "calculateRiskScore"
deploy_lambda "executeIntervention"

echo ""
echo "✅ All ML Integration Lambdas deployed successfully!"
echo ""
echo "Next steps:"
echo "1. Add API Gateway routes for /calculate-risk and /risk-score"
echo "2. Update frontend to include ML wellness widget"
echo "3. Test the integration"
