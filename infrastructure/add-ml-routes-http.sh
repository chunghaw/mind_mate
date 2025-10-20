#!/bin/bash

# Add ML routes to HTTP API Gateway
set -e

echo "🔧 Adding ML routes to HTTP API Gateway..."

REGION="us-east-1"
API_ID="h8iyzk1h3k"  # MindMateAPI HTTP API

echo "📍 Using API Gateway: $API_ID"

# Function to create route for HTTP API
create_http_route() {
    local ROUTE_KEY=$1
    local LAMBDA_NAME=$2
    
    echo ""
    echo "Creating $ROUTE_KEY endpoint..."
    
    # Get Lambda ARN
    LAMBDA_ARN=$(aws lambda get-function --function-name "$LAMBDA_NAME" --region "$REGION" --query 'Configuration.FunctionArn' --output text)
    echo "  Lambda ARN: $LAMBDA_ARN"
    
    # Create integration
    INTEGRATION_ID=$(aws apigatewayv2 create-integration \
        --api-id "$API_ID" \
        --integration-type AWS_PROXY \
        --integration-uri "$LAMBDA_ARN" \
        --payload-format-version "2.0" \
        --region "$REGION" \
        --query 'IntegrationId' \
        --output text)
    
    echo "  Integration ID: $INTEGRATION_ID"
    
    # Create route
    ROUTE_ID=$(aws apigatewayv2 create-route \
        --api-id "$API_ID" \
        --route-key "$ROUTE_KEY" \
        --target "integrations/$INTEGRATION_ID" \
        --region "$REGION" \
        --query 'RouteId' \
        --output text)
    
    echo "  Route ID: $ROUTE_ID"
    
    # Add Lambda permission
    aws lambda add-permission \
        --function-name "$LAMBDA_NAME" \
        --statement-id "apigateway-http-$(echo $ROUTE_KEY | tr ' /' '-')" \
        --action lambda:InvokeFunction \
        --principal apigateway.amazonaws.com \
        --source-arn "arn:aws:execute-api:${REGION}:*:${API_ID}/*/*" \
        --region "$REGION" 2>/dev/null || echo "  (Permission already exists)"
    
    echo "  ✅ $ROUTE_KEY endpoint created"
}

# Create ML routes
create_http_route "POST /calculate-risk" "calculateRiskScore"
create_http_route "POST /extract-mood-features" "mindmate-extractMoodFeatures"
create_http_route "POST /extract-behavioral-features" "mindmate-extractBehavioralFeatures"
create_http_route "POST /extract-sentiment-features" "mindmate-extractSentimentFeatures"

echo ""
echo "✅ ML routes added successfully!"
echo ""
echo "API Endpoint: https://${API_ID}.execute-api.${REGION}.amazonaws.com"
echo ""
echo "New endpoints:"
echo "  POST /calculate-risk - Calculate risk score"
echo "  POST /extract-mood-features - Extract mood features"
echo "  POST /extract-behavioral-features - Extract behavioral features"
echo "  POST /extract-sentiment-features - Extract sentiment features"
