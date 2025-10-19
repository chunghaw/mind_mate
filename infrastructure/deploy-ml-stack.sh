#!/bin/bash

# Deploy ML Prediction System Infrastructure
# This script deploys the CloudFormation stack for the ML prediction system

set -e

echo "🚀 Deploying Mind Mate ML Prediction System Infrastructure..."

# Get AWS Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "📋 AWS Account ID: $AWS_ACCOUNT_ID"

# Set variables
STACK_NAME="MindMate-ML-Prediction"
TEMPLATE_FILE="infrastructure/ml-prediction-stack.yaml"
REGION=${AWS_REGION:-us-east-1}
MODEL_BUCKET_NAME="mindmate-ml-models"

echo "📦 Stack Name: $STACK_NAME"
echo "🌍 Region: $REGION"
echo "🪣 Model Bucket: ${MODEL_BUCKET_NAME}-${AWS_ACCOUNT_ID}"

# Check if stack exists
if aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION >/dev/null 2>&1; then
    echo "♻️  Stack exists. Updating..."
    
    aws cloudformation update-stack \
        --stack-name $STACK_NAME \
        --template-body file://$TEMPLATE_FILE \
        --parameters ParameterKey=ModelBucketName,ParameterValue=$MODEL_BUCKET_NAME \
        --capabilities CAPABILITY_NAMED_IAM \
        --region $REGION
    
    echo "⏳ Waiting for stack update to complete..."
    aws cloudformation wait stack-update-complete \
        --stack-name $STACK_NAME \
        --region $REGION
    
    echo "✅ Stack updated successfully!"
else
    echo "🆕 Creating new stack..."
    
    aws cloudformation create-stack \
        --stack-name $STACK_NAME \
        --template-body file://$TEMPLATE_FILE \
        --parameters ParameterKey=ModelBucketName,ParameterValue=$MODEL_BUCKET_NAME \
        --capabilities CAPABILITY_NAMED_IAM \
        --region $REGION
    
    echo "⏳ Waiting for stack creation to complete..."
    aws cloudformation wait stack-create-complete \
        --stack-name $STACK_NAME \
        --region $REGION
    
    echo "✅ Stack created successfully!"
fi

# Get stack outputs
echo ""
echo "📊 Stack Outputs:"
aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
    --output table

# Create initial folder structure in S3
echo ""
echo "📁 Creating S3 folder structure..."
BUCKET_NAME="${MODEL_BUCKET_NAME}-${AWS_ACCOUNT_ID}"

aws s3api put-object --bucket $BUCKET_NAME --key models/ --region $REGION || true
aws s3api put-object --bucket $BUCKET_NAME --key training/ --region $REGION || true
aws s3api put-object --bucket $BUCKET_NAME --key training/train/ --region $REGION || true
aws s3api put-object --bucket $BUCKET_NAME --key training/validation/ --region $REGION || true

echo "✅ S3 folder structure created!"

# Save outputs to .env file
echo ""
echo "💾 Saving configuration to .env..."

# Get outputs
RISK_TABLE=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query 'Stacks[0].Outputs[?OutputKey==`RiskAssessmentsTableName`].OutputValue' --output text)
TRAINING_TABLE=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query 'Stacks[0].Outputs[?OutputKey==`TrainingJobsTableName`].OutputValue' --output text)
INTERVENTIONS_TABLE=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query 'Stacks[0].Outputs[?OutputKey==`InterventionsTableName`].OutputValue' --output text)
ML_BUCKET=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query 'Stacks[0].Outputs[?OutputKey==`MLModelsBucketName`].OutputValue' --output text)
ML_LAMBDA_ROLE=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query 'Stacks[0].Outputs[?OutputKey==`MLLambdaRoleArn`].OutputValue' --output text)
SAGEMAKER_ROLE=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query 'Stacks[0].Outputs[?OutputKey==`SageMakerRoleArn`].OutputValue' --output text)
SNS_TOPIC=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query 'Stacks[0].Outputs[?OutputKey==`MLAlertsSnsTopicArn`].OutputValue' --output text)
KMS_KEY=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query 'Stacks[0].Outputs[?OutputKey==`KMSKeyId`].OutputValue' --output text)

# Append to .env file
cat >> .env << EOF

# ML Prediction System Configuration
RISK_ASSESSMENTS_TABLE=$RISK_TABLE
TRAINING_JOBS_TABLE=$TRAINING_TABLE
INTERVENTIONS_TABLE=$INTERVENTIONS_TABLE
ML_MODELS_BUCKET=$ML_BUCKET
ML_LAMBDA_ROLE_ARN=$ML_LAMBDA_ROLE
SAGEMAKER_ROLE_ARN=$SAGEMAKER_ROLE
ML_ALERTS_SNS_TOPIC=$SNS_TOPIC
ML_KMS_KEY_ID=$KMS_KEY
EOF

echo "✅ Configuration saved to .env"

echo ""
echo "🎉 ML Prediction System Infrastructure deployed successfully!"
echo ""
echo "Next steps:"
echo "1. Update the SNS topic subscription email in the CloudFormation template"
echo "2. Deploy Lambda functions using: ./infrastructure/deploy-ml-lambdas.sh"
echo "3. Upload initial training data and train the first model"
