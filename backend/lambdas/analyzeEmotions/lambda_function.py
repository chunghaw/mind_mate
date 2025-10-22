import json
import os
import boto3
from datetime import datetime

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

def lambda_handler(event, context):
    """
    Use Bedrock to analyze emotions and mental health indicators in user messages
    """
    # CRITICAL: Handle OPTIONS first before any other processing
    request_method = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method')
    if request_method == 'OPTIONS' or not event.get('body'):
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({})
        }
    
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
        
        # Enhanced ML Analysis format for frontend
        insights = []
        risk_score = 20  # Base risk
        
        # Enhanced emotion mapping with more nuanced analysis
        emotion_emoji = {
            'sad': '😢', 'anxious': '😰', 'hopeless': '😞', 'angry': '😠',
            'happy': '😊', 'neutral': '😐', 'worried': '😟', 'stressed': '😤',
            'depressed': '😔', 'lonely': '😞', 'overwhelmed': '😵', 'frustrated': '😤',
            'scared': '😨', 'confused': '😕', 'excited': '🤩', 'grateful': '🙏',
            'tired': '😴', 'numb': '😶', 'empty': '😶‍🌫️'
        }
        
        primary_emotion = emotion_data.get('primary_emotion', 'neutral')
        emoji = emotion_emoji.get(primary_emotion, '🧠')
        
        # More sophisticated emotion analysis
        if primary_emotion in ['hopeless', 'depressed', 'empty', 'numb']:
            insights.append(f"{emoji} Severe emotional distress: {primary_emotion}")
            risk_score += 35
        elif primary_emotion in ['sad', 'lonely', 'overwhelmed']:
            insights.append(f"{emoji} Concerning emotional state: {primary_emotion}")
            risk_score += 25
        elif primary_emotion in ['anxious', 'worried', 'stressed', 'scared']:
            insights.append(f"{emoji} Elevated anxiety/stress: {primary_emotion}")
            risk_score += 20
        elif primary_emotion in ['angry', 'frustrated']:
            insights.append(f"{emoji} Emotional dysregulation: {primary_emotion}")
            risk_score += 15
        elif primary_emotion in ['happy', 'excited', 'grateful']:
            insights.append(f"{emoji} Positive emotional state: {primary_emotion}")
            risk_score = max(5, risk_score - 20)
        else:
            insights.append(f"{emoji} Emotional state: {primary_emotion}")
        
        # Enhanced sentiment analysis with context
        sentiment = emotion_data.get('sentiment', 'neutral')
        if sentiment == 'negative':
            insights.append(f"📉 Negative sentiment pattern (AI confidence: {emotion_data.get('confidence', 85)}%)")
            risk_score += 25
        elif sentiment == 'positive':
            insights.append(f"📈 Positive sentiment pattern (AI confidence: {emotion_data.get('confidence', 85)}%)")
            risk_score = max(10, risk_score - 15)
        else:
            insights.append(f"😐 Neutral sentiment baseline")
        
        # Enhanced risk indicator processing
        risk_indicators = emotion_data.get('risk_indicators', [])
        critical_indicators = ['crisis_language', 'suicidal_ideation', 'self_harm']
        high_risk_indicators = ['hopelessness', 'severe_depression', 'panic']
        moderate_risk_indicators = ['isolation', 'low_mood', 'anxiety', 'distress']
        
        for indicator in risk_indicators:
            if indicator in critical_indicators:
                insights.append(f"🚨 CRITICAL: {indicator.replace('_', ' ').title()} detected")
                risk_score += 50
            elif indicator in high_risk_indicators:
                insights.append(f"⚠️ HIGH RISK: {indicator.replace('_', ' ').title()} indicators")
                risk_score += 30
            elif indicator in moderate_risk_indicators:
                insights.append(f"📊 {indicator.replace('_', ' ').title()} patterns detected")
                risk_score += 15
            else:
                # Generic risk indicator
                insights.append(f"🔍 {indicator.replace('_', ' ').title()} noted")
                risk_score += 10
        
        # Add contextual explanation with length limit
        explanation = emotion_data.get('explanation', '')
        if explanation and len(explanation) < 120:
            # Clean up explanation
            clean_explanation = explanation.replace('User expresses', 'Detected:').replace('user', 'individual')
            insights.append(f"💭 {clean_explanation}")
        
        # Enhanced confidence calculation
        base_confidence = emotion_data.get('confidence', 85)
        # Adjust confidence based on analysis complexity
        if len(risk_indicators) > 2:
            confidence = min(95, base_confidence + 5)  # More indicators = higher confidence
        elif len(risk_indicators) == 0 and primary_emotion == 'neutral':
            confidence = max(60, base_confidence - 10)  # Less clear signals = lower confidence
        else:
            confidence = base_confidence
        
        # Cap risk score appropriately
        risk_score = min(95, max(5, risk_score))
        
        # Add ML method indicator
        if len(insights) < 4:  # Ensure we have enough insights
            insights.append(f"🤖 Analysis method: Bedrock AI + Pattern Recognition")
        
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