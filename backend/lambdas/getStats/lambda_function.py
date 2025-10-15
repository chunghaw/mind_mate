import os, json, datetime
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('TABLE_NAME', 'EmoCompanion'))

def _resp(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "OPTIONS,GET"
        },
        "body": json.dumps(body, default=str)
    }

def lambda_handler(event, context):
    try:
        # Get userId from query params or default
        user_id = event.get('queryStringParameters', {}).get('userId', 'demo-user') if event.get('queryStringParameters') else 'demo-user'
        
        # Get all mood entries
        mood_response = table.query(
            KeyConditionExpression=Key('PK').eq(f'USER#{user_id}') & Key('SK').begins_with('MOOD#'),
            ScanIndexForward=False,
            Limit=100
        )
        moods = mood_response.get('Items', [])
        
        # Calculate streak (consecutive days with at least 1 mood entry)
        today = datetime.date.today()
        streak = 0
        check_date = today
        
        while True:
            date_str = check_date.isoformat()
            has_entry = any(m.get('ts', '').startswith(date_str) for m in moods)
            if has_entry:
                streak += 1
                check_date -= datetime.timedelta(days=1)
            else:
                break
        
        # Get last 7 days mood data for trend
        seven_days_ago = (today - datetime.timedelta(days=7)).isoformat()
        recent_moods = [m for m in moods if m.get('ts', '') >= seven_days_ago]
        
        # Calculate average mood
        if recent_moods:
            avg_mood = sum(m.get('mood', 5) for m in recent_moods) / len(recent_moods)
        else:
            avg_mood = 0
        
        # Build 7-day mood trend (one value per day)
        mood_trend = []
        for i in range(7):
            day = today - datetime.timedelta(days=6-i)
            day_str = day.isoformat()
            day_moods = [m.get('mood', 5) for m in moods if m.get('ts', '').startswith(day_str)]
            if day_moods:
                mood_trend.append({
                    'date': day_str,
                    'mood': round(sum(day_moods) / len(day_moods), 1)
                })
            else:
                mood_trend.append({
                    'date': day_str,
                    'mood': None
                })
        
        # Count total check-ins
        total_checkins = len(moods)
        
        # Get selfie count
        selfie_response = table.query(
            KeyConditionExpression=Key('PK').eq(f'USER#{user_id}') & Key('SK').begins_with('SELFIE#'),
            Select='COUNT'
        )
        total_selfies = selfie_response.get('Count', 0)
        
        return _resp(200, {
            'ok': True,
            'stats': {
                'streak': streak,
                'totalCheckins': total_checkins,
                'totalSelfies': total_selfies,
                'avgMood': round(avg_mood, 1),
                'moodTrend': mood_trend
            }
        })
        
    except Exception as e:
        return _resp(500, {'error': str(e)})
