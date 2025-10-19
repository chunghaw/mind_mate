# ML Prediction System Setup Guide

This guide walks you through setting up the ML Prediction System for Mind Mate.

## Overview

The ML Prediction System uses machine learning to predict mental health crisis risk 3-7 days in advance. It includes:

- **Feature Engineering**: Extract mood, behavioral, and sentiment features
- **Model Training**: Train ensemble models using SageMaker
- **Risk Scoring**: Real-time risk assessment for all users
- **Interventions**: Automated proactive support based on risk levels
- **Monitoring**: Track model performance and trigger retraining

## Prerequisites

1. **AWS CLI** configured with appropriate credentials
2. **Python 3.11** installed locally
3. **Existing Mind Mate infrastructure** deployed (main CloudFormation stack)
4. **At least 60 days of user data** for initial model training

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ML Prediction System                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  EventBridge → Orchestrator → Risk Scoring → Interventions  │
│                      ↓              ↓                        │
│                  Features      DynamoDB                      │
│                      ↓                                       │
│                  S3 Models                                   │
│                                                              │
│  EventBridge → Training Data Prep → SageMaker Training      │
│                                           ↓                  │
│                                      New Models → S3         │
└─────────────────────────────────────────────────────────────┘
```

## Step 1: Deploy Infrastructure

Deploy the ML infrastructure stack:

```bash
./infrastructure/deploy-ml-stack.sh
```

This creates:
- **3 DynamoDB tables**: RiskAssessments, TrainingJobs, Interventions
- **1 S3 bucket**: For models and training data (encrypted with KMS)
- **2 IAM roles**: For Lambda and SageMaker
- **1 SNS topic**: For system alerts
- **2 EventBridge rules**: Daily assessment and monthly retraining

### Verify Deployment

```bash
# Check stack status
aws cloudformation describe-stacks --stack-name MindMate-ML-Prediction

# List DynamoDB tables
aws dynamodb list-tables | grep MindMate

# Check S3 bucket
aws s3 ls | grep mindmate-ml-models
```

## Step 2: Configure SNS Alerts

Update the SNS topic subscription with your admin email:

```bash
# Get SNS topic ARN
SNS_TOPIC=$(aws cloudformation describe-stacks \
  --stack-name MindMate-ML-Prediction \
  --query 'Stacks[0].Outputs[?OutputKey==`MLAlertsSnsTopicArn`].OutputValue' \
  --output text)

# Subscribe your email
aws sns subscribe \
  --topic-arn $SNS_TOPIC \
  --protocol email \
  --notification-endpoint your-admin-email@example.com

