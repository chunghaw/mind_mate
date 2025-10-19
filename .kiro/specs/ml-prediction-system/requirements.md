# Requirements Document - ML Prediction System

## Introduction

The ML Prediction System is a proactive mental health monitoring feature that uses machine learning to identify users at risk of mental health crises 3-7 days before they occur. The system analyzes mood trends, behavioral patterns, sentiment, and contextual data to generate risk scores and trigger early interventions. This feature aims to shift Mind Mate from reactive support to proactive prevention.

## Requirements

### Requirement 1: Feature Engineering Pipeline

**User Story:** As a data scientist, I want to automatically extract meaningful features from user data, so that the ML model can identify risk patterns effectively.

#### Acceptance Criteria

1. WHEN a user has at least 7 days of mood data THEN the system SHALL extract mood trend features including 7-day, 14-day, and 30-day trends
2. WHEN extracting mood features THEN the system SHALL calculate statistical measures including mean, standard deviation, variance, min, and max values
3. WHEN analyzing mood patterns THEN the system SHALL identify consecutive low mood days (threshold ≤ 4) and mood decline rates
4. WHEN a user has interaction history THEN the system SHALL extract behavioral features including check-in frequency, session duration, and engagement trends
5. WHEN a user has sent messages THEN the system SHALL use AWS Comprehend to extract sentiment features including sentiment trends and negative/positive frequencies
6. WHEN extracting features THEN the system SHALL handle missing data gracefully by using median imputation or default values
7. WHEN feature extraction fails THEN the system SHALL log the error and return a partial feature set without blocking the pipeline

### Requirement 2: Training Data Preparation

**User Story:** As a machine learning engineer, I want to prepare labeled training datasets from historical user data, so that I can train accurate risk prediction models.

#### Acceptance Criteria

1. WHEN preparing training data THEN the system SHALL only include users with at least 60 days of historical data
2. WHEN labeling data THEN the system SHALL identify crisis events based on mood scores ≤ 2 for 3+ consecutive days OR explicit crisis indicators in messages
3. WHEN creating labels THEN the system SHALL use a 7-day lookahead window to determine if a crisis occurred after the feature extraction point
4. WHEN splitting data THEN the system SHALL use 80% for training and 20% for validation with temporal ordering preserved
5. WHEN preparing datasets THEN the system SHALL balance classes using oversampling or class weights to handle imbalanced data
6. WHEN storing training data THEN the system SHALL anonymize all PII and store feature vectors in S3 in CSV format
7. WHEN training data is insufficient THEN the system SHALL log a warning and skip model training

### Requirement 3: SageMaker Model Training

**User Story:** As a machine learning engineer, I want to train ensemble models using SageMaker, so that I can deploy accurate risk prediction models at scale.

#### Acceptance Criteria

1. WHEN training is triggered THEN the system SHALL use SageMaker with ml.m5.xlarge instances for training
2. WHEN training models THEN the system SHALL train both Random Forest and Gradient Boosting classifiers as an ensemble
3. WHEN configuring models THEN the system SHALL use hyperparameters: n_estimators=200, max_depth=10, class_weight='balanced'
4. WHEN training completes THEN the system SHALL evaluate models using AUC, precision, recall, and F1 scores on validation data
5. WHEN model performance is acceptable (AUC > 0.75, Recall > 0.70) THEN the system SHALL save models to S3
6. WHEN training completes THEN the system SHALL generate and store feature importance rankings
7. WHEN training fails THEN the system SHALL log detailed error information and send alerts to administrators

### Requirement 4: Real-time Risk Scoring

**User Story:** As a user, I want the system to continuously monitor my mental health patterns, so that I can receive timely support when I need it most.

#### Acceptance Criteria

1. WHEN a daily risk assessment is triggered THEN the system SHALL extract current features for the user
2. WHEN features are extracted THEN the system SHALL load trained models from S3 and generate risk probability scores
3. WHEN calculating risk THEN the system SHALL ensemble predictions from both Random Forest and Gradient Boosting models
4. WHEN a risk score is calculated THEN the system SHALL classify it into levels: minimal (<0.2), low (0.2-0.4), moderate (0.4-0.6), high (0.6-0.8), critical (≥0.8)
5. WHEN risk assessment completes THEN the system SHALL store the risk score, level, and timestamp in DynamoDB
6. WHEN risk level is high or critical THEN the system SHALL trigger appropriate interventions automatically
7. WHEN risk scoring fails THEN the system SHALL log the error and default to the user's last known risk level

### Requirement 5: Automated Daily Risk Assessment

**User Story:** As a system administrator, I want risk assessments to run automatically every day, so that all active users are continuously monitored without manual intervention.

#### Acceptance Criteria

