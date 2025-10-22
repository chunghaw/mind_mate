#!/bin/bash

# Check SageMaker Training Job Status

JOB_NAME="mindmate-risk-model-20251022-v2"
REGION="us-east-1"

echo "🔍 Checking training job status..."
echo ""

# Get status
STATUS=$(aws sagemaker describe-training-job \
  --training-job-name $JOB_NAME \
  --region $REGION \
  --query 'TrainingJobStatus' \
  --output text)

echo "📊 Job Name: $JOB_NAME"
echo "📍 Status: $STATUS"
echo ""

# Show different messages based on status
case $STATUS in
  "InProgress")
    echo "⏳ Training is in progress..."
    echo "   This typically takes 5-10 minutes."
    echo ""
    echo "💡 Run this script again in a few minutes to check progress."
    ;;
  "Completed")
    echo "✅ Training completed successfully!"
    echo ""
    echo "📦 Model artifacts saved to:"
    MODEL_PATH=$(aws sagemaker describe-training-job \
      --training-job-name $JOB_NAME \
      --region $REGION \
      --query 'ModelArtifacts.S3ModelArtifacts' \
      --output text)
    echo "   $MODEL_PATH"
    echo ""
    echo "🎯 Next steps:"
    echo "   1. Download and inspect model metrics"
    echo "   2. Copy models to 'latest' folder"
    echo "   3. Update Lambda to use ML models"
    ;;
  "Failed")
    echo "❌ Training failed!"
    echo ""
    echo "📋 Failure reason:"
    aws sagemaker describe-training-job \
      --training-job-name $JOB_NAME \
      --region $REGION \
      --query 'FailureReason' \
      --output text
    echo ""
    echo "💡 Check CloudWatch logs for details:"
    echo "   aws logs tail /aws/sagemaker/TrainingJobs --filter-pattern $JOB_NAME"
    ;;
  "Stopped")
    echo "⚠️  Training was stopped."
    ;;
  *)
    echo "❓ Unknown status: $STATUS"
    ;;
esac

echo ""
echo "🔗 View in AWS Console:"
echo "   https://console.aws.amazon.com/sagemaker/home?region=$REGION#/jobs/$JOB_NAME"
