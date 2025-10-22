#!/bin/bash

# Deploy Risk Calculation API Gateway

set -e

echo "🚀 Deploying Risk Calculation API Gateway..."

# Get AWS Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=${AWS_REGION:-us-east-1}

echo "📋 AWS Account ID: $AWS_ACCOUNT_ID"
echo "🌍 Region: $REGION"

# Check if API Gateway exists
API_ID=$(aws apigateway get-rest-apis --query 'items[?name==`MindMate-Risk-API`].id' --output text)

if [ -z "$API_ID" ]; then
    echo "🆕 Creating new API Gateway..."
    
    # Create API Gateway
    API_ID=$(aws apigateway create-rest-api \
        --name "MindMate-Risk-API" \
        --description "API for Mind Mate risk calculation" \
        --endpoint-configuration types=REGIONAL \
        --query 'id' --output text)
    
    echo "✅ API Gateway created: $API_ID"
else
    echo "♻️  Using existing API Gateway: $API_ID"
fi

# Get root resource ID
ROOT_RESOURCE_ID=$(aws apigateway get-resources \
    --rest-api-id $API_ID \
    --query 'items[?path==`/`].id' \
    --output text)

echo "📁 Root resource ID: $ROOT_RESOURCE_ID"

# Create /risk resource
RISK_RESOURCE_ID=$(aws apigateway get-resources \
    --rest-api-id $API_ID \
    --query 'items[?pathPart==`risk`].id' \
    --output text)

if [ -z "$RISK_RESOURCE_ID" ]; then
    echo "🆕 Creating /risk resource..."
    RISK_RESOURCE_ID=$(aws apigateway create-resource \
        --rest-api-id $API_ID \
        --parent-id $ROOT_RESOURCE_ID \
        --path-part "risk" \
        --query 'id' --output text)
    echo "✅ /risk resource created: $RISK_RESOURCE_ID"
else
    echo "♻️  Using existing /risk resource: $RISK_RESOURCE_ID"
fi

# Create /risk/calculate resource
CALCULATE_RESOURCE_ID=$(aws apigateway get-resources \
    --rest-api-id $API_ID \
    --query 'items[?pathPart==`calculate`].id' \
    --output text)

if [ -z "$CALCULATE_RESOURCE_ID" ]; then
    echo "🆕 Creating /risk/calculate resource..."
    CALCULATE_RESOURCE_ID=$(aws apigateway create-resource \
        --rest-api-id $API_ID \
        --parent-id $RISK_RESOURCE_ID \
        --path-part "calculate" \
        --query 'id' --output text)
    echo "✅ /risk/calculate resource created: $CALCULATE_RESOURCE_ID"
else
    echo "♻️  Using existing /risk/calculate resource: $CALCULATE_RESOURCE_ID"
fi

# Create POST method
echo "🔧 Setting up POST method..."
aws apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $CALCULATE_RESOURCE_ID \
    --http-method POST \
    --authorization-type NONE \
    --no-api-key-required 2>/dev/null || echo "Method already exists"

# Enable CORS
echo "🌐 Setting up CORS..."
aws apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $CALCULATE_RESOURCE_ID \
    --http-method OPTIONS \
    --authorization-type NONE \
    --no-api-key-required 2>/dev/null || echo "OPTIONS method already exists"

# Set up Lambda integration
LAMBDA_ARN="arn:aws:lambda:$REGION:$AWS_ACCOUNT_ID:function:mindmate-calculateRiskScore"

echo "🔗 Setting up Lambda integration..."
aws apigateway put-integration \
    --rest-api-id $API_ID \
    --resource-id $CALCULATE_RESOURCE_ID \
    --http-method POST \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri "arn:aws:apigateway:$REGION:lambda:path/2015-03-31/functions/$LAMBDA_ARN/invocations"

# Set up method response
aws apigateway put-method-response \
    --rest-api-id $API_ID \
    --resource-id $CALCULATE_RESOURCE_ID \
    --http-method POST \
    --status-code 200 \
    --response-parameters method.response.header.Access-Control-Allow-Origin=false

# Set up CORS responses
aws apigateway put-method-response \
    --rest-api-id $API_ID \
    --resource-id $CALCULATE_RESOURCE_ID \
    --http-method OPTIONS \
    --status-code 200 \
    --response-parameters method.response.header.Access-Control-Allow-Origin=false,method.response.header.Access-Control-Allow-Methods=false,method.response.header.Access-Control-Allow-Headers=false

# Set up CORS integration
aws apigateway put-integration \
    --rest-api-id $API_ID \
    --resource-id $CALCULATE_RESOURCE_ID \
    --http-method OPTIONS \
    --type MOCK \
    --request-templates '{"application/json":"{\"statusCode\": 200}"}'

aws apigateway put-integration-response \
    --rest-api-id $API_ID \
    --resource-id $CALCULATE_RESOURCE_ID \
    --http-method OPTIONS \
    --status-code 200 \
    --response-parameters method.response.header.Access-Control-Allow-Origin="'*'",method.response.header.Access-Control-Allow-Methods="'GET,POST,OPTIONS'",method.response.header.Access-Control-Allow-Headers="'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"

# Give API Gateway permission to invoke Lambda
echo "🔐 Setting up Lambda permissions..."
aws lambda add-permission \
    --function-name mindmate-calculateRiskScore \
    --statement-id apigateway-invoke \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:$REGION:$AWS_ACCOUNT_ID:$API_ID/*/*" 2>/dev/null || echo "Permission already exists"

# Deploy API
echo "🚀 Deploying API..."
aws apigateway create-deployment \
    --rest-api-id $API_ID \
    --stage-name prod \
    --description "Risk calculation API deployment"

# Get API URL
API_URL="https://$API_ID.execute-api.$REGION.amazonaws.com/prod"

echo ""
echo "🎉 API Gateway deployed successfully!"
echo ""
echo "API Details:"
echo "  API ID: $API_ID"
echo "  Region: $REGION"
echo "  Stage: prod"
echo ""
echo "Endpoint:"
echo "  POST $API_URL/risk/calculate"
echo ""
echo "Test the API:"
echo "  curl -X POST $API_URL/risk/calculate \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"userId\":\"test-user\"}'"
echo ""
echo "Update frontend API_BASE to:"
echo "  const API_BASE = \"$API_URL\";"