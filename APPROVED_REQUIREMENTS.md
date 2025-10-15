# ✅ Approved Requirements - Mind Mate

## 🎯 Confirmed Decisions

### **1. Historical Context**
- ✅ Use ALL historical chat, not just yesterday
- ✅ 30 days of conversation history in context
- ✅ Semantic search with OpenSearch for relevant past conversations

### **2. Home Screen Features**
- ✅ Chat with Buddy
- ✅ **NEW: Activities to Do with Buddy** (activity library)
- ✅ View My Progress
- ✅ Settings

### **3. Activity Library**
- ✅ Store in DynamoDB (not Postgres/Vercel)
- ✅ Pre-populated with HeartPet-inspired activities
- ✅ Categories: Breathing, Movement, Mindfulness, Social, Creative
- ✅ Each activity: title, description, duration, steps, category, tags

### **4. Voice Agent**
- ✅ Implement real-time voice conversation
- ✅ Similar to ChatGPT voice function
- ✅ Use Amazon Transcribe (streaming) + Bedrock + Amazon Polly
- ✅ WebSocket for real-time bidirectional communication

### **5. Pet Avatar**
- ✅ Generate with Bedrock Titan Image G1
- ✅ Show pet image on EVERY page (primary UI element)
- ✅ Persistent in header/top of screen
- ✅ Animated reactions based on context

### **6. Authentication**
- ✅ Amazon Cognito required
- ✅ Every user gets unique pet
- ✅ No demo mode - proper user accounts

### **7. Semantic Search**
- ✅ Use OpenSearch (Option 2)
- ✅ Vector embeddings with Bedrock Titan Embeddings
- ✅ Index all conversations for retrieval

### **8. ML Prediction System**
- ✅ Detailed implementation required
- ✅ SageMaker for custom risk prediction model
- ✅ Features: mood trends, sentiment analysis, behavioral patterns
- ✅ Output: Risk score (0-1), early warning triggers

---

## 📋 Detailed Requirements

[See TECHNICAL_SPEC.md for full implementation details]
