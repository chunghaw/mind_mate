import json
import os
from datetime import datetime, timedelta
from decimal import Decimal
import boto3
import numpy as np

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('TABLE_NAME', 'EmoCompanion'))

def decimal_to_float(obj):
    """Convert DynamoDB Decimal to float"""
    if isinstance(obj, Decimal):
        return float(obj)
    return obj

def get_user_interactions(user_id, days=30):
    """Query DynamoDB for user's mood logs and selfies as interactions"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query mood entries (primary interaction type)
        response = table.query(
            KeyConditionExpression='PK = :pk AND SK BETWEEN :start AND :end',
            ExpressionAttributeValues={
                ':pk': f'USER#{user_id}',
                ':start': f'MOOD#{start_date.isoformat()}',
                ':end': f'MOOD#{end_date.isoformat()}Z'
            }
        )
        
        interactions = []
        for item in response.get('Items', []):
            if item.get('type') == 'MOOD':
                interactions.append({
                    'type': 'mood_log',
                    'timestamp': item.get('ts'),
                    'mood': decimal_to_float(item.get('mood', 5)),
                    'notes': item.get('notes', ''),
                    'tags': item.get('tags', [])
                })
        
        # Query selfie entries
        selfie_response = table.query(
            KeyConditionExpression='PK = :pk AND SK BETWEEN :start AND :end',
            ExpressionAttributeValues={
                ':pk': f'USER#{user_id}',
                ':start': f'SELFIE#{start_date.isoformat()}',
                ':end': f'SELFIE#{end_date.isoformat()}Z'
            }
        )
        
        for item in selfie_response.get('Items', []):
            if item.get('type') == 'SELFIE':
                interactions.append({
                    'type': 'selfie',
                    'timestamp': item.get('ts'),
                    'emotions': item.get('emotions', {})
                })
        
        # Sort by timestamp
        interactions.sort(key=lambda x: x['timestamp'])
        return interactions
        
    except Exception as e:
        print(f"Error querying interactions: {e}")
        return []

def calculate_engagement_trend(interactions):
    """Calculate trend in engagement over time"""
    if len(interactions) < 7:
        return 0.0
    
    try:
        # Group by day and count interactions per day
        daily_counts = {}
        for interaction in interactions:
            try:
                dt = datetime.fromisoformat(interaction['timestamp'].replace('Z', '+00:00'))
                date_key = dt.date().isoformat()
                daily_counts[date_key] = daily_counts.get(date_key, 0) + 1
            except:
                continue
        
        if len(daily_counts) < 2:
            return 0.0
        
        # Calculate trend
        dates = sorted(daily_counts.keys())
        counts = [daily_counts[d] for d in dates]
        
        x = np.arange(len(counts))
        y = np.array(counts)
        
        coefficients = np.polyfit(x, y, 1)
        slope = float(coefficients[0])
        
        return slope
    except Exception as e:
        print(f"Error calculating engagement trend: {e}")
        return 0.0

def calculate_response_time_trend(interactions):
    """Calculate trend in time between interactions"""
    if len(interactions) < 3:
        return 0.0
    
    try:
        response_times = []
        for i in range(1, len(interactions)):
            try:
                t1 = datetime.fromisoformat(interactions[i-1]['timestamp'].replace('Z', '+00:00'))
                t2 = datetime.fromisoformat(interactions[i]['timestamp'].replace('Z', '+00:00'))
                hours_between = (t2 - t1).total_seconds() / 3600
                response_times.append(hours_between)
            except:
                continue
        
        if len(response_times) < 2:
            return 0.0
        
        # Calculate trend (positive = increasing time between interactions = declining engagement)
        x = np.arange(len(response_times))
        y = np.array(response_times)
        
        coefficients = np.polyfit(x, y, 1)
        slope = float(coefficients[0])
        
        return slope
    except Exception as e:
        print(f"Error calculating response time trend: {e}")
        return 0.0

def count_late_night_interactions(interactions):
    """Count interactions between 11 PM and 5 AM"""
    if not interactions:
        return 0
    
    try:
        late_night_count = 0
        for interaction in interactions:
            try:
                dt = datetime.fromisoformat(interaction['timestamp'].replace('Z', '+00:00'))
                hour = dt.hour
                if hour >= 23 or hour < 5:
                    late_night_count += 1
            except:
                continue
        
        return late_night_count
    except Exception as e:
        print(f"Error counting late night interactions: {e}")
        return 0

def calculate_weekend_usage_change(interactions):
    """Calculate difference in weekend vs weekday usage"""
    if not interactions:
        return 0.0
    
    try:
        weekend_count = 0
        weekday_count = 0
        
        for interaction in interactions:
            try:
                dt = datetime.fromisoformat(interaction['timestamp'].replace('Z', '+00:00'))
                day_of_week = dt.weekday()
                
                if day_of_week >= 5:  # Saturday=5, Sunday=6
                    weekend_count += 1
                else:
                    weekday_count += 1
            except:
                continue
        
        # Calculate per-day average
        weekend_avg = weekend_count / 8  # Assuming ~4 weeks = 8 weekend days
        weekday_avg = weekday_count / 20  # Assuming ~4 weeks = 20 weekday days
        
        return float(weekend_avg - weekday_avg)
    except Exception as e:
        print(f"Error calculating weekend usage change: {e}")
        return 0.0

def calculate_usage_consistency(interactions):
    """Calculate consistency of usage (lower variance = more consistent)"""
    if len(interactions) < 7:
        return 0.0
    
    try:
        # Group by day
        daily_counts = {}
        for interaction in interactions:
            try:
                dt = datetime.fromisoformat(interaction['timestamp'].replace('Z', '+00:00'))
                date_key = dt.date().isoformat()
                daily_counts[date_key] = daily_counts.get(date_key, 0) + 1
            except:
                continue
        
        if len(daily_counts) < 2:
            return 0.0
        
        counts = list(daily_counts.values())
        return float(np.std(counts))
    except Exception as e:
        print(f"Error calculating usage consistency: {e}")
        return 0.0

def count_negative_words(interactions):
    """Count negative words in notes"""
    negative_words = [
        'sad', 'depressed', 'anxious', 'worried', 'stressed', 'overwhelmed',
        'hopeless', 'helpless', 'alone', 'lonely', 'tired', 'exhausted',
        'angry', 'frustrated', 'scared', 'afraid', 'terrible', 'awful',
        'bad', 'worse', 'worst', 'hate', 'cry', 'crying', 'pain', 'hurt'
    ]
    
    try:
        total_words = 0
        negative_count = 0
        
        for interaction in interactions:
            if interaction.get('type') == 'mood_log':
                notes = interaction.get('notes', '').lower()
                if notes:
                    words = notes.split()
                    total_words += len(words)
                    negative_count += sum(1 for word in words if word in negative_words)
        
        if total_words == 0:
            return 0.0
        
        return negative_count / total_words
    except Exception as e:
        print(f"Error counting negative words: {e}")
        return 0.0

def count_help_seeking(interactions):
    """Count help-seeking phrases in notes"""
    help_phrases = [
        'help', 'need help', 'what should i do', 'i don\'t know',
        'advice', 'suggest', 'recommendation', 'what can i',
        'how do i', 'struggling', 'can\'t cope', 'too much'
    ]
    
    try:
        help_count = 0
        total_interactions = 0
        
        for interaction in interactions:
            if interaction.get('type') == 'mood_log':
                total_interactions += 1
                notes = interaction.get('notes', '').lower()
                if any(phrase in notes for phrase in help_phrases):
                    help_count += 1
        
        if total_interactions == 0:
            return 0.0
        
        return help_count / total_interactions
    except Exception as e:
        print(f"Error counting help seeking: {e}")
        return 0.0

def extract_behavioral_features(user_id, days=30):
    """Extract all behavioral features"""
    interactions = get_user_interactions(user_id, days)
    
    if not interactions:
        # Return default features if no data
        return {
            'daily_checkin_frequency': 0.0,
            'avg_session_duration': 0.0,
            'engagement_trend': 0.0,
            'response_time_trend': 0.0,
            'activity_completion_rate': 0.0,
            'selfie_frequency': 0.0,
            'avg_message_length': 0.0,
            'negative_word_frequency': 0.0,
            'help_seeking_frequency': 0.0,
            'late_night_usage': 0,
            'weekend_usage_change': 0.0,
            'usage_consistency': 0.0,
            'total_interactions': 0,
            'mood_logs_count': 0,
            'selfies_count': 0
        }
    
    # Count interaction types
    mood_logs = [i for i in interactions if i['type'] == 'mood_log']
    selfies = [i for i in interactions if i['type'] == 'selfie']
    
    # Calculate message lengths
    message_lengths = [len(i.get('notes', '')) for i in mood_logs if i.get('notes')]
    avg_message_length = float(np.mean(message_lengths)) if message_lengths else 0.0
    
    # Calculate activity completion (using mood logs with suggestions as proxy)
    logs_with_suggestions = [i for i in mood_logs if i.get('tags')]
    activity_completion_rate = len(logs_with_suggestions) / max(len(mood_logs), 1)
    
    features = {
        # Engagement features
        'daily_checkin_frequency': len(interactions) / days,
        'avg_session_duration': 120.0,  # Placeholder - would need session tracking
        'engagement_trend': calculate_engagement_trend(interactions),
        'response_time_trend': calculate_response_time_trend(interactions),
        
        # Activity features
        'activity_completion_rate': activity_completion_rate,
        'selfie_frequency': len(selfies) / days,
        
        # Communication features
        'avg_message_length': avg_message_length,
        'negative_word_frequency': count_negative_words(interactions),
        'help_seeking_frequency': count_help_seeking(interactions),
        
        # Temporal patterns
        'late_night_usage': count_late_night_interactions(interactions),
        'weekend_usage_change': calculate_weekend_usage_change(interactions),
        'usage_consistency': calculate_usage_consistency(interactions),
        
        # Metadata
        'total_interactions': len(interactions),
        'mood_logs_count': len(mood_logs),
        'selfies_count': len(selfies)
    }
    
    return features

def lambda_handler(event, context):
    """Lambda handler for behavioral feature extraction"""
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
        features = extract_behavioral_features(user_id, days)
        
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
                'message': 'Failed to extract behavioral features'
            })
        }
