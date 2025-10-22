# Intervention System - Visual Flow

## Complete Intervention Journey

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    TRIGGER: High Risk Detected                           │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                        ┌──────────────────────┐
                        │  calculateRiskScore  │
                        │  Lambda              │
                        │                      │
                        │  Risk Score: 0.72    │
                        │  Risk Level: HIGH    │
                        └──────────────────────┘
                                    │
                                    ▼
                        ┌──────────────────────┐
                        │  Check Threshold     │
                        │  if risk >= 0.6:     │
                        │    trigger()         │
                        └──────────────────────┘
                                    │
                                    ▼
                        ┌──────────────────────┐
                        │  Async Invoke        │
                        │  executeIntervention │
                        │  Lambda              │
                        └──────────────────────┘
                                    │
                                    │
┌─────────────────────────────────────────────────────────────────────────┐
│                    STEP 1: Check Frequency Rules                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                        ┌──────────────────────┐
                        │  Get Last            │
                        │  Intervention        │
                        │  from DynamoDB       │
                        └──────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
        ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
        │  Last: 2 hours   │ │  Last: 2 days    │ │  No previous     │
        │  ago             │ │  ago             │ │  intervention    │
        │                  │ │                  │ │                  │
        │  High risk needs │ │  High risk needs │ │  ✅ Send         │
        │  24h gap         │ │  24h gap         │ │  intervention    │
        │                  │ │                  │ │                  │
        │  ❌ Too soon     │ │  ✅ Can send     │ │                  │
        │  Skip            │ │  Continue        │ │                  │
        └──────────────────┘ └──────────────────┘ └──────────────────┘
                                    │
                                    │
┌─────────────────────────────────────────────────────────────────────────┐
│                    STEP 2: Gather Context                                │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
        ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
        │  User Profile    │ │  Recent Activity │ │  Previous        │
        │                  │ │                  │ │  Interventions   │
        │  • Name: Sarah   │ │  • Mood logs     │ │                  │
        │  • Age: 28       │ │  • Chat history  │ │  • Count: 2      │
        │  • Timezone: PST │ │  • App usage     │ │  • Last response │
        └──────────────────┘ └──────────────────┘ └──────────────────┘
                                    │
                                    ▼
                        ┌──────────────────────┐
                        │  Context Object      │
                        │  {                   │
                        │    name: "Sarah",    │
                        │    risk_factors: [   │
                        │      "Declining mood"│
                        │      "Isolation"     │
                        │    ],                │
                        │    mood_avg: 3.2,    │
                        │    themes: [...]     │
                        │  }                   │
                        └──────────────────────┘
                                    │
                                    │
┌─────────────────────────────────────────────────────────────────────────┐
│                    STEP 3: Generate Message                              │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                        ┌──────────────────────┐
                        │  Build Prompt for    │
                        │  Bedrock Claude      │
                        └──────────────────────┘
                                    │
                                    ▼
                ┌───────────────────────────────────────┐
                │  Prompt:                              │
                │  "Generate empathetic intervention    │
                │   message for Sarah who shows:        │
                │   - Declining mood (avg 3.2/10)       │
                │   - Mentions of isolation             │
                │   - Increased late-night usage        │
                │                                       │
                │   Be warm, specific, offer support."  │
                └───────────────────────────────────────┘
                                    │
                                    ▼
                        ┌──────────────────────┐
                        │  Bedrock Claude      │
                        │  (Claude 3 Sonnet)   │
                        │                      │
                        │  Generates:          │
                        │  Personalized,       │
                        │  Empathetic,         │
                        │  Actionable message  │
                        └──────────────────────┘
                                    │
                                    ▼
                ┌───────────────────────────────────────┐
                │  Generated Message:                   │
                │                                       │
                │  "Hi Sarah,                           │
                │                                       │
                │   I've noticed you've been having a   │
                │   tough week. Your mood has been      │
                │   lower than usual, and you've        │
                │   mentioned feeling isolated in our   │
                │   recent chats.                       │
                │                                       │
                │   I'm here for you. Would you like    │
                │   to talk about what's been           │
                │   bothering you?                      │
                │                                       │
                │   You're not alone. 💙"               │
                └───────────────────────────────────────┘
                                    │
                                    │
