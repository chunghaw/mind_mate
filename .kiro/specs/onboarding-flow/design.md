# Onboarding Flow - Design Document

## Overview

This document outlines the technical design for implementing the complete onboarding flow with AWS Cognito authentication, personality selection, and user personalization as specified in PRODUCT_VISION.md.

## Architecture

### High-Level Flow
```
User Opens App
    ↓
Check localStorage for auth token
    ↓
[No token] → Welcome Screen → Login/Signup
    ↓
    ├─ Username/Password → Cognito Auth
    │
    └─ Google Sign-In → Cognito Auth
           ↓
       [First time Google user] → Set Username/Password Screen
           ↓
       [Password set] → Continue
    ↓
[Has token] → Verify token → Check onboarding status
    ↓
[New user] → Personality Selection → Name Input → Introduction → Main App
    ↓
[Returning user] → Main App (with personalized greeting)

Note: After setting password, Google users can login with username/password next time
```

### Component Architecture
```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (SPA)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ Welcome  │→ │  Login   │→ │Onboarding│→ Main App   │
│  │ Screen   │  │  Screen  │  │  Flow    │             │
│  └──────────┘  └──────────┘  └──────────┘             │
│         ↓              ↓              ↓                 │
│    Amplify Auth    Cognito      API Gateway            │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                   AWS Cognito                            │
│  ┌──────────────┐  ┌──────────────┐                    │
│  │  User Pool   │  │   Identity   │                    │
│  │              │  │   Provider   │                    │
│  │ - Username   │  │  (Google)    │                    │
│  │ - Password   │  └──────────────┘                    │
│  │ - Email      │                                       │
│  └──────────────┘                                       │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                  API Gateway + Lambda                    │
│  ┌──────────────┐  ┌──────────────┐                    │
│  │  Authorizer  │→ │   Lambda     │                    │
│  │ (Verify JWT) │  │  Functions   │                    │
│  └──────────────┘  └──────────────┘                    │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                     DynamoDB                             │
│  Table: EmoCompanion                                     │
│  PK: USER#{cognitoUserId}                               │
│  SK: PROFILE | MOOD#{ts} | SELFIE#{ts}                 │
└─────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. Frontend Components

#### WelcomeScreen Component
```javascript
// Displays app introduction
// Shows "Get Started" button
// Navigates to LoginScreen
```

#### LoginScreen Component
```javascript
// Username + Password inputs
// "Log In" button
// "Sign Up" link
// "Sign in with Google" button
// Integrates with AWS Amplify Auth
```

#### SignupScreen Component
```javascript
// Username, Email, Password inputs
// "Create Account" button
// Calls Cognito signUp API
// Handles email verification
```

#### SetPasswordScreen Component (for Google users)
```javascript
// Shown after first Google sign-in
// "Set up direct login" message
// Username input (optional, defaults to email)
// Password input
// "Save" button
// Calls API to set password for Cognito user
// Navigates to onboarding or main app
```

#### PersonalitySelector Component
```javascript
// Displays 4 personality cards
// Stores selection in state
// Calls API to save personality
// Navigates to NameInput
```

#### NameInput Component
```javascript
// Pet asks "What should I call you?"
// Text input for user name
// Validates input
// Calls API to save name
// Navigates to Introduction
```

#### Introduction Component
```javascript
// Pet greets user by name
// Explains Mind Mate purpose
// "Let's Go!" button
// Marks onboarding complete
// Navigates to Main App
```

### 2. AWS Cognito Setup

#### User Pool Configuration
```yaml
UserPool:
  Type: AWS::Cognito::UserPool
  Properties:
    UserPoolName: MindMateUsers
    UsernameAttributes:
      - email
    AutoVerifiedAttributes:
      - email
    Policies:
      PasswordPolicy:
        MinimumLength: 8
        RequireUppercase: true
        RequireLowercase: true
        RequireNumbers: true
        RequireSymbols: false
    Schema:
      - Name: email
        Required: true
        Mutable: false
      - Name: name
        Required: false
        Mutable: true
      - Name: preferred_username
        Required: false
        Mutable: true
      - Name: custom:hasPassword
        AttributeDataType: String
        Mutable: true
        Required: false
