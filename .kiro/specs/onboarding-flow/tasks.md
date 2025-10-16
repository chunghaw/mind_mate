# Onboarding Flow - Implementation Tasks

## Task 1: Set up AWS Cognito Infrastructure
Create and configure Cognito User Pool with Google OAuth support.

- [ ] 1.1 Create Cognito User Pool via CloudFormation
  - Define password policy (min 8 chars, uppercase, lowercase, numbers)
  - Set email as username attribute
  - Enable email verification
  - Add custom attribute `custom:hasPassword`
  - _Requirements: 2.14-2.22_

- [ ] 1.2 Configure Google Identity Provider
  - Create Google OAuth 2.0 credentials in Google Cloud Console
  - Add Google as identity provider in Cognito
  - Configure attribute mapping (email, name, sub)
  - Set callback URLs for local and production
  - _Requirements: 2.23-2.27_

- [ ] 1.3 Create Cognito User Pool Client
  - Configure for web app (no client secret)
  - Enable OAuth flows (code, implicit)
  - Add allowed OAuth scopes (email, openid, profile)
  - Set callback and logout URLs
  - _Requirements: 2.1-2.27_

- [ ] 1.4 Create DynamoDB GSI for email lookup
  - Add Global Secondary Index on email field
  - Configure projection (ALL attributes)
  - _Requirements: 2.8-2.10_

## Task 2: Implement Lambda Authorizer
Create JWT verification for API Gateway.

- [ ] 2.1 Create cognitoAuthorizer Lambda function
  - Fetch JWKS keys from Cognito
  - Verify JWT token signature
  - Extract userId from token
  - Generate IAM policy (Allow/Deny)
  - Cache JWKS keys for performance
  - _Requirements: 2.7-2.13_

- [ ] 2.2 Configure API Gateway authorizer
  - Attach Lambda authorizer to API Gateway
  - Set authorization header as token source
  - Configure token validation
  - _Requirements: 2.7-2.13_

- [ ] 2.3 Update existing Lambda functions
  - Modify getProfile to use authorizer userId
  - Modify updateProfile to use authorizer userId
  - Modify logMood to use authorizer userId
  - Modify analyzeSelfie to use authorizer userId
  - Modify getStats to use authorizer userId
  - _Requirements: 6.4-6.5_

## Task 3: Create setPassword Lambda
Allow Google users to set username/password.

- [ ] 3.1 Create setPassword Lambda function
  - Get userId from authorizer context
  - Parse username and password from request body
  - Call Cognito AdminSetUserPassword API
  - Update user attributes (preferred_username, custom:hasPassword)
  - Return success response
  - _Requirements: 2.23-2.27_

- [ ] 3.2 Add API Gateway route
  - Create POST /set-password route
  - Attach Lambda integration
  - Enable CORS
  - Require authorization
  - _Requirements: 2.23-2.27_

## Task 4: Implement Frontend Authentication
Integrate AWS Amplify Auth in frontend.

- [ ] 4.1 Install and configure Amplify
  - Add AWS Amplify library to project
  - Configure Auth with Cognito User Pool details
  - Set OAuth configuration (domain, scopes, redirects)
  - _Requirements: 2.1-2.27_

- [ ] 4.2 Implement auth utility functions
  - Create login(username, password) function
  - Create signUp(username, email, password) function
  - Create signInWithGoogle() function
  - Create setPasswordForGoogleUser(username, password) function
  - Create checkAuthStatus() function
  - Create logout() function
  - _Requirements: 2.1-2.27_

- [ ] 4.3 Implement token management
  - Store JWT token in localStorage
  - Store userId in localStorage
  - Implement automatic token refresh
  - Clear tokens on logout
  - _Requirements: 7.1-7.5_

## Task 5: Create Onboarding UI Components
Build all onboarding screens with gentle green theme.

- [ ] 5.1 Create WelcomeScreen component
  - Display Mind Mate logo/title
  - Show tagline "Your AI Pet Companion for Mental Wellness"
  - Add "Get Started" button
  - Navigate to LoginScreen on click
  - Apply gentle green theme
  - _Requirements: 1.1-1.5_

- [ ] 5.2 Create LoginScreen component
  - Add username input field
  - Add password input field
  - Add "Log In" button
  - Add "Sign Up" link
  - Add "Sign in with Google" button
  - Implement form validation
  - Show error messages
  - Call login() on submit
  - Apply gentle green theme
  - _Requirements: 2.1-2.13_

- [ ] 5.3 Create SignupScreen component
  - Add username input field
  - Add email input field
  - Add password input field
  - Add "Create Account" button
  - Implement form validation
  - Show verification message after signup
  - Call signUp() on submit
  - Apply gentle green theme
  - _Requirements: 2.14-2.22_

