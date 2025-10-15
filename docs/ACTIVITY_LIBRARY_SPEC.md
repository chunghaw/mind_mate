# Activity Library - Technical Specification

## 📚 Overview

Activities are pre-defined micro-actions (30 seconds to 5 minutes) that users can do with their pet companion. Inspired by HeartPet's action system.

## 🗄️ DynamoDB Schema

### **Activities Table**

**Table Name**: `EmoCompanion` (same table, different SK pattern)

**Item Structure**:
```json
{
  "PK": "ACTIVITY",
  "SK": "ACT#breathing_001",
  "activityId": "breathing_001",
  "title": "5-4-3-2-1 Grounding",
  "description": "A quick grounding exercise to calm anxiety",
  "category": "breathing",
  "duration": 180,
  "steps": [
    "Find 5 things you can see",
    "Find 4 things you can touch",
    "Find 3 things you can hear",
    "Find 2 things you can smell",
    "Find 1 thing you can taste"
  ],
  "tags": ["anxiety", "grounding", "quick", "indoor"],
  "why": "Grounding techniques help anchor you in the present moment when anxiety feels overwhelming",
  "embedding": [0.123, -0.456, ...],
  "effectiveness": 4.5,
  "completionCount": 0
}
```

### **User Activity Completion**

**Item Structure**:
```json
{
  "PK": "USER#user123",
  "SK": "COMPLETION#2025-01-15T10:30:00Z",
  "activityId": "breathing_001",
  "completed": true,
  "duration": 180,
  "helpful": true,
  "userFeedback": "Really helped calm me down",
  "coinsEarned": 20,
  "ts": "2025-01-15T10:30:00Z"
}
```

## 📋 Activity Categories & Examples

### **1. Breathing (10 activities)**
- Box Breathing (4-4-4-4)
- 5-4-3-2-1 Grounding
- Deep Belly Breathing
- 4-7-8 Relaxation Breath
- Alternate Nostril Breathing

### **2. Movement (10 activities)**
- 2-Minute Walk
- Desk Stretches
- Shoulder Rolls
- Neck Stretches
- Standing Meditation

### **3. Mindfulness (10 activities)**
- Body Scan (2 min)
- Gratitude Practice
- Present Moment Awareness
- Loving-Kindness Meditation
- Mindful Observation

### **4. Social (8 activities)**
- Text a Friend
- Share a Compliment
- Call Someone You Love
- Join Online Community
- Express Gratitude to Someone

### **5. Creative (8 activities)**
- Doodle for 2 Minutes
- Write 3 Sentences
- Hum a Favorite Song
- Take a Creative Photo
- Free-Form Journaling

### **6. Reset (8 activities)**
- Splash Cold Water on Face
- Drink a Glass of Water
- Step Outside
- Change Your Environment
- Listen to Uplifting Music

**Total: ~54 activities**

## 🔍 Semantic Search with OpenSearch

### **Architecture**:
```
User Message
    ↓
Bedrock Titan Embeddings (generate query vector)
    ↓
OpenSearch Vector Search (find similar activities)
    ↓
Top 5 relevant activities
    ↓
Claude filters based on:
  - User's current mood
  - Recent activity history
  - Time of day
  - User preferences
    ↓
Best 2-3 activities recommended
```

### **Implementation**:
```python
# Lambda: recommendActivity

import boto3
from opensearchpy import OpenSearch

bedrock = boto3.client('bedrock-runtime')
opensearch = OpenSearch(
    hosts=[{'host': os.environ['OPENSEARCH_ENDPOINT'], 'port': 443}],
    http_auth=(os.environ['OPENSEARCH_USER'], os.environ['OPENSEARCH_PASS']),
    use_ssl=True
)

def recommend_activity(user_id, user_message, mood, context):
    # 1. Generate embedding for user's message
    embedding_response = bedrock.invoke_model(
        modelId='amazon.titan-embed-text-v1',
        body=json.dumps({"inputText": user_message})
    )
    query_embedding = json.loads(embedding_response['body'].read())['embedding']
    
    # 2. Search OpenSearch for similar activities
    search_query = {
        "size": 10,
        "query": {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                    "params": {"query_vector": query_embedding}
                }
            }
        }
    }
    
    results = opensearch.search(index="activities", body=search_query)
    candidate_activities = [hit['_source'] for hit in results['hits']['hits']]
    
    # 3. Get user's activity history
    history = get_user_activity_history(user_id, days=7)
    
    # 4. Use Claude to filter and rank activities
    filter_prompt = f"""
    User: {context['userName']}
    Current mood: {mood}
    Message: "{user_message}"
    
    Recent activities completed:
    {format_history(history)}
    
    Candidate activities:
    {json.dumps(candidate_activities, indent=2)}
    
    Select the 2-3 BEST activities for this user right now.
    Consider:
    - Current emotional state
    - What they haven't tried recently
    - Time of day
    - Difficulty level
    
    Return JSON array of activity IDs in priority order.
    """
    
    # Call Claude for intelligent filtering
    filtered = call_claude(filter_prompt)
    
    return filtered['activities']
```

