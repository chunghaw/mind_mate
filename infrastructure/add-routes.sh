#!/bin/bash
# Add routes and integrations to existing API Gateway

set -e

API_ID="h8iyzk1h3k"
REGION="us-east-1"
ACCOUNT_ID="403745271636"

echo "🚀 Adding integrations and routes to API Gateway..."
echo "API ID: $API_ID"
echo ""

# Function to create integration and route
create_route() {
  local METHOD=$1
  local PATH=$2
  local LAMBDA_NAME=$3
  
  echo "📦 Creating $METHOD $PATH → $LAMBDA_NAME"
  
  LAMBDA_ARN="arn:aws:lambda:$REGION:$ACCOUNT_ID:function:$LAMBDA_NAME"
  
  # Give API Gateway permission to invoke Lambda
  aws lambda add-permission \
    --function-name $LAMBDA_NAME \
    --statement-id apigateway-$API_ID-$(date +%s) \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:$REGION:$ACCOUNT_ID:$API_ID/*/*" \
    --region $REGION 2>/dev/null || echo "  Permission already exists"
  
  # Create integration
  INTEGRATION_ID=$(aws apigatewayv2 create-integration \
    --api-id $API_ID \
    --integration-type AWS_PROXY \
    --integration-uri $LAMBDA_ARN \
    --payload-format-version 2.0 \
    --region $REGION \
    --query 'IntegrationId' \
    --output text)
  
  echo "  Integration ID: $INTEGRATION_ID"
  
  # Create route
  aws apigatewayv2 create-route \
    --api-id $API_ID \
    --route-key "$METHOD $PATH" \
    --target "integrations/$INTEGRATION_ID" \
    --region $REGION > /dev/null
  
  echo "  ✅ Route created"
  echo ""
}

# Create all routes
create_route "POST" "/mood" "logMood"
create_route "POST" "/selfie" "analyzeSelfie"
create_route "POST" "/avatar" "generateAvatar"
create_route "GET" "/profile" "getProfile"
create_route "POST" "/profile" "updateProfile"
create_route "GET" "/stats" "getStats"

# Get API endpoint
API_ENDPOINT=$(aws apigatewayv2 get-api \
  --api-id $API_ID \
  --region $REGION \
  --query 'ApiEndpoint' \
  --output text)

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 All routes created successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "API Endpoint: $API_ENDPOINT"
echo ""
echo "Routes:"
echo "  POST $API_ENDPOINT/mood"
echo "  POST $API_ENDPOINT/selfie"
echo "  POST $API_ENDPOINT/avatar"
echo "  GET  $API_ENDPOINT/profile"
echo "  POST $API_ENDPOINT/profile"
echo "  GET  $API_ENDPOINT/stats"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🧪 Test with:"
echo "curl -X POST \"$API_ENDPOINT/mood\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"userId\":\"demo-user\",\"mood\":8,\"tags\":[\"happy\"]}'"
