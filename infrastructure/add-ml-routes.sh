#!/bin/bash

# Add ML-related routes to API Gateway
# This script adds /calculate-risk and /risk-score endpoints

set -e

echo "🔧 Adding ML routes to API Gateway..."

# Get environment variables
source .env

REGION=${Region:-us-east-1}

# Get API Gateway ID
API_ID=$(aws apigateway get-rest-apis --region "$REGION" --query "items[?name=='MindMateAPI'].id" --output text)

if [ -z "$API_ID" ]; then
    echo "❌ Error: MindMateAPI not found"
    exit 1
fi

echo "📍 Found API Gateway: $API_ID"

# Get root resource ID
ROOT_ID=$(aws apigateway get-resources --rest-api-id "$API_ID" --region "$REGION" --query "items[?path=='/'].id" --output text)

echo "📍 Root resource ID: $ROOT_ID"

# Function to create route
create_route() {
    local PATH_PART=$1
    local LAMBDA_NAME=$2
    local METHOD=$3
    
    echo ""
    echo "Creating /$PATH_PART endpoint..."
    
    # Create resource
    RESOURCE_ID=$(aws apigateway create-resource \
        --rest-api-id "$API_ID" \
        --parent-id "$ROOT_ID" \
        --path-part "$PATH_PART" \
        --region "$REGION" \
        --query 'id' \
        --output text 2>/dev/null || \
        aws apigateway get-resources \
            --rest-api-id "$API_ID" \
            --region "$REGION" \
            --query "items[?pathPart=='$PATH_PART'].id" \
            --output text)
    
    echo "  Resource ID: $RESOURCE_ID"
    
    # Create OPTIONS method for CORS
    aws apigateway put-method \
        --rest-api-id "$API_ID" \
        --resource-id "$RESOURCE_ID" \
        --http-method OPTIONS \
        --authorization-type NONE \
        --region "$REGION" 2>/dev/null || true
    
    aws apigateway put-integration \
        --rest-api-id "$API_ID" \
        --resource-id "$RESOURCE_ID" \
        --http-method OPTIONS \
        --type MOCK \
        --request-templates '{"application/json": "{\"statusCode\": 200}"}' \
        --region "$REGION" 2>/dev/null || true
    
    aws apigateway put-method-response \
        --rest-api-id "$API_ID" \
        --resource-id "$RESOURCE_ID" \
        --http-method OPTIONS \
        --status-code 200 \
        --response-parameters '{"method.response.header.Access-Control-Allow-Headers": true, "method.response.header.Access-Control-Allow-Methods": true, "method.response.header.Access-Control-Allow-Origin": true}' \
        --region "$REGION" 2>/dev/null || true
    
    aws apigateway put-integration-response \
        --rest-api-id "$API_ID" \
        --resource-id "$RESOURCE_ID" \
        --http-method OPTIONS \
        --status-code 200 \
        --response-parameters '{"method.response.header.Access-Control-Allow-Headers": "'"'"'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"'"'", "method.response.header.Access-Control-Allow-Methods": "'"'"'GET,POST,OPTIONS'"'"'", "method.response.header.Access-Control-Allow-Origin": "'"'"'*'"'"'"}' \
        --region "$REGION" 2>/dev/null || true
    
    # Create main method
    aws apigateway put-method \
        --rest-api-id "$API_ID" \
        --resource-id "$RESOURCE_ID" \
        --http-method "$METHOD" \
        --authorization-type NONE \
        --region "$REGION" 2>/dev/null || true
    
    # Get Lambda ARN
    LAMBDA_ARN=$(aws lambda get-function --function-name "$LAMBDA_NAME" --region "$REGION" --query 'Configuration.FunctionArn' --output text)
    
    # Create integration
    aws apigateway put-integration \
        --rest-api-id "$API_ID" \
        --resource-id "$RESOURCE_ID" \
        --http-method "$METHOD" \
        --type AWS_PROXY \
        --integration-http-method POST \
        --uri "arn:aws:apigateway:${REGION}:lambda:path/2015-03-31/functions/${LAMBDA_ARN}/invocations" \
        --region "$REGION" 2>/dev/null || true
    
    # Add Lambda permission
    aws lambda add-permission \
        --function-name "$LAMBDA_NAME" \
        --statement-id "apigateway-${PATH_PART}-${METHOD}" \
        --action lambda:InvokeFunction \
        --principal apigateway.amazonaws.com \
        --source-arn "arn:aws:execute-api:${REGION}:*:${API_ID}/*/${METHOD}/${PATH_PART}" \
        --region "$REGION" 2>/dev/null || true
    
    echo "  ✅ /$PATH_PART endpoint created"
}

# Create routes
create_route "calculate-risk" "calculateRiskScore" "POST"
create_route "risk-score" "getRiskScore" "GET"

# Deploy API
echo ""
echo "🚀 Deploying API changes..."
aws apigateway create-deployment \
    --rest-api-id "$API_ID" \
    --stage-name prod \
    --region "$REGION" > /dev/null

echo ""
echo "✅ ML routes added successfully!"
echo ""
echo "API Endpoint: https://${API_ID}.execute-api.${REGION}.amazonaws.com/prod"
echo ""
echo "New endpoints:"
echo "  POST /calculate-risk - Trigger risk assessment"
echo "  GET  /risk-score     - Get latest risk score"
