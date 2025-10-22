#!/bin/bash

# Fix demo login issue for Mind Mate
set -e

echo "🔧 Fixing demo login issue"
echo "=========================="

USER_POOL_ID="us-east-1_lWwId4NJq"
USERNAME="demo_user"
PASSWORD="DemoML2024!"
EMAIL="demo@mindmate.ai"

echo "Step 1: Creating demo user..."

# Create user with proper escaping
aws cognito-idp admin-create-user \
    --user-pool-id "$USER_POOL_ID" \
    --username "$USERNAME" \
    --user-attributes Name=email,Value="$EMAIL" Name=email_verified,Value=true \
    --temporary-password "TempPass123!" \
    --message-action SUPPRESS \
    --region us-east-1

echo "Step 2: Setting permanent password..."

# Set permanent password
aws cognito-idp admin-set-user-password \
    --user-pool-id "$USER_POOL_ID" \
    --username "$USERNAME" \
    --password "$PASSWORD" \
    --permanent \
    --region us-east-1

echo "✅ Demo user created successfully!"
echo ""
echo "Demo Credentials:"
echo "Username: $USERNAME"
echo "Password: $PASSWORD"
echo ""
echo "Now you can login at frontend/index.html"