# ML System Flow Diagram

## Complete End-to-End Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER INTERACTIONS                                │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
            ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
            │  Log Mood    │ │  Chat with   │ │  Use App     │
            │  (1-10)      │ │  Bedrock     │ │  Features    │
            └──────────────┘ └──────────────┘ └──────────────┘
                    │               │               │
                    ▼               ▼               ▼
            ┌──────────────────────────────────────────────────┐
            │            DynamoDB Tables                        │
            │  • MoodLogs                                       │
            │  • ChatHistory                                    │
            │  • UserActivity                                   │
            └──────────────────────────────────────────────────┘
                                    │
                                    │
┌─────────────────────────────────────────────────────────────────────────┐
│                    FEATURE EXTRACTION (Real-Time)                        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
        ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
        │ extractMood      │ │ extractBehavioral│ │ extractSentiment │
        │ Features         │ │ Features         │ │ Features         │
        │                  │ │                  │ │                  │
        │ • mood_trend     │ │ • engagement     │ │ • sentiment_score│
        │ • mood_mean      │ │ • late_night     │ │ • crisis_keywords│
        │ • volatility     │ │ • consistency    │ │ • despair_words  │
        │ (21 features)    │ │ (15 features)    │ │ (13 features)    │
        └──────────────────┘ └──────────────────┘ └──────────────────┘
                    │               │               │
                    └───────────────┼───────────────┘
                                    │
                                    ▼
                        ┌──────────────────────┐
                        │  49 Features Vector  │
                        │  [-0.25, 3.5, ...]   │
                        └──────────────────────┘
                                    │
                                    ▼
                        ┌──────────────────────┐
                        │  DynamoDB            │
                        │  UserFeatures Table  │
                        └──────────────────────┘
                                    │
                                    │
┌─────────────────────────────────────────────────────────────────────────┐
│                    DAILY RISK ASSESSMENT (6 AM)                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                        ┌──────────────────────┐
                        │  EventBridge Rule    │
                        │  (Daily at 6 AM)     │
                        └──────────────────────┘
                                    │
                                    ▼
                        ┌──────────────────────┐
                        │  riskAssessment      │
                        │  Orchestrator Lambda │
                        └──────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
            For each active user:
                                    │
                                    ▼
                        ┌──────────────────────┐
                        │  calculateRiskScore  │
                        │  Lambda              │
                        └──────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
        ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
        │  Load Models     │ │  Get Features    │ │  Make Prediction │
        │  from S3         │ │  from DynamoDB   │ │  (Ensemble)      │
        │                  │ │                  │ │                  │
        │  • rf_model.pkl  │ │  • 49 features   │ │  RF: 0.68        │
        │  • gb_model.pkl  │ │  • User history  │ │  GB: 0.72        │
        │                  │ │                  │ │  Avg: 0.70       │
        └──────────────────┘ └──────────────────┘ └──────────────────┘
                                                            │
                                                            ▼
                                                ┌──────────────────────┐
                                                │  Risk Score: 0.70    │
                                                │  Risk Level: HIGH    │
                                                └──────────────────────┘
                                                            │
                                                            ▼
                                                ┌──────────────────────┐
                                                │  DynamoDB            │
                                                │  RiskAssessments     │
                                                └──────────────────────┘
                                                            │
                                                            │
┌─────────────────────────────────────────────────────────────────────────┐
│                    INTERVENTION (If High Risk)                           │
└─────────────────────────────────────────────────────────────────────────┘
                                                            │
                                                            ▼
                                                ┌──────────────────────┐
                                                │  If risk >= 0.7      │
                                                │  Trigger Intervention│
                                                └──────────────────────┘
                                                            │
                                                            ▼
                                                ┌──────────────────────┐
                                                │  executeIntervention │
                                                │  Lambda              │
                                                └──────────────────────┘
                                                            │
                                    ┌───────────────────────┼───────────────────────┐
                                    │                       │                       │
                                    ▼                       ▼                       ▼
                        ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
                        │  Generate        │   │  Send via        │   │  Log             │
                        │  Personalized    │   │  Bedrock Agent   │   │  Intervention    │
                        │  Message         │   │                  │   │                  │
                        │  (Bedrock)       │   │  "Hi Sarah,      │   │  • Timestamp     │
                        │                  │   │   I noticed..."  │   │  • Risk score    │
                        │                  │   │                  │   │  • Message sent  │
                        └──────────────────┘   └──────────────────┘   └──────────────────┘
                                                            │
                                                            │
