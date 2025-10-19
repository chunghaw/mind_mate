# Extract Behavioral Features Lambda

This Lambda function extracts behavioral and engagement features from a user's interaction history for ML risk prediction.

## Features Extracted

### Engagement Features
- `daily_checkin_frequency`: Average interactions per day
- `avg_session_duration`: Average session length (placeholder: 120s)
- `engagement_trend`: Trend in daily interaction count (slope)
- `response_time_trend`: Trend in time between interactions

### Activity Features
- `activity_completion_rate`: Proportion of mood logs with tags/activities
- `selfie_frequency`: Average selfies per day

### Communication Features
- `avg_message_length`: Average length of mood notes
- `negative_word_frequency`: Proportion of negative words in notes
- `help_seeking_frequency`: Proportion of notes with help-seeking phrases

### Temporal Patterns
- `late_night_usage`: Count of interactions between 11 PM - 5 AM
- `weekend_usage_change`: Difference in weekend vs weekday usage
- `usage_consistency`: Standard deviation of daily interaction counts

### Metadata
- `total_interactions`: Total interactions in period
- `mood_logs_count`: Number of mood logs
- `selfies_count`: Number of selfies

## Input

```json
{
  "userId": "user123",
  "days": 30
}
```

## Output

```json
{
  "statusCode": 200,
  "body": {
    "daily_checkin_frequency": 0.85,
    "engagement_trend": -0.05,
    "response_time_trend": 2.3,
    "activity_completion_rate": 0.72,
    "selfie_frequency": 0.15,
    "avg_message_length": 45.2,
    "negative_word_frequency": 0.15,
    "help_seeking_frequency": 0.08,
    "late_night_usage": 3,
    "weekend_usage_change": -0.2,
    "usage_consistency": 1.5,
    "total_interactions": 25,
    "mood_logs_count": 22,
    "selfies_count": 3
  }
}
```

## Deployment

```bash
./backend/lambdas/extractBehavioralFeatures/deploy.sh
```

## Testing

```bash
aws lambda invoke \
  --function-name mindmate-extractBehavioralFeatures \
  --payload file://backend/lambdas/extractBehavioralFeatures/test_payload.json \
  response.json \
  --region us-east-1

cat response.json | jq
```

## Dependencies

- `boto3`: AWS SDK
- `numpy`: Statistical calculations

## Environment Variables

- `TABLE_NAME`: DynamoDB table name (default: EmoCompanion)

## IAM Permissions Required

- `dynamodb:Query` on EmoCompanion table
- `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents`

## Error Handling

- Returns default features if user has no interaction data
- Handles missing data gracefully
- Logs errors to CloudWatch
- Returns 500 status code on unexpected errors

## Performance

- **Memory**: 1024 MB
- **Timeout**: 60 seconds
- **Typical execution**: 3-6 seconds for 30 days of data
- **Cold start**: ~3 seconds (includes numpy import)

## Data Sources

Queries DynamoDB for:
1. **Mood Logs**: `PK = USER#{userId}`, `SK BETWEEN MOOD#{start} AND MOOD#{end}`
2. **Selfies**: `PK = USER#{userId}`, `SK BETWEEN SELFIE#{start} AND SELFIE#{end}`

## Feature Engineering Notes

### Engagement Trend
Uses linear regression to detect increasing or decreasing engagement over time. Negative slope indicates declining engagement.

### Response Time Trend
Measures time between consecutive interactions. Increasing trend suggests user is checking in less frequently.

### Negative Word Detection
Scans mood notes for keywords like: sad, depressed, anxious, worried, stressed, overwhelmed, hopeless, helpless, alone, lonely, tired, exhausted, angry, frustrated, scared, afraid, terrible, awful, bad, worse, worst, hate, cry, crying, pain, hurt.

### Help-Seeking Detection
Identifies phrases like: help, need help, what should i do, i don't know, advice, suggest, recommendation, what can i, how do i, struggling, can't cope, too much.

### Late Night Usage
Interactions between 11 PM and 5 AM may indicate sleep disturbances or crisis moments.

### Weekend Usage Change
Compares weekend (Sat/Sun) to weekday usage. Negative change may indicate work-related stress relief on weekends.

## Requirements Satisfied

✅ **Requirement 1.4**: Extract behavioral features from interaction history  
✅ **Requirement 1.6**: Handle missing data gracefully with defaults  
✅ **Requirement 1.7**: Log errors without blocking the pipeline

## Behavioral Risk Indicators

High-risk patterns:
- Declining engagement trend (negative slope)
- Increasing response time between interactions
- High negative word frequency (> 0.2)
- High help-seeking frequency (> 0.15)
- Frequent late-night usage (> 5 in 30 days)
- Low activity completion rate (< 0.3)
- High usage consistency variance (erratic patterns)
