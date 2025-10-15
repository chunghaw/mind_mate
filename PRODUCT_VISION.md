# 🐾 Mind Mate - Complete Product Vision & User Journey

## 🎯 Core Value Propositions

### **1. Emotional Intelligence at Scale**
- **Multi-modal emotion detection** via text, facial expressions, and environmental context
- **Predictive mental health modeling** identifying risk patterns 3-7 days before crisis points
- **Contextual intervention delivery** adapting to user mood, history, and preferences
- **Continuous learning** from user interactions to improve accuracy and personalization

### **2. Personalized AI Pet Companionship**
- **Dynamic pet personalities** that evolve based on user interactions and emotional patterns
- **Contextual dialogue system** where pets remember conversations, celebrate progress, and provide comfort
- **Gamified wellness journey** with pet growth tied to user mental health improvements
- **Emotional bond building** through consistent, empathetic interactions

### **3. Proactive Mental Health Prevention**
- **Early warning system** detecting burnout, anxiety, and depression indicators
- **Automated intervention pipeline** delivering personalized coping strategies before crisis
- **Historical context awareness** - "Hey, you had a tough day yesterday, how are you feeling today?"
- **LLM-driven everything** - No hardcoded responses, all dynamic and contextual

---

## 🚀 Complete User Experience Journey

### **Phase 1: First-Time User Onboarding**

#### **Step 1: Welcome & Introduction**
```
┌─────────────────────────────────────┐
│                                     │
│         🐾 Mind Mate                │
│                                     │
│   Your AI Pet Companion for         │
│   Mental Wellness                   │
│                                     │
│   ┌─────────────────────────────┐  │
│   │   🌟 Get Started            │  │
│   └─────────────────────────────┘  │
│                                     │
└─────────────────────────────────────┘
```

**What happens:**
- User sees welcoming animation
- Brief explanation: "I'm here to support your mental wellness journey"
- No login required for demo (optional Cognito later)

---

#### **Step 2: Pet Personality Selection**
```
┌─────────────────────────────────────┐
│  Choose Your Companion              │
│                                     │
│  ┌──────────┐  ┌──────────┐       │
│  │    🐶    │  │    🐱    │       │
│  │  Gentle  │  │ Playful  │       │
│  │ Guardian │  │   Pal    │       │
│  └──────────┘  └──────────┘       │
│                                     │
│  ┌──────────┐  ┌──────────┐       │
│  │    🐉    │  │    🦊    │       │
│  │ Focused  │  │Sensitive │       │
│  │  Friend  │  │   Soul   │       │
│  └──────────┘  └──────────┘       │
│                                     │
│  Each personality has a unique      │
│  way of supporting you!             │
└─────────────────────────────────────┘
```

**What happens:**
- User selects one of 4 personalities
- Each has distinct communication style:
  - **Gentle Guardian**: Nurturing, supportive, patient
  - **Playful Pal**: Energetic, fun, motivating
  - **Focused Friend**: Calm, direct, mindful
  - **Sensitive Soul**: Empathetic, understanding, validating

**Backend:**
- Stores personality in DynamoDB
- This affects ALL future LLM responses

---

#### **Step 3: Pet Avatar Generation (Optional)**
```
┌─────────────────────────────────────┐
│  Let's create your companion!       │
│                                     │
│  [Generating your unique pet...]    │
│                                     │
│  🎨 ✨ 🐶 ✨ 🎨                    │
│                                     │
│  Using AI to create a special       │
│  companion just for you...          │
└─────────────────────────────────────┘
```

**What happens:**
- Calls `generateAvatar` Lambda
- Uses Bedrock Titan Image G1 to create unique pet
- Stores avatar URL in DynamoDB
- Falls back to emoji if generation fails

**Backend:**
```python
# Lambda: generateAvatar
# Calls Bedrock Titan with personality-specific prompt
# Returns S3 URL of generated image
```

---

#### **Step 4: Pet Asks for User's Name**
```
┌─────────────────────────────────────┐
│         🐶                          │
│                                     │
│  Pet: "Hi there! I'm so excited     │
│        to be your companion!        │
│        What should I call you?"     │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Your name...                │   │
│  └─────────────────────────────┘   │
│                                     │
│  [Continue]                         │
└─────────────────────────────────────┘
```

**What happens:**
- Pet uses personality-specific greeting
- User enters their preferred name
- Stored in DynamoDB profile
- Used in ALL future interactions

---

#### **Step 5: Pet Introduces Itself**
```
┌─────────────────────────────────────┐
│         🐶                          │
│                                     │
│  Pet: "Nice to meet you, Sarah!     │
│        You can call me Buddy.       │
│        I'm here to support your     │
│        mental wellness journey.     │
│                                     │
│        I'll check in with you,      │
│        listen to how you're         │
│        feeling, and suggest         │
│        activities that might help.  │
│                                     │
│        Ready to start?"             │
│                                     │
│  [Let's Go!]                        │
└─────────────────────────────────────┘
```

