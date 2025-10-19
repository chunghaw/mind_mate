# ML Integration Visual Diagrams

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Mind Mate Frontend                           │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │              │  │              │  │              │             │
│  │  Mood Tab    │  │  Selfie Tab  │  │  Stats Tab   │             │
│  │              │  │              │  │              │             │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘             │
│         │                 │                 │                      │
│         └─────────────────┼─────────────────┘                      │
│                           │                                        │
│                  ┌────────▼────────┐                               │
│                  │                 │                               │
│                  │  ML Wellness    │  ← NEW COMPONENT              │
│                  │  Widget         │                               │
│                  │                 │                               │
│                  │  😊 Doing Great │                               │
│                  │  Last: 2h ago   │                               │
│                  │  [🔄 Refresh]   │                               │
│                  │                 │                               │
│                  └────────┬────────┘                               │
│                           │                                        │
└───────────────────────────┼────────────────────────────────────────┘
                            │
                            │ HTTPS REST API
                            │
┌───────────────────────────▼────────────────────────────────────────┐
│                      API Gateway                                    │
│                                                                     │
│  Existing:                    New:                                 │
│  /mood                        /calculate-risk  ← NEW               │
│  /selfie                      /risk-score      ← NEW               │
│  /stats                                                            │
│  /profile                                                          │
│                                                                     │
└───────────────────────────┬────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│              │    │              │    │              │
│   logMood    │    │calculateRisk │    │ getRiskScore │
│   Lambda     │    │Score Lambda  │    │   Lambda     │
│  (existing)  │    │   (NEW)      │    │  (existing)  │
│              │    │              │    │              │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                    │
       │                   ▼                    │
       │          ┌──────────────────┐          │
       │          │                  │          │
       │          │ Feature          │          │
       │          │ Extraction       │          │
       │          │ Lambdas          │          │
       │          │                  │          │
       │          │ • Mood (20)      │          │
       │          │ • Behavioral(15) │          │
       │          │ • Sentiment (14) │          │
       │          │                  │          │
       │          └──────┬───────────┘          │
       │                 │                      │
       │                 ▼                      │
       │          ┌──────────────────┐          │
       │          │                  │          │
       │          │executeIntervention│         │
       │          │Lambda (NEW)      │          │
       │          │                  │          │
       │          │ • Bedrock Claude │          │
       │          │ • Chat Messages  │          │
       │          │ • Activities     │          │
       │          │ • Crisis Resources│         │
       │          │                  │          │
       │          └──────┬───────────┘          │
       │                 │                      │
       ▼                 ▼                      ▼