┌─────────────────────────────────────────────────────────────────────────┐
│                    STEP 4: Send Intervention                             │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
        ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
        │  Send via        │ │  Store in        │ │  Send Push       │
        │  Bedrock Agent   │ │  Chat History    │ │  Notification    │
        │                  │ │                  │ │                  │
        │  InvokeAgent()   │ │  DynamoDB        │ │  "Mind Mate has  │
        │  with message    │ │  ChatHistory     │ │   sent you a     │
        │                  │ │  table           │ │   message"       │
        └──────────────────┘ └──────────────────┘ └──────────────────┘
                                    │
                                    ▼
                        ┌──────────────────────┐
                        │  Log Intervention    │
                        │  in DynamoDB         │
                        │                      │
                        │  Interventions Table │
                        └──────────────────────┘
                                    │
                                    ▼
                ┌───────────────────────────────────────┐
                │  Intervention Record:                 │
                │  {                                    │
                │    interventionId: "...",             │
                │    userId: "user-123",                │
                │    timestamp: "2025-10-22T10:00:00Z", │
                │    riskLevel: "high",                 │
                │    riskScore: 0.72,                   │
                │    messageGenerated: "Hi Sarah...",   │
                │    userResponded: false,              │
                │    responseTimestamp: null            │
                │  }                                    │
                └───────────────────────────────────────┘
                                    │
                                    │