**What happens:**
- LLM-generated introduction based on personality
- Explains what Mind Mate does
- Sets expectations for the experience

---

### **Phase 2: Daily Interaction - The Core Experience**

#### **Home Screen (Returning User)**
```
┌─────────────────────────────────────┐
│  🐶 Buddy              💰 150  🔥 7 │
├─────────────────────────────────────┤
│                                     │
│         [Pet Avatar]                │
│                                     │
│  "Welcome back, Sarah! 👋           │
│   I've been thinking about you.     │
│   How are you feeling today?"       │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ 💬 Chat with Buddy          │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ 📊 View My Progress         │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ ⚙️ Settings                 │   │
│  └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

**Key Features:**
- **Personalized greeting** using user's name
- **Contextual message** based on:
  - Time of day
  - Last interaction
  - Recent mood patterns
  - Yesterday's conversation
- **Streak counter** for daily engagement
- **Coin balance** for gamification

**Backend:**
```python
# Lambda: getGreeting
# Inputs: userId, timestamp, lastMoodData
# Process:
#   1. Get user profile (name, personality)
#   2. Get last 3 days of mood data
#   3. Call Bedrock Claude with context:
#      - User name
#      - Pet personality
#      - Recent mood history
#      - Time of day
#   4. Generate contextual greeting
# Output: Personalized greeting message
```

---

#### **Chat Interface - The Heart of Mind Mate**
```
┌─────────────────────────────────────┐
│  🐶 Buddy                      [×]  │
├─────────────────────────────────────┤
│                                     │
│  🐶 "Hi Sarah! I noticed you had   │
│      a tough day yesterday with     │
│      work stress. How are you       │
│      feeling today? Any better?"    │
│                                     │
│  👤 "Still feeling overwhelmed...   │
│      so much to do"                 │
│                                     │
│  🐶 "I hear you, Sarah. Feeling    │
│      overwhelmed is really hard.    │
│      Let's take this one step at    │
│      a time together.               │
│                                     │
│      💡 Try this: Take 5 deep      │
│      breaths with me right now.     │
│      Breathe in for 4, hold for 4,  │
│      out for 4.                     │
│                                     │
│      💡 Or: Step outside for just  │
│      2 minutes. Fresh air can help  │
│      reset your mind.               │
│                                     │
│      Which sounds better to you?"   │
│                                     │
├─────────────────────────────────────┤
│  Type your message...               │
│  😊 📸 🎤                [Send]     │
└─────────────────────────────────────┘
```

**Key Features:**

1. **Historical Context Awareness**
   - Pet remembers yesterday's conversation
   - References past struggles and victories
   - Builds on previous coping strategies

2. **LLM-Driven Responses**
   - ALL responses generated by Claude
   - No hardcoded messages
   - Personality-specific tone

3. **Actionable Suggestions**
   - 2-3 specific, doable activities
   - Based on user's context and history
   - Inspired by HeartPet's micro-actions

4. **Optional Inputs**
   - Text is primary (always available)
   - Mood emoji (optional quick-select)
   - Photo (optional for deeper analysis)
   - Voice (optional for accessibility)

**Backend Flow:**
```python
# Lambda: chatWithPet
# Inputs:
#   - userId
#   - message (text)
#   - mood (optional)
#   - imageSelfie (optional)
#   - imageEnv (optional)

# Process:
#   1. Get user profile (name, personality, history)
#   2. Get last 7 days of conversations
#   3. Get last 3 mood entries
#   4. If image provided:
#      - Call Rekognition for emotion/scene analysis
#      - Extract emotion scores
#   5. Build comprehensive context for Claude:
#      - User name
#      - Pet name and personality
#      - Current message
#      - Recent conversation history
#      - Mood trends
#      - Emotion analysis (if available)
#      - Time of day, day of week
#   6. Call Bedrock Claude with personality-specific system prompt
#   7. Generate response with:
#      - Empathetic reflection
#      - Validation of feelings
#      - 2-3 specific coping strategies
#      - Encouragement
#   8. Store conversation in DynamoDB
#   9. Award coins (15-25 based on engagement)
#   10. Update mood trend data

# Output:
#   - petMessage (LLM-generated response)
#   - copingStrategies (array of suggestions)
#   - coinsEarned
#   - emotionDetected (if image provided)
```

**Example Bedrock Prompt:**
```
You are Buddy, a Gentle Guardian personality AI pet companion for Sarah.

CONTEXT:
- User: Sarah
- Time: Tuesday, 2:30 PM
- Yesterday: Sarah shared feeling stressed about work deadlines
- Recent trend: Mood declining from 7 to 5 over 3 days
- Current message: "Still feeling overwhelmed... so much to do"

