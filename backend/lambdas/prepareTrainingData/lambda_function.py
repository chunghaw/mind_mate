import json
import os
from datetime import datetime, timedelta
from decimal import Decimal
import boto3
import csv
from io import StringIO

dynamodb = boto3.resource('dynamodb')
lambda_client = boto3.client('lambda')
s3 = boto3.client('s3')
table = dynamodb.Table(os.environ.get('TABLE_NAME', 'EmoCompanion'))
training_jobs_table = dynamodb.Table(os.environ.get('TRAINING_JOBS_TABLE', 'MindMate-TrainingJobs'))

ML_MODELS_BUCKET = os.environ.get('ML_MODELS_BUCKET')

def decimal_to_float(obj):
    """Convert DynamoDB Decimal to float"""
    if isinstance(obj, Decimal):
        return float(obj)
    return obj

def get_active_users(min_days=60):
    """Get users with at least min_days of data"""
    try:
        # Scan for all users (in production, maintain a user index)
        response = table.scan(
            FilterExpression='begins_with(SK, :profile)',
            ExpressionAttributeValues={':profile': 'PROFILE'}
        )
        
        users = []
        for item in response.get('Items', []):
            user_id = item.get('userId')
            if user_id:
                # Check if user has enough history
                mood_response = table.query(
                    KeyConditionExpression='PK = :pk AND begins_with(SK, :mood)',
                    ExpressionAttributeValues={
                        ':pk': f'USER#{user_id}',
                        ':mood': 'MOOD#'
                    },
                    Select='COUNT'
                )
                
                if mood_response.get('Count', 0) >= min_days:
                    users.append({
                        'userId': user_id,
                        'moodCount': mood_response.get('Count', 0)
                    })
        
        print(f"Found {len(users)} users with at least {min_days} days of data")
        return users
        
    except Exception as e:
        print(f"Error getting active users: {e}")
        return []

def extract_all_features(user_id, days=30):
    """Extract features from all three feature extraction Lambdas"""
    try:
        payload = json.dumps({'userId': user_id, 'days': days})
        
        # Invoke mood features Lambda
        mood_response = lambda_client.invoke(
            FunctionName='mindmate-extractMoodFeatures',
            InvocationType='RequestResponse',
            Payload=payload
        )
        mood_result = json.loads(mood_response['Payload'].read())
        mood_features = json.loads(mood_result.get('body', '{}'))
        
        # Invoke behavioral features Lambda
        behavioral_response = lambda_client.invoke(
            FunctionName='mindmate-extractBehavioralFeatures',
            InvocationType='RequestResponse',
            Payload=payload
        )
        behavioral_result = json.loads(behavioral_response['Payload'].read())
        behavioral_features = json.loads(behavioral_result.get('body', '{}'))
        
        # Invoke sentiment features Lambda
        sentiment_response = lambda_client.invoke(
            FunctionName='mindmate-extractSentimentFeatures',
            InvocationType='RequestResponse',
            Payload=payload
        )
        sentiment_result = json.loads(sentiment_response['Payload'].read())
        sentiment_features = json.loads(sentiment_result.get('body', '{}'))
        
        # Combine all features
        all_features = {
            **mood_features,
            **behavioral_features,
            **sentiment_features
        }
        
        return all_features
        
    except Exception as e:
        print(f"Error extracting features for user {user_id}: {e}")
        return None

def check_crisis_occurred(user_id, days_ahead=7):
    """Check if user experienced a crisis in the next days_ahead days"""
    try:
        # Look ahead from current point
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=days_ahead)
        
        # Query mood entries in lookahead window
        response = table.query(
            KeyConditionExpression='PK = :pk AND SK BETWEEN :start AND :end',
            ExpressionAttributeValues={
                ':pk': f'USER#{user_id}',
                ':start': f'MOOD#{start_date.isoformat()}',
                ':end': f'MOOD#{end_date.isoformat()}Z'
            }
        )
        
        moods = []
        crisis_keywords_found = False
        
        for item in response.get('Items', []):
            if item.get('type') == 'MOOD':
                mood_value = decimal_to_float(item.get('mood', 5))
                moods.append(mood_value)
                
                # Check for crisis keywords in notes
                notes = item.get('notes', '').lower()
                crisis_keywords = ['suicide', 'suicidal', 'kill myself', 'end my life', 
                                 'want to die', 'self harm', 'hurt myself']
                if any(keyword in notes for keyword in crisis_keywords):
                    crisis_keywords_found = True
        
        # Crisis criteria:
        # 1. Three or more consecutive days with mood <= 2
        # 2. Crisis keywords found in any message
        if crisis_keywords_found:
            return 1
        
        if len(moods) >= 3:
            consecutive_low = 0
            for mood in moods:
                if mood <= 2:
                    consecutive_low += 1
                    if consecutive_low >= 3:
                        return 1
                else:
                    consecutive_low = 0
        
        return 0
        
    except Exception as e:
        print(f"Error checking crisis for user {user_id}: {e}")
        return 0

def prepare_dataset(users, days=30):
    """Prepare training dataset from users"""
    dataset = []
    
    for i, user in enumerate(users):
        try:
            user_id = user['userId']
            print(f"Processing user {i+1}/{len(users)}: {user_id}")
            
            # Extract features
            features = extract_all_features(user_id, days)
            
            if not features:
                print(f"  Skipping user {user_id}: No features extracted")
                continue
            
            # Get label (crisis in next 7 days)
            label = check_crisis_occurred(user_id, days_ahead=7)
            
            # Add userId and label
            features['userId'] = user_id
            features['label'] = label
            
            dataset.append(features)
            print(f"  User {user_id}: label={label}, features={len(features)}")
            
        except Exception as e:
            print(f"Error processing user {user['userId']}: {e}")
            continue
    
    return dataset

