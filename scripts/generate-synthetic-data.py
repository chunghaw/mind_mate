#!/usr/bin/env python3
"""
Generate Synthetic Training Data for Hackathon Demo
Creates realistic mood logs and training data without real users
"""

import boto3
import random
import json
from datetime import datetime, timedelta
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('EmoCompanion')

# Synthetic user profiles
DEMO_USERS = [
    {
        'userId': 'demo_user_stable',
        'pattern': 'stable',  # Consistently good mood
        'crisis_risk': 0.1
    },
    {
        'userId': 'demo_user_declining',
        'pattern': 'declining',  # Gradual mood decline
        'crisis_risk': 0.7
    },
    {
        'userId': 'demo_user_crisis',
        'pattern': 'crisis',  # Severe crisis pattern
        'crisis_risk': 0.95
    },
    {
        'userId': 'demo_user_recovering',
        'pattern': 'recovering',  # Improving mood
        'crisis_risk': 0.2
    },
    {
        'userId': 'demo_user_volatile',
        'pattern': 'volatile',  # Erratic mood swings
        'crisis_risk': 0.6
    }
]

# Mood notes templates
STABLE_NOTES = [
    "Feeling good today, work went well",
    "Had a productive day, feeling accomplished",
    "Enjoyed time with friends, feeling happy",
    "Relaxing weekend, feeling refreshed",
    "Good workout today, feeling energized"
]

DECLINING_NOTES = [
    "Feeling a bit stressed about work",
    "Tired today, struggling to focus",
    "Work pressure is building up",
    "Feeling overwhelmed with tasks",
    "Having trouble sleeping, feeling anxious"
]

CRISIS_NOTES = [
    "Feeling hopeless, can't see a way forward",
    "Everything feels pointless, so tired",
    "Feeling alone, nobody understands",
    "Can't cope anymore, too much pressure",
    "Feeling worthless, nothing matters",
    "So isolated, no one to talk to",
    "Exhausted, can't go on like this"
]

RECOVERING_NOTES = [
    "Starting to feel a bit better",
    "Had a good conversation with a friend",
    "Trying some coping strategies, helping a bit",
    "Feeling more hopeful today",
    "Small wins today, feeling encouraged"
]

VOLATILE_NOTES = [
    "Mood swings today, up and down",
    "Started good but ended badly",
    "Feeling confused about everything",
    "Can't predict how I'll feel",
    "Emotional rollercoaster today"
]


def generate_mood_pattern(pattern, day, total_days=90):
    """Generate mood score based on pattern"""
    
    if pattern == 'stable':
        # Consistently good mood (6-8)
        base = 7
        variation = random.uniform(-1, 1)
        return max(1, min(10, base + variation))
    
    elif pattern == 'declining':
        # Gradual decline from 7 to 3
        progress = day / total_days
        base = 7 - (4 * progress)
        variation = random.uniform(-0.5, 0.5)
        return max(1, min(10, base + variation))
    
    elif pattern == 'crisis':
        # Severe decline to crisis levels
        if day < 30:
            base = 5
        elif day < 60:
            base = 3
        else:
            base = 2  # Crisis level
        variation = random.uniform(-0.5, 0.5)
        return max(1, min(10, base + variation))
    
    elif pattern == 'recovering':
        # Improving from 4 to 7
        progress = day / total_days
        base = 4 + (3 * progress)
        variation = random.uniform(-0.5, 0.5)
        return max(1, min(10, base + variation))
    
    elif pattern == 'volatile':
        # Random swings between 3 and 8
        return random.uniform(3, 8)
    
    return 5


def get_notes_for_pattern(pattern, mood):
    """Get appropriate notes based on pattern and mood"""
    
    if pattern == 'stable':
        return random.choice(STABLE_NOTES)
    elif pattern == 'declining':
        return random.choice(DECLINING_NOTES)
    elif pattern == 'crisis':
        return random.choice(CRISIS_NOTES)
    elif pattern == 'recovering':
        return random.choice(RECOVERING_NOTES)
    elif pattern == 'volatile':
        return random.choice(VOLATILE_NOTES)
    
    return "Feeling okay today"


def generate_user_data(user_profile, days=90):
    """Generate synthetic mood logs for a user"""
    
    user_id = user_profile['userId']
    pattern = user_profile['pattern']
    
    print(f"\nGenerating data for {user_id} ({pattern} pattern)...")
    
    # Create user profile
    table.put_item(Item={
        'PK': f'USER#{user_id}',
        'SK': 'PROFILE',
        'type': 'PROFILE',
        'userId': user_id,
        'personality': 'gentle',
        'petName': 'Demo Buddy',
        'createdAt': (datetime.utcnow() - timedelta(days=days)).isoformat()
    })
    
    # Generate mood logs
    start_date = datetime.utcnow() - timedelta(days=days)
    
    for day in range(days):
        # Skip some days randomly (realistic)
        if random.random() < 0.15:  # 15% missing days
            continue
        
        current_date = start_date + timedelta(days=day)
        mood = generate_mood_pattern(pattern, day, days)
        notes = get_notes_for_pattern(pattern, mood)
        
        # Add some tags
        tags = []
        if mood >= 7:
            tags = random.sample(['happy', 'productive', 'social'], k=random.randint(0, 2))
        elif mood <= 4:
            tags = random.sample(['stressed', 'tired', 'anxious'], k=random.randint(0, 2))
        
        # Store mood log
        table.put_item(Item={
            'PK': f'USER#{user_id}',
            'SK': f'MOOD#{current_date.isoformat()}Z',
            'type': 'MOOD',
            'userId': user_id,
            'mood': Decimal(str(round(mood, 1))),
            'notes': notes,
            'tags': tags,
            'ts': current_date.isoformat() + 'Z'
        })
        
        # Occasionally add selfies
        if random.random() < 0.1:  # 10% of days
            emotions = {
                'HAPPY': Decimal(str(max(0, (mood - 5) / 5))),
                'SAD': Decimal(str(max(0, (5 - mood) / 5))),
                'CALM': Decimal(str(0.3))
            }
            
            table.put_item(Item={
                'PK': f'USER#{user_id}',
                'SK': f'SELFIE#{current_date.isoformat()}Z',
                'type': 'SELFIE',
                'userId': user_id,
                'emotions': emotions,
                'ts': current_date.isoformat() + 'Z'
            })
    
    print(f"  ✓ Generated {days} days of data for {user_id}")


def generate_all_demo_data():
    """Generate data for all demo users"""
    
    print("="*60)
    print("Generating Synthetic Training Data for Demo")
    print("="*60)
    
    for user_profile in DEMO_USERS:
        generate_user_data(user_profile, days=90)
    
    print("\n" + "="*60)
    print("✅ Synthetic data generation complete!")
    print("="*60)
    print(f"\nGenerated data for {len(DEMO_USERS)} demo users:")
    for user in DEMO_USERS:
        print(f"  - {user['userId']}: {user['pattern']} pattern (crisis risk: {user['crisis_risk']*100:.0f}%)")
    
    print("\nNext steps:")
    print("1. Run feature extraction: aws lambda invoke --function-name mindmate-extractMoodFeatures ...")
    print("2. Run data preparation: aws lambda invoke --function-name mindmate-prepareTrainingData ...")
    print("3. Train model with generated data")


if __name__ == '__main__':
    generate_all_demo_data()
