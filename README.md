# Mind Mate 🧠🐶

**AI-Powered Mental Health Companion with Real-Time Risk Assessment**

Mind Mate is an intelligent mental health support platform that combines conversational AI with machine learning to provide personalized mental wellness support, real-time risk assessment, and proactive intervention recommendations.

---

## 🌟 Live Demo

**🔗 [https://main.d3pktquxaop3su.amplifyapp.com/](https://main.d3pktquxaop3su.amplifyapp.com/)**

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Technical Architecture](#-technical-architecture)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Core Components](#-core-components)
- [Machine Learning Pipeline](#-machine-learning-pipeline)
- [Security & Privacy](#-security--privacy)
- [Deployment](#-deployment)
- [Cost Optimization](#-cost-optimization)
- [Future Roadmap](#-future-roadmap)
- [Contributing](#-contributing)
- [Support](#-support)
- [License](#-license)

---

## 🎯 Overview

### Vision

Create an accessible, AI-powered mental health companion that can detect early warning signs of mental health crises and provide immediate, personalized support while connecting users to professional resources when needed.

### Problem Statement

Mental health challenges affect millions globally, yet many face barriers to accessing timely support:
- Long wait times for professional care
- Stigma around seeking help
- Lack of 24/7 support availability
- Difficulty recognizing early warning signs

### Solution

Mind Mate addresses these challenges through:
- **24/7 AI Companion**: Always-available empathetic support
- **Predictive Analytics**: Early detection of mental health risks
- **Personalized Insights**: Tailored recommendations based on user patterns
- **Professional Integration**: Seamless connection to crisis resources


---

## ✨ Key Features

### 🤖 Conversational AI Companion
- **Powered by AWS Bedrock (Claude 3 Haiku)**
- Context-aware, empathetic conversations
- Persistent chat history across sessions
- Personality-based response adaptation
- Crisis intervention protocols

### 📊 Real-Time Risk Assessment
- **Machine Learning Pipeline** for mental health risk scoring
- Multi-dimensional analysis:
  - Mood pattern tracking (7-day trends)
  - Behavioral change detection
  - Sentiment analysis
  - Crisis keyword identification
- Dynamic risk levels: MINIMAL → LOW → MODERATE → HIGH → CRITICAL
- Predictive modeling for early intervention

### 🎨 Intelligent Dashboard
- Real-time wellness score visualization
- 7-day risk prediction with confidence metrics
- ML feature importance analysis
- Personalized insights and recommendations
- Historical trend analysis

### 🔐 Secure Authentication
- **AWS Cognito** integration
- Google OAuth support
- Secure user onboarding with personality assessment
- HIPAA-compliant data handling practices

### 🏗️ Scalable Architecture
- **100% Serverless AWS infrastructure**
- Auto-scaling based on demand
- Real-time data processing
- Cost-optimized for any scale

---

## 🏛️ Technical Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
│  React-like Vanilla JS SPA • Progressive Web App Features   │
│  Real-time Dashboard • AI Chat • ML Insights Visualization  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway (HTTP)                      │
│           RESTful Endpoints • CORS • Authorization          │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬────────────┐
        ▼            ▼            ▼            ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   AWS Lambda │ │  AWS Bedrock │ │  AWS Cognito │ │  SageMaker   │
│   Functions  │ │  (Claude 3)  │ │    (Auth)    │ │  (Training)  │
│              │ │              │ │              │ │              │
│ • Chat       │ │ • AI Chat    │ │ • OAuth 2.0  │ │ • RF Model   │
│ • ML Scoring │ │ • Empathy    │ │ • JWT Tokens │ │ • GB Model   │
│ • Features   │ │ • Crisis Det │ │ • MFA        │ │ • Ensemble   │
└──────┬───────┘ └──────────────┘ └──────────────┘ └──────┬───────┘
       │                                                    │
       │                                                    │
       ▼                                                    ▼
┌─────────────────────────────────────────────────────────────┐
│                       Data Layer                             │
│  DynamoDB (NoSQL) • S3 (Storage) • CloudWatch (Monitoring)  │
│  • User Data  • Mood Logs  • Chat History  • ML Models     │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

#### Frontend
- **Framework**: Vanilla JavaScript (React-like patterns)
- **Styling**: Modern CSS with animations
- **Charts**: Chart.js for data visualization
- **PWA**: Service workers for offline capability
- **Hosting**: AWS Amplify

#### Backend Services
- **Compute**: AWS Lambda (Python 3.12)
- **API**: API Gateway (HTTP API)
- **AI/ML**: AWS Bedrock (Claude 3 Haiku)
- **Authentication**: AWS Cognito
- **Database**: DynamoDB
- **Storage**: S3
- **Monitoring**: CloudWatch

#### Machine Learning
- **Feature Extraction**: Custom Lambda functions
- **Risk Scoring**: Real-time ML pipeline (rule-based + statistical models)
- **Model Training**: AWS SageMaker (Random Forest + Gradient Boosting ensemble)
- **Data Processing**: Python with NumPy/Pandas patterns
- **Model Storage**: S3 for trained models
- **Training Pipeline**: Automated retraining with new data

---

## 🚀 Quick Start

### Prerequisites

- AWS Account with appropriate permissions
- AWS CLI v2 configured (`aws configure`)
- Git
- Basic familiarity with AWS Console

### 1. Clone Repository

```bash
git clone https://github.com/chunghaw/mind_mate.git
cd mind_mate
```

### 2. Deploy Infrastructure

#### Step 2.1: Deploy Authentication (Cognito)

```bash
cd infrastructure
chmod +x deploy-cognito.sh
./deploy-cognito.sh
```

This creates:
- Cognito User Pool
- Google OAuth integration
- User pool client

#### Step 2.2: Deploy ML Infrastructure

```bash
chmod +x deploy-ml-stack.sh
./deploy-ml-stack.sh
```

This creates:
- DynamoDB tables for ML features
- IAM roles for Lambda functions
- CloudWatch log groups

#### Step 2.3: Deploy Lambda Functions

```bash
chmod +x deploy-lambdas.sh
./deploy-lambdas.sh
```

This deploys all backend Lambda functions:
- Chat handler (Bedrock integration)
- Mood logging
- ML feature extraction
- Risk score calculation
- Chat history management

#### Step 2.4: Configure API Gateway

```bash
chmod +x add-ml-routes-http.sh
./add-ml-routes-http.sh
```

This adds all API routes for ML endpoints.

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your AWS resources:
# - COGNITO_USER_POOL_ID
# - COGNITO_CLIENT_ID
# - API_GATEWAY_URL
# - AWS_REGION (default: us-east-1)
```

### 4. Deploy Frontend

#### Option A: AWS Amplify (Recommended)

```bash
# Create Amplify app
aws amplify create-app --name mind-mate --region us-east-1

# Create branch
aws amplify create-branch \
  --app-id YOUR_APP_ID \
  --branch-name main

# Start deployment
aws amplify start-job \
  --app-id YOUR_APP_ID \
  --branch-name main \
  --job-type RELEASE
```

#### Option B: Manual S3 + CloudFront

```bash
# Sync frontend files to S3
aws s3 sync frontend/ s3://your-bucket-name/ --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id YOUR_DIST_ID \
  --paths "/*"
```

### 5. Verify Deployment

Visit your Amplify URL or CloudFront distribution and:
1. Sign up with Google OAuth
2. Complete personality assessment
3. Start chatting with Mind Mate
4. Check the dashboard for wellness insights

---

## 📁 Project Structure

```
mind_mate/
│
├── 📱 frontend/                          # Frontend Application
│   ├── index.html                        # Root redirect page
│   ├── onboarding.html                   # Auth & personality assessment
│   ├── mind-mate-hackathon.html          # Main app (Dashboard/Chat/AI Report)
│   ├── check-auth.html                   # Auth debugging tool
│   ├── ml-wellness-widget.js             # ML visualization components
│   └── ml-wellness-widget.css            # Widget styling
│
├── ⚡ backend/lambdas/                   # AWS Lambda Functions
│   ├── chat/                             # AI conversation handler (Bedrock)
│   ├── getChatHistory/                   # Retrieve conversation history
│   ├── logMood/                          # Log user mood entries
│   ├── analyzeSelfie/                    # Image emotion analysis
│   ├── dailyRecap/                       # Generate daily summaries
│   ├── generateAvatar/                   # AI avatar generation
│   ├── setPassword/                      # User password management
│   ├── cognitoAuthorizer/                # API authorization
│   │
│   └── ML Pipeline Functions:
│       ├── calculateRiskScore/           # Main risk assessment engine
│       ├── extractMoodFeatures/          # Mood pattern analysis
│       ├── extractBehavioralFeatures/    # Behavior change detection
│       ├── extractSentimentFeatures/     # Sentiment analysis
│       └── prepareTrainingData/          # ML data preparation
│
├── 🏗️ infrastructure/                    # Infrastructure as Code
│   ├── cognito-stack.yaml                # Authentication infrastructure
│   ├── ml-prediction-stack.yaml          # ML infrastructure
│   ├── deploy-cognito.sh                 # Cognito deployment script
│   ├── deploy-ml-stack.sh                # ML deployment script
│   ├── deploy-lambdas.sh                 # Lambda deployment script
│   └── add-ml-routes-http.sh             # API Gateway configuration
│
├── 🤖 sagemaker/                         # ML Model Training
│   ├── train.py                          # SageMaker training script
│   │                                     # - Random Forest (200 trees)
│   │                                     # - Gradient Boosting
│   │                                     # - Ensemble prediction
│   ├── example_training_data.csv         # Sample training data (49 features)
│   └── README.md                         # Training documentation
│
├── 📚 docs/                              # Documentation
│   ├── API_REFERENCE.md                  # API documentation
│   ├── DEPLOYMENT_CHECKLIST.md           # Deployment guide
│   ├── ML_PREDICTION_SPEC.md             # ML specifications
│   ├── DEMO_SCRIPT.md                    # Demo walkthrough
│   ├── COST_BREAKDOWN.md                 # AWS cost analysis
│   ├── TROUBLESHOOTING.md                # Common issues & solutions
│   ├── GOOGLE_OAUTH_SETUP.md             # OAuth configuration
│   └── BEDROCK_PROMPTS.md                # AI prompt engineering
│
├── 🧪 test/                              # Testing
│   └── sample-payloads.json              # API test payloads
│
├── 📋 scripts/                           # Utility Scripts
│   └── generate-synthetic-data.py        # Test data generation
│
├── .kiro/specs/                          # Feature Specifications
│   ├── onboarding-flow/                  # Onboarding feature spec
│   ├── ml-prediction-system/             # ML system spec
│   └── hackathon-demo-ui/                # UI design spec
│
├── amplify.yml                           # AWS Amplify configuration
├── .env                                  # Environment variables
├── .gitignore                            # Git ignore rules
├── LICENSE                               # MIT License
├── CONTRIBUTING.md                       # Contribution guidelines
└── README.md                             # This file
```

---

## 🔧 Core Components

### 1. AI Conversation Engine

**Location**: `backend/lambdas/chat/lambda_function.py`

**Features**:
- Powered by AWS Bedrock (Claude 3 Haiku)
- Context-aware conversations with personality adaptation
- Crisis intervention detection and protocols
- Conversation history integration
- Empathetic response generation

**Key Capabilities**:
```python
# Personality-based system prompts
# Crisis keyword detection
# Conversation context management
# Streaming response support
# Error handling and fallbacks
```

### 2. ML Risk Assessment Engine

**Location**: `backend/lambdas/calculateRiskScore/lambda_function.py`

**Risk Calculation Algorithm**:
```python
risk_score = (
    mood_risk * 0.4 +           # 40% weight - mood patterns
    behavioral_risk * 0.3 +     # 30% weight - engagement patterns
    sentiment_risk * 0.3        # 30% weight - language analysis
)

# Risk Levels:
# 0.0-0.2: MINIMAL   - Stable mental health
# 0.2-0.4: LOW       - Minor concerns
# 0.4-0.6: MODERATE  - Attention needed
# 0.6-0.8: HIGH      - Intervention recommended
# 0.8-1.0: CRITICAL  - Immediate support required
```

**Features Analyzed**:
- 7-day mood average and trends
- Consecutive low mood days
- Check-in frequency patterns
- Sentiment ratios (positive/negative)
- Crisis keyword presence
- Temporal patterns

### 3. Frontend Application

**Location**: `frontend/mind-mate-hackathon.html`

**Architecture**:
- Single-page application (SPA)
- Component-based structure
- State management
- Real-time updates
- Responsive design (mobile-first)

**Key Features**:
- Three-tab interface (Dashboard, Chat, AI Report)
- Real-time ML visualization
- Chat history persistence
- Smooth animations and transitions
- Accessibility compliant (WCAG 2.1)

### 4. Authentication System

**Location**: `infrastructure/cognito-stack.yaml`

**Features**:
- Google OAuth integration
- Secure token management
- Session persistence
- Password reset flows
- MFA support (optional)

### 5. ML Model Training (SageMaker)

**Location**: `sagemaker/train.py`

**Architecture**:
- **Random Forest**: 200 estimators, max depth 10
- **Gradient Boosting**: Adaptive learning, class balancing
- **Ensemble**: Averages predictions from both models

**Training Process**:
```python
# Triggered by prepareTrainingData Lambda
# 1. Load training data from S3
# 2. Train Random Forest model
# 3. Train Gradient Boosting model
# 4. Evaluate ensemble performance
# 5. Save models to S3 if metrics acceptable
# 6. Update model registry in DynamoDB
```

**Performance Metrics**:
- AUC (Area Under ROC): > 0.80
- Recall (catch crises): > 0.75
- Precision (valid alerts): > 0.60
- F1 Score: > 0.65

**Feature Importance**:
Top predictive features:
1. `mood_trend_7day` - Recent mood trajectory
2. `consecutive_low_days` - Sustained low mood
3. `negative_sentiment_frequency` - Negative language
4. `crisis_keywords` - Explicit crisis indicators
5. `engagement_trend` - Declining engagement

**Training Cost**: ~$0.04 per training run (ml.m5.xlarge, 10 minutes)

### 6. Data Storage

**DynamoDB Tables**:
- `EmoCompanion` - Main data store
  - User profiles
  - Mood logs
  - Chat history
  - Selfie analysis results
  
- `MoodFeatures` - ML feature store
  - Extracted mood patterns
  - Behavioral metrics
  - Sentiment scores

- `TrainingJobs` - Model training registry
  - Training job metadata
  - Model performance metrics
  - Model S3 locations

**S3 Buckets**:
- User-uploaded images
- Generated avatars
- ML training data exports
- Trained ML models (Random Forest, Gradient Boosting)

---

## 🧠 Machine Learning Pipeline

### Overview

The ML system analyzes multiple dimensions of user data to provide real-time mental health risk assessment and predictive insights.

### Pipeline Architecture

```
User Interactions
       ↓
┌──────────────────────────────────────┐
│   Feature Extraction Layer           │
│  ┌────────────────────────────────┐  │
│  │  extractMoodFeatures           │  │
│  │  - 7-day mood average          │  │
│  │  - Mood trend analysis         │  │
│  │  - Consecutive low days        │  │
│  │  - Volatility metrics          │  │
│  └────────────────────────────────┘  │
│  ┌────────────────────────────────┐  │
│  │  extractBehavioralFeatures     │  │
│  │  - Check-in frequency          │  │
│  │  - Engagement patterns         │  │
│  │  - Response time analysis      │  │
│  │  - Activity consistency        │  │
│  └────────────────────────────────┘  │
│  ┌────────────────────────────────┐  │
│  │  extractSentimentFeatures      │  │
│  │  - Positive/negative ratios    │  │
│  │  - Crisis keyword detection    │  │
│  │  - Emotional intensity         │  │
│  │  - Language pattern changes    │  │
│  └────────────────────────────────┘  │
└──────────────────┬───────────────────┘
                   ↓
         ┌─────────────────────┐
         │  calculateRiskScore │
         │  - Weighted scoring │
         │  - Risk level calc  │
         │  - Confidence score │
         │  - Recommendations  │
         └─────────┬───────────┘
                   ↓
            Risk Assessment
         (MINIMAL → CRITICAL)
```

### Feature Extraction Details

#### 1. Mood Features (`extractMoodFeatures`)

**Metrics Calculated**:
- **7-day average**: Mean mood score over past week
- **Trend direction**: Linear regression slope
- **Consecutive low days**: Count of days with mood ≤ 4
- **Volatility**: Standard deviation of mood scores
- **Recovery rate**: Speed of mood improvement

**Risk Indicators**:
- Average mood ≤ 4.0 → High risk
- Negative trend (slope < -0.5) → Increasing risk
- 3+ consecutive low days → Moderate risk
- High volatility (σ > 2.5) → Instability

#### 2. Behavioral Features (`extractBehavioralFeatures`)

**Metrics Calculated**:
- **Check-in frequency**: Daily interaction rate
- **Engagement score**: Quality of interactions
- **Response patterns**: Time-of-day analysis
- **Consistency**: Regularity of usage

**Risk Indicators**:
- Decreased check-ins (< 50% of baseline) → Withdrawal
- Late-night activity spikes → Sleep disruption
- Irregular patterns → Instability

#### 3. Sentiment Features (`extractSentimentFeatures`)

**Metrics Calculated**:
- **Positive/negative ratio**: Balance of sentiment
- **Crisis keywords**: Presence of concerning terms
- **Emotional intensity**: Strength of expressions
- **Language complexity**: Communication patterns

**Risk Indicators**:
- Negative ratio > 70% → High risk
- Crisis keywords present → Immediate attention
- Decreased complexity → Cognitive changes

### Risk Score Calculation

**Formula**:
```python
def calculate_risk_score(mood_features, behavioral_features, sentiment_features):
    # Mood risk (40% weight)
    mood_risk = calculate_mood_risk(
        avg_mood=mood_features['avg_7day'],
        trend=mood_features['trend'],
        consecutive_low=mood_features['consecutive_low_days']
    )
    
    # Behavioral risk (30% weight)
    behavioral_risk = calculate_behavioral_risk(
        checkin_freq=behavioral_features['checkin_frequency'],
        engagement=behavioral_features['engagement_score']
    )
    
    # Sentiment risk (30% weight)
    sentiment_risk = calculate_sentiment_risk(
        pos_neg_ratio=sentiment_features['positive_negative_ratio'],
        crisis_keywords=sentiment_features['crisis_keywords_present']
    )
    
    # Weighted combination
    final_risk = (
        mood_risk * 0.4 +
        behavioral_risk * 0.3 +
        sentiment_risk * 0.3
    )
    
    return {
        'risk_score': final_risk,
        'risk_level': get_risk_level(final_risk),
        'confidence': calculate_confidence(mood_features, behavioral_features),
        'contributing_factors': identify_factors(mood_risk, behavioral_risk, sentiment_risk)
    }
```

### Predictive Modeling

**Machine Learning Models** (AWS SageMaker):
- **Random Forest Classifier**: Ensemble of 200 decision trees
- **Gradient Boosting Classifier**: Adaptive learning with boosting
- **Ensemble Prediction**: Averages both models for robustness
- **Training**: Automated retraining pipeline with new data
- **Performance**: AUC > 0.80, Recall > 0.75, Precision > 0.60

**7-Day Prediction**:
- Uses historical patterns to forecast future risk
- Considers seasonal trends and personal baselines
- Provides confidence intervals
- Updates daily with new data

**Early Warning System**:
- Detects subtle pattern changes before crisis
- ML-powered alerts 3-7 days in advance
- Recommends preventive interventions
- Connects to professional resources when needed

**Model Training Pipeline**:
```
User Data → Feature Extraction → Training Data Prep → 
SageMaker Training → Model Evaluation → S3 Storage → 
Lambda Risk Scoring → Real-time Predictions
```

---

## 🔐 Security & Privacy

### Data Protection

**Encryption**:
- **In Transit**: TLS 1.3 for all API communications
- **At Rest**: AES-256 encryption for DynamoDB and S3
- **Key Management**: AWS KMS for encryption keys

**Access Control**:
- **Authentication**: AWS Cognito with OAuth 2.0
- **Authorization**: Fine-grained IAM policies
- **API Security**: JWT token validation
- **Rate Limiting**: API Gateway throttling

**Privacy Measures**:
- **No PII in Logs**: Sensitive data redacted
- **Data Minimization**: Only essential data collected
- **User Control**: Data export and deletion capabilities
- **Anonymization**: Analytics use anonymized data

### Compliance

**HIPAA Readiness**:
- AWS HIPAA-eligible services used
- Audit logging enabled
- Access controls implemented
- Encryption at all layers

**GDPR Compliance**:
- Right to access (data export)
- Right to deletion (account removal)
- Data portability (JSON export)
- Consent management

**SOC 2**:
- AWS infrastructure compliance
- Security monitoring
- Incident response procedures

### Crisis Intervention Protocols

**Automated Detection**:
- ML-powered crisis keyword detection
- Risk score threshold monitoring
- Behavioral pattern analysis

**Escalation Procedures**:
1. **MINIMAL/LOW**: Supportive messages, self-help resources
2. **MODERATE**: Proactive check-ins, coping strategies
3. **HIGH**: Professional resource recommendations
4. **CRITICAL**: Immediate crisis hotline information, emergency contacts

**Resource Integration**:
- National Suicide Prevention Lifeline: 988
- Crisis Text Line: Text HOME to 741741
- International resources via findahelpline.com
- Local emergency services (911)

### Ethical AI Practices

**Transparency**:
- Clear disclosure of AI usage
- Explanation of risk scores
- Feature importance visibility

**Fairness**:
- Bias testing and mitigation
- Diverse training data
- Regular model audits

**Accountability**:
- Human oversight of critical decisions
- Audit trails for all actions
- Regular ethics reviews

---

## 🚀 Deployment

### Deployment Options

#### Option 1: AWS Amplify (Recommended)

**Advantages**:
- Automatic CI/CD with GitHub integration
- Built-in SSL certificates
- Global CDN distribution
- Zero-downtime deployments
- Custom domain support
- Preview environments for PRs

**Setup**:
```bash
# Connect to GitHub repository
aws amplify create-app \
  --name mind-mate \
  --repository https://github.com/chunghaw/mind_mate \
  --oauth-token YOUR_GITHUB_TOKEN

# Configure build settings (uses amplify.yml)
# Automatic deployments on git push
```

#### Option 2: S3 + CloudFront

**Advantages**:
- Full control over caching
- Custom security headers
- Advanced routing rules
- Cost optimization options

**Setup**:
```bash
# Create S3 bucket
aws s3 mb s3://mind-mate-frontend --region us-east-1

# Enable static website hosting
aws s3 website s3://mind-mate-frontend \
  --index-document index.html \
  --error-document index.html

# Create CloudFront distribution
aws cloudfront create-distribution \
  --origin-domain-name mind-mate-frontend.s3.amazonaws.com \
  --default-root-object index.html

# Deploy frontend
aws s3 sync frontend/ s3://mind-mate-frontend/ --delete
```

#### Option 3: Docker Container

**Advantages**:
- Hybrid/on-premises deployment
- Full environment control
- Custom runtime configurations

**Setup**:
```dockerfile
FROM nginx:alpine
COPY frontend/ /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Environment Configuration

**Required Environment Variables**:
```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=123456789012

# Cognito
COGNITO_USER_POOL_ID=us-east-1_XXXXXXXXX
COGNITO_CLIENT_ID=XXXXXXXXXXXXXXXXXXXXXXXXXX
COGNITO_DOMAIN=mind-mate-auth

# API Gateway
API_GATEWAY_URL=https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com

# DynamoDB
DYNAMODB_TABLE_NAME=EmoCompanion
MOOD_FEATURES_TABLE=MoodFeatures

# S3
S3_BUCKET_NAME=mind-mate-uploads

# Bedrock
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
```

### Monitoring & Observability

**CloudWatch Dashboards**:
- API request metrics
- Lambda execution times
- Error rates and types
- User engagement metrics

**Alarms**:
- High error rates (> 5%)
- Slow response times (> 3s)
- DynamoDB throttling
- Lambda concurrent executions

**Logging**:
- Structured JSON logs
- Request/response tracing
- Error stack traces
- User action audit logs

### CI/CD Pipeline

**GitHub Actions Workflow**:
```yaml
name: Deploy Mind Mate
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy Lambdas
        run: ./infrastructure/deploy-lambdas.sh
      - name: Deploy Frontend
        run: aws s3 sync frontend/ s3://${{ secrets.S3_BUCKET }}/
```

---

## 💰 Cost Optimization

### AWS Services Cost Breakdown

#### Monthly Cost Estimates (by user scale)

**1,000 Active Users**:
- AWS Bedrock (Claude 3 Haiku): ~$30
  - ~10 messages/user/day × 1K users × $0.00025/1K tokens
- Lambda: ~$5
  - ~50 invocations/user/day × 1K users × $0.0000002/request
- DynamoDB: ~$10
  - On-demand pricing, ~5 GB storage
- API Gateway: ~$3
  - HTTP API: $1.00 per million requests
- SageMaker: ~$1
  - Monthly model retraining (ml.m5.xlarge, 10 min)
- Amplify Hosting: ~$2
  - Build minutes + data transfer
- S3: ~$1
  - Storage + requests
- Cognito: Free
  - First 50,000 MAU free

**Total: ~$52/month for 1K users**

**10,000 Active Users**:
- AWS Bedrock: ~$250
- Lambda: ~$40
- DynamoDB: ~$80
- API Gateway: ~$25
- SageMaker: ~$5 (weekly retraining)
- Amplify: ~$15
- S3: ~$8
- Cognito: ~$25 (above free tier)

**Total: ~$448/month for 10K users**

**100,000 Active Users**:
- AWS Bedrock: ~$2,000
- Lambda: ~$300
- DynamoDB: ~$600
- API Gateway: ~$200
- SageMaker: ~$20 (daily retraining)
- Amplify: ~$100
- S3: ~$50
- Cognito: ~$250

**Total: ~$3,520/month for 100K users**

### Cost Optimization Strategies

**1. Bedrock Optimization**:
```python
# Use shorter prompts
# Cache system prompts
# Implement response streaming
# Use Claude 3 Haiku (cheapest model)
```

**2. Lambda Optimization**:
```python
# Increase memory for faster execution (lower cost)
# Use Lambda layers for shared dependencies
# Implement connection pooling
# Enable Lambda SnapStart
```

**3. DynamoDB Optimization**:
```python
# Use on-demand for variable traffic
# Implement efficient query patterns
# Use TTL for automatic data expiration
# Compress large items
```

**4. API Gateway Optimization**:
```python
# Use HTTP API (cheaper than REST API)
# Implement caching for repeated requests
# Batch requests where possible
```

**5. S3 Optimization**:
```python
# Use S3 Intelligent-Tiering
# Implement lifecycle policies
# Compress images before upload
# Use CloudFront for caching
```

**6. SageMaker Optimization**:
```python
# Use spot instances for training (70% cost savings)
# Train only when sufficient new data accumulated
# Use ml.m5.large for smaller datasets
# Implement early stopping to reduce training time
# Cache preprocessed features
```

### Free Tier Benefits

**First Year Free**:
- Lambda: 1M requests/month
- DynamoDB: 25 GB storage
- S3: 5 GB storage
- CloudWatch: 10 custom metrics

**Always Free**:
- Cognito: 50,000 MAU
- Lambda: 1M requests/month
- DynamoDB: 25 WCU, 25 RCU

### Budget Alerts

**Setup Cost Monitoring**:
```bash
# Create budget alert
aws budgets create-budget \
  --account-id 123456789012 \
  --budget file://budget.json \
  --notifications-with-subscribers file://notifications.json
```

**budget.json**:
```json
{
  "BudgetName": "MindMate-Monthly",
  "BudgetLimit": {
    "Amount": "100",
    "Unit": "USD"
  },
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST"
}
```

---

## 🔮 Future Roadmap

### Phase 1: Enhanced ML (Q1 2025)

**Advanced Models**:
- [ ] Deep learning models (LSTM, Transformers) for pattern recognition
- [ ] Transformer-based sentiment analysis (BERT, RoBERTa)
- [ ] Multi-modal analysis (text + voice + image)
- [ ] Personalized intervention recommendations
- [ ] XGBoost and LightGBM ensemble models

**Model Training** (SageMaker - Already Implemented ✅):
- [x] SageMaker integration for custom models
- [x] Random Forest + Gradient Boosting ensemble
- [x] Automated model retraining pipeline
- [ ] A/B testing framework for model versions
- [ ] Hyperparameter optimization (HPO)
- [ ] Federated learning for privacy

### Phase 2: Professional Integration (Q2 2025)

**Therapist Dashboard**:
- [ ] Client progress tracking
- [ ] Session notes and insights
- [ ] Risk alert notifications
- [ ] Secure messaging

**Appointment System**:
- [ ] Calendar integration
- [ ] Video call support (Amazon Chime)
- [ ] Automated reminders
- [ ] Insurance verification

**Clinical Tools**:
- [ ] Standardized assessment tools (PHQ-9, GAD-7)
- [ ] Treatment plan tracking
- [ ] Outcome measurement
- [ ] Research data export

### Phase 3: Community Features (Q3 2025)

**Peer Support**:
- [ ] Anonymous support groups
- [ ] Moderated forums
- [ ] Peer matching algorithm
- [ ] Community guidelines enforcement

**Social Features**:
- [ ] Achievement system
- [ ] Progress sharing (opt-in)
- [ ] Wellness challenges
- [ ] Gratitude journal

**Content Library**:
- [ ] Guided meditations
- [ ] Coping skill videos
- [ ] Educational articles
- [ ] Crisis resources

### Phase 4: Advanced Analytics (Q4 2025)

**Population Health**:
- [ ] Aggregate trend analysis
- [ ] Geographic insights
- [ ] Demographic patterns
- [ ] Seasonal variations

**Research Platform**:
- [ ] De-identified data sharing
- [ ] Research collaboration tools
- [ ] Publication support
- [ ] Grant application assistance

**Predictive Analytics**:
- [ ] Long-term outcome prediction
- [ ] Treatment response modeling
- [ ] Relapse prevention
- [ ] Resource allocation optimization

### Phase 5: Global Expansion (2026)

**Internationalization**:
- [ ] Multi-language support (10+ languages)
- [ ] Cultural adaptation
- [ ] Local crisis resources
- [ ] Regional compliance (GDPR, PIPEDA, etc.)

**Accessibility**:
- [ ] Voice-first interface
- [ ] Screen reader optimization
- [ ] Low-bandwidth mode
- [ ] SMS-based access

**Partnerships**:
- [ ] Healthcare provider integrations
- [ ] Insurance partnerships
- [ ] Academic collaborations
- [ ] NGO partnerships

---

## 🤝 Contributing

We welcome contributions from the community! Mind Mate is built to help people, and your expertise can make a real difference.

### How to Contribute

#### 1. Code Contributions

**Getting Started**:
```bash
# Fork the repository
git clone https://github.com/YOUR_USERNAME/mind_mate.git
cd mind_mate

# Create a feature branch
git checkout -b feature/your-feature-name

# Make your changes and commit
git add .
git commit -m "feat: add your feature description"

# Push and create a pull request
git push origin feature/your-feature-name
```

**Development Guidelines**:
- Follow existing code style and patterns
- Write clear commit messages (Conventional Commits)
- Add tests for new features
- Update documentation
- Ensure all tests pass before submitting

#### 2. Documentation

Help improve our documentation:
- Fix typos and clarify instructions
- Add examples and use cases
- Translate documentation
- Create video tutorials

#### 3. Bug Reports

Found a bug? Please report it:
- Use GitHub Issues
- Include steps to reproduce
- Provide error messages and logs
- Specify your environment

#### 4. Feature Requests

Have an idea? We'd love to hear it:
- Open a GitHub Discussion
- Describe the use case
- Explain the expected behavior
- Consider implementation approaches

### Code of Conduct

**Our Pledge**:
We are committed to providing a welcoming and inclusive environment for all contributors, regardless of background or identity.

**Expected Behavior**:
- Be respectful and considerate
- Welcome diverse perspectives
- Focus on constructive feedback
- Prioritize user wellbeing

**Unacceptable Behavior**:
- Harassment or discrimination
- Trolling or insulting comments
- Privacy violations
- Unethical use of the platform

### Development Setup

**Prerequisites**:
- Python 3.12+
- Node.js 18+ (for local testing)
- AWS CLI configured
- Git

**Local Development**:
```bash
# Install Python dependencies
pip install -r requirements.txt

# Run local tests
python -m pytest

# Test Lambda functions locally
sam local invoke chat -e test/sample-payloads.json

# Start local frontend server
cd frontend
python -m http.server 8000
```

### Testing

**Unit Tests**:
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_risk_calculation.py

# Run with coverage
pytest --cov=backend/lambdas
```

**Integration Tests**:
```bash
# Test API endpoints
./test/run-integration-tests.sh

# Test ML pipeline
python scripts/test-ml-pipeline.py
```

### Pull Request Process

1. **Update Documentation**: Ensure README and docs reflect your changes
2. **Add Tests**: Include unit and integration tests
3. **Pass CI/CD**: All automated checks must pass
4. **Code Review**: Address reviewer feedback
5. **Squash Commits**: Clean up commit history before merge

### Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project website (coming soon)

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## 📞 Support

### Documentation

**Comprehensive Guides**:
- 📖 [API Reference](docs/API_REFERENCE.md) - Complete API documentation
- 🚀 [Deployment Checklist](docs/DEPLOYMENT_CHECKLIST.md) - Step-by-step deployment
- 🔧 [Troubleshooting Guide](docs/TROUBLESHOOTING.md) - Common issues and solutions
- 🤖 [ML Prediction Spec](docs/ML_PREDICTION_SPEC.md) - ML system details
- 🎭 [Demo Script](docs/DEMO_SCRIPT.md) - Walkthrough for presentations
- 💰 [Cost Breakdown](docs/COST_BREAKDOWN.md) - Detailed cost analysis
- 🔐 [Google OAuth Setup](docs/GOOGLE_OAUTH_SETUP.md) - Authentication configuration
- 💬 [Bedrock Prompts](docs/BEDROCK_PROMPTS.md) - AI prompt engineering

### Community Support

**GitHub**:
- 💬 [Discussions](https://github.com/chunghaw/mind_mate/discussions) - Ask questions, share ideas
- 🐛 [Issues](https://github.com/chunghaw/mind_mate/issues) - Report bugs, request features
- 📋 [Projects](https://github.com/chunghaw/mind_mate/projects) - Track development progress

**Communication Channels**:
- Email: support@mindmate.ai (coming soon)
- Twitter: @MindMateAI (coming soon)
- Discord: Join our community (coming soon)

### Professional Services

**Enterprise Support**:
- 🏥 Healthcare integration consulting
- 🏢 Custom deployment assistance
- 🎓 Training workshops
- 🔒 Security audits
- 📊 Custom analytics

**Contact**: enterprise@mindmate.ai (coming soon)

### Getting Help

**Before Asking**:
1. Check the [documentation](docs/)
2. Search [existing issues](https://github.com/chunghaw/mind_mate/issues)
3. Review [troubleshooting guide](docs/TROUBLESHOOTING.md)

**When Asking**:
- Provide clear description
- Include error messages
- Share relevant code snippets
- Specify your environment

### Crisis Resources

**If you're in crisis, please reach out immediately**:

**United States**:
- 🆘 Emergency: 911
- 📞 Suicide Prevention Lifeline: 988
- 💬 Crisis Text Line: Text HOME to 741741

**International**:
- 🌍 Find a Helpline: [findahelpline.com](https://findahelpline.com)

**Mind Mate is not a substitute for professional mental health care.**

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### MIT License Summary

**Permissions**:
- ✅ Commercial use
- ✅ Modification
- ✅ Distribution
- ✅ Private use

**Conditions**:
- 📋 License and copyright notice must be included

**Limitations**:
- ❌ No liability
- ❌ No warranty

---

## 🙏 Acknowledgments

### Technology Partners

**AWS Services**:
- Amazon Bedrock for conversational AI
- AWS Lambda for serverless compute
- Amazon DynamoDB for data storage
- AWS Amplify for hosting and CI/CD
- Amazon Cognito for authentication

**AI Models**:
- Anthropic Claude 3 Haiku for empathetic conversations
- AWS Rekognition for image analysis

### Open Source Community

Thank you to the open source projects that made this possible:
- Chart.js for data visualization
- Python community for excellent libraries
- AWS CDK/SAM for infrastructure as code

### Mental Health Professionals

Special thanks to mental health professionals who provided guidance on:
- Ethical AI practices
- Crisis intervention protocols
- Risk assessment methodologies
- User experience considerations

### Contributors

Thank you to all contributors who have helped improve Mind Mate:
- [View all contributors](https://github.com/chunghaw/mind_mate/graphs/contributors)

---

## ⚠️ Important Disclaimer

**Medical Disclaimer**:

Mind Mate is designed to **supplement, not replace**, professional mental health care. This application:

- ❌ Is NOT a substitute for professional medical advice, diagnosis, or treatment
- ❌ Should NOT be used for medical emergencies
- ❌ Does NOT provide crisis intervention services
- ✅ IS a supportive tool for mental wellness tracking
- ✅ CAN help identify patterns and trends
- ✅ SHOULD be used alongside professional care

**If you are experiencing a mental health crisis**:
- Call 911 (US) or your local emergency number
- Call the National Suicide Prevention Lifeline: 988
- Text HOME to 741741 (Crisis Text Line)
- Go to your nearest emergency room

**Always consult with qualified healthcare professionals** for medical advice and treatment decisions.

---

## 📊 Project Status

**Current Version**: 1.0.0 (Production Ready)

**Status Badges**:
- ✅ Deployment: Live on AWS Amplify
- ✅ Backend: All services operational
- ✅ ML Pipeline: Active and processing
- ✅ Security: HIPAA-ready architecture
- ✅ Documentation: Comprehensive

**Recent Updates**:
- 2025-01: Initial production release
- 2025-01: ML risk assessment system deployed
- 2025-01: Google OAuth integration complete
- 2025-01: Dashboard and visualization launched

---

## 🌟 Star History

If you find Mind Mate helpful, please consider giving it a star on GitHub! ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=chunghaw/mind_mate&type=Date)](https://star-history.com/#chunghaw/mind_mate&Date)

---

<div align="center">

## Built with ❤️ for Mental Health Awareness

**[🌐 Live Demo](https://main.d3pktquxaop3su.amplifyapp.com/)** • 
**[📚 Documentation](docs/)** • 
**[🤝 Contribute](CONTRIBUTING.md)** • 
**[💬 Discussions](https://github.com/chunghaw/mind_mate/discussions)**

---

### Quick Links

[Features](#-key-features) • 
[Architecture](#-technical-architecture) • 
[Quick Start](#-quick-start) • 
[ML Pipeline](#-machine-learning-pipeline) • 
[Security](#-security--privacy) • 
[Deployment](#-deployment) • 
[Roadmap](#-future-roadmap)

---

**Mind Mate** - Your AI companion for mental wellness 🧠🐶

*Making mental health support accessible, intelligent, and compassionate*

</div>