YOUR PERSONALITY:
- Gentle, nurturing, patient
- Use warm, supportive language
- Focus on small, achievable steps
- Celebrate small wins
- Never clinical or robotic

TASK:
Respond to Sarah with:
1. Acknowledgment of her feelings (reference yesterday)
2. Empathetic validation
3. 2-3 specific, actionable coping strategies (30 seconds to 5 minutes each)
4. Gentle encouragement

IMPORTANT:
- Keep response under 100 words
- Be conversational, not preachy
- Offer choices, don't command
- Reference her name naturally
- Sound like a caring friend, not a therapist

RESPONSE:
```

---

#### **Activity Completion Flow**
```
┌─────────────────────────────────────┐
│  🐶 Buddy                           │
├─────────────────────────────────────┤
│                                     │
│  "Great choice, Sarah! Let's do     │
│   the breathing exercise together." │
│                                     │
│  ┌─────────────────────────────┐   │
│  │                             │   │
│  │    Breathe In... 4          │   │
│  │         ●                   │   │
│  │                             │   │
│  └─────────────────────────────┘   │
│                                     │
│  [Timer: 2:30 remaining]            │
│                                     │
└─────────────────────────────────────┘

After completion:

┌─────────────────────────────────────┐
│  🐶 Buddy                           │
├─────────────────────────────────────┤
│                                     │
│  "You did it, Sarah! 🎉            │
│   How do you feel now?"             │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ 😊 Better                   │   │
│  │ 😐 About the same           │   │
│  │ 😔 Still struggling         │   │
│  └─────────────────────────────┘   │
│                                     │
│  +20 coins earned! 💰              │
│                                     │
└─────────────────────────────────────┘
```

**What happens:**
- Guided activity with timer
- Post-activity check-in
- LLM-generated encouragement
- Coin reward
- Effectiveness tracking for future recommendations

---

#### **Progress View**
```
┌─────────────────────────────────────┐
│  📊 Your Journey                    │
├─────────────────────────────────────┤
│                                     │
│  🔥 Current Streak: 7 days          │
│  ✅ Total Check-ins: 42             │
│  💰 Coins Earned: 150               │
│                                     │
│  📈 Mood Trend (Last 7 Days)        │
│  ┌─────────────────────────────┐   │
│  │     ▁▂▃▅▆▇█                 │   │
│  │  Mon Tue Wed Thu Fri Sat Sun│   │
│  └─────────────────────────────┘   │
│                                     │
│  💬 Recent Conversations            │
│  ┌─────────────────────────────┐   │
│  │ Today: "Feeling better..."  │   │
│  │ Yesterday: "Work stress..." │   │
│  │ 2 days ago: "Anxious..."    │   │
│  └─────────────────────────────┘   │
│                                     │
│  🎯 Most Helpful Activities         │
│  • Deep breathing (5 times)         │
│  • Short walks (3 times)            │
│  • Journaling (2 times)             │
│                                     │
└─────────────────────────────────────┘
```

---

### **Phase 3: Proactive Support & Prevention**

#### **Morning Check-in (Contextual)**
```
┌─────────────────────────────────────┐
│  🐶 Buddy                           │
├─────────────────────────────────────┤
│                                     │
│  "Good morning, Sarah! ☀️          │
│                                     │
│   I noticed you've had 3 tough      │
│   days in a row. I'm here for you.  │
│                                     │
│   How did you sleep last night?     │
│   Sometimes rest makes a big        │
│   difference."                      │
│                                     │
│  [Chat with Buddy]                  │
│                                     │
└─────────────────────────────────────┘
```

**Triggered by:**
- Risk detection algorithm
- 3+ days of declining mood
- LLM generates proactive outreach

---

#### **Daily Recap Email**
```
Subject: 🐾 Your Daily Mind Mate Recap - Tuesday

Hi Sarah,

Here's what we noticed today:

🎯 Today's Mood: 6/10 (Improving!)
💬 We chatted about: Work stress and overwhelm
✅ You tried: Deep breathing exercise
🌟 Progress: You're on a 7-day streak!

Yesterday you were feeling stressed, and today you're 
already taking steps to feel better. That's real progress!

Tomorrow's suggestion: Try starting your day with a 
2-minute gratitude practice. It can help set a positive 
tone.

Keep going, Sarah. You're doing great! 🐶

- Buddy

[View Full Dashboard]
```

**Backend:**
- EventBridge triggers `dailyRecap` Lambda at 8 PM
- Aggregates day's data
- Calls Claude to generate personalized recap
- Sends via SES

---

## 🤖 Technical Implementation Details

### **Real-Time Conversation with RAG**

**Yes, we can implement RAG (Retrieval-Augmented Generation):**

```python
# Lambda: chatWithPet (Enhanced with RAG)

