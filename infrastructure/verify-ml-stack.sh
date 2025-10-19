#!/bin/bash

# Verify ML Prediction System Infrastructure
# This script checks that all infrastructure components are properly deployed

set -e

echo "🔍 Verifying Mind Mate ML Prediction System Infrastructure..."
echo ""

STACK_NAME="MindMate-ML-Prediction"
REGION=${AWS_REGION:-us-east-1}
ERRORS=0

# Function to check and report
check_resource() {
    local resource_type=$1
    local resource_name=$2
    local check_command=$3
    
    echo -n "Checking $resource_type: $resource_name... "
    if eval $check_command > /dev/null 2>&1; then
        echo "✅"
    else
        echo "❌"
        ((ERRORS++))
    fi
}

# Check CloudFormation Stack
echo "📦 CloudFormation Stack"
check_resource "Stack" "$STACK_NAME" "aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION"

# Get stack outputs
if aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION > /dev/null 2>&1; then
    RISK_TABLE=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query 'Stacks[0].Outputs[?OutputKey==`RiskAssessmentsTableName`].OutputValue' --output text)
    TRAINING_TABLE=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query 'Stacks[0].Outputs[?OutputKey==`TrainingJobsTableName`].OutputValue' --output text)
    INTERVENTIONS_TABLE=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query 'Stacks[0].Outputs[?OutputKey==`InterventionsTableName`].OutputValue' --output text)
    ML_BUCKET=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query 'Stacks[0].Outputs[?OutputKey==`MLModelsBucketName`].OutputValue' --output text)
    
    echo ""
    echo "🗄️  DynamoDB Tables"
    check_resource "Table" "$RISK_TABLE" "aws dynamodb describe-table --table-name $RISK_TABLE --region $REGION"
    check_resource "Table" "$TRAINING_TABLE" "aws dynamodb describe-table --table-name $TRAINING_TABLE --region $REGION"
    check_resource "Table" "$INTERVENTIONS_TABLE" "aws dynamodb describe-table --table-name $INTERVENTIONS_TABLE --region $REGION"
    
    echo ""
    echo "🪣  S3 Bucket"
    check_resource "Bucket" "$ML_BUCKET" "aws s3 ls s3://$ML_BUCKET --region $REGION"
    
    # Check S3 folder structure
    echo ""
    echo "📁 S3 Folder Structure"
    check_resource "Folder" "models/" "aws s3 ls s3://$ML_BUCKET/models/ --region $REGION"
    check_resource "Folder" "training/" "aws s3 ls s3://$ML_BUCKET/training/ --region $REGION"
    
    echo ""
    echo "🔐 IAM Roles"
    check_resource "Role" "MindMate-MLLambdaRole" "aws iam get-role --role-name MindMate-MLLambdaRole"
    check_resource "Role" "MindMate-SageMakerRole" "aws iam get-role --role-name MindMate-SageMakerRole"
    
    echo ""
    echo "🔔 SNS Topic"
    SNS_TOPIC=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query 'Stacks[0].Outputs[?OutputKey==`MLAlertsSnsTopicArn`].OutputValue' --output text)
    check_resource "Topic" "MindMate-MLAlerts" "aws sns get-topic-attributes --topic-arn $SNS_TOPIC --region $REGION"
    
    echo ""
    echo "⏰ EventBridge Rules"
    check_resource "Rule" "MindMate-DailyRiskAssessment" "aws events describe-rule --name MindMate-DailyRiskAssessment --region $REGION"
    check_resource "Rule" "MindMate-MonthlyRetraining" "aws events describe-rule --name MindMate-MonthlyRetraining --region $REGION"
    
    echo ""
    echo "🔑 KMS Key"
    KMS_KEY=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query 'Stacks[0].Outputs[?OutputKey==`KMSKeyId`].OutputValue' --output text)
    check_resource "Key" "mindmate-ml-data" "aws kms describe-key --key-id $KMS_KEY --region $REGION"
    
    echo ""
    echo "λ Lambda Functions"
    check_resource "Function" "mindmate-riskAssessmentOrchestrator" "aws lambda get-function --function-name mindmate-riskAssessmentOrchestrator --region $REGION"
    check_resource "Function" "mindmate-prepareTrainingData" "aws lambda get-function --function-name mindmate-prepareTrainingData --region $REGION"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $ERRORS -eq 0 ]; then
    echo "✅ All infrastructure components verified successfully!"
    echo ""
    echo "📊 Stack Outputs:"
    aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
        --output table
    
    echo ""
    echo "🎉 Infrastructure is ready for Lambda deployment!"
else
    echo "❌ Found $ERRORS error(s). Please review the output above."
    exit 1
fi
