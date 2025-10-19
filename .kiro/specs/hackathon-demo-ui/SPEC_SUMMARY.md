# Hackathon Demo UI - Spec Summary

## Overview
This spec defines the implementation of a hybrid AI-first hackathon demo UI for Mind Mate, optimized for a 3-minute presentation that showcases both technical sophistication and user experience.

## Key Features
1. **AI Wellness Hero Section** (40%) - Sticky header with animated wellness score, 49 features display, risk level, and ML confidence
2. **Processing Animation** - Visual representation of ML feature extraction and model inference
3. **Chat Interface** (30%) - AI companion with personalized insights and inline metrics
4. **ML Insight Cards** (20%) - AI-generated insights with confidence levels
5. **Full AI Report Modal** - Detailed feature breakdown and 7-day prediction
6. **Quick Actions Bar** (10%) - Fast access to mood logging and AI analysis

## Tech Stack
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Backend**: AWS Lambda (existing)
  - logMood
  - calculateRiskScore
  - extractMoodFeatures
  - extractBehavioralFeatures
  - extractSentimentFeatures
- **Storage**: DynamoDB (EmoCompanion, RiskAssessments tables)

## Color Scheme
- Primary Green: #86efac, #4ade80, #bbf7d0
- AI Accents: #5eead4 (teal), #6ee7b7 (mint)
- Background: #f0f9f4
- Text: #2d3748

## Implementation Phases
1. **Phase 1**: Core structure and CSS system
2. **Phase 2**: AI Wellness Hero section
3. **Phase 3**: Processing animation
4. **Phase 4**: Chat interface
5. **Phase 5**: ML insight cards
6. **Phase 6**: Full AI report modal
7. **Phase 7**: Quick actions bar
8. **Phase 8**: Backend integration
9. **Phase 9**: State management
10. **Phase 10**: Demo script flow
11. **Phase 11**: Responsive design
12. **Phase 12**: Polish and optimize
13. **Phase 13**: Deployment

## Demo Script Timeline
- **0:00-0:30**: Show hero section with animated metrics
- **0:30-1:30**: Demonstrate ML processing with animation
- **1:30-2:15**: Display full AI report modal
- **2:15-3:00**: Show complete integrated view

## Success Criteria
- ✅ Displays 49 features analyzed
- ✅ Shows 94% ML confidence
- ✅ Animates wellness score smoothly
- ✅ Processes mood logs with visual feedback
- ✅ Integrates with real Lambda functions
- ✅ Falls back gracefully to demo mode
- ✅ Completes demo in 3 minutes

## Files
- **Requirements**: `.kiro/specs/hackathon-demo-ui/requirements.md`
- **Design**: `.kiro/specs/hackathon-demo-ui/design.md`
- **Tasks**: `.kiro/specs/hackathon-demo-ui/tasks.md`
- **Implementation**: `frontend/mind-mate-hackathon.html` (to be created)

## Next Steps
To begin implementation, open `tasks.md` and click "Start task" next to task 1.

The implementation will be done incrementally, with each task building on the previous ones. You can review and test each phase before moving to the next.
