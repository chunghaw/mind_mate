import json
import os
import boto3
from datetime import datetime

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

def lambda_handler(event, context):
    """
    Use Bedrock to analyze emotions and mental health indicators in user messages
    """
    try:
        # Parse request
        body = json.loads(event.get('body', '{}')) if isinstance(event.get('body'), str) else event
        
        user_message = body.get('message', '')
        user_id = body.get('userId', 'anonymous')
        
        if not user_message:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST'
                },
                'body': json.dumps({'error': 'message is required'})
            }
        
        # Bedrock prompt for emotion analysis
        system_prompt = """You are an expert mental health AI that analyzes text for emotional indicators and mental health signals.

Analyze the user's message and return a JSON response with:
1. Primary emotion (sad, anxious, hopeless, angry, neutral, happy, etc.)
2. Sentiment (negative, neutral, positive) 
3. Risk indicators (crisis_language, isolation, hopelessness, etc.)
4. Confidence score (0-100)
5. Brief explanation

CRITICAL: Pay attention to context. "not feeling good" is NEGATIVE, not positive.

Example response format:
{
  "primary_emotion": "sad",
  "sentiment": "negative", 
  "risk_indicators": ["low_mood", "distress"],
  "confidence": 85,
  "explanation": "User expresses negative feelings and low mood"
}

Be accurate and contextually aware. Focus on mental health indicators."""

        # Call Bedrock Claude
        bedrock_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 300,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": f"Analyze this message for emotions and mental health indicators: '{user_message}'"
                }
            ],
            "temperature": 0.3  # Lower temperature for more consistent analysis
        }
        
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            body=json.dumps(bedrock_body)
        )
        
        response_body = json.loads(response['body'].read())
        ai_response = response_body['content'][0]['text']
        
        # Parse JSON response from Claude
        try:
            # Extract JSON from response (Claude sometimes adds extra text)
            import re
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                emotion_data = json.loads(json_match.group())
            else:
                # Fallback if JSON parsing fails
                emotion_data = {
                    "primary_emotion": "unknown",
                    "sentiment": "neutral",
                    "risk_indicators": [],
                    "confidence": 50,
                    "explanation": "Could not parse emotion analysis"
                }
        except:
            # Fallback parsing
            emotion_data = {
                "primary_emotion": "unknown", 
                "sentiment": "neutral",
                "risk_indicators": [],
                "confidence": 50,
                "explanation": "Error parsing emotion analysis"
            }
        
        # Convert to ML Analysis format for frontend
        insights = []
        risk_score = 20  # Base risk
        
        # Add primary emotion insight
        emotion_emoji = {
            'sad': '😢', 'anxious': '😰', 'hopeless': '😞', 'angry': '😠',
            'happy': '😊', 'neutral': '😐', 'worried': '😟', 'stressed': '😤',
            'depressed': '😔', 'lonely': '😞', 'overwhelmed': '😵'
        }
        
        emoji = emotion_emoji.get(emotion_data.get('primary_emotion', 'neutral'), '🧠')
        insights.append(f"{emoji} Primary emotion: {emotion_data.get('primary_emotion', 'unknown')}")
        
        # Add sentiment analysis
        sentiment = emotion_data.get('sentiment', 'neutral')
        if sentiment == 'negative':
            insights.append(f"📉 Negative sentiment detected (Bedrock AI)")
            risk_score += 25
        elif sentiment == 'positive':
            insights.append(f"📈 Positive sentiment detected (Bedrock AI)")
            risk_score = max(10, risk_score - 15)
        
        # Add risk indicators
        risk_indicators = emotion_data.get('risk_indicators', [])
        for indicator in risk_indicators:
            if indicator == 'crisis_language':
                insights.append(f"🚨 Crisis language detected")
                risk_score += 40
            elif indicator == 'hopelessness':
                insights.append(f"😞 Hopelessness indicators found")
                risk_score += 30
            elif indicator == 'isolation':
                insights.append(f"🏠 Social isolation signals")
                risk_score += 20
            elif indicator == 'low_mood':
                insights.append(f"📉 Low mood indicators")
                risk_score += 15
            elif indicator == 'anxiety':
                insights.append(f"😰 Anxiety markers detected")
                risk_score += 15
            elif indicator == 'distress':
                insights.append(f"😣 Emotional distress signals")
                risk_score += 10
        
        # Add explanation if available
        explanation = emotion_data.get('explanation', '')
        if explanation and len(explanation) < 100:
            insights.append(f"💭 {explanation}")
        
        confidence = emotion_data.get('confidence', 85)
        risk_score = min(95, max(5, risk_score))
        
        print(f"✅ Emotion analysis complete for user {user_id}: {emotion_data.get('primary_emotion')} ({sentiment})")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({
                'insights': insights,
                'riskScore': risk_score,
                'confidence': confidence,
                'emotionData': emotion_data,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })
        }
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({
                'error': str(e),
                'insights': ['Error analyzing emotions'],
                'riskScore': 20,
                'confidence': 0
            })
        }