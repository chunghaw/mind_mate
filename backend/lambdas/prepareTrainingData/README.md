# Prepare Training Data Lambda

This Lambda function prepares training datasets for SageMaker by aggregating features from all feature extraction Lambdas, labeling crisis events, and creating train/validation splits.

## Functionality

### 1. User Selection
- Scans DynamoDB for users with sufficient history (default: 60+ days)
- Filters users with adequate mood log entries

### 2. Feature Extraction
- Invokes all 3 feature extraction Lambdas for each user:
  - `extractMoodFeatures` (20 features)
  - `extractBehavioralFeatures` (15 features)
  - `extractSentimentFeatures` (14 features)
- Aggregates 49 total features per user

### 3. Crisis Labeling
- Looks ahead 7 days from current point
- Labels as crisis (1) if:
  - 3+ consecutive days with mood ≤ 2, OR
  - Crisis keywords found (suicide, self-harm, etc.)
- Labels as non-crisis (0) otherwise

### 4. Data Processing
- **Anonymization**: Removes userId, replaces with sample_id
- **Class Balancing**: Oversamples minority class to balance dataset
- **Train/Val Split**: 80/20 split (configurable)

### 5. S3 Upload
- Saves datasets as CSV files to S3
- Format: `training/train_{timestamp}.csv` and `training/validation_{timestamp}.csv`

## Input

```json
{
  "minDays": 60,
  "validationSplit": 0.2
}
```

## Output

```json
{
  "statusCode": 200,
  "body": {
    "success": true,
    "trainPath": "s3://mindmate-ml-models-{account}/training/train_20251019_065000.csv",
    "validationPath": "s3://mindmate-ml-models-{account}/training/validation_20251019_065000.csv",
    "totalSamples": 500,
    "trainSamples": 400,
    "validationSamples": 100,
    "trainPositiveClass": 200,
    "trainNegativeClass": 200,
    "valPositiveClass": 50,
    "valNegativeClass": 50,
    "timestamp": "20251019_065000"
  }
}
```

## Deployment

```bash
./backend/lambdas/prepareTrainingData/deploy.sh
```

## Testing

```bash
aws lambda invoke \
  --function-name mindmate-prepareTrainingData \
  --payload file://backend/lambdas/prepareTrainingData/test_payload.json \
  response.json \
  --region us-east-1

cat response.json | jq
```

## Dependencies

- `boto3`: AWS SDK (Lambda, DynamoDB, S3)

## Environment Variables

- `TABLE_NAME`: DynamoDB table name (default: EmoCompanion)
- `TRAINING_JOBS_TABLE`: Training jobs tracking table
- `ML_MODELS_BUCKET`: S3 bucket for training data

## IAM Permissions Required

- `dynamodb:Scan`, `dynamodb:Query` on EmoCompanion table
- `dynamodb:PutItem` on TrainingJobs table
- `lambda:InvokeFunction` for feature extraction Lambdas
- `s3:PutObject` on ML models bucket
- `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents`

## Performance

- **Memory**: 2048 MB (higher for processing many users)
- **Timeout**: 900 seconds (15 minutes)
- **Typical execution**: 5-10 minutes for 100 users
- **Scales with**: Number of users × feature extraction time

## Crisis Detection Criteria

### Positive Label (Crisis = 1)
1. **Mood-based**: 3+ consecutive days with mood ≤ 2 in next 7 days
2. **Keyword-based**: Any crisis keywords in messages:
   - suicide, suicidal
   - kill myself, end my life
   - want to die, better off dead
   - self harm, hurt myself

### Negative Label (Non-Crisis = 0)
- No crisis indicators in next 7 days

## Data Anonymization

Removes all PII before training:
- `userId` → `sample_id` (e.g., sample_000001)
- No names, emails, or identifiable information
- Only numerical features retained

## Class Balancing

Uses oversampling to handle imbalanced data:
- Duplicates minority class samples
- Ensures 50/50 class distribution
- Prevents model bias toward majority class

## CSV Format

Output CSV includes:
- 49 feature columns (mood, behavioral, sentiment)
- 1 label column (0 or 1)
- 1 sample_id column

Example:
```csv
sample_id,mood_trend_7day,mood_mean_7day,...,label
sample_000001,-0.15,5.2,...,0
sample_000002,0.05,3.8,...,1
```

## Error Handling

- Returns 400 if insufficient users (< 10)
- Returns 400 if insufficient samples (< 10)
- Returns 500 if S3 upload fails
- Logs all errors to CloudWatch
- Continues processing if individual user fails

## Minimum Requirements

- **Users**: At least 10 users with 60+ days of data
- **Samples**: At least 10 samples after feature extraction
- **Features**: All 49 features must be present

## Workflow Integration

This Lambda is triggered by:
1. **Manual invocation**: For initial training
2. **EventBridge schedule**: Monthly retraining (1st of month)
3. **API call**: On-demand training

After completion:
- Triggers `triggerModelTraining` Lambda
- Passes S3 paths to SageMaker training job

## Monitoring

Logs to CloudWatch:
- User processing progress
- Feature extraction results
- Class distribution
- S3 upload status
- Final dataset statistics

## Requirements Satisfied

✅ **Requirement 2.1**: Include users with 60+ days of data  
✅ **Requirement 2.2**: Label crisis events based on mood and keywords  
✅ **Requirement 2.3**: Use 7-day lookahead window  
✅ **Requirement 2.4**: 80/20 train/validation split  
✅ **Requirement 2.5**: Balance classes using oversampling  
✅ **Requirement 2.6**: Anonymize PII, store in S3 as CSV  
✅ **Requirement 8.1**: Anonymize all PII before training

## Cost Estimate

For 100 users:
- Lambda execution: ~10 minutes × $0.0000166667/GB-second × 2GB = $0.02
- Feature extraction: 3 Lambdas × 100 users × 5 seconds = $0.10
- S3 storage: Negligible (< $0.01)
- **Total per run**: ~$0.13

Monthly retraining: ~$0.13/month
