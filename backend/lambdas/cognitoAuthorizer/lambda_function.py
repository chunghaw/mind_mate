import json
import jwt
import requests
from jwt.algorithms import RSAAlgorithm

REGION = 'us-east-1'
USER_POOL_ID = 'us-east-1_0xN9Gguz1'
JWKS_URL = f'https://cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}/.well-known/jwks.json'

# Cache JWKS keys
jwks_keys = None

def lambda_handler(event, context):
    """
    Lambda authorizer to verify Cognito JWT tokens
    """
    try:
        # Extract token from Authorization header
        token = event.get('authorizationToken', '').replace('Bearer ', '')
        
        if not token:
            print('No token provided')
            return generate_policy('user', 'Deny', event['methodArn'])
        
        # Get JWKS keys (cached)
        global jwks_keys
        if not jwks_keys:
            print('Fetching JWKS keys...')
            response = requests.get(JWKS_URL, timeout=5)
            jwks_keys = response.json()['keys']
        
        # Decode token header to get kid
        headers = jwt.get_unverified_header(token)
        kid = headers['kid']
        
        # Find matching key
        key = next((k for k in jwks_keys if k['kid'] == kid), None)
        if not key:
            print(f'Key with kid {kid} not found')
            return generate_policy('user', 'Deny', event['methodArn'])
        
        # Convert JWK to public key
        public_key = RSAAlgorithm.from_jwk(json.dumps(key))
        
        # Verify and decode token
        payload = jwt.decode(
            token,
            public_key,
            algorithms=['RS256'],
            options={'verify_aud': False}  # Cognito doesn't always include aud
        )
        
        # Extract user ID from token
        user_id = payload['sub']
        email = payload.get('email', '')
        
        print(f'Token verified for user: {user_id}')
        
        # Generate allow policy
        return generate_policy(user_id, 'Allow', event['methodArn'], {
            'userId': user_id,
            'email': email
        })
        
    except jwt.ExpiredSignatureError:
        print('Token expired')
        return generate_policy('user', 'Deny', event['methodArn'])
    except jwt.InvalidTokenError as e:
        print(f'Invalid token: {e}')
        return generate_policy('user', 'Deny', event['methodArn'])
    except Exception as e:
        print(f'Authorization error: {e}')
        return generate_policy('user', 'Deny', event['methodArn'])

def generate_policy(principal_id, effect, resource, context=None):
    """
    Generate IAM policy for API Gateway
    """
    policy = {
        'principalId': principal_id,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'execute-api:Invoke',
                'Effect': effect,
                'Resource': resource
            }]
        }
    }
    
    if context:
        policy['context'] = context
    
    return policy