# Confirm subscription via email
```

## Step 3: Deploy Lambda Functions

The Lambda functions will be deployed in subsequent tasks. The infrastructure includes placeholder functions that will be replaced.

## Infrastructure Components

### DynamoDB Tables

#### RiskAssessments Table
- **Purpose**: Store daily risk scores for all users
- **Keys**: userId (PK), timestamp (SK)
- **TTL**: 90 days
- **Attributes**: riskScore, riskLevel, features, interventionsTriggered

#### TrainingJobs Table
- **Purpose**: Track model training jobs and metrics
- **Keys**: jobId (PK)
- **Attributes**: status, metrics, modelS3Path, featureImportance

#### Interventions Table
- **Purpose**: Log all interventions sent to users
- **Keys**: interventionId (PK)
- **GSI**: UserInterventionsIndex (userId, timestamp)
- **Attributes**: riskLevel, interventionType, messageGenerated, userResponse

### S3 Bucket Structure

```
mindmate-ml-models-{account-id}/
├── models/
│   ├── rf_model.pkl          # Random Forest model
│   ├── gb_model.pkl          # Gradient Boosting model
│   └── feature_importance.pkl
├── training/
│   ├── train/
│   │   └── train.csv
│   └── validation/
│       └── validation.csv
```

### IAM Roles

#### MLLambdaExecutionRole
Permissions for ML Lambda functions:
- DynamoDB: Read/write to all ML tables and EmoCompanion table
- S3: Read/write to ML models bucket
- KMS: Encrypt/decrypt with ML data key
- Comprehend: Sentiment analysis
- Bedrock: Generate intervention messages
- Lambda: Invoke other Lambda functions
- SNS: Publish alerts
- SageMaker: Create and manage training jobs

#### SageMakerExecutionRole
Permissions for SageMaker training:
- S3: Read training data, write models
- KMS: Encrypt/decrypt data
- CloudWatch: Write logs

### EventBridge Rules

#### Daily Risk Assessment
- **Schedule**: 6 AM UTC daily
- **Target**: riskAssessmentOrchestrator Lambda
- **Purpose**: Assess risk for all active users

#### Monthly Retraining
- **Schedule**: 1st of each month at midnight UTC
- **Target**: prepareTrainingData Lambda
- **Purpose**: Retrain models with new data

## Environment Variables

After deployment, these variables are added to `.env`:

```bash
# ML Prediction System
RISK_ASSESSMENTS_TABLE=MindMate-RiskAssessments
TRAINING_JOBS_TABLE=MindMate-TrainingJobs
INTERVENTIONS_TABLE=MindMate-Interventions
ML_MODELS_BUCKET=mindmate-ml-models-{account-id}
ML_LAMBDA_ROLE_ARN=arn:aws:iam::{account-id}:role/MindMate-MLLambdaRole
SAGEMAKER_ROLE_ARN=arn:aws:iam::{account-id}:role/MindMate-SageMakerRole
ML_ALERTS_SNS_TOPIC=arn:aws:sns:{region}:{account-id}:MindMate-MLAlerts
ML_KMS_KEY_ID={key-id}
```

## Security Features

### Encryption
- **At Rest**: All DynamoDB tables and S3 objects encrypted with KMS
- **In Transit**: TLS for all API calls
- **Key Management**: Dedicated KMS key for ML data

### Access Control
- **Least Privilege**: IAM roles grant only necessary permissions
- **Resource Isolation**: ML resources separate from main application
- **Audit Trail**: CloudWatch logs for all operations

### Privacy
- **Data Anonymization**: PII removed before training
- **TTL**: Risk assessments auto-deleted after 90 days
- **Opt-out**: Users can disable ML predictions

## Cost Estimates

For 10,000 active users:

| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| Lambda | Feature extraction + inference | $50 |
| SageMaker | Monthly training (spot instances) | $30 |
| DynamoDB | On-demand with TTL | $40 |
| Comprehend | Sentiment analysis | $30 |
| S3 | Model storage | $5 |
| KMS | Encryption operations | $5 |
| **Total** | | **~$160** |

### Cost Optimization Tips

1. **Use Lambda memory caching** for models (reduces S3 calls)
2. **Enable DynamoDB TTL** for automatic data cleanup
3. **Use SageMaker spot instances** for training (70% savings)
4. **Batch Comprehend requests** when possible
5. **Monitor CloudWatch metrics** to identify optimization opportunities

## Monitoring

### CloudWatch Dashboards

After full deployment, you'll have dashboards for:
- Risk score distribution
- Intervention frequencies
- Model performance metrics
- Lambda execution times
- Error rates

### Alarms

Set up alarms for:
- Lambda errors > 5% in 5 minutes
- Risk scoring latency > 10 seconds
- Model performance degradation
- Training job failures

### Logs

All Lambda functions log to CloudWatch Logs:
- `/aws/lambda/mindmate-extractMoodFeatures`
- `/aws/lambda/mindmate-extractBehavioralFeatures`
- `/aws/lambda/mindmate-extractSentimentFeatures`
- `/aws/lambda/mindmate-calculateRiskScore`
- `/aws/lambda/mindmate-executeIntervention`
- `/aws/lambda/mindmate-riskAssessmentOrchestrator`
- `/aws/lambda/mindmate-prepareTrainingData`

## Troubleshooting

### Stack Deployment Fails

**Issue**: CloudFormation stack creation fails

**Solutions**:
1. Check IAM permissions for CloudFormation
2. Verify bucket name is unique (includes account ID)
3. Check region supports all services (SageMaker, Comprehend)
4. Review CloudFormation events for specific error

### SNS Subscription Not Confirmed

**Issue**: Not receiving alert emails

**Solutions**:
1. Check spam folder for confirmation email
2. Verify email address is correct
3. Resubscribe using AWS CLI or Console

### KMS Key Access Denied

**Issue**: Lambda can't decrypt data

**Solutions**:
1. Verify Lambda role has KMS permissions
2. Check KMS key policy includes Lambda service
3. Ensure key is in same region as resources

## Next Steps

After infrastructure is deployed:

1. ✅ **Task 1 Complete**: Infrastructure deployed
2. 📝 **Task 2**: Implement mood feature extraction Lambda
3. 📝 **Task 3**: Implement behavioral feature extraction Lambda
4. 📝 **Task 4**: Implement sentiment feature extraction Lambda
5. 📝 **Task 5**: Implement training data preparation
6. 📝 **Task 6**: Create SageMaker training script
7. 📝 **Task 7**: Implement model training orchestration
8. 📝 **Task 8**: Implement real-time risk scoring
9. 📝 **Task 9**: Implement intervention system
10. 📝 **Task 10**: Set up automated daily assessment
11. 📝 **Task 11**: Implement model monitoring
12. 📝 **Task 12**: Set up observability
13. 📝 **Task 13**: Implement privacy controls
14. 📝 **Task 14**: Create deployment documentation

## Support

For issues or questions:
1. Check CloudWatch Logs for error details
2. Review SNS alerts for system notifications
3. Consult the main ML_PREDICTION_SPEC.md document
4. Check AWS service health dashboard

## References

- [ML Prediction Spec](./ML_PREDICTION_SPEC.md)
- [Product Vision](../PRODUCT_VISION.md)
- [AWS SageMaker Documentation](https://docs.aws.amazon.com/sagemaker/)
- [AWS Comprehend Documentation](https://docs.aws.amazon.com/comprehend/)
