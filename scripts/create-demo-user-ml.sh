#!/bin/bash

# Create ML-Powered Demo User
# This script creates a comprehensive demo user with rich ML features

set -e

echo "🧠 Mind Mate - Creating ML Demo User"
echo "=================================="

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed"
    echo "Please install Node.js and try again"
    exit 1
fi

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS CLI not configured or no permissions"
    echo "Please run 'aws configure' and try again"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install aws-sdk uuid
fi

# Set environment variables
export AWS_REGION=${AWS_REGION:-us-east-1}
export DYNAMODB_TABLE=${DYNAMODB_TABLE:-EmoCompanion}

echo "🔧 Configuration:"
echo "   AWS Region: $AWS_REGION"
echo "   DynamoDB Table: $DYNAMODB_TABLE"
echo ""

# Run the demo user creation script
echo "🚀 Creating demo user with ML features..."
node scripts/create-demo-user-ml.js

echo ""
echo "✅ Demo user creation complete!"
echo ""
echo "🎯 Demo Instructions:"
echo "1. Open your Mind Mate application"
echo "2. Use demo bypass or login with:"
echo "   - User ID: demo_ml_user"
echo "   - Email: demo@mindmate.ai"
echo "3. Navigate to dashboard to see ML analysis"
echo "4. Check AI Report for detailed insights"
echo ""
echo "📊 What to highlight in demo:"
echo "• 49 ML features extracted and analyzed"
echo "• Risk score of 73% (HIGH risk level)"
echo "• Declining mood trend over 14 days"
echo "• Crisis language detection in messages"
echo "• Proactive intervention recommendations"
echo ""
echo "🎬 Ready for demo presentation!"