```

#### Google Identity Provider
```yaml
UserPoolIdentityProvider:
  Type: AWS::Cognito::UserPoolIdentityProvider
  Properties:
    UserPoolId: !Ref UserPool
    ProviderName: Google
    ProviderType: Google
    ProviderDetails:
      client_id: ${GOOGLE_CLIENT_ID}
      client_secret: ${GOOGLE_CLIENT_SECRET}
      authorize_scopes: "email profile openid"
    AttributeMapping:
      email: email
      name: name
      username: sub
```

#### User Pool Client
```yaml
UserPoolClient:
  Type: AWS::Cognito::UserPoolClient
  Properties:
    ClientName: MindMateWebApp
    UserPoolId: !Ref UserPool
    GenerateSecret: false
    SupportedIdentityProviders:
      - COGNITO
      - Google
    CallbackURLs:
      - http://localhost:8000
      - https://your-amplify-url.amplifyapp.com
    LogoutURLs:
      - http://localhost:8000
      - https://your-amplify-url.amplifyapp.com
    AllowedOAuthFlows:
      - code
      - implicit
    AllowedOAuthScopes:
      - email
      - openid
      - profile
    AllowedOAuthFlowsUserPoolClient: true
```

### 3. Frontend Authentication Integration

#### Amplify Configuration
```javascript
// Configure Amplify Auth
import { Amplify } from 'aws-amplify';

Amplify.configure({
    Auth: {
        region: 'us-east-1',
        userPoolId: 'us-east-1_XXXXXXXXX',
        userPoolWebClientId: 'XXXXXXXXXXXXXXXXXXXXXXXXXX',
        oauth: {
            domain: 'mindmate.auth.us-east-1.amazoncognito.com',
            scope: ['email', 'profile', 'openid'],
            redirectSignIn: 'http://localhost:8000/',
            redirectSignOut: 'http://localhost:8000/',
            responseType: 'code'
        }
    }
});
```

#### Login Implementation
```javascript
import { Auth } from 'aws-amplify';

// Username/Password Login
async function login(username, password) {
    try {
        const user = await Auth.signIn(username, password);
        const session = await Auth.currentSession();
        const token = session.getIdToken().getJwtToken();
        const userId = user.attributes.sub;
        
        // Store in localStorage
        localStorage.setItem('mindmate_token', token);
        localStorage.setItem('mindmate_userId', userId);
        
        // Check onboarding status
        const profile = await fetchProfile(userId, token);
        
        if (profile.onboardingComplete) {
            navigateToMainApp();
        } else {
            navigateToOnboarding();
        }
    } catch (error) {
        console.error('Login error:', error);
        showError(error.message);
    }
}

// Google Sign-In
async function signInWithGoogle() {
    try {
        await Auth.federatedSignIn({ provider: 'Google' });
        // Cognito handles redirect and callback
        // After successful Google auth, check if user has password set
        const user = await Auth.currentAuthenticatedUser();
        const hasPassword = user.attributes['custom:hasPassword'];
        
        if (!hasPassword) {
            // First time Google user - prompt to set username/password
            navigateToSetPassword();
        } else {
            // Returning Google user with password set
            checkOnboardingStatus();
        }
    } catch (error) {
        console.error('Google sign-in error:', error);
    }
}

