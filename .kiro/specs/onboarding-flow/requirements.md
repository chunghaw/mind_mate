# Onboarding Flow - Requirements

## Introduction

Implement the complete first-time user onboarding experience as specified in PRODUCT_VISION.md. This creates an emotional connection between the user and their AI companion through a guided setup process.

## Requirements

### Requirement 1: Welcome Screen

**User Story:** As a first-time user, I want to see a welcoming introduction, so that I understand what Mind Mate is and feel invited to start.

#### Acceptance Criteria
1. WHEN user opens the app for the first time THEN system SHALL display welcome screen
2. WHEN welcome screen is shown THEN system SHALL display app name "Mind Mate"
3. WHEN welcome screen is shown THEN system SHALL display tagline "Your AI Pet Companion for Mental Wellness"
4. WHEN welcome screen is shown THEN system SHALL display "Get Started" button
5. WHEN user clicks "Get Started" THEN system SHALL navigate to login screen

### Requirement 2: Authentication (Login/Signup)

**User Story:** As a user, I want to securely log in with username/password or Google, so that my data is protected and I can access my companion from any device.

#### Acceptance Criteria

**Login Screen:**
1. WHEN user reaches login screen THEN system SHALL display "Welcome to Mind Mate" message
2. WHEN login screen is shown THEN system SHALL display username input field
3. WHEN login screen is shown THEN system SHALL display password input field
4. WHEN login screen is shown THEN system SHALL display "Log In" button
5. WHEN login screen is shown THEN system SHALL display "Sign Up" link
6. WHEN login screen is shown THEN system SHALL display "Sign in with Google" button

**Username/Password Login:**
7. WHEN user enters username and password THEN system SHALL validate inputs are not empty
8. WHEN user clicks "Log In" THEN system SHALL authenticate via AWS Cognito
9. WHEN authentication succeeds THEN system SHALL receive JWT token and userId
10. WHEN authentication succeeds THEN system SHALL check if onboarding is complete
11. WHEN onboarding is complete THEN system SHALL navigate to main app
12. WHEN onboarding is not complete THEN system SHALL navigate to personality selection
13. WHEN authentication fails THEN system SHALL display error message

**Sign Up:**
14. WHEN user clicks "Sign Up" THEN system SHALL navigate to signup screen
15. WHEN signup screen is shown THEN system SHALL display username input field
16. WHEN signup screen is shown THEN system SHALL display email input field
17. WHEN signup screen is shown THEN system SHALL display password input field
18. WHEN signup screen is shown THEN system SHALL display "Create Account" button
19. WHEN user submits signup THEN system SHALL create account via AWS Cognito
20. WHEN account is created THEN system SHALL send verification email
21. WHEN account is created THEN system SHALL navigate to personality selection
22. WHEN signup fails THEN system SHALL display error message

**Google OAuth:**
23. WHEN user clicks "Sign in with Google" THEN system SHALL redirect to Google OAuth
24. WHEN Google authentication succeeds THEN system SHALL receive user info and token
25. WHEN Google authentication succeeds THEN system SHALL create/update Cognito user
26. WHEN Google user is new THEN system SHALL navigate to personality selection
27. WHEN Google user is returning THEN system SHALL navigate to main app

### Requirement 3: Personality Selection

**User Story:** As a first-time user, I want to choose my companion's personality, so that I get support in a style that resonates with me.

#### Acceptance Criteria
1. WHEN user reaches personality selection THEN system SHALL display 4 personality options
2. WHEN personality options are shown THEN system SHALL display Gentle Guardian (🐶)
3. WHEN personality options are shown THEN system SHALL display Playful Pal (🐱)
4. WHEN personality options are shown THEN system SHALL display Focused Friend (🐉)
5. WHEN personality options are shown THEN system SHALL display Sensitive Soul (🦊)
6. WHEN user selects a personality THEN system SHALL highlight the selected option
7. WHEN user confirms selection THEN system SHALL store personality in profile
8. WHEN personality is stored THEN system SHALL navigate to name input

### Requirement 4: User Name Collection

**User Story:** As a first-time user, I want my companion to ask for my name, so that our interaction feels personal and caring.

#### Acceptance Criteria
1. WHEN user reaches name input THEN system SHALL display pet avatar with selected personality
2. WHEN name input is shown THEN system SHALL display personality-specific greeting
3. WHEN name input is shown THEN system SHALL ask "What should I call you?"
4. WHEN user enters name THEN system SHALL validate name is not empty
5. WHEN user submits name THEN system SHALL store name in profile
6. WHEN name is stored THEN system SHALL navigate to introduction

### Requirement 5: Pet Introduction

**User Story:** As a first-time user, I want my companion to introduce itself, so that I understand what it will do and feel welcomed.

#### Acceptance Criteria
1. WHEN user reaches introduction THEN system SHALL display pet avatar
2. WHEN introduction is shown THEN system SHALL use user's name in greeting
3. WHEN introduction is shown THEN system SHALL introduce pet's name
4. WHEN introduction is shown THEN system SHALL explain Mind Mate's purpose
5. WHEN introduction is shown THEN system SHALL display "Let's Go!" button
6. WHEN user clicks "Let's Go!" THEN system SHALL navigate to main app
7. WHEN user clicks "Let's Go!" THEN system SHALL mark onboarding as complete

### Requirement 6: Returning User Experience

**User Story:** As a returning user, I want to skip onboarding, so that I can quickly access the main app.

#### Acceptance Criteria
1. WHEN user opens app THEN system SHALL check if onboarding is complete
2. WHEN onboarding is complete THEN system SHALL navigate directly to main app
3. WHEN onboarding is not complete THEN system SHALL start from welcome screen
4. WHEN user profile exists THEN system SHALL load personality and name
5. WHEN main app loads THEN system SHALL display personalized greeting

### Requirement 7: State Persistence

**User Story:** As a user, I want my onboarding progress saved, so that I don't lose my setup if I close the app.

#### Acceptance Criteria
1. WHEN user completes any onboarding step THEN system SHALL save progress to localStorage
2. WHEN user returns to app THEN system SHALL resume from last completed step
3. WHEN onboarding is complete THEN system SHALL set onboardingComplete flag
4. WHEN user data is saved THEN system SHALL include userId, personality, userName, petName
5. WHEN app loads THEN system SHALL check localStorage before showing welcome screen

## Technical Notes

### Authentication
- Use **AWS Cognito** for user management
- Support username/password authentication
- Support Google OAuth 2.0 (federated identity)
- Store JWT tokens in localStorage
- Use Cognito userId (sub) as primary user identifier

### Frontend
- Use AWS Amplify Auth library for Cognito integration
- Implement Google Sign-In button
- Store auth tokens securely
- Handle token refresh automatically
- Implement logout functionality

### Backend
- Verify JWT tokens in Lambda authorizer
- Use Cognito userId for all DynamoDB operations
- Create user profile on first login
- Link Google accounts to Cognito users

### State Management
- Store auth state in localStorage
- Store onboarding progress in DynamoDB
- Use personality to determine pet emoji and greeting style
- Implement smooth transitions between steps
- Maintain gentle green theme throughout

## Success Criteria

- First-time users complete onboarding flow
- Returning users skip directly to main app
- User feels personal connection with companion
- Personality affects all future interactions
- State persists across sessions