def chat_with_pet(user_id, message):
    # 1. Retrieve relevant context from user's history
    relevant_conversations = retrieve_similar_conversations(
        user_id=user_id,
        query=message,
        top_k=3
    )
    
    relevant_moods = get_recent_moods(user_id, days=7)
    
    # 2. Build context for Claude
    context = f"""
    User: {user_profile['name']}
    Pet: {pet_profile['name']} ({pet_profile['personality']})
    
    Recent relevant conversations:
    {format_conversations(relevant_conversations)}
    
    Recent mood trend:
    {format_mood_trend(relevant_moods)}
    
    Current message: {message}
    """
    
    # 3. Call Bedrock Claude with full context
    response = bedrock.invoke_model(
        modelId='anthropic.claude-3-sonnet-20240229',
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "system": get_personality_prompt(pet_profile['personality']),
            "messages": [
                {"role": "user", "content": context}
            ]
        })
    )
    
    return parse_response(response)
```

**For semantic search, we can use:**
- **Option 1**: DynamoDB + Bedrock Embeddings (simple)
- **Option 2**: OpenSearch with vector search (advanced)
- **Option 3**: In-memory similarity using embeddings (fastest for demo)

---

### **Historical Context Examples**

**Scenario 1: User had bad day yesterday**
```
User yesterday: "Work is so stressful, I can't handle it"
User today: "Hey"

Pet response (LLM-generated with context):
"Hi Sarah! I've been thinking about you since yesterday. 
You were dealing with a lot of work stress. How are you 
feeling today? Any better, or still tough?"
```

**Scenario 2: User completed activity yesterday**
```
User yesterday: Completed breathing exercise, felt better
User today: "Feeling anxious again"

Pet response:
"Hey Sarah, I remember the breathing exercise really 
helped you yesterday. Want to try that again? Or would 
you like to try something different today?"
```

**Scenario 3: Positive trend**
```
User: 3 days of improving mood
User today: "Feeling good!"

Pet response:
"Sarah! That's amazing! You've been feeling better for 
3 days now. I'm so proud of you! What's been helping 
the most?"
```

---

## 🎨 UI/UX Design Principles

### **1. Conversation-First**
- Chat interface is primary interaction
- Everything else is secondary
- Feels like texting a friend

### **2. Optional Everything**
- Mood selection: Optional
- Photos: Optional
- Voice: Optional
- Only text is required

### **3. Personality-Driven**
- UI colors match personality
- Animations match personality
- Language matches personality

### **4. Mobile-First**
- Thumb-friendly buttons
- Large touch targets
- Minimal scrolling

### **5. Delightful Micro-interactions**
- Coin animations
- Pet reactions
- Typing indicators
- Celebration effects

---

## ✅ What You Get as a User

### **Immediate Benefits:**
1. **Someone who listens** - Always available, never judges
2. **Remembers everything** - Builds on past conversations
3. **Personalized support** - Adapts to your needs
4. **Actionable help** - Specific things you can do right now
5. **Progress tracking** - See your journey over time

### **Long-term Benefits:**
1. **Early warning** - Catches problems before crisis
2. **Pattern recognition** - Helps you understand triggers
3. **Habit building** - Reinforces healthy coping strategies
4. **Emotional intelligence** - Learn about your own emotions
5. **Professional connection** - Seamless handoff to therapist if needed

---

## 📋 Features Summary

### **Must Have (Phase 1)**
- ✅ Onboarding with personality selection
- ✅ Name collection (user + pet)
- ✅ Real-time chat with LLM
- ✅ Historical context awareness
- ✅ Coping strategy suggestions
- ✅ Coin rewards
- ✅ Basic progress tracking

### **Should Have (Phase 2)**
- ✅ Photo analysis (optional)
- ✅ Voice input (optional)
- ✅ Daily recap emails
- ✅ Conversation history view
- ✅ Mood trend visualization
- ✅ Activity completion tracking

### **Nice to Have (Phase 3)**
- ⏸️ Risk detection alerts
- ⏸️ Professional referral
- ⏸️ QuickSight dashboard
- ⏸️ Social features
- ⏸️ Cognito authentication

---

## ❓ Questions for Approval

1. **RAG Implementation**: Use DynamoDB + embeddings or OpenSearch?
2. **Avatar Generation**: Titan Image or just emoji for demo?
3. **Authentication**: Demo mode (no login) or Cognito from start?
4. **Conversation Storage**: How many days of history to keep in context?
5. **Activity Library**: Should I create a database of activities, or let LLM generate them dynamically?

---

**This is the complete vision. Please review and let me know what to modify before I implement anything!** 🎯