// Set Password for Google Users
async function setPasswordForGoogleUser(username, password) {
    try {
        const user = await Auth.currentAuthenticatedUser();
        
        // Update username attribute
        await Auth.updateUserAttributes(user, {
            'preferred_username': username,
            'custom:hasPassword': 'true'
        });
        
        // Set password (requires admin API or custom Lambda)
        await fetch(`${API}/set-password`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${await getToken()}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        showMessage('Password set! You can now login with username/password');
        checkOnboardingStatus();
    } catch (error) {
        console.error('Set password error:', error);
        showError(error.message);
    }
}

// Sign Up
async function signUp(username, email, password) {
    try {
        const { user } = await Auth.signUp({
            username,
            password,
            attributes: {
                email
            }
        });
        
        // Show verification message
        showMessage('Please check your email to verify your account');
        
        // Navigate to onboarding after verification
        navigateToOnboarding();
    } catch (error) {
        console.error('Sign up error:', error);
        showError(error.message);
    }
}

// Check Auth Status on App Load
async function checkAuthStatus() {
    try {
        const user = await Auth.currentAuthenticatedUser();
        const session = await Auth.currentSession();
        const token = session.getIdToken().getJwtToken();
        const userId = user.attributes.sub;
        
        // User is logged in
        const profile = await fetchProfile(userId, token);
        
        if (profile.onboardingComplete) {
            navigateToMainApp();
        } else {
            navigateToOnboarding();
        }
    } catch (error) {
        // User is not logged in
        navigateToWelcomeScreen();
    }
}
```

### 4. Backend Lambda Authorizer

#### JWT Verification
```python
# Lambda: cognitoAuthorizer
import json
import jwt
import requests
from jwt.algorithms import RSAAlgorithm

REGION = 'us-east-1'
USER_POOL_ID = 'us-east-1_XXXXXXXXX'
JWKS_URL = f'https://cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}/.well-known/jwks.json'

# Cache JWKS keys
jwks_keys = None

def lambda_handler(event, context):
    token = event['authorizationToken'].replace('Bearer ', '')
    
    try:
        # Get JWKS keys
        global jwks_keys
        if not jwks_keys:
            response = requests.get(JWKS_URL)
            jwks_keys = response.json()['keys']
        
        # Decode token header
        headers = jwt.get_unverified_header(token)
        kid = headers['kid']
        
        # Find matching key
        key = next(k for k in jwks_keys if k['kid'] == kid)
        public_key = RSAAlgorithm.from_jwk(json.dumps(key))
        
        # Verify token
        payload = jwt.decode(
            token,
            public_key,
            algorithms=['RS256'],
            audience=None,  # Set to client ID in production
            options={'verify_aud': False}
        )
        
        user_id = payload['sub']
        
        # Generate policy
        return generate_policy(user_id, 'Allow', event['methodArn'])
        
    except Exception as e:
        print(f'Authorization error: {e}')
        return generate_policy('user', 'Deny', event['methodArn'])

def generate_policy(principal_id, effect, resource):
    return {
        'principalId': principal_id,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'execute-api:Invoke',
                'Effect': effect,
                'Resource': resource
            }]
        },
        'context': {
            'userId': principal_id
        }
    }
```

### 5. Updated Lambda Functions

#### getProfile (with Cognito userId)
```python
def lambda_handler(event, context):
    # Get userId from authorizer context
    user_id = event['requestContext']['authorizer']['userId']
    
    # Get profile from DynamoDB
    response = table.get_item(Key={
        'PK': f'USER#{user_id}',
        'SK': 'PROFILE'
    })
    
    if not response.get('Item'):
        # Create default profile for new user
        profile = {
            'PK': f'USER#{user_id}',
            'SK': 'PROFILE',
            'userId': user_id,
            'onboardingComplete': False,
            'createdAt': datetime.utcnow().isoformat()
        }
        table.put_item(Item=profile)
        return _resp(200, {'ok': True, 'profile': profile})
    
    return _resp(200, {'ok': True, 'profile': response['Item']})
```

#### updateProfile (save onboarding data)
```python
def lambda_handler(event, context):
    user_id = event['requestContext']['authorizer']['userId']
    body = json.loads(event['body'])
    
    # Update profile with onboarding data
    table.update_item(
        Key={'PK': f'USER#{user_id}', 'SK': 'PROFILE'},
        UpdateExpression='SET personality = :p, userName = :n, petName = :pn, onboardingComplete = :oc',
        ExpressionAttributeValues={
            ':p': body.get('personality'),
            ':n': body.get('userName'),
            ':pn': body.get('petName'),
            ':oc': body.get('onboardingComplete', False)
        }
    )
    
    return _resp(200, {'ok': True})
```

#### setPassword (for Google users to set username/password)
```python
import boto3