1. WHEN the daily schedule triggers (6 AM UTC) THEN the system SHALL identify all active users (logged in within last 7 days)
2. WHEN active users are identified THEN the system SHALL invoke risk assessment Lambda for each user asynchronously
3. WHEN processing users THEN the system SHALL handle rate limits by batching requests appropriately
4. WHEN daily assessment completes THEN the system SHALL log summary statistics including total users processed and average risk scores
5. WHEN assessment fails for a user THEN the system SHALL retry up to 3 times with exponential backoff
6. WHEN all retries fail THEN the system SHALL log the failure and continue processing other users
7. WHEN daily assessment completes THEN the system SHALL send a summary report to administrators

### Requirement 6: Early Warning Interventions

**User Story:** As a user at risk, I want to receive proactive support and resources, so that I can get help before reaching a crisis point.

#### Acceptance Criteria

1. WHEN risk level is "high" THEN the system SHALL send a caring check-in message through the chat interface
2. WHEN risk level is "critical" THEN the system SHALL provide immediate crisis resources including hotline numbers (988, Crisis Text Line)
3. WHEN sending interventions THEN the system SHALL use Bedrock Claude to generate personalized, empathetic messages based on user personality and history
4. WHEN providing resources THEN the system SHALL include specific coping activities tailored to the user's preferences
5. WHEN critical risk is detected THEN the system SHALL send push notifications if the user has enabled them
6. WHEN interventions are triggered THEN the system SHALL log all intervention details for monitoring and evaluation
7. WHEN a user responds to an intervention THEN the system SHALL track the response and adjust future intervention strategies

### Requirement 7: Model Monitoring and Retraining

**User Story:** As a machine learning engineer, I want to continuously monitor model performance and retrain when needed, so that prediction accuracy remains high over time.

#### Acceptance Criteria

1. WHEN 30 days of predictions have accumulated THEN the system SHALL calculate performance metrics comparing predictions to actual outcomes
2. WHEN calculating metrics THEN the system SHALL compute precision, recall, F1 score, AUC, false positive rate, and false negative rate
3. WHEN model performance degrades (AUC < 0.75 OR Recall < 0.70) THEN the system SHALL automatically trigger retraining
4. WHEN retraining is triggered THEN the system SHALL use all available historical data including new data since last training
5. WHEN new models are trained THEN the system SHALL compare performance to existing models before deployment
6. WHEN new models perform better THEN the system SHALL automatically deploy them to production
7. WHEN monitoring detects issues THEN the system SHALL send alerts to administrators with detailed performance reports

### Requirement 8: Privacy and Ethics

**User Story:** As a user, I want my data to be protected and used ethically, so that I can trust the system with my sensitive mental health information.

#### Acceptance Criteria

1. WHEN preparing training data THEN the system SHALL anonymize all personally identifiable information (PII)
2. WHEN storing features THEN the system SHALL encrypt data at rest using AWS KMS
3. WHEN transmitting data THEN the system SHALL use TLS encryption for all data in transit
4. WHEN a user opts out THEN the system SHALL exclude their data from ML training and stop generating risk scores
5. WHEN displaying risk information THEN the system SHALL never show raw risk scores to users, only supportive messages
6. WHEN false positives occur THEN the system SHALL treat them as acceptable (better to check in unnecessarily than miss someone in need)
7. WHEN critical alerts are generated THEN the system SHALL log them for human oversight and review

### Requirement 9: Performance and Scalability

**User Story:** As a system administrator, I want the ML system to scale efficiently, so that it can support thousands of users without performance degradation.

#### Acceptance Criteria

1. WHEN processing 10,000 users THEN the daily risk assessment SHALL complete within 2 hours
2. WHEN calculating risk scores THEN each individual assessment SHALL complete within 5 seconds
3. WHEN loading models THEN the system SHALL cache models in Lambda memory to avoid repeated S3 downloads
4. WHEN feature extraction is slow THEN the system SHALL use parallel processing where possible
5. WHEN costs exceed budget THEN the system SHALL send alerts and provide cost optimization recommendations
6. WHEN scaling to 100,000 users THEN the system SHALL maintain performance by using SageMaker batch transform for bulk predictions
7. WHEN system load is high THEN the system SHALL prioritize high-risk users for assessment

### Requirement 10: Monitoring and Observability

**User Story:** As a system administrator, I want comprehensive monitoring and logging, so that I can troubleshoot issues and ensure the system is working correctly.

#### Acceptance Criteria

1. WHEN any Lambda function executes THEN the system SHALL log execution details including duration, memory usage, and errors
2. WHEN risk scores are calculated THEN the system SHALL emit CloudWatch metrics for risk level distribution
3. WHEN interventions are triggered THEN the system SHALL track intervention types, frequencies, and user responses
4. WHEN model training completes THEN the system SHALL log training metrics and feature importance
5. WHEN errors occur THEN the system SHALL send alerts to administrators via SNS
6. WHEN viewing dashboards THEN administrators SHALL see real-time metrics for system health, model performance, and user risk distribution
7. WHEN auditing is required THEN the system SHALL provide complete audit trails for all risk assessments and interventions
