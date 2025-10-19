# Implementation Plan - Hackathon Demo UI

- [x] 1. Set up project structure and base HTML
  - Create `frontend/mind-mate-hackathon.html` with semantic HTML5 structure
  - Add viewport meta tag and responsive configuration
  - Set up container with max-width 480px and centered layout
  - _Requirements: 1, 9_

- [x] 2. Implement CSS styling system
  - [x] 2.1 Define CSS custom properties for color scheme
    - Primary green colors (#86efac, #4ade80, #bbf7d0)
    - AI accent colors (#5eead4, #6ee7b7)
    - Neutral colors (backgrounds, text, borders)
    - _Requirements: 1, 10_
  
  - [x] 2.2 Create base styles and typography
    - Set up font families (Inter, -apple-system)
    - Define font sizes and weights
    - Add responsive font scaling
    - _Requirements: 9, 10_
  
  - [x] 2.3 Implement animation keyframes
    - countUp animation for score
    - slideIn animation for cards
    - pulse animation for avatar
    - spin animation for loading icons
    - typing animation for dots
    - _Requirements: 10_

- [ ] 3. Build AI Wellness Hero section
  - [x] 3.1 Create hero HTML structure
    - Add header with title and AI badge
    - Create wellness score display area
    - Add progress bar container
    - Build metrics grid (2x2)
    - Add "View Full AI Report" button
    - _Requirements: 1_
  
  - [ ] 3.2 Style hero section with gradient background
    - Apply green gradient (#86efac → #4ade80)
    - Add sticky positioning with z-index 100
    - Style metric cards with glassmorphism effect
    - Add box shadow for depth
    - _Requirements: 1, 10_
  
  - [ ] 3.3 Implement score counter animation
    - Create WellnessHero JavaScript class
    - Implement animateScore() method with easeOut
    - Add requestAnimationFrame loop
    - Update DOM with animated values
    - _Requirements: 1, 10_
  
  - [ ] 3.4 Implement progress bar animation
    - Add CSS transition with cubic-bezier timing
    - Create updateProgressBar() method
    - Animate width from 0% to target percentage
    - _Requirements: 1, 10_
  
  - [ ] 3.5 Add next assessment countdown timer
    - Create countdown function
    - Update every second
    - Format as "Xh Ym"
    - _Requirements: 1_

- [ ] 4. Build processing animation component
  - [ ] 4.1 Create processing animation HTML structure
    - Add processing title
    - Create three processing steps
    - Add step icons and labels
    - _Requirements: 2_
  
  - [ ] 4.2 Implement ProcessingAnimation class
    - Create show() method to add to DOM
    - Implement animate() method for stage transitions
    - Add timing for each stage (1s intervals)
    - Implement auto-removal after completion
    - _Requirements: 2_
  
  - [ ] 4.3 Style processing animation
    - Add teal border and background
    - Style step icons with loading state
    - Add spin animation for loading icons
    - _Requirements: 2, 10_

- [ ] 5. Build chat interface
  - [ ] 5.1 Create chat container structure
    - Add companion header with avatar and info
    - Create scrollable messages container
    - Add custom scrollbar styling
    - _Requirements: 3_
  
  - [ ] 5.2 Implement ChatInterface class
    - Create addMessage() method
    - Implement renderMessage() method
    - Add formatText() for highlighting technical terms
    - Implement scrollToBottom() utility
    - _Requirements: 3_
  
  - [ ] 5.3 Style message bubbles
    - Create companion message style (left-aligned)
    - Create user message style (right-aligned, green)
    - Add border radius and shadows
    - Style message timestamps
    - _Requirements: 3, 10_
  
  - [ ] 5.4 Implement typing indicator
    - Create showTyping() method
    - Add three animated dots
    - Implement hideTyping() method
    - Style with typing animation
    - _Requirements: 3, 10_
  
  - [ ] 5.5 Add input area
    - Create text input field
    - Add send button with arrow icon
    - Implement handleKeyPress for Enter key
    - Style with focus states
    - _Requirements: 3_

- [ ] 6. Build ML insight card component
  - [ ] 6.1 Create InsightCard class
    - Implement static create() method
    - Implement static add() method
    - Add slide-in animation trigger
    - _Requirements: 4_
  
  - [ ] 6.2 Style insight cards
    - Add light green tinted background
    - Create header with icon and label
    - Style body text
    - Add footer with confidence and data points
    - Apply slide-in animation
    - _Requirements: 4, 10_

- [ ] 7. Build full AI report modal
  - [ ] 7.1 Create modal HTML structure
    - Add modal overlay with backdrop
    - Create modal content container
    - Add modal header with title and close button
    - Create modal body container
    - _Requirements: 5_
  
  - [ ] 7.2 Implement modal functions
    - Create showFullReport() function
    - Implement generateFullReport() function
    - Add closeModal() function
    - Handle click outside to close
    - _Requirements: 5_
  
  - [ ] 7.3 Create feature breakdown display
    - Group features by category (Mood, Behavioral, Sentiment)
    - Display feature values with labels
    - Add visual indicators (arrows, colors)
    - _Requirements: 5_
  
  - [ ] 7.4 Add 7-day prediction chart
    - Create simple bar chart or line visualization
    - Display daily risk percentages
    - Show intervention threshold line
    - Highlight current risk vs threshold
    - _Requirements: 5_
  
  - [ ] 7.5 Style modal
    - Add backdrop blur effect
    - Style modal content with border radius
    - Add max-height and scrolling
    - Style close button
    - _Requirements: 5, 10_

- [ ] 8. Build quick actions bar
  - [ ] 8.1 Create quick actions HTML
    - Add three action buttons (Quick Mood, AI Analysis, Activities)
    - Use emoji icons with text labels
    - _Requirements: 6_
  
  - [ ] 8.2 Style quick actions
    - Create pill-shaped buttons
    - Add gradient to AI Analysis button
    - Implement hover effects
    - Add horizontal scroll for mobile
    - _Requirements: 6, 10_
  
  - [ ] 8.3 Implement quick action handlers
    - Create quickMood() function
    - Create triggerAIAnalysis() function
    - Create showActivities() function
    - _Requirements: 6_

- [ ] 9. Integrate with backend APIs
  - [ ] 9.1 Create APIClient class
    - Set up API_BASE constant from environment
    - Implement error handling wrapper
    - Add getDemoRiskData() fallback
    - _Requirements: 7_
  
  - [ ] 9.2 Implement logMood API integration
    - Create logMood() method
    - POST to /mood endpoint
    - Handle response and update UI
    - Add error handling
    - _Requirements: 7_
  
  - [ ] 9.3 Implement calculateRisk API integration
    - Create calculateRisk() method
    - POST to /calculate-risk endpoint
    - Parse response with 49 features
    - Update wellness hero with results
    - Trigger processing animation
    - _Requirements: 7, 2_
  
  - [ ] 9.4 Add demo mode fallback
    - Detect API failures
    - Return simulated data
    - Show user-friendly message
    - _Requirements: 7_

- [ ] 10. Implement state management
  - [ ] 10.1 Create AppState class
    - Define wellness state properties
    - Define chat state properties
    - Define processing state properties
    - Define modal state properties
    - _Requirements: All_
  
  - [ ] 10.2 Implement state update methods
    - Create updateWellness() method
    - Create updateChat() method
    - Create updateProcessing() method
    - Create updateModal() method
    - _Requirements: All_
  
  - [ ] 10.3 Add state persistence
    - Save to localStorage
    - Load on app initialization
    - Handle missing data gracefully
    - _Requirements: 7_

- [ ] 11. Implement demo script flow
  - [ ] 11.1 Create demo initialization
    - Load with wellness score 8.5
    - Show 49 features analyzed
    - Display 94% confidence
    - Set risk level to LOW
    - Start countdown timer
    - _Requirements: 8_
  
  - [ ] 11.2 Add welcome message
    - Display companion greeting
    - Include AI analysis mention
    - Add initial insight card
    - _Requirements: 8_
  
  - [ ] 11.3 Implement quick mood demo flow
    - Trigger processing animation
    - Call calculateRisk API
    - Display AI response with metrics
    - Add new insight card
    - _Requirements: 8_
  
  - [ ] 11.4 Test full demo script timing
    - Verify 0:00-0:30 hero display
    - Verify 0:30-1:30 processing flow
    - Verify 1:30-2:15 modal display
    - Verify 2:15-3:00 complete view
    - _Requirements: 8_

- [ ] 12. Add responsive design
  - [ ] 12.1 Implement mobile layout
    - Set max-width 480px
    - Adjust font sizes for small screens
    - Ensure touch targets are 44px minimum
    - _Requirements: 9_
  
  - [ ] 12.2 Implement desktop layout
    - Center container with box shadow
    - Maintain mobile-first design
    - Add hover states for desktop
    - _Requirements: 9_
  
  - [ ] 12.3 Test on multiple viewports
    - Test on 320px (small mobile)
    - Test on 375px (iPhone)
    - Test on 768px (tablet)
    - Test on 1024px+ (desktop)
    - _Requirements: 9_

- [ ] 13. Polish and optimize
  - [ ] 13.1 Optimize animations
    - Ensure 60fps performance
    - Use transform and opacity only
    - Add will-change hints
    - Test on lower-end devices
    - _Requirements: 10_
  
  - [ ] 13.2 Add accessibility features
    - Add ARIA labels to interactive elements
    - Ensure keyboard navigation works
    - Test color contrast ratios
    - Add focus indicators
    - _Requirements: Design_
  
  - [ ] 13.3 Test error scenarios
    - Test with API offline
    - Test with slow network
    - Test with invalid data
    - Verify fallback messages display
    - _Requirements: 7_
  
  - [ ] 13.4 Final demo rehearsal
    - Run through complete 3-minute script
    - Verify all animations work smoothly
    - Test modal open/close
    - Verify all metrics display correctly
    - _Requirements: 8_

- [ ] 14. Add tooltips to AI Report indicators
  - [ ] 14.1 Create tooltip component
    - Add tooltip HTML structure with info icon
    - Style tooltip with dark background and white text
    - Position tooltip relative to indicator
    - Add hover and click interactions
    - _Requirements: 5_
  
  - [ ] 14.2 Add explanatory text for each indicator
    - Temporal trend: Explain 7-day mood trajectory
    - Mood volatility: Explain stability measurement
    - Consecutive low mood days: Explain risk factor
    - Mean affective score: Explain baseline mood
    - Daily interaction frequency: Explain engagement metric
    - Platform engagement score: Explain usage patterns
    - Circadian disruption: Explain sleep pattern impact
    - Sentiment scores: Explain text analysis metrics
    - _Requirements: 5_
  
  - [ ] 14.3 Implement tooltip JavaScript
    - Create Tooltip class with show/hide methods
    - Add event listeners for hover/click
    - Handle mobile touch events
    - Auto-hide on outside click
    - _Requirements: 5_

- [ ] 15. Implement conversational AI chat
  - [ ] 15.1 Integrate with AWS Bedrock chat API
    - Create sendChatMessage() function
    - POST user message to chat endpoint
    - Receive streaming or complete response
    - Display AI response in chat bubble
    - _Requirements: 3, 7_
  
  - [ ] 15.2 Implement conversation context
    - Maintain conversation history
    - Send previous messages for context
    - Include user wellness data in system prompt
    - Personalize responses based on risk level
    - _Requirements: 3, 7_
  
  - [ ] 15.3 Add chat features
    - Show typing indicator while waiting
    - Handle multi-turn conversations
    - Add error handling for failed messages
    - Implement retry logic
    - _Requirements: 3_
  
  - [ ] 15.4 Style conversational responses
    - Format AI responses with proper line breaks
    - Highlight key insights in responses
    - Add timestamp to each message
    - Ensure proper scrolling behavior
    - _Requirements: 3, 10_

- [ ] 16. Create deployment version
  - Copy `mind-mate-hackathon.html` to production location
  - Update API_BASE to production URL
  - Minify CSS and JavaScript (optional)
  - Test in production environment
  - _Requirements: All_
