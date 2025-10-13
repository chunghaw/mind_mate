# Bedrock Prompt Engineering Guide

## Daily Recap Prompt (Used in dailyRecap Lambda)

```python
prompt = f"""You are Mind Mate, a supportive AI pet companion. 
Given the user's data from {yesterday_str}:
{mood_summary}
{emotion_summary}

Write a warm, encouraging daily recap (max 150 words) that:
- Reflects their emotional trend kindly
- Acknowledges any challenges
- Suggests 2 practical coping strategies
Keep tone friendly and supportive, not clinical."""
```

**Example Output:**
```
Hey there! 🐾 Yesterday was a bit of a mixed bag, wasn't it? I noticed your 
mood averaged around 6/10, with some stress showing through. That's totally 
okay - we all have those days!

Here's what might help today:
1. Try a 5-minute breathing exercise when you feel tension building
2. Take a short walk outside during lunch - even 10 minutes can reset your mood

Remember, you're doing great just by checking in with yourself. Keep it up! 💙
```

## Risk Prevention Prompt (Used in riskScan Lambda)

```python
prompt = f"""You are Mind Mate, a caring AI companion. The user has shown concerning patterns:
- 7-day average mood: {avg_mood:.1f}/10
- Trend: {risk_reason}

Write a gentle, supportive message (max 200 words) that:
- Acknowledges they might be going through a tough time
- Encourages them without being pushy
- Suggests 2-3 evidence-based self-care actions
- Reminds them professional help is available if needed
Keep tone warm, non-judgmental, and hopeful."""
```

**Example Output:**
```
Hi friend 🐾

I've noticed your mood has been lower than usual this week (averaging 3.8/10). 
I want you to know that it's okay to not be okay, and I'm here with you.

When things feel heavy, these small steps can help:
• Reach out to someone you trust - even a quick text counts
• Try the 5-4-3-2-1 grounding technique when anxiety hits
• Set one tiny goal for today (like making your bed or drinking water)

If these feelings persist, please consider talking to a mental health 
professional. There's no shame in asking for help - it's actually one of the 
bravest things you can do.

You're not alone in this. 💙

Resources:
- Crisis Text Line: Text HOME to 741741
- National Suicide Prevention Lifeline: 988
```

## Avatar Generation Prompt (Used in generateAvatar Lambda)

```python
prompt = f"A cute cartoon-style AI pet avatar: {pet_description}. Friendly, warm, approachable style. Digital art."
```

**Tips for Better Avatars:**
- Be specific: "fluffy orange tabby cat with green eyes"
- Add personality: "playful", "wise", "energetic"
- Specify style: "cartoon", "watercolor", "pixel art"

## Coping Strategy Prompt (Optional Enhancement)

```python
prompt = f"""Based on the user's current mood ({mood}/10) and context ({scene_labels}), 
suggest ONE specific, actionable micro-habit they can do right now (in under 5 minutes).

Format: Just the suggestion, no preamble.
Examples:
- "Take 3 deep breaths, counting to 4 on each inhale and exhale"
- "Stand up and stretch your arms above your head for 30 seconds"
- "Write down one thing you're grateful for today"
"""
```

## Prompt Best Practices

### 1. Be Specific
❌ "Write something supportive"
✅ "Write a warm, encouraging message (max 150 words) that acknowledges challenges and suggests 2 coping strategies"

### 2. Set Constraints
- Word/token limits
- Tone requirements
- Format specifications

### 3. Provide Context
- User's mood data
- Detected emotions
- Time period
- Trends

### 4. Use Examples
Show the model what good output looks like (few-shot prompting)

### 5. Iterate
Test prompts with different inputs and refine based on outputs

## Model Selection

**Claude 3 Haiku** (Recommended for Mind Mate)
- Fast and cheap
- Great for empathetic text
- Good at following instructions
- Cost: ~$0.25 per 1M input tokens

**Claude 3 Sonnet** (If you need better quality)
- More nuanced responses
- Better at complex reasoning
- Cost: ~$3 per 1M input tokens

**Amazon Nova** (Alternative)
- AWS-native model
- Similar capabilities to Claude
- May have better latency

## Testing Prompts

```bash
# Test directly via AWS CLI
aws bedrock-runtime invoke-model \
  --model-id anthropic.claude-3-haiku-20240307-v1:0 \
  --body '{"anthropic_version":"bedrock-2023-05-31","max_tokens":300,"messages":[{"role":"user","content":"You are Mind Mate..."}]}' \
  --cli-binary-format raw-in-base64-out \
  output.json

cat output.json | jq -r '.content[0].text'
```

## Safety Considerations

### Use Bedrock Guardrails
- Filter harmful content
- Redact PII
- Block inappropriate topics

### Fallback Messages
Always have a default message if Bedrock fails:

```python
try:
    response = bedrock.invoke_model(...)
except Exception as e:
    recap_text = "Keep going! Try a 2-min breathing break and a 10-min walk."
```

### Avoid Medical Advice
- Never diagnose conditions
- Don't prescribe treatments
- Always suggest professional help for serious concerns

## Token Optimization

**Reduce costs by:**
1. Keeping prompts concise
2. Using shorter max_tokens
3. Caching system prompts (if available)
4. Batching requests when possible

**Example Cost Calculation:**
- Daily recap: ~200 input + 150 output tokens = 350 tokens
- Cost per recap: ~$0.0001
- Monthly (30 recaps): ~$0.003