┌─────────────────────────────────────────────────────┐
│                    DynamoDB                          │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │          │  │          │  │          │         │
│  │ MoodLogs │  │   Risk   │  │Interventions│      │
│  │          │  │Assessments│  │          │         │
│  │(existing)│  │  (NEW)   │  │  (NEW)   │         │
│  │          │  │          │  │          │         │
│  └──────────┘  └──────────┘  └──────────┘         │
│                                                      │
└─────────────────────────────────────────────────────┘
```

## Data Flow: Risk Assessment

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: User Logs Mood                                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                    User clicks "Save Mood"
                            │
                            ▼
                    POST /mood
                    {mood: 7, notes: "..."}
                            │
                            ▼
                    logMood Lambda
                            │
                            ▼
                    DynamoDB.put(MoodLogs)
                            │
                            ▼
                    Response: {ok: true}

┌─────────────────────────────────────────────────────────────┐
│ Step 2: Calculate Risk (Manual or Scheduled)                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                    POST /calculate-risk
                    {userId: "user123"}
                            │
                            ▼
                    calculateRiskScore Lambda
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
extractMoodFeatures  extractBehavioral  extractSentiment
        │                   │                   │
        ▼                   ▼                   ▼
    Query Moods        Query Interactions  Query Messages
        │                   │                   │
        ▼                   ▼                   ▼
    20 features        15 features         14 features
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                            ▼
                    Combine 49 features
                            │
                            ▼
                    Calculate Risk Score
                    (rule-based algorithm)
                            │
                            ▼
                    risk_score = 0.68
                    risk_level = "high"
                            │
                            ▼
                    DynamoDB.put(RiskAssessments)
                            │
                            ▼
                    if risk_level in ["high", "critical"]
                            │
                            ▼
                    Invoke executeIntervention (async)
                            │
                            ▼
                    Response: {
                      ok: true,
                      riskScore: 0.68,
                      riskLevel: "high",
                      interventionTriggered: true
                    }

┌─────────────────────────────────────────────────────────────┐
│ Step 3: Execute Intervention (if needed)                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                    executeIntervention Lambda
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
    Get User Profile   Get Mood Trend    Get Risk Factors
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                            ▼
                    Generate Message
                    (Bedrock Claude)
                            │
                            ▼
                    "Hey Sarah, I've noticed you might
                     be going through a tough time..."
                            │
                            ▼
                    Create Priority Chat Message
                    DynamoDB.put(Messages)
                            │
                            ▼
                    Suggest Coping Activities
                    - Deep breathing
                    - Gentle walk
                    - Journaling
                            │
                            ▼
                    if risk_level == "critical"
                    Add Crisis Resources
                    - 988 Lifeline
                    - Crisis Text Line
                            │
                            ▼
                    Log Intervention
                    DynamoDB.put(Interventions)
                            │
                            ▼
                    Response: {
                      ok: true,
                      interventionsSent: [
                        "proactive_checkin",
                        "coping_activities"
                      ]
                    }

┌─────────────────────────────────────────────────────────────┐
│ Step 4: Display in Widget                                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                    Widget auto-refresh (5 min)
                    or manual refresh
                            │
                            ▼
                    GET /risk-score?userId=user123
                            │
                            ▼
                    getRiskScore Lambda
                            │
                            ▼
                    Query latest assessment
                    DynamoDB.query(RiskAssessments)
                            │
                            ▼
                    Response: {
                      ok: true,
                      riskScore: 0.68,
                      riskLevel: "high",
                      lastAssessment: "2025-10-19T10:30:00Z",
                      interventionTriggered: true
                    }
                            │
                            ▼
                    Widget updates display:
                    ┌─────────────────────┐
                    │ 💚 Wellness Check   │
                    │                     │
                    │ 😟 Need Support     │
                    │ Your companion is   │
                    │ here to help        │
                    │                     │
                    │ 💌 Your companion   │
                    │ has sent you a      │
                    │ message             │
                    │                     │
                    │ Last: 2h ago        │
                    └─────────────────────┘
```

## Risk Scoring Algorithm

```
┌─────────────────────────────────────────────────────────────┐
│ Input: 49 Features                                          │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Mood         │    │ Behavioral   │    │ Sentiment    │
│ Features     │    │ Features     │    │ Features     │
│              │    │              │    │              │
│ • Mean       │    │ • Check-ins  │    │ • Trend      │
│ • Trend      │    │ • Engagement │    │ • Negative % │
│ • Volatility │    │ • Late night │    │ • Keywords   │
│ • Low days   │    │ • Completion │    │ • Hopeless   │
│              │    │              │    │              │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                           ▼
                   ┌───────────────┐
                   │ Risk Factors  │
                   │ Detection     │
                   └───────┬───────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ Mood < 4     │   │ Declining    │   │ Crisis       │
│ +0.25        │   │ Engagement   │   │ Keywords     │
│              │   │ +0.15        │   │ +0.30        │
└──────┬───────┘   └──────┬───────┘   └──────┬───────┘
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
                          ▼
                  ┌───────────────┐
                  │ Sum Risk      │
                  │ Factors       │
                  └───────┬───────┘
                          │
                          ▼
                  risk_score = 0.68
                          │
                          ▼
                  ┌───────────────┐
                  │ Classify      │
                  │ Risk Level    │
                  └───────┬───────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
    < 0.2           0.2-0.4           0.4-0.6
    minimal           low             moderate
                                          │
                      ┌───────────────────┼───────────────────┐
                      │                   │                   │
                      ▼                   ▼                   ▼
                  0.6-0.8             ≥ 0.8
                   high              critical
                      │                   │
                      └───────────────────┘
                                │
                                ▼
                        Trigger Intervention
```

