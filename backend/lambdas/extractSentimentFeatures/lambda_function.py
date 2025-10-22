import json
import os
from datetime import datetime, timedelta
from decimal import Decimal
import boto3

dynamodb = boto3.resource('dynamodb')
comprehend = boto3.client('comprehend', region_name='us-east-1')
table = dynamodb.Table(os.environ.get('TABLE_NAME', 'EmoCompanion'))

def decimal_to_float(obj):
    """Convert DynamoDB Decimal to float"""
    if isinstance(obj, Decimal):
        return float(obj)
    return obj

def get_user_messages(user_id, days=30):
    """Query DynamoDB for user's mood log messages and chat messages"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        messages = []
        
        # Query mood entries with notes
        mood_response = table.query(
            KeyConditionExpression='PK = :pk AND SK BETWEEN :start AND :end',
            ExpressionAttributeValues={
                ':pk': f'USER#{user_id}',
                ':start': f'MOOD#{start_date.isoformat()}',
                ':end': f'MOOD#{end_date.isoformat()}Z'
            }
        )
        
        for item in mood_response.get('Items', []):
            if item.get('type') == 'MOOD' and item.get('notes'):
                messages.append({
                    'text': item.get('notes', ''),
                    'timestamp': item.get('ts'),
                    'mood': decimal_to_float(item.get('mood', 5))
                })
        
        # Query chat messages (user messages only, not AI responses)
        chat_response = table.query(
            KeyConditionExpression='PK = :pk AND begins_with(SK, :chat_prefix)',
            ExpressionAttributeValues={
                ':pk': f'USER#{user_id}',
                ':chat_prefix': 'CHAT#'
            }
        )
        
        for item in chat_response.get('Items', []):
            if item.get('type') == 'CHAT' and item.get('userMessage'):
                # Filter by date after retrieval
                item_timestamp = item.get('timestamp', item.get('ts', ''))
                try:
                    item_date = datetime.fromisoformat(item_timestamp.replace('Z', '+00:00'))
                    if item_date >= start_date:
                        messages.append({
                            'text': item.get('userMessage', ''),
                            'timestamp': item_timestamp,
                            'mood': decimal_to_float(item.get('wellnessScore', 5))  # Use wellness score as mood proxy
                        })
                except Exception as e:
                    print(f"Error parsing timestamp {item_timestamp}: {e}")
                    # Include anyway if timestamp parsing fails
                    messages.append({
                        'text': item.get('userMessage', ''),
                        'timestamp': item_timestamp,
                        'mood': 5
                    })
        
        # Sort by timestamp
        messages.sort(key=lambda x: x['timestamp'])
        return messages
        
    except Exception as e:
        print(f"Error querying messages: {e}")
        return []

def analyze_sentiment_batch(messages):
    """Analyze sentiment using AWS Comprehend in batches"""
    if not messages:
        return []
    
    sentiments = []
    
    try:
        # Comprehend has a limit of 25 documents per batch
        batch_size = 25
        
        for i in range(0, len(messages), batch_size):
            batch = messages[i:i + batch_size]
            texts = [m['text'][:5000] for m in batch]  # Comprehend max 5000 bytes per doc
            
            try:
                # Batch sentiment detection
                response = comprehend.batch_detect_sentiment(
                    TextList=texts,
                    LanguageCode='en'
                )
                
                # Process results
                for j, result in enumerate(response.get('ResultList', [])):
                    sentiments.append({
                        'sentiment': result.get('Sentiment'),
                        'scores': {
                            'Positive': result.get('SentimentScore', {}).get('Positive', 0),
                            'Negative': result.get('SentimentScore', {}).get('Negative', 0),
                            'Neutral': result.get('SentimentScore', {}).get('Neutral', 0),
                            'Mixed': result.get('SentimentScore', {}).get('Mixed', 0)
                        },
                        'timestamp': batch[j]['timestamp'],
                        'mood': batch[j]['mood']
                    })
                
                # Handle errors in batch
                for error in response.get('ErrorList', []):
                    print(f"Comprehend error for index {error.get('Index')}: {error.get('ErrorMessage')}")
                    # Add default sentiment for failed items
                    if error.get('Index') < len(batch):
                        sentiments.append({
                            'sentiment': 'NEUTRAL',
                            'scores': {'Positive': 0.25, 'Negative': 0.25, 'Neutral': 0.5, 'Mixed': 0},
                            'timestamp': batch[error.get('Index')]['timestamp'],
                            'mood': batch[error.get('Index')]['mood']
                        })
                        
            except Exception as e:
                print(f"Error in batch sentiment analysis: {e}")
                # Add default sentiments for entire batch on error
                for msg in batch:
                    sentiments.append({
                        'sentiment': 'NEUTRAL',
                        'scores': {'Positive': 0.25, 'Negative': 0.25, 'Neutral': 0.5, 'Mixed': 0},
                        'timestamp': msg['timestamp'],
                        'mood': msg['mood']
                    })
        
        return sentiments
        
    except Exception as e:
        print(f"Error in sentiment analysis: {e}")
        return []

def calculate_sentiment_trend(sentiments):
    """Calculate trend in sentiment scores over time"""
    if len(sentiments) < 2:
        return 0.0
    
    try:
        # Use negative sentiment scores for trend
        negative_scores = [s['scores']['Negative'] for s in sentiments]
        
        n = len(negative_scores)
        if n < 2:
            slope = 0.0
        else:
            x_vals = list(range(n))
            x_mean = sum(x_vals) / n
            y_mean = sum(negative_scores) / n
            
            numerator = sum((x_vals[i] - x_mean) * (negative_scores[i] - y_mean) for i in range(n))
            denominator = sum((x_vals[i] - x_mean) ** 2 for i in range(n))
            
            slope = numerator / denominator if denominator != 0 else 0.0
        
        return slope
    except Exception as e:
        print(f"Error calculating sentiment trend: {e}")
        return 0.0

def calculate_sentiment_volatility(sentiments):
    """Calculate volatility in sentiment scores"""
    if len(sentiments) < 2:
        return 0.0
    
    try:
        negative_scores = [s['scores']['Negative'] for s in sentiments]
        daily_changes = [abs(negative_scores[i] - negative_scores[i-1]) 
                        for i in range(1, len(negative_scores))]
        return float(sum(daily_changes) / len(daily_changes)) if daily_changes else 0.0
    except Exception as e:
        print(f"Error calculating sentiment volatility: {e}")
        return 0.0

def count_despair_keywords(messages):
    """Count despair-related keywords"""
    despair_keywords = [
        'hopeless', 'pointless', 'worthless', 'useless', 'give up',
        'no point', 'why bother', 'nothing matters', 'end it',
        'can\'t go on', 'no future', 'no hope', 'meaningless'
    ]
    
    try:
        count = 0
        for msg in messages:
            text = msg['text'].lower()
            count += sum(1 for keyword in despair_keywords if keyword in text)
        
        return count
    except Exception as e:
        print(f"Error counting despair keywords: {e}")
        return 0

def count_isolation_keywords(messages):
    """Count isolation-related keywords"""
    isolation_keywords = [
        'alone', 'lonely', 'isolated', 'no one', 'nobody',
        'by myself', 'no friends', 'abandoned', 'left out',
        'disconnected', 'withdrawn', 'solitary'
    ]
    
    try:
        count = 0
        for msg in messages:
            text = msg['text'].lower()
            count += sum(1 for keyword in isolation_keywords if keyword in text)
        
        return count
    except Exception as e:
        print(f"Error counting isolation keywords: {e}")
        return 0

def calculate_hopelessness_score(messages, sentiments):
    """Calculate hopelessness score based on sentiment and keywords"""
    if not messages or not sentiments:
        return 0.0
    
    try:
        # Combine negative sentiment with despair keywords
        negative_scores = [s['scores']['Negative'] for s in sentiments]
        avg_negative = sum(negative_scores) / len(negative_scores) if negative_scores else 0.0
        despair_count = count_despair_keywords(messages)
        
        # Normalize despair count (0-1 scale, max 5 keywords)
        despair_normalized = min(despair_count / 5.0, 1.0)
        
        # Weighted combination
        hopelessness = (0.6 * avg_negative) + (0.4 * despair_normalized)
        
        return float(hopelessness)
    except Exception as e:
        print(f"Error calculating hopelessness score: {e}")
        return 0.0

def detect_crisis_keywords(messages):
    """Detect critical crisis keywords"""
    crisis_keywords = [
        'suicide', 'suicidal', 'kill myself', 'end my life', 'want to die',
        'better off dead', 'self harm', 'hurt myself', 'cut myself'
    ]
    
    try:
        crisis_count = 0
        for msg in messages:
            text = msg['text'].lower()
            if any(keyword in text for keyword in crisis_keywords):
                crisis_count += 1
        
        return crisis_count
    except Exception as e:
        print(f"Error detecting crisis keywords: {e}")
        return 0

def extract_sentiment_features(user_id, days=30):
    """Extract all sentiment-related features"""
    messages = get_user_messages(user_id, days)
    
    if not messages:
        # Return default features if no data
        return {
            'sentiment_trend_7day': 0.0,
            'sentiment_trend_30day': 0.0,
            'negative_sentiment_frequency': 0.0,
            'positive_sentiment_frequency': 0.0,
            'neutral_sentiment_frequency': 0.0,
            'mixed_sentiment_frequency': 0.0,
            'avg_negative_score': 0.0,
            'avg_positive_score': 0.0,
            'avg_neutral_score': 0.0,
            'sentiment_volatility': 0.0,
            'despair_keywords': 0,
            'isolation_keywords': 0,
            'hopelessness_score': 0.0,
            'crisis_keywords': 0,
            'total_messages_analyzed': 0
        }
    
    # Analyze sentiment using Comprehend
    sentiments = analyze_sentiment_batch(messages)
    
    if not sentiments:
        # Fallback if Comprehend fails
        return {
            'sentiment_trend_7day': 0.0,
            'sentiment_trend_30day': 0.0,
            'negative_sentiment_frequency': 0.0,
            'positive_sentiment_frequency': 0.0,
            'neutral_sentiment_frequency': 0.0,
            'mixed_sentiment_frequency': 0.0,
            'avg_negative_score': 0.0,
            'avg_positive_score': 0.0,
            'avg_neutral_score': 0.0,
            'sentiment_volatility': 0.0,
            'despair_keywords': count_despair_keywords(messages),
            'isolation_keywords': count_isolation_keywords(messages),
            'hopelessness_score': 0.0,
            'crisis_keywords': detect_crisis_keywords(messages),
            'total_messages_analyzed': len(messages)
        }
    
    # Get recent sentiments for 7-day trend
    sentiments_7day = sentiments[-7:] if len(sentiments) >= 7 else sentiments
    
    # Calculate sentiment frequencies
    total = len(sentiments)
    negative_count = len([s for s in sentiments if s['sentiment'] == 'NEGATIVE'])
    positive_count = len([s for s in sentiments if s['sentiment'] == 'POSITIVE'])
    neutral_count = len([s for s in sentiments if s['sentiment'] == 'NEUTRAL'])
    mixed_count = len([s for s in sentiments if s['sentiment'] == 'MIXED'])
    
    features = {
        # Sentiment trends
        'sentiment_trend_7day': calculate_sentiment_trend(sentiments_7day),
        'sentiment_trend_30day': calculate_sentiment_trend(sentiments),
        
        # Sentiment frequencies
        'negative_sentiment_frequency': negative_count / total,
        'positive_sentiment_frequency': positive_count / total,
        'neutral_sentiment_frequency': neutral_count / total,
        'mixed_sentiment_frequency': mixed_count / total,
        
        # Sentiment scores
        'avg_negative_score': float(sum(s['scores']['Negative'] for s in sentiments) / len(sentiments)) if sentiments else 0.0,
        'avg_positive_score': float(sum(s['scores']['Positive'] for s in sentiments) / len(sentiments)) if sentiments else 0.0,
        'avg_neutral_score': float(sum(s['scores']['Neutral'] for s in sentiments) / len(sentiments)) if sentiments else 0.0,
        
        # Volatility
        'sentiment_volatility': calculate_sentiment_volatility(sentiments),
        
        # Crisis indicators
        'despair_keywords': count_despair_keywords(messages),
        'isolation_keywords': count_isolation_keywords(messages),
        'hopelessness_score': calculate_hopelessness_score(messages, sentiments),
        'crisis_keywords': detect_crisis_keywords(messages),
        
        # Metadata
        'total_messages_analyzed': len(messages)
    }
    
    return features

def lambda_handler(event, context):
    """Lambda handler for sentiment feature extraction"""
    try:
        # Parse input
        user_id = event.get('userId')
        days = event.get('days', 30)
        
        if not user_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'userId is required'})
            }
        
        # Extract features
        features = extract_sentiment_features(user_id, days)
        
        return {
            'statusCode': 200,
            'body': json.dumps(features)
        }
        
    except Exception as e:
        print(f"Error in lambda_handler: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'Failed to extract sentiment features'
            })
        }
