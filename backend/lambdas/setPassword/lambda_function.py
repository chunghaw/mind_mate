import json
import boto3
import os

cognito = boto3.client('cognito-idp')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('TABLE_NAME', 'EmoCompanion'))

USER_POOL_ID = os.environ.get('USER_POOL_ID', 'us-east-1_0xN9Gguz1')

def lambda_handler(event, context):
    """
    Set username and password for Google OAuth users
    This allows them to login directly with username/password next time
    """
    try:
        print(f"Event: {json.dumps(event)}")
        
        # Get userId from authorizer context or claims
        try:
            user_id = event['requestContext']['authorizer']['userId']
        except (KeyError, TypeError):
            # Try to get from JWT claims
            try:
                user_id = event['requestContext']['authorizer']['jwt']['claims']['sub']
            except (KeyError, TypeError):
                print("ERROR: No userId found in authorizer context")
                return _resp(401, {'error': 'Unauthorized - no user ID found'})
        
        print(f"User ID: {user_id}")
        
        # Parse request body
        body = json.loads(event['body'])
        username = body.get('username')
        password = body.get('password')
        
        if not username or not password:
            return _resp(400, {'error': 'Username and password are required'})
        
        # Validate password
        if len(password) < 8:
            return _resp(400, {'error': 'Password must be at least 8 characters'})
        
        # Get user's current info from Cognito
        try:
            user_response = cognito.admin_get_user(
                UserPoolId=USER_POOL_ID,
                Username=user_id
            )
        except cognito.exceptions.UserNotFoundException:
            return _resp(404, {'error': 'User not found'})
        
        # Set permanent password for the user
        try:
            cognito.admin_set_user_password(
                UserPoolId=USER_POOL_ID,
                Username=user_id,
                Password=password,
                Permanent=True
            )
        except Exception as e:
            print(f'Error setting password: {e}')
            return _resp(500, {'error': f'Failed to set password: {str(e)}'})
        
        # Update user attributes with preferred_username
        try:
            cognito.admin_update_user_attributes(
                UserPoolId=USER_POOL_ID,
                Username=user_id,
                UserAttributes=[
                    {'Name': 'preferred_username', 'Value': username},
                    {'Name': 'custom:hasPassword', 'Value': 'true'}
                ]
            )
        except Exception as e:
            print(f'Error updating attributes: {e}')
            # Continue even if this fails
        
        # Update profile in DynamoDB
        try:
            table.update_item(
                Key={'PK': f'USER#{user_id}', 'SK': 'PROFILE'},
                UpdateExpression='SET hasPassword = :hp, username = :u',
                ExpressionAttributeValues={
                    ':hp': True,
                    ':u': username
                }
            )
        except Exception as e:
            print(f'Error updating profile: {e}')
            # Continue even if this fails
        
        return _resp(200, {
            'ok': True,
            'message': 'Password set successfully. You can now login with username/password.'
        })
        
    except Exception as e:
        print(f'Unexpected error: {e}')
        return _resp(500, {'error': str(e)})

def _resp(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'POST,OPTIONS'
        },
        'body': json.dumps(body)
    }