## Widget States

```
┌─────────────────────────────────────────────────────────────┐
│ State 1: Loading                                            │
└─────────────────────────────────────────────────────────────┘

    ┌─────────────────────┐
    │ 💚 Wellness Check   │
    │                     │
    │     ⟳ Loading...    │
    │                     │
    │ Checking wellness   │
    │ status...           │
    │                     │
    └─────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ State 2: No Data                                            │
└─────────────────────────────────────────────────────────────┘

    ┌─────────────────────┐
    │ 💚 Wellness Check   │
    │                     │
    │ ❓ No Data          │
    │                     │
    │ Check in with your  │
    │ mood to get started │
    │                     │
    │ Last: Never         │
    └─────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ State 3: Minimal Risk (Green)                               │
└─────────────────────────────────────────────────────────────┘

    ┌─────────────────────┐
    │ 💚 Wellness Check   │
    │                     │
    │ 😊 Doing Great      │
    │                     │
    │ Your wellness       │
    │ indicators look     │
    │ positive            │
    │                     │
    │ Last: 2h ago        │
    └─────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ State 4: High Risk (Orange) + Intervention                  │
└─────────────────────────────────────────────────────────────┘

    ┌─────────────────────┐
    │ 💚 Wellness Check   │
    │                     │
    │ 😟 Need Support     │
    │                     │
    │ Your companion is   │
    │ here to help        │
    │                     │
    │ 💌 Your companion   │
    │ has sent you a      │
    │ message             │
    │                     │
    │ Last: 2h ago        │
    └─────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ State 5: Critical Risk (Red) + Intervention                 │
└─────────────────────────────────────────────────────────────┘

    ┌─────────────────────┐
    │ 💚 Wellness Check   │
    │                     │
    │ 💙 Reach Out        │
    │                     │
    │ Please connect with │
    │ support resources   │
    │                     │
    │ 💌 Your companion   │
    │ has sent you a      │
    │ message             │
    │                     │
    │ Last: 30m ago       │
    └─────────────────────┘
```

## File Structure

```
aws_ai_agent_hackathon/
│
├── backend/
│   └── lambdas/
│       ├── calculateRiskScore/          ← NEW
│       │   └── lambda_function.py
│       ├── executeIntervention/         ← NEW
│       │   └── lambda_function.py
│       ├── getRiskScore/                (existing, works with new system)
│       │   └── lambda_function.py
│       ├── extractMoodFeatures/         (from tasks 1-6)
│       ├── extractBehavioralFeatures/   (from tasks 1-6)
│       └── extractSentimentFeatures/    (from tasks 1-6)
│
├── frontend/
│   ├── mind-mate-v3.html               (existing)
│   ├── mind-mate-ml.html               ← NEW (generated)
│   ├── ml-wellness-widget.js           ← NEW
│   └── ml-wellness-widget.css          ← NEW
│
├── infrastructure/
│   ├── deploy-ml-lambdas.sh            ← NEW
│   ├── add-ml-routes.sh                ← NEW
│   └── ml-prediction-stack.yaml        (from tasks 1-6)
│
├── scripts/
│   └── integrate-ml-widget.sh          ← NEW
│
├── docs/
│   ├── ML_INTEGRATION_COMPLETE.md      ← NEW
│   └── ML_INTEGRATION_DIAGRAM.md       ← NEW (this file)
│
├── ML_FULL_INTEGRATION_GUIDE.md        ← NEW
├── ML_INTEGRATION_QUICK_START.md       ← NEW
├── ML_INTEGRATION_SUMMARY.md           ← NEW
├── ML_INTEGRATION_COMPLETE.md          ← NEW
└── DEPLOY_ML_INTEGRATION.md            ← NEW
```

---

**Visual Guide Complete**
**Version**: 1.0.0
**Date**: October 19, 2025