cognito = boto3.client('cognito-idp')
USER_POOL_ID = os.environ['USER_POOL_ID']

def lambda_handler(event, context):
    user_id = event['requestContext']['authorizer']['userId']
    body = json.loads(event['body'])
    
    username = body.get('username')
    password = body.get('password')
    
    try:
        # Get user's email from Cognito
        user_response = cognito.admin_get_user(
            UserPoolId=USER_POOL_ID,
            Username=user_id
        )
        
        email = next(
            attr['Value'] for attr in user_response['UserAttributes'] 
            if attr['Name'] == 'email'
        )
        
        # Set permanent password for the user
        cognito.admin_set_user_password(
            UserPoolId=USER_POOL_ID,
            Username=user_id,
            Password=password,
            Permanent=True
        )
        
        # Update preferred_username attribute
        cognito.admin_update_user_attributes(
            UserPoolId=USER_POOL_ID,
            Username=user_id,
            UserAttributes=[
                {'Name': 'preferred_username', 'Value': username},
                {'Name': 'custom:hasPassword', 'Value': 'true'}
            ]
        )
        
        return _resp(200, {
            'ok': True,
            'message': 'Password set successfully. You can now login with username/password.'
        })
        
    except Exception as e:
        print(f'Set password error: {e}')
        return _resp(500, {'error': str(e)})
```

## Data Models

### User Profile (DynamoDB)
```json
{
    "PK": "USER#{cognitoUserId}",
    "SK": "PROFILE",
    "userId": "cognito-sub-uuid",
    "email": "user@example.com",
    "userName": "Sarah",
    "personality": "gentle",
    "petName": "Buddy",
    "onboardingComplete": true,
    "createdAt": "2025-10-16T10:00:00Z",
    "lastLoginAt": "2025-10-16T14:30:00Z"
}
```

### Cognito User Attributes
```json
{
    "sub": "uuid-from-cognito",
    "email": "user@example.com",
    "email_verified": true,
    "name": "Sarah Johnson",
    "identities": [
        {
            "userId": "google-user-id",
            "providerName": "Google",
            "providerType": "Google"
        }
    ]
}
```

## State Management

### localStorage Schema
```javascript
{
    "mindmate_token": "jwt-token-string",
    "mindmate_userId": "cognito-sub-uuid",
    "mindmate_email": "user@example.com",
    "mindmate_onboardingStep": "personality|name|intro|complete"
}
```

### Onboarding State Machine
```
START
  ↓
[Check Auth] → Not Authenticated → Welcome → Login/Signup
  ↓
Authenticated
  ↓
[Check Profile] → onboardingComplete: false
  ↓
Personality Selection (save to DB)
  ↓
Name Input (save to DB)
  ↓
Introduction (mark complete in DB)
  ↓
Main App
```

## Error Handling

### Authentication Errors
- Invalid credentials → Show error message
- Network error → Retry with exponential backoff
- Token expired → Refresh token automatically
- Verification required → Show verification prompt

### Onboarding Errors
- API failure → Save state locally, retry on next load
- Invalid input → Show validation message
- Network timeout → Allow offline mode, sync later

## Testing Strategy

### Unit Tests
- Auth functions (login, signup, token verification)
- Component rendering (each onboarding screen)
- State management (localStorage, API calls)
- Input validation

### Integration Tests
- Complete onboarding flow (new user)
- Login flow (returning user)
- Google OAuth flow
- Token refresh
- API authorization

### E2E Tests
- New user signup → onboarding → main app
- Returning user login → main app
- Google sign-in → onboarding/main app
- Logout → login again

## Security Considerations

- JWT tokens stored in localStorage (XSS protection via CSP)
- HTTPS only in production
- Cognito handles password hashing and security
- API Gateway validates JWT on every request
- No sensitive data in frontend code
- Rate limiting on auth endpoints

## Performance Optimization

- Cache JWKS keys in Lambda authorizer
- Lazy load onboarding screens
- Preload main app assets during onboarding
- Minimize API calls (batch profile updates)
- Use Amplify Auth caching

---

**Status**: Design complete ✅  
**Next**: Create tasks.md for implementation
