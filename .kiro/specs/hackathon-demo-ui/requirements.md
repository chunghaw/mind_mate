# Requirements Document - Hackathon Demo UI

## Introduction

This spec defines the requirements for building a hybrid AI-first hackathon demo UI for Mind Mate. The goal is to create a compelling 3-minute demo that showcases both technical sophistication (ML/AI capabilities) and user experience (empathetic companion interface). The UI must highlight the unique value proposition: predicting mental health crises 3-7 days before they happen using 49 ML features.

## Requirements

### Requirement 1: AI Wellness Hero Section

**User Story:** As a hackathon judge, I want to immediately see the AI/ML capabilities and wellness metrics, so that I understand the technical sophistication of the solution.

#### Acceptance Criteria

1. WHEN the app loads THEN the system SHALL display a prominent AI Wellness Hero section occupying 40% of the viewport
2. WHEN the wellness score is calculated THEN the system SHALL animate the score from 0 to the actual value (e.g., 8.5/10) over 1 second
3. WHEN displaying metrics THEN the system SHALL show:
   - Wellness Score (0-10 scale) with animated progress bar
   - 49 Features Analyzed count
   - Risk Level (LOW/MODERATE/HIGH) with color coding
   - ML Model Confidence percentage (e.g., 94%)
   - Next Assessment countdown timer
