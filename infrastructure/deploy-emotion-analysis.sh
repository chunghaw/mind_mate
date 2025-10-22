#!/bin/bash

# Deploy Emotion Analysis Lambda
echo "🧠 Deploying Emotion Analysis Lambda..."

# Create deployment package
cd backend/lambdas/analyzeEmotions
zip -r ../../../emotion-analysis-lambda.zip .
cd ../../../

# Deploy Lambda function
aws lambda create-function \
    --function-name mindmate-analyzeEmotions \
    --runtime python3.9 \
    --role arn:aws:iam::403745271636:role/MindMateLambdaRole \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://emotion-analysis-lambda.zip \
    --timeout 30 \
    --memory-size 256 \
    --region us-east-1 || \
aws lambda update-function-code \
    --function-name mindmate-analyzeEmotions \
    --zip-file fileb://emotion-analysis-lambda.zip \
    --region us-east-1

# Update function configuration
aws lambda update-function-configuration \
    --function-name mindmate-analyzeEmotions \
    --timeout 30 \
    --memory-size 256 \
    --region us-east-1

# Add API Gateway permissions
aws lambda add-permission \
    --function-name mindmate-analyzeEmotions \
    --statement-id api-gateway-invoke \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:us-east-1:403745271636:h8iyzk1h3k/*" \
    --region us-east-1 2>/dev/null || echo "Permission already exists"

# Clean up
rm emotion-analysis-lambda.zip

echo "✅ Emotion Analysis Lambda deployed successfully!"
echo "📝 Next: Add /analyze-emotions route to API Gateway"