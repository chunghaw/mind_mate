#!/bin/bash

# Add /analyze-emotions route to API Gateway
echo "🔗 Adding emotion analysis route to API Gateway..."

API_ID="h8iyzk1h3k"
REGION="us-east-1"

# Create the route
aws apigatewayv2 create-route \
    --api-id $API_ID \
    --route-key "POST /analyze-emotions" \
    --target "integrations/$(aws apigatewayv2 create-integration \
        --api-id $API_ID \
        --integration-type AWS_PROXY \
        --integration-uri "arn:aws:lambda:$REGION:403745271636:function:mindmate-analyzeEmotions" \
        --payload-format-version "2.0" \
        --query 'IntegrationId' \
        --output text)" \
    --region $REGION

# Add CORS preflight
aws apigatewayv2 create-route \
    --api-id $API_ID \
    --route-key "OPTIONS /analyze-emotions" \
    --target "integrations/$(aws apigatewayv2 create-integration \
        --api-id $API_ID \
        --integration-type AWS_PROXY \
        --integration-uri "arn:aws:lambda:$REGION:403745271636:function:mindmate-analyzeEmotions" \
        --payload-format-version "2.0" \
        --query 'IntegrationId' \
        --output text)" \
    --region $REGION

echo "✅ Emotion analysis route added to API Gateway!"
echo "🌐 Endpoint: https://$API_ID.execute-api.$REGION.amazonaws.com/analyze-emotions"