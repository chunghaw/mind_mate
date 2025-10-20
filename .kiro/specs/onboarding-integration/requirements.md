# Onboarding Integration Requirements

## Goal
Integrate the onboarding flow from `onboarding.html` (commit ebc8330) into `mind-mate-hackathon.html` so users see onboarding screens on first visit, then the main 3-tab app.

## Requirements

### 1. Show Onboarding on First Visit
- WHEN user visits for first time THEN show onboarding screens
- WHEN user completes onboarding THEN show main app
- WHEN user returns THEN skip onboarding, show main app directly

### 2. Onboarding Screens to Integrate
From `onboarding.html`:
1. Welcome screen with "Get Started with Google" button
2. Google OAuth login (Cognito)
3. Set password screen (optional)
4. Pet companion selection (🐶🐱🐉🦊)
5. Name input screen
6. Intro screen

### 3. Main App Screens (Keep Existing)
From `mind-mate-hackathon.html`:
1. Dashboard tab
2. Chat tab  
3. AI Report tab

### 4. Integration Logic
- Add onboarding CSS to existing styles
- Add onboarding HTML screens before main app
- Hide main app initially if first visit
- Show onboarding screens with screen transitions
- On completion: hide onboarding, show main app, save to localStorage
- On return visit: check localStorage, skip onboarding

### 5. Data Flow
- Onboarding saves: user ID, pet selection, username to localStorage
- Main app reads: user ID, pet emoji, username from localStorage
- Chat uses saved user ID for persistent history
- Pet emoji appears in chat interface

## Success Criteria
- First-time user sees full onboarding flow
- Returning user goes straight to main app
- Pet selection persists and shows in chat
- Username used in greetings
- No duplicate code or conflicts
- All existing features still work