┌─────────────────────────────────────────────────────────────────────────┐
│                    STEP 5: User Receives                                 │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                        ┌──────────────────────┐
                        │  User's Phone        │
                        │                      │
                        │  🔔 Notification     │
                        │  "Mind Mate has sent │
                        │   you a message"     │
                        └──────────────────────┘
                                    │
                                    ▼
                        ┌──────────────────────┐
                        │  User Opens App      │
                        └──────────────────────┘
                                    │
                                    ▼
        ┌───────────────────────────────────────────────┐
        │  Chat Interface                               │
        │  ┌─────────────────────────────────────────┐  │
        │  │  🤖 Mind Mate • Just now                │  │
        │  │  ┌───────────────────────────────────┐  │  │
        │  │  │ Hi Sarah,                         │  │  │
        │  │  │                                   │  │  │
        │  │  │ I've noticed you've been having   │  │  │
        │  │  │ a tough week. Your mood has been  │  │  │
        │  │  │ lower than usual, and you've      │  │  │
        │  │  │ mentioned feeling isolated.       │  │  │
        │  │  │                                   │  │  │
        │  │  │ I'm here for you. Would you like  │  │  │
        │  │  │ to talk about what's been         │  │  │
        │  │  │ bothering you?                    │  │  │
        │  │  │                                   │  │  │
        │  │  │ You're not alone. 💙              │  │  │
        │  │  └───────────────────────────────────┘  │  │
        │  │                                         │  │
        │  │  [Talk to me] [Get resources] [I'm OK]  │  │
        │  └─────────────────────────────────────────┘  │
        └───────────────────────────────────────────────┘
                                    │
                                    │
┌─────────────────────────────────────────────────────────────────────────┐
│                    STEP 6: Track Response                                │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
        ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
        │  User clicks     │ │  User types      │ │  User dismisses  │
        │  "Talk to me"    │ │  response        │ │  "I'm OK"        │
        │                  │ │                  │ │                  │
        │  ✅ High         │ │  ✅ High         │ │  ⚠️  Low         │
        │  engagement      │ │  engagement      │ │  engagement      │
        └──────────────────┘ └──────────────────┘ └──────────────────┘
                                    │
                                    ▼
                        ┌──────────────────────┐
                        │  Update Intervention │
                        │  Record              │
                        │                      │
                        │  userResponded: true │
                        │  responseTime: 300s  │
                        │  engagement: "high"  │
                        └──────────────────────┘
                                    │
                                    ▼
                        ┌──────────────────────┐
                        │  Continue            │
                        │  Conversation        │
                        │                      │
                        │  Bedrock Agent       │
                        │  provides support    │
                        └──────────────────────┘
                                    │
                                    │
┌─────────────────────────────────────────────────────────────────────────┐
│                    STEP 7: Follow-up Assessment                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                        ┌──────────────────────┐
                        │  24 Hours Later      │
                        │  Calculate new       │
                        │  risk score          │
                        └──────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
        ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
        │  Risk Decreased  │ │  Risk Same       │ │  Risk Increased  │
        │  0.72 → 0.55     │ │  0.72 → 0.70     │ │  0.72 → 0.85     │
        │                  │ │                  │ │                  │
        │  ✅ Intervention │ │  ⚠️  Continue    │ │  🚨 Escalate     │
        │  effective       │ │  monitoring      │ │  to critical     │
        │                  │ │                  │ │                  │
        │  Reduce          │ │  Send follow-up  │ │  Immediate       │
        │  frequency       │ │  in 24h          │ │  intervention    │
        └──────────────────┘ └──────────────────┘ └──────────────────┘
```

## Intervention Types by Risk Level

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    MINIMAL RISK (0.0 - 0.19)                            │
├─────────────────────────────────────────────────────────────────────────┤
│  Intervention: None                                                      │
│  Message: N/A                                                            │
│  Frequency: N/A                                                          │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                    LOW RISK (0.2 - 0.39)                                │
├─────────────────────────────────────────────────────────────────────────┤
│  Intervention: Encouragement                                             │
│  Message: "Great job staying consistent! Keep it up! 💙"                │
│  Frequency: Weekly                                                       │
│  Tone: Positive, supportive                                              │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                    MODERATE RISK (0.4 - 0.59)                           │
├─────────────────────────────────────────────────────────────────────────┤
│  Intervention: Check-in                                                  │
│  Message: "I noticed your mood has been lower. How are you feeling?"    │
│  Frequency: Every 3 days                                                 │
│  Tone: Caring, gentle                                                    │
│  Actions: Offer activities, coping strategies                            │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                    HIGH RISK (0.6 - 0.79)                               │
├─────────────────────────────────────────────────────────────────────────┤
│  Intervention: Proactive Support                                         │
│  Message: "I'm concerned about you. Let's talk about what's going on."  │
│  Frequency: Daily                                                        │
│  Tone: Concerned, supportive                                             │
│  Actions: Offer counselor connection, crisis resources                   │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                    CRITICAL RISK (0.8 - 1.0)                            │
├─────────────────────────────────────────────────────────────────────────┤
│  Intervention: Crisis Intervention                                       │
│  Message: "I'm very worried. Please call 988 or text HOME to 741741"   │
│  Frequency: Immediate + every 6 hours                                    │
│  Tone: Urgent, direct, supportive                                        │
│  Actions: Crisis hotlines, emergency resources, admin alert              │
└─────────────────────────────────────────────────────────────────────────┘
```

## Response Tracking Flow

```
User Receives Intervention
          │
          ▼
┌─────────────────────┐
│  Response Options   │
├─────────────────────┤
│  1. Talk to me      │ → High engagement → Continue conversation
│  2. Get resources   │ → Medium engagement → Show resources
│  3. I'm okay        │ → Low engagement → Acknowledge, reduce frequency
│  4. Not now         │ → No engagement → Snooze 24h, try again
│  5. No response     │ → No engagement → Follow up in 6-12h
└─────────────────────┘
          │
          ▼
┌─────────────────────┐
│  Track in DynamoDB  │
├─────────────────────┤
│  • Response type    │
│  • Response time    │
│  • Engagement level │
│  • Resources used   │
│  • Conversation len │
└─────────────────────┘
          │
          ▼
┌─────────────────────┐
│  Calculate Impact   │
├─────────────────────┤
│  • Risk before      │
│  • Risk after       │
│  • Risk change      │
│  • Effectiveness    │
└─────────────────────┘
```

## Key Metrics Dashboard

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    INTERVENTION METRICS                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  📊 Response Rate                                                        │
│  ████████████████████████░░░░░░░░ 75%                                   │
│  (Users who respond within 1 hour)                                      │
│                                                                          │
│  💬 Engagement Rate                                                      │
│  ████████████████░░░░░░░░░░░░░░░░ 60%                                   │
│  (Users who have meaningful conversation)                               │
│                                                                          │
│  📉 Risk Reduction                                                       │
│  ████████████░░░░░░░░░░░░░░░░░░░░ 40%                                   │
│  (Users with lower risk after intervention)                             │
│                                                                          │
│  🆘 Resource Access                                                      │
│  ████████░░░░░░░░░░░░░░░░░░░░░░░░ 30%                                   │
│  (Users who access crisis resources)                                    │
│                                                                          │
│  ⏱️  Average Response Time                                               │
│  15 minutes                                                              │
│                                                                          │
│  📈 Interventions Sent (Last 7 Days)                                    │
│  • Low risk: 12                                                          │
│  • Moderate risk: 8                                                      │
│  • High risk: 5                                                          │
│  • Critical risk: 2                                                      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

