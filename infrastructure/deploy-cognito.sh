#!/bin/bash

# Mind Mate - Deploy Cognito Stack
# This script deploys the Cognito User Pool with Google OAuth

set -e

echo "🔐 Deploying Mind Mate Cognito Stack..."
echo ""

# Check if Google credentials are provided
if [ -z "$GOOGLE_CLIENT_ID" ] || [ -z "$GOOGLE_CLIENT_SECRET" ]; then
    echo "❌ Error: Google OAuth credentials not set"
    echo ""
    echo "Please set the following environment variables:"
    echo "  export GOOGLE_CLIENT_ID='your-google-client-id'"
    echo "  export GOOGLE_CLIENT_SECRET='your-google-client-secret'"
    echo ""
    echo "To get Google OAuth credentials:"
    echo "1. Go to: https://console.cloud.google.com/apis/credentials"
    echo "2. Create OAuth 2.0 Client ID"
    echo "3. Add authorized redirect URIs:"
    echo "   - http://localhost:8000"
    echo "   - https://mindmate-ACCOUNT_ID.auth.us-east-1.amazoncognito.com/oauth2/idpresponse"
    echo ""
    exit 1
fi

# Get callback URL (default to localhost)
CALLBACK_URL="${CALLBACK_URL:-http://localhost:8000}"
LOGOUT_URL="${LOGOUT_URL:-http://localhost:8000}"

echo "📋 Configuration:"
echo "  Callback URL: $CALLBACK_URL"
echo "  Logout URL: $LOGOUT_URL"
echo "  Region: us-east-1"
echo ""

# Deploy CloudFormation stack
echo "🚀 Deploying CloudFormation stack..."
aws cloudformation deploy \
  --template-file cognito-stack.yaml \
  --stack-name mindmate-cognito \
  --parameter-overrides \
    GoogleClientId="$GOOGLE_CLIENT_ID" \
    GoogleClientSecret="$GOOGLE_CLIENT_SECRET" \
    CallbackURL="$CALLBACK_URL" \
    LogoutURL="$LOGOUT_URL" \
  --capabilities CAPABILITY_IAM \
  --region us-east-1

echo ""
echo "✅ Cognito stack deployed successfully!"
echo ""

# Get stack outputs
echo "📊 Stack Outputs:"
aws cloudformation describe-stacks \
  --stack-name mindmate-cognito \
  --region us-east-1 \
  --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
  --output table

echo ""
echo "💾 Saving configuration to .env file..."

# Get outputs
USER_POOL_ID=$(aws cloudformation describe-stacks \
  --stack-name mindmate-cognito \
  --region us-east-1 \
  --query 'Stacks[0].Outputs[?OutputKey==`UserPoolId`].OutputValue' \
  --output text)

CLIENT_ID=$(aws cloudformation describe-stacks \
  --stack-name mindmate-cognito \
  --region us-east-1 \
  --query 'Stacks[0].Outputs[?OutputKey==`UserPoolClientId`].OutputValue' \
  --output text)

DOMAIN=$(aws cloudformation describe-stacks \
  --stack-name mindmate-cognito \
  --region us-east-1 \
  --query 'Stacks[0].Outputs[?OutputKey==`UserPoolDomain`].OutputValue' \
  --output text)

# Append to .env file
cat >> ../.env << EOF

# Cognito Configuration (added $(date))
COGNITO_USER_POOL_ID=$USER_POOL_ID
COGNITO_CLIENT_ID=$CLIENT_ID
COGNITO_DOMAIN=$DOMAIN
COGNITO_REGION=us-east-1
EOF

echo ""
echo "✅ Configuration saved to .env"
echo ""
echo "📝 Next steps:"
echo "1. Update Google OAuth redirect URIs with:"
echo "   https://$DOMAIN/oauth2/idpresponse"
echo ""
echo "2. Update frontend with Cognito configuration"
echo ""
echo "3. Deploy Lambda authorizer"
echo ""
echo "🎉 Cognito setup complete!"
