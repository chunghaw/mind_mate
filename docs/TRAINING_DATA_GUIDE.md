# Training Data Guide

## Overview

The ML model needs **historical user data** to learn patterns that predict mental health crises. Here's exactly what data is needed and how it's collected.

## Data Requirements

### Minimum Requirements
- **Users**: At least 10 users
- **History**: Each user needs 60+ days of mood logs
- **Samples**: At least 10 training samples after feature extraction

### Ideal Dataset
- **Users**: 100-1000 users
- **History**: 90+ days per user
- **Samples**: 500-5000 training samples
- **Crisis cases**: 5-10% of samples (naturally occurring)

## What Data is Collected

### 1. Mood Logs (Primary Data Source)
Users log their mood daily through the app:

```json
{
  "userId": "user123",
  "mood": 6,
  "notes": "Feeling better today, work was manageable",
  "tags": ["work", "productive"],
  "timestamp": "2025-10-19T14:30:00Z"
}
```

**Stored in DynamoDB**:
- `PK`: `USER#user123`
- `SK`: `MOOD#2025-10-19T14:30:00Z`
- `type`: `MOOD`
- `mood`: 6 (scale 1-10)
- `notes`: Text description
- `tags`: Activity tags

### 2. Selfies (Optional)
Users can upload selfies for emotion analysis:

```json
{
  "userId": "user123",
  "imageUrl": "s3://bucket/selfies/...",
  "emotions": {
    "HAPPY": 0.75,
    "SAD": 0.15,
    "CALM": 0.10
  },
  "timestamp": "2025-10-19T14:30:00Z"
}
```

### 3. User Profile
Basic user information:

```json
{
  "userId": "user123",
  "personality": "gentle",
  "petName": "Buddy",
  "createdAt": "2025-08-01T00:00:00Z"
}
```

## How Training Data is Generated

### Step 1: User Logs Moods Over Time

**Day 1-60**: User logs moods daily
```
Day 1:  Mood 7, "Starting to use the app"
Day 2:  Mood 6, "Work was stressful"
Day 3:  Mood 5, "Feeling tired"
...
Day 60: Mood 4, "Struggling with anxiety"
```

### Step 2: Feature Extraction

After 60 days, the system extracts **49 features**:

**Mood Features (20)**:
- `mood_trend_7day`: -0.15 (declining)
- `mood_mean_7day`: 5.2 (average mood)
- `consecutive_low_days`: 2 (days with mood ≤ 4)
- `mood_volatility`: 1.2 (daily changes)
- etc.

**Behavioral Features (15)**:
- `daily_checkin_frequency`: 0.85 (checks in 85% of days)
- `engagement_trend`: -0.05 (slightly declining)
- `negative_word_frequency`: 0.15 (15% negative words)
- `late_night_usage`: 3 (3 late-night check-ins)
- etc.

**Sentiment Features (14)**:
- `negative_sentiment_frequency`: 0.35 (35% negative)
- `avg_negative_score`: 0.42 (AWS Comprehend score)
- `despair_keywords`: 2 (hopeless, pointless)
- `crisis_keywords`: 0 (no crisis words)
- etc.

### Step 3: Crisis Labeling

The system looks ahead 7 days to see if a crisis occurred:

**Crisis = 1** (Positive case):
- 3+ consecutive days with mood ≤ 2, OR
- Crisis keywords found (suicide, self-harm, etc.)

**Non-Crisis = 0** (Negative case):
- No crisis indicators in next 7 days

**Example**:
```
Days 1-60: Features extracted → mood_trend_7day = -0.15
Days 61-67: Check for crisis
  Day 62: Mood 2, "feeling hopeless"
  Day 63: Mood 1, "can't go on"
  Day 64: Mood 2, "everything is pointless"
  → Label = 1 (Crisis detected)
```

### Step 4: CSV Generation

All features + label combined into one row:

```csv
sample_id,mood_trend_7day,mood_mean_7day,...,crisis_keywords,label
sample_000001,-0.15,5.2,...,0,0
sample_000002,0.05,3.8,...,0,1
```

## Example Training Data

See `sagemaker/example_training_data.csv` for a complete example with 10 samples.

### Sample Breakdown

**Sample 1 (Non-Crisis)**:
- Mood trend: -0.15 (slight decline)
- Average mood: 5.2 (moderate)
- Consecutive low days: 2
- Negative sentiment: 35%
- Crisis keywords: 0
- **Label: 0** (No crisis)

**Sample 2 (Crisis)**:
- Mood trend: 0.05 (stable but low)
- Average mood: 3.8 (low)
- Consecutive low days: 4
- Negative sentiment: 55%
- Despair keywords: 5
- Crisis keywords: 0
- **Label: 1** (Crisis occurred)

**Sample 4 (Crisis)**:
- Mood trend: -0.25 (sharp decline)
- Average mood: 2.5 (very low)
- Consecutive low days: 5
- Negative sentiment: 68%
- Despair keywords: 8
- Isolation keywords: 9
- Crisis keywords: 1 (explicit crisis language)
- **Label: 1** (Crisis occurred)

