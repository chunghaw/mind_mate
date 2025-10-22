#!/bin/bash

# Deploy executeIntervention Lambda Function

set -e

echo "🚀 Deploying executeIntervention Lambda..."

# Get AWS Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=${AWS_REGION:-us-east-1}

echo "📋 AWS Account ID: $AWS_ACCOUNT_ID"
echo "🌍 Region: $REGION"

# Lambda configuration
FUNCTION_NAME="mindmate-executeIntervention"
LAMBDA_DIR="backend/lambdas/executeIntervention"
ROLE_NAME="MindMate-MLLambdaRole"

# Get role ARN
ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text 2>/dev/null || echo "")

if [ -z "$ROLE_ARN" ]; then
    echo "❌ Error: Role $ROLE_NAME not found"
    echo "Please deploy ML infrastructure first: ./infrastructure/deploy-ml-stack.sh"
    exit 1
fi

echo "✅ Using IAM Role: $ROLE_ARN"

# Get environment variables from .env
if [ -f .env ]; then
    source .env
fi

# Set environment variables for Lambda
ENV_VARS="Variables={"
ENV_VARS+="INTERVENTIONS_TABLE=${INTERVENTIONS_TABLE:-MindMate-Interventions},"
ENV_VARS+="CHAT_HISTORY_TABLE=${CHAT_HISTORY_TABLE:-MindMate-ChatHistory},"
ENV_VARS+="USERS_TABLE=${USERS_TABLE:-MindMate-Users},"
ENV_VARS+="MOOD_LOGS_TABLE=${MOOD_LOGS_TABLE:-MindMate-MoodLogs},"
ENV_VARS+="BEDROCK_AGENT_ID=${BEDROCK_AGENT_ID:-8W0ULUYHAE},"
ENV_VARS+="BEDROCK_AGENT_ALIAS_ID=${BEDROCK_AGENT_ALIAS_ID:-TSTALIASID},"
ENV_VARS+="ML_ALERTS_SNS_TOPIC=${ML_ALERTS_SNS_TOPIC:-}"
ENV_VARS+="}"

echo "📦 Packaging Lambda function..."

# Create deployment package
cd $LAMBDA_DIR
zip -q -r /tmp/executeIntervention.zip lambda_function.py
cd - > /dev/null

echo "✅ Package created"

# Check if function exists
FUNCTION_EXISTS=$(aws lambda get-function --function-name $FUNCTION_NAME --region $REGION 2>/dev/null || echo "")

if [ -z "$FUNCTION_EXISTS" ]; then
    echo "🆕 Creating new Lambda function..."
    
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime python3.11 \
        --role $ROLE_ARN \
        --handler lambda_function.lambda_handler \
        --zip-file fileb:///tmp/executeIntervention.zip \
        --timeout 60 \
        --memory-size 512 \
        --environment "$ENV_VARS" \
        --region $REGION \
        --description "Execute proactive interventions for high-risk users"
    
    echo "✅ Lambda function created"
else
    echo "♻️  Updating existing Lambda function..."
    
    # Update function code
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb:///tmp/executeIntervention.zip \
        --region $REGION
    
    # Wait for update to complete
    echo "⏳ Waiting for code update to complete..."
    aws lambda wait function-updated \
        --function-name $FUNCTION_NAME \
        --region $REGION
    
    # Update function configuration
    aws lambda update-function-configuration \
        --function-name $FUNCTION_NAME \
        --timeout 60 \
        --memory-size 512 \
        --environment "$ENV_VARS" \
        --region $REGION
    
    echo "✅ Lambda function updated"
fi

# Clean up
rm /tmp/executeIntervention.zip

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "Function details:"
echo "  Name: $FUNCTION_NAME"
echo "  Region: $REGION"
echo "  Runtime: python3.11"
echo "  Timeout: 60 seconds"
echo "  Memory: 512 MB"
echo ""
echo "Environment variables:"
echo "  INTERVENTIONS_TABLE: ${INTERVENTIONS_TABLE:-MindMate-Interventions}"
echo "  CHAT_HISTORY_TABLE: ${CHAT_HISTORY_TABLE:-MindMate-ChatHistory}"
echo "  BEDROCK_AGENT_ID: ${BEDROCK_AGENT_ID:-8W0ULUYHAE}"
echo ""
echo "Test the function:"
echo "  aws lambda invoke --function-name $FUNCTION_NAME \\"
echo "    --payload '{\"userId\":\"test-user\",\"riskLevel\":\"high\",\"riskScore\":0.75,\"riskFactors\":[\"Declining mood\"]}' \\"
echo "    /tmp/response.json && cat /tmp/response.json"
