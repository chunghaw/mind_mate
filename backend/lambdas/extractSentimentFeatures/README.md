# Extract Sentiment Features Lambda

This Lambda function extracts sentiment-related features from user messages using AWS Comprehend for ML risk prediction.

## Features Extracted

### Sentiment Trends
- `sentiment_trend_7day`: Trend in negative sentiment over last 7 days
- `sentiment_trend_30day`: Trend in negative sentiment over last 30 days

### Sentiment Frequencies
- `negative_sentiment_frequency`: Proportion of negative messages
- `positive_sentiment_frequency`: Proportion of positive messages
- `neutral_sentiment_frequency`: Proportion of neutral messages
- `mixed_sentiment_frequency`: Proportion of mixed sentiment messages

### Sentiment Scores
- `avg_negative_score`: Average negative sentiment score (0-1)
- `avg_positive_score`: Average positive sentiment score (0-1)
- `avg_neutral_score`: Average neutral sentiment score (0-1)

### Volatility
- `sentiment_volatility`: Average change in negative sentiment between messages

### Crisis Indicators
- `despair_keywords`: Count of despair-related keywords
- `isolation_keywords`: Count of isolation-related keywords
- `hopelessness_score`: Combined score of negative sentiment + despair keywords
- `crisis_keywords`: Count of critical crisis keywords (suicide, self-harm)

### Metadata
- `total_messages_analyzed`: Number of messages processed

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
    "sentiment_trend_7day": 0.05,
    "negative_sentiment_frequency": 0.35,
    "avg_negative_score": 0.42,
    "sentiment_volatility": 0.18,
    "despair_keywords": 2,
    "isolation_keywords": 3,
    "hopelessness_score": 0.25,
    "crisis_keywords": 0,
    "total_messages_analyzed": 20
  }
}
```

## Deployment

```bash
./backend/lambdas/extractSentimentFeatures/deploy.sh
```

## Testing

```bash
aws lambda invoke \
  --function-name mindmate-extractSentimentFeatures \
  --payload file://backend/lambdas/extractSentimentFeatures/test_payload.json \
  response.json \
  --region us-east-1

cat response.json | jq
```

## Dependencies

- `boto3`: AWS SDK (includes Comprehend client)
- `numpy`: Statistical calculations

## Environment Variables

- `TABLE_NAME`: DynamoDB table name (default: EmoCompanion)

## IAM Permissions Required

- `dynamodb:Query` on EmoCompanion table
- `comprehend:DetectSentiment` for sentiment analysis
- `comprehend:BatchDetectSentiment` for batch processing
- `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents`

## AWS Comprehend Integration

### Batch Processing
- Processes up to 25 messages per batch (Comprehend limit)
- Handles errors gracefully with fallback to default sentiment
- Truncates messages to 5000 bytes (Comprehend limit)

### Sentiment Detection
Returns 4 sentiment types:
- **POSITIVE**: Positive emotions
- **NEGATIVE**: Negative emotions
- **NEUTRAL**: Neutral tone
- **MIXED**: Mixed emotions

Each with confidence scores (0-1) for all 4 categories.

### Error Handling
- Falls back to keyword-based detection if Comprehend fails
- Returns default features if no messages available
- Logs errors to CloudWatch
- Never blocks the pipeline

## Performance

- **Memory**: 1024 MB
- **Timeout**: 120 seconds (longer due to Comprehend API calls)
- **Typical execution**: 5-15 seconds for 30 days of data
- **Cold start**: ~3 seconds
- **Comprehend latency**: ~1-2 seconds per batch of 25 messages

## Crisis Keyword Detection

### Despair Keywords
hopeless, pointless, worthless, useless, give up, no point, why bother, nothing matters, end it, can't go on, no future, no hope, meaningless

### Isolation Keywords
alone, lonely, isolated, no one, nobody, by myself, no friends, abandoned, left out, disconnected, withdrawn, solitary

### Crisis Keywords (Critical)
suicide, suicidal, kill myself, end my life, want to die, better off dead, self harm, hurt myself, cut myself

## Hopelessness Score Calculation

Combines two factors:
1. **Negative Sentiment** (60% weight): Average negative score from Comprehend
2. **Despair Keywords** (40% weight): Normalized count of despair keywords

Formula: `hopelessness = (0.6 × avg_negative) + (0.4 × min(despair_count/5, 1.0))`

## Cost Considerations

AWS Comprehend pricing (as of 2024):
- $0.0001 per unit (100 characters)
- Average message: ~50 characters = $0.00005
- 30 days of data (~20 messages): ~$0.001 per user assessment
- 10,000 users daily: ~$10/day = ~$300/month

Cost optimization:
- Batch processing reduces API calls
- Only analyzes messages with text content
- Caches results when possible

## Requirements Satisfied

✅ **Requirement 1.5**: Use AWS Comprehend for sentiment analysis  
✅ **Requirement 1.6**: Handle Comprehend API failures gracefully  
✅ **Requirement 1.7**: Log errors without blocking the pipeline

## High-Risk Indicators

Patterns suggesting elevated risk:
- **Increasing negative trend**: sentiment_trend > 0.05
- **High negative frequency**: negative_sentiment_frequency > 0.5
- **High negative score**: avg_negative_score > 0.6
- **High volatility**: sentiment_volatility > 0.3
- **Despair keywords**: despair_keywords > 3
- **Isolation keywords**: isolation_keywords > 3
- **High hopelessness**: hopelessness_score > 0.5
- **Crisis keywords**: crisis_keywords > 0 (immediate alert)

## Data Source

Queries DynamoDB for mood logs with notes:
- `PK = USER#{userId}`
- `SK BETWEEN MOOD#{start_date} AND MOOD#{end_date}`
- Filters for items with `notes` field populated
