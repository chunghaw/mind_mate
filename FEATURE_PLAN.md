# Mind Mate - Feature Plan & Discussion

## 🎯 **Current Status**
- ✅ Backend: All Lambda functions deployed
- ✅ API Gateway: Routes configured
- ✅ Database: DynamoDB table created
- ⚠️ Frontend: Basic UI exists but missing key features

---

## 🚨 **Issues Identified**

### 1. **Missing LLM Integration**
- **Problem**: No AI response/analysis shown to user
- **Expected**: After check-in, user should see AI-generated empathetic response
- **Missing**: Call to Bedrock Claude for analysis and coping suggestions

### 2. **Wrong User Flow**
- **Current**: Direct to mood logging
- **Expected**: 
  1. Login/Welcome
  2. Pet selection & avatar generation
  3. Pet asks for user's name
  4. Pet greets user by name
  5. Then access features

### 3. **Mood Selection Not Optional**
- **Problem**: Forced to select mood
- **Expected**: User can just chat/share thoughts without mood selection

### 4. **Missing Onboarding**
- No first-time user experience
- No pet personality selection
- No avatar generation flow
- No name collection

### 5. **Missing Features from agent.md**
- Daily recap emails (backend exists, not triggered)
- Risk detection (backend exists, not shown in UI)
- Insights dashboard
- Coping strategy suggestions

---

## 📝 **Proposed User Flow**

### **First-Time User (Onboarding)**
```
1. Welcome Screen
   "Hi! I'm Mind Mate 🐾"
   [Get Started]

2. Pet Selection
   "Choose your companion:"
   🐶 Gentle Guardian
   🐱 Playful Pal
   🐉 Focused Friend
   🦊 Sensitive Soul
   [Select & Generate Avatar]

3. Name Your Pet (Optional)
   "What would you like to call me?"
   [Text input] or [Skip - use default]

4. Pet Asks Your Name
   Pet: "Nice to meet you! How should I greet you?"
   [Text input]
   [Save]

5. Welcome Message
   Pet: "Hi [UserName]! I'm here to support your mental wellness..."
   [Continue to Home]
```

### **Returning User Flow**
```
1. Home Screen
   Pet avatar + "Welcome back, [UserName]! 👋"
   
2. Main Options:
   - 💬 Chat with [PetName]
   - 📊 View My Progress
   - ⚙️ Settings
```

### **Chat/Check-in Flow**
```
1. Chat Interface
   Pet: "How are you doing today, [UserName]?"
   
2. User Input (All Optional):
   - Text: "Share your thoughts..."
   - Mood: [Optional emoji selection]
   - 📸 Photo: [Optional selfie/environment]
   - 🎤 Voice: [Optional voice input]
   [Send]

3. AI Processing
   [Loading animation]
   "Analyzing your message..."

4. AI Response
   Pet avatar + empathetic response from Claude:
   - Reflection on what user shared
   - Emotional validation
   - 2-3 coping suggestions
   - Encouragement
   
5. Actions
   [Save to Journal]
   [View Suggestions]
   [Chat More]
```

---

## 🤖 **LLM Integration Plan**

### **New Lambda: `chatWithPet`**
**Purpose**: Main conversational interface

**Input**:
```json
{
  "userId": "user123",
  "message": "I'm feeling stressed about work",
  "mood": "anxious",  // optional
  "imageSelfie": "base64...",  // optional
  "imageEnv": "base64..."  // optional
}
```

**Process**:
1. Get user's pet personality from DynamoDB
2. If images provided, call Rekognition for emotion/scene analysis
3. Build context-aware prompt for Claude
4. Call Bedrock with personality-specific system prompt
5. Generate empathetic response + coping suggestions
6. Store conversation in DynamoDB
7. Award coins

**Output**:
```json
{
  "ok": true,
  "response": {
    "petMessage": "I hear you're feeling stressed...",
    "emotionDetected": "anxious",
    "copingStrategies": [
      "Take 5 deep breaths",
      "Step outside for 2 minutes"
    ],
    "encouragement": "You're doing great by checking in!"
  },
  "coinsEarned": 15
}
```

---

## 📋 **Features to Implement (Priority Order)**

### **Phase 1: Core Experience (Must Have)**
1. ✅ Onboarding flow
2. ✅ Pet selection & avatar generation
3. ✅ Name collection (user & pet)
4. ✅ Chat interface with LLM
5. ✅ AI response display
6. ✅ Optional mood/photo input

### **Phase 2: Engagement (Should Have)**
7. ✅ Coin system (already done)
8. ✅ Stats dashboard (already done)
9. ✅ Conversation history
10. ✅ Daily recap trigger button

### **Phase 3: Advanced (Nice to Have)**
11. ⏸️ Risk detection alerts
12. ⏸️ QuickSight dashboard
13. ⏸️ Social features
14. ⏸️ Cognito authentication

---

## 🎨 **UI/UX Improvements Needed**

### **Home Screen**
```
┌─────────────────────────────────┐
│  🐶 [Pet Avatar]                │
│  "Welcome back, Sarah! 👋"      │
│                                 │
│  ┌─────────────────────────┐   │
│  │ 💬 Chat with Buddy      │   │
│  └─────────────────────────┘   │
│                                 │
│  ┌─────────────────────────┐   │
│  │ 📊 My Progress          │   │
│  └─────────────────────────┘   │
│                                 │
│  ┌─────────────────────────┐   │
│  │ ⚙️ Settings             │   │
│  └─────────────────────────┘   │
│                                 │
│  💰 Coins: 150  🔥 Streak: 7   │
└─────────────────────────────────┘
```

### **Chat Screen**
```
┌─────────────────────────────────┐
│  🐶 Buddy                       │
│  💰 150                         │
├─────────────────────────────────┤
│                                 │
│  🐶 "Hi Sarah! How are you?"   │
│                                 │
│  👤 "Feeling stressed..."       │
│                                 │
│  🐶 "I hear you're stressed.   │
│      Let's take a moment..."    │
│      💡 Try: Deep breathing     │
│      💡 Try: Short walk         │
│                                 │
├─────────────────────────────────┤
│  [Type your message...]         │
│  😊 📸 🎤                       │
│  [Send]                         │
└─────────────────────────────────┘
```

---

## ❓ **Questions for You**

1. **Onboarding**: Should we require login/auth, or allow demo mode?
2. **Avatar Generation**: Generate with Titan, or just use emoji?
3. **Chat History**: Show previous conversations, or just current session?
4. **Mood Selection**: Keep as optional quick-select, or remove entirely?
5. **Daily Recap**: Manual trigger button, or automatic email only?

---

## ✅ **Approval Process**

**Before I implement anything:**
1. You review this plan
2. You approve/modify each feature
3. I update agent.md with approved changes
4. Then I implement

**What would you like to:**
- ✏️ Modify in this plan?
- ✅ Approve to implement?
- ❌ Remove/skip?

---

**Let's discuss and finalize the plan before any coding!** 🎯