- [ ] 5.4 Create SetPasswordScreen component
  - Show "Set up direct login" message
  - Add username input (optional, default to email)
  - Add password input
  - Add "Save" button
  - Implement validation
  - Call setPasswordForGoogleUser() on submit
  - Apply gentle green theme
  - _Requirements: 2.23-2.27_

- [ ] 5.5 Create PersonalitySelector component
  - Display 4 personality cards (Gentle, Playful, Focused, Sensitive)
  - Show emoji icons (🐶🐱🐉🦊)
  - Show personality descriptions
  - Highlight selected personality
  - Add "Continue" button
  - Call API to save personality
  - Navigate to NameInput
  - Apply gentle green theme
  - _Requirements: 3.1-3.8_

- [ ] 5.6 Create NameInput component
  - Display pet avatar with selected personality
  - Show personality-specific greeting
  - Ask "What should I call you?"
  - Add text input for user name
  - Validate input (not empty)
  - Add "Continue" button
  - Call API to save name
  - Navigate to Introduction
  - Apply gentle green theme
  - _Requirements: 4.1-4.6_

- [ ] 5.7 Create Introduction component
  - Display pet avatar
  - Greet user by name
  - Introduce pet's name
  - Explain Mind Mate's purpose
  - Add "Let's Go!" button
  - Mark onboarding complete in API
  - Navigate to Main App
  - Apply gentle green theme
  - _Requirements: 5.1-5.7_

## Task 6: Implement Onboarding State Management
Handle navigation and state persistence.

- [ ] 6.1 Create onboarding state manager
  - Track current onboarding step
  - Store step in localStorage
  - Implement navigation between steps
  - Handle back button
  - _Requirements: 7.1-7.5_

- [ ] 6.2 Implement app initialization logic
  - Check auth status on app load
  - Check onboarding status
  - Navigate to appropriate screen
  - Handle returning users
  - _Requirements: 6.1-6.5_

- [ ] 6.3 Implement profile API calls
  - Create fetchProfile(userId, token) function
  - Create savePersonality(personality) function
  - Create saveName(userName, petName) function
  - Create markOnboardingComplete() function
  - _Requirements: 3.8, 4.6, 5.7_

## Task 7: Update Main App Integration
Connect onboarding to existing main app.

- [ ] 7.1 Update main app to require authentication
  - Check for auth token on load
  - Redirect to login if not authenticated
  - Load user profile after auth
  - _Requirements: 6.1-6.5_

- [ ] 7.2 Implement personalized greeting
  - Use userName in greetings
  - Use petName in UI
  - Use personality for AI responses
  - _Requirements: 6.5_

- [ ] 7.3 Add logout functionality
  - Add logout button in settings
  - Clear localStorage on logout
  - Call Auth.signOut()
  - Redirect to welcome screen
  - _Requirements: 6.1-6.5_

## Task 8: Testing and Polish
Test complete flow and fix issues.

- [ ] 8.1 Test new user signup flow
  - Complete signup with username/password
  - Verify email verification works
  - Complete onboarding
  - Verify profile saved correctly
  - _Requirements: 2.14-2.22_

- [ ] 8.2 Test Google OAuth flow
  - Sign in with Google
  - Set username/password
  - Complete onboarding
  - Logout and login with username/password
  - Verify it works without Google
  - _Requirements: 2.23-2.27_

- [ ] 8.3 Test returning user flow
  - Login with existing account
  - Verify skips onboarding
  - Verify loads profile correctly
  - Verify personalized greeting
  - _Requirements: 6.1-6.5_

- [ ] 8.4 Test error scenarios
  - Invalid credentials
  - Network errors
  - Token expiration
  - Incomplete onboarding
  - _Requirements: All_

- [ ] 8.5 Polish UI and transitions
  - Smooth animations between screens
  - Loading states
  - Error messages
  - Success feedback
  - Consistent gentle green theme
  - _Requirements: All_

## Task 9: Documentation and Deployment
Document changes and deploy to production.

- [ ] 9.1 Update API documentation
  - Document new /set-password endpoint
  - Document authentication requirements
  - Update example requests with auth headers
  - _Requirements: All_

- [ ] 9.2 Create deployment guide
  - Document Cognito setup steps
  - Document Google OAuth setup
  - Document environment variables
  - _Requirements: All_

- [ ] 9.3 Deploy to production
  - Deploy CloudFormation stack with Cognito
  - Deploy Lambda functions
  - Deploy frontend to Amplify
  - Test production deployment
  - _Requirements: All_

---

**Total Tasks**: 9 main tasks, 35 sub-tasks  
**Estimated Time**: 2-3 days  
**Priority**: High (blocks main app usage)