## 📊 Activity Effectiveness Tracking

### **Learning System**:
```python
# After user completes activity
def track_effectiveness(user_id, activity_id, helpful, mood_before, mood_after):
    # Store completion
    table.put_item(Item={
        'PK': f'USER#{user_id}',
        'SK': f'COMPLETION#{timestamp}',
        'activityId': activity_id,
        'helpful': helpful,
        'moodBefore': mood_before,
        'moodAfter': mood_after,
        'improvement': mood_after - mood_before
    })
    
    # Update activity effectiveness score
    table.update_item(
        Key={'PK': 'ACTIVITY', 'SK': f'ACT#{activity_id}'},
        UpdateExpression='ADD completionCount :inc, totalHelpful :helpful',
        ExpressionAttributeValues={
            ':inc': 1,
            ':helpful': 1 if helpful else 0
        }
    )
    
    # Update user's category preferences
    activity = get_activity(activity_id)
    if helpful:
        table.update_item(
            Key={'PK': f'USER#{user_id}', 'SK': 'PREFERENCES'},
            UpdateExpression='ADD #cat :weight',
            ExpressionAttributeNames={'#cat': activity['category']},
            ExpressionAttributeValues={':weight': 0.1}
        )
```

## 🔄 Activity Recommendation Flow

```
User sends message: "I'm feeling anxious"
    ↓
1. Generate embedding of message
    ↓
2. OpenSearch finds 10 similar activities
    ↓
3. Get user's last 7 days of completions
    ↓
4. Claude filters based on:
   - Current mood (anxious)
   - Haven't done recently
   - User's category preferences
   - Time available
    ↓
5. Return top 2-3 activities
    ↓
6. Present to user with pet's encouragement
```

## 📝 Sample Activities (HeartPet-Inspired)

### **Breathing Category**
```json
{
  "activityId": "breathing_001",
  "title": "Box Breathing",
  "description": "A calming 4-4-4-4 breathing pattern",
  "category": "breathing",
  "duration": 120,
  "steps": [
    "Breathe in slowly for 4 counts",
    "Hold your breath for 4 counts",
    "Breathe out slowly for 4 counts",
    "Hold empty for 4 counts",
    "Repeat 4 times"
  ],
  "tags": ["anxiety", "stress", "quick", "indoor", "anywhere"],
  "why": "Box breathing activates your parasympathetic nervous system, helping you feel calmer",
  "difficulty": "easy"
}
```

### **Movement Category**
```json
{
  "activityId": "movement_001",
  "title": "2-Minute Walk",
  "description": "A quick walk to reset your mind",
  "category": "movement",
  "duration": 120,
  "steps": [
    "Stand up from where you are",
    "Walk slowly for 1 minute in any direction",
    "Notice your surroundings as you walk",
    "Turn around and walk back",
    "Take a deep breath when you return"
  ],
  "tags": ["stress", "energy", "outdoor", "movement"],
  "why": "Movement releases endorphins and helps clear mental fog",
  "difficulty": "easy"
}
```

## 🎯 Next Steps

1. Create seed data script with 54 activities
2. Generate embeddings for each activity
3. Set up OpenSearch cluster
4. Index activities with embeddings
5. Implement recommendation Lambda

---

**Status**: Requirements documented ✅
**Next**: Create detailed technical specs for each component
EOF