┌─────────────────────────────────────────────────────────────────────────┐
│                    WEB APP DISPLAY                                       │
└─────────────────────────────────────────────────────────────────────────┘
                                                            │
                                                            ▼
                                                ┌──────────────────────┐
                                                │  User Opens App      │
                                                └──────────────────────┘
                                                            │
                                                            ▼
                                                ┌──────────────────────┐
                                                │  Frontend Fetches    │
                                                │  /risk/calculate     │
                                                └──────────────────────┘
                                                            │
                                                            ▼
                                                ┌──────────────────────┐
                                                │  API Gateway         │
                                                │  → Lambda            │
                                                └──────────────────────┘
                                                            │
                                                            ▼
                                                ┌──────────────────────┐
                                                │  Return Risk Data    │
                                                │  {                   │
                                                │    riskScore: 0.70,  │
                                                │    riskLevel: "high",│
                                                │    factors: [...]    │
                                                │  }                   │
                                                └──────────────────────┘
                                                            │
                                                            ▼
                                    ┌───────────────────────────────────────┐
                                    │  ML Wellness Widget                   │
                                    │  ┌─────────────────────────────────┐  │
                                    │  │  ⚠️  High Risk - 70%            │  │
                                    │  │                                 │  │
                                    │  │  Risk Factors:                  │  │
                                    │  │  • Missing check-ins (3 days)   │  │
                                    │  │  • Mood declining for 7 days    │  │
                                    │  │  • High negative sentiment      │  │
                                    │  │                                 │  │
                                    │  │  [Get Support Now]              │  │
                                    │  └─────────────────────────────────┘  │
                                    └───────────────────────────────────────┘
                                                            │
                                                            │
┌─────────────────────────────────────────────────────────────────────────┐
│                    MODEL TRAINING (Monthly)                              │
└─────────────────────────────────────────────────────────────────────────┘
                                                            │
                                                            ▼
                                                ┌──────────────────────┐
                                                │  EventBridge Rule    │
                                                │  (1st of month)      │
                                                └──────────────────────┘
                                                            │
                                                            ▼
                                                ┌──────────────────────┐
                                                │  prepareTrainingData │
                                                │  Lambda              │
                                                └──────────────────────┘
                                                            │
                                    ┌───────────────────────┼───────────────────────┐
                                    │                       │                       │
                                    ▼                       ▼                       ▼
                        ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
                        │  Collect Data    │   │  Label Samples   │   │  Upload to S3    │
                        │  from Past Month │   │                  │   │                  │
                        │                  │   │  Did crisis      │   │  training-data/  │
                        │  • All users     │   │  occur in next   │   │  monthly.csv     │
                        │  • 30 days ago   │   │  7 days?         │   │                  │
                        │  • 49 features   │   │  Yes → label=1   │   │  1000+ samples   │
                        │                  │   │  No → label=0    │   │                  │
                        └──────────────────┘   └──────────────────┘   └──────────────────┘
                                                                                │
                                                                                ▼
                                                                    ┌──────────────────────┐
                                                                    │  SageMaker Training  │
                                                                    │  Job                 │
                                                                    └──────────────────────┘
                                                                                │
                                                    ┌───────────────────────────┼───────────────────────────┐
                                                    │                           │                           │
                                                    ▼                           ▼                           ▼
                                        ┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
                                        │  Train Random    │       │  Train Gradient  │       │  Evaluate        │
                                        │  Forest          │       │  Boosting        │       │  Performance     │
                                        │                  │       │                  │       │                  │
                                        │  200 trees       │       │  200 trees       │       │  AUC, Recall,    │
                                        │  Max depth: 10   │       │  Max depth: 10   │       │  Precision       │
                                        └──────────────────┘       └──────────────────┘       └──────────────────┘
                                                    │                           │                           │
                                                    └───────────────────────────┼───────────────────────────┘
                                                                                │
                                                                                ▼
                                                                    ┌──────────────────────┐
                                                                    │  Save Models to S3   │
                                                                    │                      │
                                                                    │  • rf_model.pkl      │
                                                                    │  • gb_model.pkl      │
                                                                    │  • metrics.json      │
                                                                    │  • feature_imp.csv   │
                                                                    └──────────────────────┘
                                                                                │
                                                                                ▼
                                                                    ┌──────────────────────┐
                                                                    │  Lambda Auto-Updates │
                                                                    │  to Use New Models   │
                                                                    └──────────────────────┘
```

## Key Components

### Data Sources
- **MoodLogs**: Daily mood ratings (1-10)
- **ChatHistory**: Conversations with Bedrock Agent
- **UserActivity**: App usage patterns

### Feature Extraction (49 features)
- **Mood Features (21)**: Trends, averages, volatility, extremes
- **Behavioral Features (15)**: Engagement, timing, consistency
- **Sentiment Features (13)**: Tone, keywords, emotional state

### ML Models
- **Random Forest**: 200 trees, learns diverse patterns
- **Gradient Boosting**: 200 trees, sequential error correction
- **Ensemble**: Averages both predictions for robustness

### Risk Levels
- **Low (0-0.39)**: Normal support
- **Medium (0.40-0.69)**: Increased monitoring
- **High (0.70-1.0)**: Immediate intervention

### Automation
- **Daily Assessment**: 6 AM every day
- **Monthly Retraining**: 1st of each month
- **Real-Time Features**: Extracted on every interaction

## Data Flow Summary

1. **User logs mood** → Stored in DynamoDB
2. **User chats** → Sentiment analyzed → Stored in DynamoDB
3. **User uses app** → Behavior tracked → Stored in DynamoDB
4. **Daily at 6 AM** → Features extracted → Risk calculated → Intervention if needed
5. **User opens app** → Risk score displayed → Support offered
6. **Monthly** → New data collected → Models retrained → Improved accuracy

## Current Status

✅ **Training Complete**: Models trained and saved to S3  
✅ **Feature Extraction**: Lambda functions ready  
✅ **Risk Calculation**: Lambda function ready  
⏳ **Integration**: Need to update Lambda to use ML models  
⏳ **Testing**: Need to test with real user data  

