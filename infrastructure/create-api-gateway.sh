#!/bin/bash
# Create API Gateway HTTP API with all routes

set -e

REGION="us-east-1"
ACCOUNT_ID="403745271636"
API_NAME="MindMateAPI"

echo "🚀 Creating API Gateway HTTP API..."

# Create the API
API_ID=$(aws apigatewayv2 create-api \
  --name "$API_NAME" \
  --protocol-type HTTP \
  --region $REGION \
  --query 'ApiId' \
  --output text)

echo "✅ API created: $API_ID"

# Enable CORS
aws apigatewayv2 update-api \
  --api-id $API_ID \
  --cors-configuration AllowOrigins='*',AllowMethods='*',AllowHeaders='*' \
  --region $REGION

echo "✅ CORS enabled"

# Create integrations for each Lambda function
declare -A LAMBDAS=(
  ["logMood"]="logMood"
  ["analyzeSelfie"]="analyzeSelfie"
  ["generateAvatar"]="generateAvatar"
  ["getProfile"]="getProfile"
  ["updateProfile"]="updateProfile"
  ["getStats"]="getStats"
)

declare -A INTEGRATION_IDS

for LAMBDA_NAME in "${!LAMBDAS[@]}"; do
  echo "📦 Creating integration for $LAMBDA_NAME..."
  
  LAMBDA_ARN="arn:aws:lambda:$REGION:$ACCOUNT_ID:function:$LAMBDA_NAME"
  
  # Give API Gateway permission to invoke Lambda
  aws lambda add-permission \
    --function-name $LAMBDA_NAME \
    --statement-id apigateway-$API_ID \
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
  
  INTEGRATION_IDS[$LAMBDA_NAME]=$INTEGRATION_ID
  echo "  ✅ Integration created: $INTEGRATION_ID"
done

# Create routes
echo ""
echo "🛣️  Creating routes..."

# POST /mood -> logMood
aws apigatewayv2 create-route \
  --api-id $API_ID \
  --route-key "POST /mood" \
  --target "integrations/${INTEGRATION_IDS[logMood]}" \
  --region $REGION
echo "✅ POST /mood -> logMood"

# POST /selfie -> analyzeSelfie
aws apigatewayv2 create-route \
  --api-id $API_ID \
  --route-key "POST /selfie" \
  --target "integrations/${INTEGRATION_IDS[analyzeSelfie]}" \
  --region $REGION
echo "✅ POST /selfie -> analyzeSelfie"

# POST /avatar -> generateAvatar
aws apigatewayv2 create-route \
  --api-id $API_ID \
  --route-key "POST /avatar" \
  --target "integrations/${INTEGRATION_IDS[generateAvatar]}" \
  --region $REGION
echo "✅ POST /avatar -> generateAvatar"

# GET /profile -> getProfile
aws apigatewayv2 create-route \
  --api-id $API_ID \
  --route-key "GET /profile" \
  --target "integrations/${INTEGRATION_IDS[getProfile]}" \
  --region $REGION
echo "✅ GET /profile -> getProfile"

# POST /profile -> updateProfile
aws apigatewayv2 create-route \
  --api-id $API_ID \
  --route-key "POST /profile" \
  --target "integrations/${INTEGRATION_IDS[updateProfile]}" \
  --region $REGION
echo "✅ POST /profile -> updateProfile"

# GET /stats -> getStats
aws apigatewayv2 create-route \
  --api-id $API_ID \
  --route-key "GET /stats" \
  --target "integrations/${INTEGRATION_IDS[getStats]}" \
  --region $REGION
echo "✅ GET /stats -> getStats"

# Get the API endpoint
API_ENDPOINT=$(aws apigatewayv2 get-api \
  --api-id $API_ID \
  --region $REGION \
  --query 'ApiEndpoint' \
  --output text)

echo ""
echo "🎉 API Gateway setup complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 API Details"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "API ID: $API_ID"
echo "API Endpoint: $API_ENDPOINT"
echo ""
echo "🔗 Routes:"
echo "  POST $API_ENDPOINT/mood"
echo "  POST $API_ENDPOINT/selfie"
echo "  POST $API_ENDPOINT/avatar"
echo "  GET  $API_ENDPOINT/profile"
echo "  POST $API_ENDPOINT/profile"
echo "  GET  $API_ENDPOINT/stats"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Next steps:"
echo "1. Copy the API Endpoint above"
echo "2. Edit frontend/app-v2.html line 139"
echo "3. Replace API URL with: $API_ENDPOINT"
echo "4. Deploy to Amplify"
echo ""
echo "💾 API Endpoint saved to: api-endpoint.txt"
echo $API_ENDPOINT > api-endpoint.txt
