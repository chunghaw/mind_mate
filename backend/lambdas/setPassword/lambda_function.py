import json
import os
import boto3

cognito = boto3.client('cognito-idp')
USER_POOL_ID = os.environ.get('USER_POOL_ID', 'us-east-1_0xN9Gguz1')

def _resp(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST"
        },
        "body": json.dumps(body)
    }

def lambda_handler(event, context):
    """
    Allow Google OAuth users to set username/password for direct login
    """
    try:
        # Get userId from authorizer context
        user_id = event['requestContext']['authorizer']['userId']
        
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        username = body.get('username', '').strip()
        password = body.get('password', '').strip()
        
        if not username or not password:
            return _resp(400, {'error': 'Username and password are required'})
        
        # Validate password strength
        if len(password) < 8:
            return _resp(400, {'error': 'Password must be at least 8 characters'})
        
        # Get user's current attributes
        try:
            user_response = cognito.admin_get_user(
                UserPoolId=USER_POOL_ID,
                Username=user_id
            )
            
            email = next(
                (attr['Value'] for attr in user_response['UserAttributes'] 
                 if attr['Name'] == 'email'),
                None
            )
        except Exception as e:
            print(f'Error getting user: {e}')
            return _resp(404, {'error': 'User not found'})
        
        # Set permanent password for the user
        try:
            cognito.admin_set_user_password(
                UserPoolId=USER_POOL_ID,
                Username=user_id,
                Password=password,
                Permanent=True
            )
            print(f'Password set for user: {user_id}')
        except Exception as e:
            print(f'Error setting password: {e}')
            return _resp(500, {'error': f'Failed to set password: {str(e)}'})
        
        # Update user attributes
        try:
            cognito.admin_update_user_attributes(
                UserPoolId=USER_POOL_ID,
                Username=user_id,
                UserAttributes=[
                    {'Name': 'preferred_username', 'Value': username},
                    {'Name': 'custom:hasPassword', 'Value': 'true'}
                ]
            )
            print(f'Attributes updated for user: {user_id}')
        except Exception as e:
            print(f'Error updating attributes: {e}')
            # Password is set, so we can continue
        
        return _resp(200, {
            'ok': True,
            'message': 'Password set successfully. You can now login with username/password.',
            'username': username,
            'email': email
        })
        
    except Exception as e:
        print(f'Unexpected error: {e}')
        return _resp(500, {'error': str(e)})
