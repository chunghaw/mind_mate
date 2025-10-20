# Onboarding Flow - Restored ✅

## Overview

The complete onboarding flow has been restored from commit `ebc8330` and integrated with the current hackathon demo.

## Onboarding Screens

### 1. Welcome Screen
- Mind Mate logo and branding
- Tagline: "Your AI Pet Companion for Mental Wellness"
- "Get Started" button

### 2. Login Screen (Google OAuth)
- "Sign in with Google" button
- Powered by AWS Cognito
- Secure OAuth 2.0 flow
- Automatic account creation on first login

### 3. Set Password Screen
- Set username/password for future direct login
- Optional - can skip and use Google OAuth only
- Stored securely in Cognito

### 4. Personality Screen (Pet Selection)
- Choose your AI companion:
  - 🐶 Loyal Dog - "Always by your side"
  - 🐱 Wise Cat - "Calm and understanding"
  - 🐰 Gentle Rabbit - "Soft and caring"
  - 🐻 Strong Bear - "Protective and warm"
  - 🦊 Clever Fox - "Smart and supportive"
- Selection stored in user profile

### 5. Name Screen
- Enter your preferred name
- Personalizes the experience
- AI companion will use this name

### 6. Intro Screen
- Explains key features:
  - Daily mood tracking
  - AI-powered insights
  - Crisis prediction (3-7 days ahead)
  - Personalized support
- "Start Your Journey" button

## Integration

### URLs
- **Onboarding**: `https://main.d3pktquxaop3su.amplifyapp.com/onboarding.html`
- **Main App**: `https://main.d3pktquxaop3su.amplifyapp.com/mind-mate-hackathon.html`

### Flow
```
User visits site
  ↓
onboarding.html (Welcome)
  ↓
Google OAuth Login
  ↓
Set Password (optional)
  ↓
Choose Pet Companion
  ↓
Enter Name
  ↓
View Intro
  ↓
Redirect to mind-mate-hackathon.html
  ↓
Main App (with persistent user ID and preferences)
```

### Data Storage

**localStorage**:
- `mindmate_user_id` - Consistent user identifier
- `mindmate_token` - Cognito JWT token
- `mindmate_userId` - Cognito user ID
- `mindmate_onboardingComplete` - Boolean flag
- `mindmate_companion` - Selected pet emoji
- `mindmate_username` - User's preferred name

**DynamoDB**:
- User profile with companion selection
- Chat history
- Mood logs
- ML predictions

## Authentication

### Cognito Configuration
- **User Pool**: `us-east-1_example`
- **Client ID**: Configured in code
- **Domain**: `mindmate-403745271636.auth.us-east-1.amazoncognito.com`
- **Identity Provider**: Google OAuth

### Google OAuth Setup
Requires Google OAuth credentials configured in Cognito:
1. Google Cloud Console → Create OAuth 2.0 Client
2. Add redirect URI: `https://mindmate-403745271636.auth.us-east-1.amazoncognito.com/oauth2/idpresponse`
3. Configure in Cognito User Pool

## Features

### Personalization
- Pet companion follows user throughout app
- Name used in greetings and conversations
- Preferences saved for future sessions

### Security
- Secure OAuth 2.0 flow
- JWT tokens for API authentication
- Password hashing in Cognito
- HTTPS only

### User Experience
- Smooth animations between screens
- Gentle green theme (mental health friendly)
- Mobile-responsive design
- Clear progress indication

## Testing

### Test the Flow
1. Visit: `https://main.d3pktquxaop3su.amplifyapp.com/onboarding.html`
2. Click "Get Started"
3. Sign in with Google
4. (Optional) Set password
5. Choose a pet companion
6. Enter your name
7. View intro
8. Redirected to main app

### Verify Integration
- Check localStorage for saved data
- Verify user ID persists across sessions
- Confirm chat history loads correctly
- Test that pet selection appears in UI

## Next Steps

### Optional Enhancements
1. **Skip Onboarding**: Add "Continue as Guest" option
2. **Edit Profile**: Allow changing pet/name later
3. **Social Login**: Add Facebook, Apple sign-in
4. **Personality Quiz**: Expand pet selection with quiz
5. **Avatar Customization**: Let users customize pet appearance

### Current Status
✅ Onboarding flow restored
✅ Integrated with main app
✅ Google OAuth working
✅ Pet selection functional
✅ User data persisted
✅ Ready for demo

## Deployment

The onboarding page will be deployed with the next Amplify build (2-3 minutes).

Access it at:
- **Onboarding**: `/onboarding.html`
- **Main App**: `/mind-mate-hackathon.html`

Users can start with onboarding for full experience, or go directly to main app for quick demo.
