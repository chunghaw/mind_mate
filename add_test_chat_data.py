#!/usr/bin/env python3

import boto3
import json
from datetime import datetime, timedelta

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('EmoCompanion')

def add_test_chat_data():
    """Add test chat data for a user with concerning messages"""
    
    test_user_id = "test-user-with-data"
    
    # Test messages with concerning content
    test_messages = [
        {
            'userMessage': 'I feel hopeless today',
            'aiResponse': 'I hear that you\'re feeling hopeless right now. That sounds really difficult.'
        },
        {
            'userMessage': 'I don\'t see the point in anything anymore',
            'aiResponse': 'It sounds like you\'re going through a really tough time. Your feelings are valid.'
        },
        {
            'userMessage': 'Sometimes I wish I could just disappear',
            'aiResponse': 'I\'m concerned about you. It sounds like you\'re in a lot of pain right now.'
        },
        {
            'userMessage': 'wanna die',
            'aiResponse': 'I\'m very worried about you. Please know that you\'re not alone and there is help available.'
        },
        {
            'userMessage': 'it sucks to be alive',
            'aiResponse': 'I understand this is an incredibly difficult time for you. Your life has value.'
        }
    ]
    
    print(f"Adding test chat data for user: {test_user_id}")
    
    # Add messages with timestamps over the last few days
    base_time = datetime.utcnow()
    
    for i, msg_data in enumerate(test_messages):
        # Spread messages over the last 3 days
        timestamp = (base_time - timedelta(hours=i*12)).isoformat() + 'Z'
        
        item = {
            'PK': f'USER#{test_user_id}',
            'SK': f'CHAT#{timestamp}',
            'type': 'CHAT',
            'userId': test_user_id,
            'userMessage': msg_data['userMessage'],
            'aiResponse': msg_data['aiResponse'],
            'sessionId': f'{test_user_id}-test',
            'timestamp': timestamp,
            'source': 'test-data'
        }
        
        try:
            table.put_item(Item=item)
            print(f"✅ Added message: {msg_data['userMessage']}")
        except Exception as e:
            print(f"❌ Failed to add message: {e}")
    
    print(f"\n🧪 Test data added for user: {test_user_id}")
    print("You can now test the risk calculation with this user ID")
    
    return test_user_id

if __name__ == "__main__":
    test_user_id = add_test_chat_data()
    
    # Test the risk calculation
    print(f"\n🔍 Testing risk calculation...")
    
    import requests
    
    try:
        response = requests.post(
            'https://h8iyzk1h3k.execute-api.us-east-1.amazonaws.com/calculate-risk',
            json={'userId': test_user_id},
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ Risk calculation successful!")
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ Risk calculation failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing risk calculation: {e}")