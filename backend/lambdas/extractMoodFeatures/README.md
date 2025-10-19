# Extract Mood Features Lambda

This Lambda function extracts mood-related features from a user's historical mood data for ML risk prediction.

## Features Extracted

### Trend Features
- `mood_trend_7day`: Linear trend over last 7 days (slope)
- `mood_trend_14day`: Linear trend over last 14 days
- `mood_trend_30day`: Linear trend over last 30 days

### Statistical Features (7-day window)
- `mood_mean_7day`: Average mood
- `mood_std_7day`: Standard deviation
- `mood_variance_7day`: Variance
- `mood_min_7day`: Minimum mood
- `mood_max_7day`: Maximum mood

### Statistical Features (14-day and 30-day windows)
- `mood_mean_14day`, `mood_std_14day`
- `mood_mean_30day`, `mood_std_30day`

### Pattern Features
- `mood_volatility`: Average daily mood change
- `consecutive_low_days`: Max consecutive days with mood ≤ 4
- `consecutive_high_days`: Max consecutive days with mood ≥ 7
- `mood_decline_rate`: Rate of mood decline (if trending down)

### Frequency Features
- `low_mood_frequency`: Proportion of days with mood ≤ 3 (last 7 days)
- `high_mood_frequency`: Proportion of days with mood ≥ 8 (last 7 days)
- `missing_days_7day`: Number of days without mood entries (last 7 days)

### Temporal Features
- `weekend_mood_diff`: Difference between weekend and weekday moods

### Metadata
- `total_mood_entries`: Total number of mood entries in the period

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
    "mood_trend_7day": -0.15,
    "mood_mean_7day": 5.2,
    "mood_std_7day": 1.8,
    "mood_volatility": 1.2,
    "consecutive_low_days": 2,
    "low_mood_frequency": 0.28,
    "missing_days_7day": 1,
    "weekend_mood_diff": 0.5,
    "total_mood_entries": 25
  }
}
```

## Deployment

```bash
./backend/lambdas/extractMoodFeatures/deploy.sh
```

## Testing

```bash
aws lambda invoke \
  --function-name mindmate-extractMoodFeatures \
  --payload file://backend/lambdas/extractMoodFeatures/test_payload.json \
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

- Returns default features if user has no mood data
- Handles missing data gracefully with median imputation
- Logs errors to CloudWatch
- Returns 500 status code on unexpected errors

## Performance

- **Memory**: 1024 MB
- **Timeout**: 60 seconds
- **Typical execution**: 2-5 seconds for 30 days of data
- **Cold start**: ~3 seconds (includes numpy import)

## Data Source

Queries DynamoDB for items matching:
- `PK = USER#{userId}`
- `SK BETWEEN MOOD#{start_date} AND MOOD#{end_date}`
- `type = MOOD`

## Feature Engineering Notes

### Trend Calculation
Uses numpy's `polyfit` for linear regression to calculate mood trend slope.

### Volatility
Measures average absolute change between consecutive mood entries.

### Consecutive Days
Tracks longest streak of low/high moods to identify sustained patterns.

### Weekend Difference
Compares average weekend mood (Sat/Sun) to weekday mood to detect work-related stress.

## Requirements Satisfied

✅ **Requirement 1.1**: Extract mood trend features for 7, 14, and 30-day windows  
✅ **Requirement 1.2**: Calculate statistical measures (mean, std, variance, min, max)  
✅ **Requirement 1.3**: Identify consecutive low mood days and decline rates  
✅ **Requirement 1.6**: Handle missing data gracefully with defaults  
✅ **Requirement 1.7**: Log errors without blocking the pipeline