4. WHEN the hero section is displayed THEN the system SHALL use a gentle green gradient background (#86efac → #4ade80)
5. WHEN the user clicks "View Full AI Report" THEN the system SHALL open a modal with detailed feature breakdown
6. WHEN the hero section is sticky THEN the system SHALL keep it visible at the top during scrolling

### Requirement 2: Real-Time ML Processing Animation

**User Story:** As a technical judge, I want to see the ML processing pipeline in action, so that I can understand how the system extracts and analyzes features.

#### Acceptance Criteria

1. WHEN a user logs a mood THEN the system SHALL display a processing animation showing:
   - "Extracting 49 features" stage
   - "Running ML model (RF + GB)" stage
   - "Analysis complete" stage
2. WHEN each processing stage completes THEN the system SHALL update the visual indicator with a checkmark
3. WHEN processing is active THEN the system SHALL show animated loading icons
4. WHEN processing completes THEN the system SHALL remove the animation after 1 second
5. WHEN features are extracted THEN the system SHALL invoke the calculateRiskScore Lambda function
6. WHEN the ML model runs THEN the system SHALL display confidence metrics in real-time

### Requirement 3: AI Companion Chat Interface

**User Story:** As a user, I want to interact with an empathetic AI companion that provides personalized insights, so that I feel supported and understood.

#### Acceptance Criteria

1. WHEN the app loads THEN the system SHALL display the AI companion with:
   - Customizable avatar (animated pet emoji)
   - Personality name (e.g., "Gentle Guardian")
   - Status message
2. WHEN the companion sends a message THEN the system SHALL include inline metrics (e.g., "Your mood improved 15% this week")
3. WHEN displaying AI responses THEN the system SHALL show a typing indicator before the message appears
4. WHEN messages are sent THEN the system SHALL store them in DynamoDB with proper structure
5. WHEN the chat loads THEN the system SHALL retrieve the last 50 messages from DynamoDB
6. WHEN AI generates insights THEN the system SHALL highlight technical terms (e.g., "AI analysis") in a different color

### Requirement 4: ML Insight Cards

**User Story:** As a user, I want to see AI-generated insights with confidence levels, so that I trust the recommendations and understand the data backing them.

#### Acceptance Criteria

1. WHEN an insight is generated THEN the system SHALL display it in a card with:
   - Insight icon (🧠)
   - Insight text (concise, actionable)
   - Confidence percentage
   - Number of data points analyzed
2. WHEN an insight card appears THEN the system SHALL animate it sliding in from the right
3. WHEN displaying insights THEN the system SHALL use a light green tinted background (#bbf7d0 with transparency)
4. WHEN multiple insights exist THEN the system SHALL stack them vertically with proper spacing
5. WHEN confidence is below 70% THEN the system SHALL display a warning indicator

### Requirement 5: Full AI Report Modal

**User Story:** As a technical judge, I want to see the detailed feature breakdown and 7-day prediction, so that I can evaluate the ML model's sophistication.

#### Acceptance Criteria

1. WHEN the user clicks "View Full AI Report" THEN the system SHALL display a modal containing:
   - Feature Analysis section (20 mood + 15 behavioral + 14 sentiment features)
   - 7-day risk prediction chart
   - Current risk score vs intervention threshold (60%)
   - Historical accuracy metrics
2. WHEN displaying feature analysis THEN the system SHALL group features by category with visual indicators
3. WHEN showing the 7-day prediction THEN the system SHALL display daily risk percentages in a chart format
4. WHEN the modal is open THEN the system SHALL allow closing via X button or clicking outside
5. WHEN feature data is unavailable THEN the system SHALL show default values with a notice

### Requirement 6: Quick Actions Bar

**User Story:** As a user, I want quick access to common actions, so that I can efficiently log moods and trigger AI analysis.

#### Acceptance Criteria

1. WHEN the app loads THEN the system SHALL display a quick actions bar with:
   - "Quick Mood" button (😄)
   - "AI Analysis" button (🧠) - highlighted with gradient
   - "Activities" button (✨)
2. WHEN the user clicks "Quick Mood" THEN the system SHALL show mood selection options
3. WHEN the user clicks "AI Analysis" THEN the system SHALL trigger the ML processing animation
4. WHEN the user clicks "Activities" THEN the system SHALL display activity suggestions
5. WHEN buttons are displayed THEN the system SHALL use pill-shaped design with icons

### Requirement 7: Backend Integration

**User Story:** As a developer, I want the UI to integrate with existing Lambda functions, so that real ML predictions and data storage work correctly.

#### Acceptance Criteria

1. WHEN a mood is logged THEN the system SHALL POST to /mood endpoint with userId, mood, tags, and notes
2. WHEN risk calculation is needed THEN the system SHALL POST to /calculate-risk endpoint with userId
3. WHEN the response is received THEN the system SHALL parse:
   - riskScore (0-1)
   - riskLevel (LOW/MODERATE/HIGH)
   - riskFactors array
   - confidence percentage
   - features object (49 features)
4. WHEN chat messages are sent THEN the system SHALL store them in DynamoDB with proper PK/SK structure
5. WHEN errors occur THEN the system SHALL display user-friendly error messages
6. WHEN API calls fail THEN the system SHALL fall back to demo mode with simulated data

### Requirement 8: Demo Script Compatibility

**User Story:** As a presenter, I want the UI to support the 3-minute demo script, so that I can effectively showcase all features within the time limit.

#### Acceptance Criteria

1. WHEN the demo starts (0:00-0:30) THEN the system SHALL display the hero section with animated metrics
2. WHEN demonstrating AI processing (0:30-1:30) THEN the system SHALL show the full processing animation
3. WHEN showing unique features (1:30-2:15) THEN the system SHALL open the full AI report modal
4. WHEN concluding (2:15-3:00) THEN the system SHALL display all elements simultaneously
5. WHEN transitioning between sections THEN the system SHALL use smooth animations
6. WHEN the demo completes THEN the system SHALL return to the main view

### Requirement 9: Responsive Design

**User Story:** As a user on any device, I want the UI to work seamlessly, so that I can access Mind Mate from mobile or desktop.

#### Acceptance Criteria

1. WHEN viewed on mobile THEN the system SHALL display in a single column layout (max-width: 480px)
2. WHEN viewed on desktop THEN the system SHALL center the container with box shadow
3. WHEN the viewport is small THEN the system SHALL adjust font sizes appropriately
4. WHEN scrolling is needed THEN the system SHALL provide smooth scrolling with custom scrollbar styling
5. WHEN the hero section is sticky THEN the system SHALL maintain proper z-index layering

### Requirement 10: Performance and Polish

**User Story:** As a hackathon judge, I want a polished, professional UI with smooth animations, so that I perceive the product as production-ready.

#### Acceptance Criteria

1. WHEN animations run THEN the system SHALL use hardware-accelerated CSS transitions
2. WHEN the score counter animates THEN the system SHALL use ease-out easing for natural motion
3. WHEN the progress bar fills THEN the system SHALL use cubic-bezier timing function
4. WHEN cards slide in THEN the system SHALL complete the animation in 300ms
5. WHEN the companion avatar is displayed THEN the system SHALL apply a subtle pulse animation
6. WHEN hover effects are triggered THEN the system SHALL provide immediate visual feedback
