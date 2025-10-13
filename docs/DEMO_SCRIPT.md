# Mind Mate - Demo Script for Hackathon

## Setup Before Demo (5 min)

1. Open Amplify app URL in browser
2. Have AWS Console open (DynamoDB, Lambda logs)
3. Have email inbox open
4. Prepare 2-3 test selfies
5. Clear browser console

## Demo Flow (5-7 minutes)

### 1. Introduction (30 sec)
"Hi! I'm presenting **Mind Mate** - an AI-powered mental wellness companion that combines mood tracking, emotion analysis, and predictive prevention to support mental health."

### 2. Show the Problem (30 sec)
"Mental health apps often feel clinical and reactive. We wanted something that's:
- Friendly and engaging (like a virtual pet)
- Proactive (predicts issues before crisis)
- Privacy-focused (no raw facial data stored)"

### 3. Live Demo - Mood Logging (1 min)
**Action:**
- Open web app
- Slide mood to 7
- Click tags: "Happy", "Productive"
- Add note: "Great day at work!"
- Click "Save Mood"

**Say:**
"Users log their daily mood with a simple slider. The data goes through API Gateway to Lambda, stored in DynamoDB. Let me show you..."

**Show:** DynamoDB table with the new entry

### 4. Live Demo - Selfie Analysis (1.5 min)
**Action:**
- Upload a smiling selfie
- Click "Analyze Emotions"
- Wait for results

**Say:**
"Now the magic happens. We upload a selfie, which goes to S3, then Amazon Rekognition detects facial emotions. Notice we only store the emotion scores - not the facial data itself. Privacy by design."

**Show:** 
- Results showing "HAPPY: 98%, CALM: 85%"
- S3 bucket with uploaded image
- DynamoDB entry with emotion scores

### 5. Live Demo - AI Pet Avatar (1 min)
**Action:**
- Type: "a fluffy orange cat with green eyes"
- Click "Create Avatar"
- Wait for generation

**Say:**
"Users can generate their own AI pet companion using Amazon Bedrock's Titan Image model. This personalizes the experience and makes mental health tracking feel less clinical."

**Show:** Generated avatar image

### 6. Daily Recap Feature (1 min)
**Action:**
- Trigger dailyRecap Lambda manually via Console
- Show email inbox

**Say:**
"Every day, Mind Mate sends a personalized recap email. It uses Claude on Bedrock to analyze the user's mood patterns and suggest evidence-based coping strategies. Let me trigger one now..."

**Show:** Email with empathetic recap message

### 7. The Killer Feature - Risk Prevention (2 min)
**Action:**
- Show DynamoDB with 7 days of low moods (pre-seeded)
- Trigger riskScan Lambda manually
- Show email inbox

**Say:**
"Here's what makes Mind Mate special: **predictive prevention**. 

If the system detects concerning patterns - like a 7-day average mood below 4, or a declining trend - it proactively sends a gentle check-in message with resources.

This isn't just mood tracking - it's early intervention. We're trying to catch mental health issues before they become crises."

**Show:** 
- Risk alert email with supportive message
- DynamoDB entry with risk flag

### 8. Architecture Overview (1 min)
**Show:** Architecture diagram from agent.md

**Say:**
"The entire system is serverless on AWS:
- **Amplify** hosts the frontend
- **API Gateway + Lambda** handle the backend
- **DynamoDB** stores all data
- **Rekognition** analyzes emotions
- **Bedrock** generates empathetic responses
- **EventBridge** schedules daily tasks
- **SES** sends emails

Total cost: under $2/month for demo usage. Fully scalable."

### 9. Impact & Future (30 sec)
**Say:**
"By combining AI, computer vision, and behavioral analytics, Mind Mate aims to reduce mental health deterioration through continuous, compassionate micro-interventions.

Future plans:
- Voice mood logging with Transcribe
- Mobile app
- Community features
- Multi-agent orchestration for deeper personalization"

### 10. Closing (15 sec)
"Thanks for watching! Mind Mate - your AI pet companion that listens, learns, and helps you care for your mind. Questions?"

## Backup Demos (If Live Demo Fails)

### Plan B: Use curl
```bash
# Show API working
curl -X POST "$API_URL/mood" \
  -H "Content-Type: application/json" \
  -d '{"userId":"demo","mood":8,"tags":["happy"]}'
```

### Plan C: Screenshots/Video
Have pre-recorded video walkthrough ready

## Key Talking Points

✅ **Serverless & Scalable** - No servers to manage
✅ **Privacy-First** - Only derived scores stored
✅ **Predictive** - Early warning system
✅ **Multi-Modal AI** - Text + Vision + Generation
✅ **Cost-Effective** - Under $2/month
✅ **Production-Ready** - Guardrails, encryption, monitoring

## Questions You Might Get

**Q: How accurate is emotion detection?**
A: Rekognition is 85-95% accurate for basic emotions. We use it as one signal among many, not the sole indicator.

**Q: What about privacy?**
A: We only store emotion scores, not facial embeddings. Images can be auto-deleted after analysis. HIPAA-compliant with proper setup.

**Q: How do you prevent false positives?**
A: Multiple signals (mood trend, slope, duration) and human-in-the-loop design. It's a nudge, not a diagnosis.

**Q: Can this scale?**
A: Yes! Serverless architecture scales automatically. DynamoDB and Lambda handle millions of requests.

**Q: What's the business model?**
A: Freemium - basic free, premium for advanced analytics, team/family plans, B2B for corporate wellness.

## Demo Checklist

- [ ] Amplify URL works
- [ ] API Gateway URL configured
- [ ] Test selfies ready
- [ ] Email inbox open
- [ ] AWS Console tabs ready
- [ ] Pre-seed low mood data for risk demo
- [ ] Test all features 30 min before
- [ ] Have backup video ready
- [ ] Charge laptop
- [ ] Test internet connection