**Sample 8 (Crisis)**:
- Mood trend: -0.32 (severe decline)
- Average mood: 1.8 (critically low)
- Consecutive low days: 6
- Negative sentiment: 75%
- Despair keywords: 12
- Isolation keywords: 11
- Crisis keywords: 2
- Late night usage: 12
- **Label: 1** (Severe crisis)

## Real-World Data Collection

### Phase 1: Beta Testing (Weeks 1-8)
- **Goal**: Collect initial data from 50-100 beta users
- **Duration**: 60-90 days
- **Expected**: 50-100 training samples
- **Use**: Initial model training

### Phase 2: Early Adoption (Months 3-6)
- **Goal**: Expand to 500-1000 users
- **Duration**: 90+ days
- **Expected**: 500-1000 training samples
- **Use**: Model refinement and validation

### Phase 3: Production (Months 6+)
- **Goal**: Scale to 10,000+ users
- **Duration**: Ongoing
- **Expected**: 5,000-10,000 training samples
- **Use**: Continuous model improvement

## Data Privacy

### Anonymization
Before training, all PII is removed:
- `userId` → `sample_id` (e.g., sample_000001)
- No names, emails, or identifiable information
- Only numerical features retained

### Example Transformation
```
Before:
userId: "john.doe@email.com"
mood: 5
notes: "Feeling stressed about work"

After:
sample_id: "sample_000001"
mood_mean_7day: 5.2
negative_word_frequency: 0.15
(notes removed, only features extracted)
```

## How to Generate Training Data

### Option 1: Use Real User Data (Recommended)
1. Deploy the app
2. Get users logging moods for 60+ days
3. Run `prepareTrainingData` Lambda
4. Training data automatically generated

### Option 2: Synthetic Data (For Testing)
Create synthetic mood logs for testing:

```python
# Generate synthetic user data
for day in range(60):
    mood = random.randint(1, 10)
    notes = generate_random_note()
    
    table.put_item(Item={
        'PK': f'USER#test_user_{i}',
        'SK': f'MOOD#{date}',
        'mood': mood,
        'notes': notes,
        'type': 'MOOD'
    })
```

### Option 3: Import Historical Data
If you have existing mental health data:

```python
# Import from CSV
for row in historical_data:
    table.put_item(Item={
        'PK': f'USER#{row["user_id"]}',
        'SK': f'MOOD#{row["date"]}',
        'mood': row['mood_score'],
        'notes': row['journal_entry'],
        'type': 'MOOD'
    })
```

## Training Data Quality

### Good Quality Indicators
✅ Consistent daily logging (80%+ days)  
✅ Detailed notes (30+ characters)  
✅ Varied mood scores (not all 5s)  
✅ Natural language in notes  
✅ Mix of positive and negative entries  

### Poor Quality Indicators
❌ Sporadic logging (< 50% days)  
❌ Empty or minimal notes  
❌ Same mood score every day  
❌ Generic/template responses  
❌ All positive or all negative  

## Cost of Data Collection

### Storage Costs
- **DynamoDB**: $0.25 per GB/month
- **60 days of data per user**: ~1 KB
- **1000 users**: ~1 MB = $0.0003/month
- **Negligible cost**

### Processing Costs
- **Feature extraction**: $0.001 per user
- **1000 users**: $1.00 per training run
- **Monthly retraining**: $1.00/month

## Timeline to First Model

### Minimum Viable Model
- **Users**: 10 users
- **Days**: 60 days
- **Timeline**: 2 months from launch
- **Accuracy**: Basic (AUC ~0.70)

### Production-Ready Model
- **Users**: 100+ users
- **Days**: 90 days
- **Timeline**: 3-4 months from launch
- **Accuracy**: Good (AUC ~0.80)

### Optimized Model
- **Users**: 1000+ users
- **Days**: 120+ days
- **Timeline**: 6+ months from launch
- **Accuracy**: Excellent (AUC ~0.85+)

## Next Steps

1. **Deploy the app** and start collecting user data
2. **Wait 60 days** for sufficient history
3. **Run prepareTrainingData** Lambda to generate CSV
4. **Train the model** using SageMaker
5. **Deploy risk scoring** for real-time predictions

## Questions?

**Q: Can I train with less than 60 days?**  
A: Yes, but accuracy will be lower. Minimum 30 days recommended.

**Q: What if I don't have crisis cases?**  
A: The model can still train, but will be less accurate at detecting crises. Consider synthetic crisis cases for initial training.

**Q: How often should I retrain?**  
A: Monthly retraining recommended as new data accumulates.

**Q: Can I use data from other mental health apps?**  
A: Yes, if you can map it to the required format (mood scores, notes, timestamps).

## Summary

**What you need**: Users logging moods daily for 60+ days  
**What you get**: CSV file with 49 features + crisis labels  
**What the model learns**: Patterns that predict crises 3-7 days in advance  
**Timeline**: 2-3 months from app launch to first model  