def anonymize_dataset(dataset):
    """Remove PII from dataset"""
    anonymized = []
    
    for i, row in enumerate(dataset):
        # Remove userId, replace with anonymous ID
        anon_row = {k: v for k, v in row.items() if k != 'userId'}
        anon_row['sample_id'] = f'sample_{i:06d}'
        anonymized.append(anon_row)
    
    return anonymized

def split_train_validation(dataset, validation_split=0.2):
    """Split dataset into train and validation sets"""
    import random
    
    # Shuffle dataset
    random.shuffle(dataset)
    
    # Calculate split point
    split_idx = int(len(dataset) * (1 - validation_split))
    
    train_data = dataset[:split_idx]
    val_data = dataset[split_idx:]
    
    return train_data, val_data

def balance_classes(dataset):
    """Balance classes using oversampling of minority class"""
    positive_samples = [d for d in dataset if d.get('label') == 1]
    negative_samples = [d for d in dataset if d.get('label') == 0]
    
    print(f"Class distribution: Positive={len(positive_samples)}, Negative={len(negative_samples)}")
    
    # Oversample minority class
    if len(positive_samples) < len(negative_samples):
        # Oversample positive class
        import random
        while len(positive_samples) < len(negative_samples):
            positive_samples.append(random.choice(positive_samples))
    elif len(negative_samples) < len(positive_samples):
        # Oversample negative class
        import random
        while len(negative_samples) < len(positive_samples):
            negative_samples.append(random.choice(negative_samples))
    
    balanced = positive_samples + negative_samples
    import random
    random.shuffle(balanced)
    
    print(f"Balanced dataset: {len(balanced)} samples")
    return balanced

def save_to_s3(dataset, filename):
    """Save dataset to S3 as CSV"""
    try:
        if not dataset:
            print("No data to save")
            return None
        
        # Convert to CSV
        output = StringIO()
        
        # Get all field names
        fieldnames = list(dataset[0].keys())
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(dataset)
        
        # Upload to S3
        csv_content = output.getvalue()
        s3_key = f'training/{filename}'
        
        s3.put_object(
            Bucket=ML_MODELS_BUCKET,
            Key=s3_key,
            Body=csv_content.encode('utf-8'),
            ContentType='text/csv'
        )
        
        s3_path = f's3://{ML_MODELS_BUCKET}/{s3_key}'
        print(f"Saved {len(dataset)} samples to {s3_path}")
        
        return s3_path
        
    except Exception as e:
        print(f"Error saving to S3: {e}")
        return None

def lambda_handler(event, context):
    """Lambda handler for training data preparation"""
    try:
        print("Starting training data preparation...")
        
        # Get configuration
        min_days = event.get('minDays', 60)
        validation_split = event.get('validationSplit', 0.2)
        
        # Get users with sufficient history
        users = get_active_users(min_days=min_days)
        
        if len(users) < 10:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': f'Insufficient users with {min_days}+ days of data',
                    'usersFound': len(users),
                    'minimumRequired': 10
                })
            }
        
        # Prepare dataset
        print(f"Preparing dataset from {len(users)} users...")
        dataset = prepare_dataset(users, days=30)
        
        if len(dataset) < 10:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Insufficient samples after feature extraction',
                    'samplesGenerated': len(dataset),
                    'minimumRequired': 10
                })
            }
        
        # Anonymize data
        print("Anonymizing dataset...")
        dataset = anonymize_dataset(dataset)
        
        # Balance classes
        print("Balancing classes...")
        dataset = balance_classes(dataset)
        
        # Split train/validation
        print(f"Splitting dataset (validation={validation_split})...")
        train_data, val_data = split_train_validation(dataset, validation_split)
        
        # Save to S3
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        train_path = save_to_s3(train_data, f'train_{timestamp}.csv')
        val_path = save_to_s3(val_data, f'validation_{timestamp}.csv')
        
        if not train_path or not val_path:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Failed to save datasets to S3'})
            }
        
        # Calculate class distribution
        train_positive = len([d for d in train_data if d.get('label') == 1])
        val_positive = len([d for d in val_data if d.get('label') == 1])
        
        result = {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'trainPath': train_path,
                'validationPath': val_path,
                'totalSamples': len(dataset),
                'trainSamples': len(train_data),
                'validationSamples': len(val_data),
                'trainPositiveClass': train_positive,
                'trainNegativeClass': len(train_data) - train_positive,
                'valPositiveClass': val_positive,
                'valNegativeClass': len(val_data) - val_positive,
                'timestamp': timestamp
            })
        }
        
        # Log to training jobs table
        try:
            training_jobs_table.put_item(Item={
                'jobId': f'data-prep-{timestamp}',
                'status': 'Completed',
                'timestamp': datetime.utcnow().isoformat(),
                'trainPath': train_path,
                'validationPath': val_path,
                'totalSamples': len(dataset),
                'trainSamples': len(train_data),
                'validationSamples': len(val_data)
            })
        except Exception as e:
            print(f"Error logging to training jobs table: {e}")
        
        return result
        
    except Exception as e:
        print(f"Error in lambda_handler: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'Failed to prepare training data'
            })
        }
