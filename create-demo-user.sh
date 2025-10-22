#!/bin/bash

# Create demo user for Mind Mate demo
set -e

echo "👤 Creating demo user for Mind Mate"
echo "=================================="

# Configuration
USER_POOL_ID="us-east-1_lWwId4NJq"
REGION="us-east-1"
USERNAME="demo_user"
PASSWORD="DemoML2024!"
EMAIL="demo@mindmate.ai"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    print_error "AWS CLI is not configured. Please run 'aws configure' first."
    exit 1
fi

print_status "Creating demo user in Cognito User Pool: $USER_POOL_ID"

# Create the user
print_status "Creating user: $USERNAME"
aws cognito-idp admin-create-user \
    --user-pool-id "$USER_POOL_ID" \
    --username "$USERNAME" \
    --user-attributes Name=email,Value="$EMAIL" Name=email_verified,Value=true \
    --temporary-password "$PASSWORD" \
    --message-action SUPPRESS \
    --region "$REGION" 2>/dev/null || print_warning "User might already exist"

# Set permanent password
print_status "Setting permanent password..."
aws cognito-idp admin-set-user-password \
    --user-pool-id "$USER_POOL_ID" \
    --username "$USERNAME" \
    --password "$PASSWORD" \
    --permanent \
    --region "$REGION"

print_success "Demo user created successfully!"

echo ""
echo "📋 Demo Credentials:"
echo "Username: $USERNAME"
echo "Password: $PASSWORD"
echo "Email: $EMAIL"
echo ""

# Test the login
print_status "Testing login credentials..."

# Create a test script to verify login works
cat > test-demo-login.js << 'EOF'
const AWS = require('aws-sdk');
const AmazonCognitoIdentity = require('amazon-cognito-identity-js');

// Configure AWS
AWS.config.region = 'us-east-1';

// Cognito configuration
const poolData = {
    UserPoolId: 'us-east-1_lWwId4NJq',
    ClientId: '5jkgbuofrsmrhme6iqtbc2c748'
};

const userPool = new AmazonCognitoIdentity.CognitoUserPool(poolData);

// Test login
const authData = {
    Username: 'demo_user',
    Password: 'DemoML2024!'
};

const authDetails = new AmazonCognitoIdentity.AuthenticationDetails(authData);
const userData = {
    Username: 'demo_user',
    Pool: userPool
};

const cognitoUser = new AmazonCognitoIdentity.CognitoUser(userData);

console.log('🔐 Testing demo user login...');

cognitoUser.authenticateUser(authDetails, {
    onSuccess: (result) => {
        console.log('✅ Login successful!');
        console.log('Token:', result.getIdToken().getJwtToken().substring(0, 50) + '...');
        process.exit(0);
    },
    onFailure: (err) => {
        console.log('❌ Login failed:', err.message);
        process.exit(1);
    }
});
EOF

# Check if Node.js is available for testing
if command -v node &> /dev/null; then
    print_status "Installing test dependencies..."
    npm install amazon-cognito-identity-js aws-sdk --silent 2>/dev/null || true
    
    print_status "Running login test..."
    if node test-demo-login.js 2>/dev/null; then
        print_success "Login test passed!"
    else
        print_warning "Login test failed, but user was created. Try logging in manually."
    fi
    
    # Cleanup
    rm -f test-demo-login.js package*.json node_modules -rf 2>/dev/null || true
else
    print_warning "Node.js not available for testing. Please test login manually."
fi

echo ""
print_success "Demo user setup complete!"
echo ""
echo "🎯 Next steps for demo:"
echo "1. Open frontend/index.html"
echo "2. Click 'Sign in with username'"
echo "3. Use credentials:"
echo "   Username: $USERNAME"
echo "   Password: $PASSWORD"
echo "4. Navigate to dashboard"
echo ""
echo "🎬 Demo is ready!"