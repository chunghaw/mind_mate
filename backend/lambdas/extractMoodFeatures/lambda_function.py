import json
import os
from datetime import datetime, timedelta
from decimal import Decimal
import boto3

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
            KeyConditionExpression='PK = :pk AND begins_with(SK, :mood_prefix)',
            ExpressionAttributeValues={
                ':pk': f'USER#{user_id}',
                ':mood_prefix': 'MOOD#'
            }
        )
        
        moods = []
        for item in response.get('Items', []):
            if item.get('type') == 'MOOD':
                # Filter by date after retrieval
                item_timestamp = item.get('timestamp', item.get('ts', ''))
                try:
                    item_date = datetime.fromisoformat(item_timestamp.replace('Z', '+00:00'))
                    if item_date >= start_date:
                        moods.append({
                            'mood': decimal_to_float(item.get('mood', 5)),
                            'timestamp': item_timestamp,
                            'tags': item.get('tags', []),
                            'notes': item.get('notes', '')
                        })
                except Exception as e:
                    print(f"Error parsing mood timestamp {item_timestamp}: {e}")
                    # Include anyway if timestamp parsing fails
                    moods.append({
                        'mood': decimal_to_float(item.get('mood', 5)),
                        'timestamp': item_timestamp,
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
        mood_values = [m['mood'] for m in moods]
        n = len(mood_values)
        
        if n < 2:
            slope = 0.0
        else:
            # Simple linear regression
            x_vals = list(range(n))
            x_mean = sum(x_vals) / n
            y_mean = sum(mood_values) / n
            
            numerator = sum((x_vals[i] - x_mean) * (mood_values[i] - y_mean) for i in range(n))
            denominator = sum((x_vals[i] - x_mean) ** 2 for i in range(n))
            
            slope = numerator / denominator if denominator != 0 else 0.0
        
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
        return float(sum(daily_changes) / len(daily_changes)) if daily_changes else 0.0
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
            weekend_avg = sum(weekend_moods) / len(weekend_moods)
            weekday_avg = sum(weekday_moods) / len(weekday_moods)
            return float(weekend_avg - weekday_avg)
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
        'mood_mean_7day': float(sum(mood_values_7) / len(mood_values_7)) if mood_values_7 else 5.0,
        'mood_std_7day': float((sum((x - sum(mood_values_7)/len(mood_values_7))**2 for x in mood_values_7) / len(mood_values_7))**0.5) if len(mood_values_7) > 1 else 0.0,
        'mood_variance_7day': float(sum((x - sum(mood_values_7)/len(mood_values_7))**2 for x in mood_values_7) / len(mood_values_7)) if len(mood_values_7) > 1 else 0.0,
        'mood_min_7day': float(min(mood_values_7)) if mood_values_7 else 5.0,
        'mood_max_7day': float(max(mood_values_7)) if mood_values_7 else 5.0,
        
        # Statistical features - 14 day
        'mood_mean_14day': float(sum(mood_values_14) / len(mood_values_14)) if mood_values_14 else 5.0,
        'mood_std_14day': float((sum((x - sum(mood_values_14)/len(mood_values_14))**2 for x in mood_values_14) / len(mood_values_14))**0.5) if len(mood_values_14) > 1 else 0.0,
        
        # Statistical features - 30 day
        'mood_mean_30day': float(sum(mood_values_30) / len(mood_values_30)) if mood_values_30 else 5.0,
        'mood_std_30day': float((sum((x - sum(mood_values_30)/len(mood_values_30))**2 for x in mood_values_30) / len(mood_values_30))**0.5) if len(mood_values_30) > 1 else 0.0,
        
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
