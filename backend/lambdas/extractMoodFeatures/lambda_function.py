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

def get_user_moods(user_id, days=30):
    """Query DynamoDB for user's mood logs"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query mood entries
        response = table.query(
            KeyConditionExpression='PK = :pk AND SK BETWEEN :start AND :end',
            ExpressionAttributeValues={
                ':pk': f'USER#{user_id}',
                ':start': f'MOOD#{start_date.isoformat()}',
                ':end': f'MOOD#{end_date.isoformat()}Z'
            }
        )
        
        moods = []
        for item in response.get('Items', []):
            if item.get('type') == 'MOOD':
                moods.append({
                    'mood': decimal_to_float(item.get('mood', 5)),
                    'timestamp': item.get('ts'),
                    'tags': item.get('tags', []),
                    'notes': item.get('notes', '')
                })
        
        # Sort by timestamp
        moods.sort(key=lambda x: x['timestamp'])
        return moods
        
    except Exception as e:
        print(f"Error querying moods: {e}")
        return []

def calculate_trend(moods):
    """Calculate linear trend using least squares"""
    if len(moods) < 2:
        return 0.0
    
    try:
        x = np.arange(len(moods))
        y = np.array([m['mood'] for m in moods])
        
        # Linear regression: y = mx + b
        coefficients = np.polyfit(x, y, 1)
        slope = float(coefficients[0])
        
        return slope
    except Exception as e:
        print(f"Error calculating trend: {e}")
        return 0.0

def calculate_volatility(moods):
    """Calculate mood volatility (average daily change)"""
    if len(moods) < 2:
        return 0.0
    
    try:
        mood_values = [m['mood'] for m in moods]
        daily_changes = [abs(mood_values[i] - mood_values[i-1]) 
                        for i in range(1, len(mood_values))]
        return float(np.mean(daily_changes))
    except Exception as e:
        print(f"Error calculating volatility: {e}")
        return 0.0

def count_consecutive_low(moods, threshold=4):
    """Count maximum consecutive days with low mood"""
    if not moods:
        return 0
    
    try:
        max_consecutive = 0
        current_consecutive = 0
        
        for mood in moods:
            if mood['mood'] <= threshold:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        
        return max_consecutive
    except Exception as e:
        print(f"Error counting consecutive low days: {e}")
        return 0

def count_consecutive_high(moods, threshold=7):
    """Count maximum consecutive days with high mood"""
    if not moods:
        return 0
    
    try:
        max_consecutive = 0
        current_consecutive = 0
        
        for mood in moods:
            if mood['mood'] >= threshold:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        
        return max_consecutive
    except Exception as e:
        print(f"Error counting consecutive high days: {e}")
        return 0

def calculate_decline_rate(moods):
    """Calculate rate of mood decline (negative trend magnitude)"""
    if len(moods) < 2:
        return 0.0
    
    try:
        trend = calculate_trend(moods)
        # Only return decline rate if trend is negative
        return abs(trend) if trend < 0 else 0.0
    except Exception as e:
        print(f"Error calculating decline rate: {e}")
        return 0.0

def calculate_weekend_difference(moods):
    """Calculate difference between weekend and weekday moods"""
    if not moods:
        return 0.0
    
    try:
        weekend_moods = []
        weekday_moods = []
        
        for mood in moods:
            try:
                # Parse timestamp to get day of week
                dt = datetime.fromisoformat(mood['timestamp'].replace('Z', '+00:00'))
                day_of_week = dt.weekday()
                
                if day_of_week >= 5:  # Saturday=5, Sunday=6
                    weekend_moods.append(mood['mood'])
                else:
                    weekday_moods.append(mood['mood'])
            except:
                continue
        
        if weekend_moods and weekday_moods:
            return float(np.mean(weekend_moods) - np.mean(weekday_moods))
        return 0.0
    except Exception as e:
        print(f"Error calculating weekend difference: {e}")
        return 0.0

def extract_mood_features(user_id, days=30):
    """Extract all mood-related features"""
    moods = get_user_moods(user_id, days)
    
    if not moods:
        # Return default features if no data
        return {
            'mood_trend_7day': 0.0,
            'mood_trend_14day': 0.0,
            'mood_trend_30day': 0.0,
            'mood_mean_7day': 5.0,
            'mood_mean_14day': 5.0,
            'mood_mean_30day': 5.0,
            'mood_std_7day': 0.0,
            'mood_std_14day': 0.0,
            'mood_std_30day': 0.0,
            'mood_variance_7day': 0.0,
            'mood_min_7day': 5.0,
            'mood_max_7day': 5.0,
            'mood_volatility': 0.0,
            'consecutive_low_days': 0,
            'consecutive_high_days': 0,
            'mood_decline_rate': 0.0,
            'low_mood_frequency': 0.0,
            'high_mood_frequency': 0.0,
            'missing_days_7day': 7,
            'weekend_mood_diff': 0.0,
            'total_mood_entries': 0
        }
    
    # Get mood values for different time windows
    moods_7day = moods[-7:] if len(moods) >= 7 else moods
    moods_14day = moods[-14:] if len(moods) >= 14 else moods
    moods_30day = moods
    
    mood_values_7 = [m['mood'] for m in moods_7day]
    mood_values_14 = [m['mood'] for m in moods_14day]
    mood_values_30 = [m['mood'] for m in moods_30day]
    
    features = {
        # Trend features
        'mood_trend_7day': calculate_trend(moods_7day),
        'mood_trend_14day': calculate_trend(moods_14day),
        'mood_trend_30day': calculate_trend(moods_30day),
        
        # Statistical features - 7 day
        'mood_mean_7day': float(np.mean(mood_values_7)) if mood_values_7 else 5.0,
        'mood_std_7day': float(np.std(mood_values_7)) if len(mood_values_7) > 1 else 0.0,
        'mood_variance_7day': float(np.var(mood_values_7)) if len(mood_values_7) > 1 else 0.0,
        'mood_min_7day': float(np.min(mood_values_7)) if mood_values_7 else 5.0,
        'mood_max_7day': float(np.max(mood_values_7)) if mood_values_7 else 5.0,
        
        # Statistical features - 14 day
        'mood_mean_14day': float(np.mean(mood_values_14)) if mood_values_14 else 5.0,
        'mood_std_14day': float(np.std(mood_values_14)) if len(mood_values_14) > 1 else 0.0,
        
        # Statistical features - 30 day
        'mood_mean_30day': float(np.mean(mood_values_30)) if mood_values_30 else 5.0,
        'mood_std_30day': float(np.std(mood_values_30)) if len(mood_values_30) > 1 else 0.0,
        
        # Pattern features
        'mood_volatility': calculate_volatility(moods_30day),
        'consecutive_low_days': count_consecutive_low(moods_30day, threshold=4),
        'consecutive_high_days': count_consecutive_high(moods_30day, threshold=7),
        'mood_decline_rate': calculate_decline_rate(moods_7day),
        
        # Frequency features
        'low_mood_frequency': len([m for m in moods_7day if m['mood'] <= 3]) / max(len(moods_7day), 1),
        'high_mood_frequency': len([m for m in moods_7day if m['mood'] >= 8]) / max(len(moods_7day), 1),
        'missing_days_7day': max(0, 7 - len(moods_7day)),
        
        # Temporal features
        'weekend_mood_diff': calculate_weekend_difference(moods_30day),
        
        # Metadata
        'total_mood_entries': len(moods)
    }
    
    return features

def lambda_handler(event, context):
    """Lambda handler for mood feature extraction"""
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
        features = extract_mood_features(user_id, days)
        
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
                'message': 'Failed to extract mood features'
            })
        }
