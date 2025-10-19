#!/bin/bash

# Deploy prepareTrainingData Lambda function

set -e

FUNCTION_NAME="mindmate-prepareTrainingData"
REGION=${AWS_REGION:-us-east-1}
LAMBDA_DIR="backend/lambdas/prepareTrainingData"

echo "📦 Deploying $FUNCTION_NAME..."

# Get environment variables
source .env 2>/dev/null || true

TABLE_NAME=${TABLE_NAME:-EmoCompanion}
TRAINING_JOBS_TABLE=${TRAINING_JOBS_TABLE}
ML_MODELS_BUCKET=${ML_MODELS_BUCKET}
ML_LAMBDA_ROLE_ARN=${ML_LAMBDA_ROLE_ARN}

if [ -z "$ML_LAMBDA_ROLE_ARN" ]; then
    echo "❌ ML_LAMBDA_ROLE_ARN not found in .env"
    exit 1
fi

if [ -z "$ML_MODELS_BUCKET" ]; then
    echo "❌ ML_MODELS_BUCKET not found in .env"
    exit 1
fi

# Create deployment package
echo "📦 Creating deployment package..."
cd $LAMBDA_DIR

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "📥 Installing dependencies..."
    pip3 install -r requirements.txt -t package/ --quiet 2>/dev/null || pip install -r requirements.txt -t package/ --quiet
    
    # Copy lambda function to package
    cp lambda_function.py package/
    
    # Create zip
    cd package
    zip -r ../function.zip . -q
    cd ..
    
    # Clean up
    rm -rf package
else
    # Just zip the lambda function
    zip function.zip lambda_function.py -q
fi

cd ../../..

echo "🚀 Deploying to AWS..."

# Check if function exists
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION >/dev/null 2>&1; then
    echo "♻️  Updating existing function..."
    
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://$LAMBDA_DIR/function.zip \
        --region $REGION \
        --no-cli-pager
    
    # Update configuration
    aws lambda update-function-configuration \
        --function-name $FUNCTION_NAME \
        --environment "Variables={TABLE_NAME=$TABLE_NAME,TRAINING_JOBS_TABLE=$TRAINING_JOBS_TABLE,ML_MODELS_BUCKET=$ML_MODELS_BUCKET}" \
        --timeout 900 \
        --memory-size 2048 \
        --region $REGION \
        --no-cli-pager
    
    echo "✅ Function updated!"
else
    echo "🆕 Creating new function..."
    
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime python3.11 \
        --role $ML_LAMBDA_ROLE_ARN \
        --handler lambda_function.lambda_handler \
        --zip-file fileb://$LAMBDA_DIR/function.zip \
        --timeout 900 \
        --memory-size 2048 \
        --environment "Variables={TABLE_NAME=$TABLE_NAME,TRAINING_JOBS_TABLE=$TRAINING_JOBS_TABLE,ML_MODELS_BUCKET=$ML_MODELS_BUCKET}" \
        --region $REGION \
        --no-cli-pager
    
    echo "✅ Function created!"
fi

# Clean up zip file
rm $LAMBDA_DIR/function.zip

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "Test the function:"
echo "aws lambda invoke --function-name $FUNCTION_NAME --payload file://$LAMBDA_DIR/test_payload.json response.json --region $REGION"
