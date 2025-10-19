# Design Document - Hackathon Demo UI

## Overview

This design document outlines the technical architecture and implementation approach for the Mind Mate Hackathon Demo UI. The design follows a hybrid approach that balances AI-first presentation with empathetic user experience, optimized for a 3-minute demo presentation.

The UI is built as a single-page application (SPA) using vanilla JavaScript, HTML5, and CSS3, integrating with existing AWS Lambda backend services for real ML predictions and data persistence.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (SPA)                       │
│  ┌──────────────────────────────────────────────────┐  │
│  │  AI Wellness Hero (Sticky Header - 40%)          │  │
│  │  - Animated Score Counter                        │  │
│  │  - 49 Features Display                           │  │
│  │  - Risk Level Indicator                          │  │
│  │  - Confidence Metrics                            │  │
│  │  - Next Assessment Timer                         │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Chat Container (Scrollable - 30%)               │  │
│  │  - Companion Avatar & Info                       │  │
│  │  - Message Bubbles (User + AI)                   │  │
│  │  - ML Insight Cards                              │  │
│  │  - Processing Animations                         │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Input Area (20%)                                │  │
│  │  - Text Input Field                              │  │
│  │  - Send Button                                   │  │
│  │  - Quick Actions Bar                             │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Modal Overlay (Hidden by default - 10%)        │  │
│  │  - Full AI Report                                │  │
│  │  - Feature Breakdown                             │  │
│  │  - 7-Day Prediction Chart                        │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↓
                    API Gateway
                          ↓
        ┌─────────────────┴─────────────────┐
        ↓                                    ↓
┌───────────────┐                  ┌──────────────────┐
│ logMood       │                  │ calculateRiskScore│
│ Lambda        │                  │ Lambda            │
└───────┬───────┘                  └────────┬─────────┘
        ↓                                   ↓
        │                          ┌────────┴────────┐
        │                          ↓                 ↓
        │                  ┌───────────────┐ ┌──────────────┐
        │                  │extractMood    │ │extractBehavior│
        │                  │Features       │ │Features       │
        │                  └───────────────┘ └──────────────┘
        │                          ↓
        │                  ┌───────────────┐
        │                  │extractSentiment│
        │                  │Features       │
        │                  └───────────────┘
        ↓                          ↓
┌─────────────────────────────────────────┐
│         DynamoDB Tables                 │
│  - EmoCompanion (Moods, Messages)       │
│  - RiskAssessments (ML Predictions)     │
└─────────────────────────────────────────┘
```

### Component Architecture

```
App State Manager
├── Wellness State
│   ├── score: number (0-10)
│   ├── riskLevel: string
│   ├── riskScore: number (0-1)
│   ├── confidence: number (0-100)
│   ├── featuresAnalyzed: number (49)
│   └── nextAssessment: string
├── Chat State
│   ├── messages: Message[]
│   ├── isTyping: boolean
│   └── companion: CompanionConfig
├── Processing State
│   ├── isProcessing: boolean
│   ├── currentStage: string
│   └── progress: number
└── Modal State
    ├── isOpen: boolean
    ├── type: string
    └── data: object
```

## Components and Interfaces

### 1. AI Wellness Hero Component

**Purpose:** Display real-time wellness metrics with ML confidence indicators

**Structure:**
```html
<div class="ai-wellness-hero">
  <div class="hero-header">
    <div class="hero-title">🧠 Mind Mate <span class="ai-badge">AI-POWERED</span></div>
    <button class="settings-btn">⚙️</button>
  </div>
  
  <div class="wellness-score-section">
    <div class="wellness-score" id="wellnessScore">8.5</div>
    <div class="wellness-label">Wellness Score</div>
    <div class="progress-container">
      <div class="progress-bar" id="progressBar"></div>
    </div>
  </div>
  
  <div class="metrics-grid">
    <div class="metric-card">
      <div class="metric-value">49</div>
      <div class="metric-label">Features Analyzed</div>
    </div>
    <!-- More metric cards -->
  </div>
  
  <button class="view-report-btn" onclick="showFullReport()">
    📊 View Full AI Report
  </button>
</div>
```

**Styling:**
- Background: `linear-gradient(135deg, #86efac 0%, #4ade80 100%)`
- Position: `sticky`, `top: 0`, `z-index: 100`
- Padding: `32px 24px`
- Box shadow: `0 4px 20px rgba(134, 239, 172, 0.15)`

**Animations:**
```css
@keyframes countUp {
  from { opacity: 0; transform: scale(0.8); }
  to { opacity: 1; transform: scale(1); }
}

.wellness-score {
  animation: countUp 1s ease-out;
}

.progress-bar {
  transition: width 1.5s cubic-bezier(0.4, 0.0, 0.2, 1);
}
```

**JavaScript Interface:**
```javascript
class WellnessHero {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.score = 0;
    this.targetScore = 0;
  }
  
  updateScore(newScore) {
    this.targetScore = newScore;
    this.animateScore();
  }
  
  animateScore() {
    // Animate from current to target over 1 second
    const duration = 1000;
    const start = this.score;
    const end = this.targetScore;
    const startTime = Date.now();
    
    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = this.easeOut(progress);
      this.score = start + (end - start) * eased;
      
      this.render();
      
      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };
    
    animate();
  }
  
  easeOut(t) {
    return 1 - Math.pow(1 - t, 3);
  }
  
  updateMetrics(data) {
    // Update all metrics
    this.updateScore(data.score);
    this.updateProgressBar(data.score / 10);
    this.updateRiskLevel(data.riskLevel);
    this.updateConfidence(data.confidence);
  }
  
  render() {
    document.getElementById('wellnessScore').textContent = this.score.toFixed(1);
  }
}
```

### 2. Processing Animation Component

**Purpose:** Visualize ML feature extraction and model inference

**Structure:**
```html
<div class="processing-animation" id="processingAnimation">
  <div class="processing-title">⚡ AI Processing...</div>
  <div class="processing-steps">
    <div class="processing-step">
      <div class="step-icon loading">⚡</div>
      <span>Extracting 49 features</span>
    </div>
    <div class="processing-step">
      <div class="step-icon">🧠</div>
      <span>Running ML model (RF + GB)</span>
    </div>
    <div class="processing-step">
      <div class="step-icon">✅</div>
      <span>Analysis complete!</span>
    </div>
  </div>
</div>
```

**Animation Sequence:**
1. Stage 1 (0-1s): Show "Extracting 49 features" with spinning icon
2. Stage 2 (1-2s): Show "Running ML model" with spinning icon
3. Stage 3 (2-3s): Show "Analysis complete" with checkmark
4. Stage 4 (3-4s): Fade out and remove from DOM

**JavaScript Interface:**
```javascript
class ProcessingAnimation {
  constructor() {
    this.stages = ['extracting', 'analyzing', 'complete'];
    this.currentStage = 0;
  }
  
  show() {
    const container = document.getElementById('chatMessages');
    const animDiv = this.createAnimationElement();
    container.appendChild(animDiv);
    this.animate();
  }
  
  animate() {
    const stages = document.querySelectorAll('.step-icon');
    
    // Stage 1: Extracting
    setTimeout(() => {
      stages[1].classList.add('loading');
      stages[1].textContent = '⚡';
    }, 1000);
    
    // Stage 2: Analyzing
    setTimeout(() => {
      stages[1].classList.remove('loading');
      stages[1].textContent = '🧠';
      stages[2].classList.add('loading');
      stages[2].textContent = '⚡';
    }, 2000);
    
    // Stage 3: Complete
    setTimeout(() => {
      stages[2].classList.remove('loading');
      stages[2].textContent = '✅';
      
      // Remove after 1 second
      setTimeout(() => {
        document.getElementById('processingAnimation').remove();
      }, 1000);
    }, 3000);
  }
}
```

### 3. Chat Interface Component

**Purpose:** Display conversation with AI companion and insights

**Message Structure:**
```javascript
interface Message {
  type: 'user' | 'companion';
  text: string;
  timestamp: string;
  metadata?: {
    confidence?: number;
    relatedInsight?: string;
  };
}
```

**Rendering:**
```javascript
class ChatInterface {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.messages = [];
  }
  
  addMessage(type, text, metadata = {}) {
    const message = { type, text, timestamp: new Date().toISOString(), metadata };
    this.messages.push(message);
    this.renderMessage(message);
    this.scrollToBottom();
  }
  
  renderMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${message.type}`;
    
    if (message.type === 'companion') {
      messageDiv.innerHTML = `
        <div class="message-avatar">🐶</div>
        <div class="message-content">
          <div class="message-bubble">${this.formatText(message.text)}</div>
          <div class="message-time">${this.formatTime(message.timestamp)}</div>
        </div>
      `;
    } else {
      messageDiv.innerHTML = `
        <div class="message-content">
          <div class="message-bubble">${message.text}</div>
          <div class="message-time">${this.formatTime(message.timestamp)}</div>
        </div>
      `;
    }
    
    this.container.appendChild(messageDiv);
  }
  
  formatText(text) {
    // Highlight technical terms
    return text.replace(/(AI analysis|ML model|features|confidence)/gi, 
      '<span style="color: #5eead4; font-weight: 600;">$1</span>');
  }
  
  showTyping() {
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typingIndicator';
    typingDiv.className = 'message companion';
    typingDiv.innerHTML = `
      <div class="message-avatar">🐶</div>
      <div class="message-content">
        <div class="message-bubble">
          <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
          </div>
        </div>
      </div>
    `;
    this.container.appendChild(typingDiv);
    this.scrollToBottom();
  }
  
  hideTyping() {
    const typing = document.getElementById('typingIndicator');
    if (typing) typing.remove();
  }
}
```

### 4. ML Insight Card Component

**Purpose:** Display AI-generated insights with confidence metrics

**Structure:**
```html
<div class="insight-card">
  <div class="insight-header">
    <span>🧠</span>
    <span>AI Insight</span>
  </div>
  <div class="insight-body">
    Your wellness patterns look stable this week. Great job maintaining consistent self-care habits!
  </div>
  <div class="insight-footer">
    <span>Confidence: 92%</span>
    <span>Based on 127 data points</span>
  </div>
</div>
```

**JavaScript Interface:**
```javascript
class InsightCard {
  static create(insight, confidence, dataPoints) {
    const card = document.createElement('div');
    card.className = 'insight-card';
    card.innerHTML = `
      <div class="insight-header">
        <span>🧠</span>
        <span>AI Insight</span>
      </div>
      <div class="insight-body">${insight}</div>
      <div class="insight-footer">
        <span>Confidence: ${confidence}%</span>
        <span>Based on ${dataPoints} data points</span>
      </div>
    `;
    return card;
  }
  
  static add(container, insight, confidence, dataPoints) {
    const card = this.create(insight, confidence, dataPoints);
    container.appendChild(card);
    
    // Trigger slide-in animation
    setTimeout(() => {
      card.style.transform = 'translateX(0)';
    }, 10);
  }
}
```

### 5. Full AI Report Modal

**Purpose:** Display detailed feature breakdown and 7-day prediction

**Structure:**
```html
<div class="modal-overlay" id="modalOverlay">
  <div class="modal-content">
    <div class="modal-header">
      <div class="modal-title">🧠 AI Wellness Report</div>
      <button class="modal-close" onclick="closeModal()">×</button>
    </div>
    <div id="modalBody">
      <!-- Dynamic content -->
    </div>
  </div>
</div>
```

**Modal Content Template:**
```javascript
function generateFullReport(data) {
  return `
    <div class="report-section">
      <h3>📊 Feature Analysis</h3>
      
      <div class="feature-category">
        <h4>Mood Features (20)</h4>
        <div class="feature-list">
          <div class="feature-item">
            <span>7-day trend:</span>
            <span class="${data.mood_trend_7day > 0 ? 'positive' : 'negative'}">
              ${data.mood_trend_7day > 0 ? '↗️' : '↘️'} 
              ${data.mood_trend_7day > 0 ? 'Improving' : 'Declining'}
            </span>
          </div>
          <div class="feature-item">
            <span>Volatility:</span>
            <span>${data.mood_volatility < 1 ? 'Low' : 'High'}</span>
          </div>
          <div class="feature-item">
            <span>Consecutive low days:</span>
            <span>${data.consecutive_low_days}</span>
          </div>
        </div>
      </div>
      
      <div class="feature-category">
        <h4>Behavioral Features (15)</h4>
        <div class="feature-list">
          <div class="feature-item">
            <span>Check-in frequency:</span>
            <span>${data.daily_checkin_frequency > 0.7 ? 'High' : 'Low'}</span>
          </div>
          <div class="feature-item">
            <span>Engagement:</span>
            <span>${(data.engagement_score * 100).toFixed(0)}%</span>
          </div>
        </div>
      </div>
      
      <div class="feature-category">
        <h4>Sentiment Features (14)</h4>
        <div class="feature-list">
          <div class="feature-item">
            <span>Positive sentiment:</span>
            <span>${(data.positive_sentiment * 100).toFixed(0)}%</span>
          </div>
          <div class="feature-item">
            <span>Crisis keywords:</span>
            <span>${data.despair_keywords > 0 ? 'Detected' : 'None detected'}</span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="report-section">
      <h3>🔮 7-Day Prediction</h3>
      <div class="prediction-chart">
        ${generatePredictionChart(data.prediction_7day)}
      </div>
      <div class="prediction-summary">
        <div class="prediction-item">
          <span>🎯 Intervention Threshold:</span>
          <span>60%</span>
        </div>
        <div class="prediction-item">
          <span>Current Risk:</span>
          <span class="${data.riskScore < 0.6 ? 'safe' : 'warning'}">
            ${(data.riskScore * 100).toFixed(0)}% 
            ${data.riskScore < 0.6 ? '(Well below)' : '(Approaching)'}
          </span>
        </div>
      </div>
    </div>
  `;
}
```

## Data Models

### Wellness State Model
```javascript
interface WellnessState {
  score: number;              // 0-10
  riskScore: number;          // 0-1
  riskLevel: 'minimal' | 'low' | 'moderate' | 'high' | 'critical';
  confidence: number;         // 0-100
  featuresAnalyzed: number;   // Always 49
  nextAssessment: string;     // Time remaining (e.g., "4h 23m")
  lastUpdated: string;        // ISO timestamp
}
```

### Feature Data Model
```javascript
interface FeatureData {
  // Mood features (20)
  mood_trend_7day: number;
  mood_mean_7day: number;
  mood_std_7day: number;
  mood_volatility: number;
  consecutive_low_days: number;
  low_mood_frequency: number;
  // ... 14 more mood features
  
  // Behavioral features (15)
  daily_checkin_frequency: number;
  engagement_score: number;
  late_night_usage: number;
  // ... 12 more behavioral features
  
  // Sentiment features (14)
  positive_sentiment: number;
  negative_sentiment: number;
  despair_keywords: number;
  hopelessness_score: number;
  // ... 10 more sentiment features
}
```

### API Response Models
```javascript
interface RiskCalculationResponse {
  ok: boolean;
  riskScore: number;
  riskLevel: string;
  riskFactors: string[];
  timestamp: string;
  interventionTriggered: boolean;
  message: string;
}

interface MoodLogResponse {
  ok: boolean;
  ts: string;
  mood: number;
}
```

## Error Handling

### API Error Handling
```javascript
class APIClient {
  async calculateRisk(userId) {
    try {
      const response = await fetch(`${API_BASE}/calculate-risk`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Risk calculation failed:', error);
      
      // Fall back to demo mode
      return this.getDemoRiskData();
    }
  }
  
  getDemoRiskData() {
    return {
      ok: true,
      riskScore: 0.23,
      riskLevel: 'low',
      riskFactors: ['Stable mood patterns', 'Consistent engagement'],
      confidence: 94,
      timestamp: new Date().toISOString()
    };
  }
}
```

### User-Facing Error Messages
```javascript
const ERROR_MESSAGES = {
  NETWORK_ERROR: "Unable to connect. Using offline mode.",
  API_ERROR: "Something went wrong. Please try again.",
  FEATURE_EXTRACTION_FAILED: "Could not analyze data. Using cached results.",
  INSUFFICIENT_DATA: "Not enough data yet. Keep logging your moods!"
};
```

## Testing Strategy

### Unit Tests
- Test score animation calculations
- Test feature data parsing
- Test risk level classification
- Test time formatting utilities

### Integration Tests
- Test API client with mock responses
- Test state management updates
- Test modal open/close behavior
- Test message rendering

### Demo Script Tests
- Test 0:00-0:30 section (hero display)
- Test 0:30-1:30 section (processing animation)
- Test 1:30-2:15 section (full report modal)
- Test 2:15-3:00 section (complete view)

### Performance Tests
- Measure animation frame rates (target: 60fps)
- Measure API response times (target: <2s)
- Measure initial load time (target: <1s)
- Test with 100+ messages in chat

## Implementation Phases

### Phase 1: Core Structure (Foundation)
- Create HTML structure with all sections
- Implement CSS styling with color scheme
- Set up JavaScript state management
- Implement basic routing/navigation

### Phase 2: AI Wellness Hero
- Implement score counter animation
- Add progress bar animation
- Create metrics grid
- Add "View Full AI Report" button
- Implement sticky positioning

### Phase 3: Processing Animation
- Create processing animation component
- Implement stage transitions
- Add loading indicators
- Integrate with API calls

### Phase 4: Chat Interface
- Implement message rendering
- Add typing indicator
- Create insight card component
- Integrate with DynamoDB storage

### Phase 5: Full AI Report Modal
- Create modal structure
- Implement feature breakdown display
- Add 7-day prediction chart
- Implement open/close animations

### Phase 6: Backend Integration
- Connect to logMood Lambda
- Connect to calculateRiskScore Lambda
- Implement error handling
- Add fallback demo mode

### Phase 7: Polish & Demo Prep
- Fine-tune animations
- Add sound effects (optional)
- Test demo script flow
- Optimize performance

## Design Decisions

### Why Vanilla JavaScript?
- No build step required
- Faster development for demo
- Easier to debug during presentation
- Smaller bundle size

### Why Sticky Hero Section?
- Keeps ML metrics always visible
- Reinforces technical sophistication
- Provides context during scrolling
- Matches demo script requirements

### Why Animated Counters?
- Creates "wow" factor for judges
- Shows real-time processing
- Emphasizes data-driven approach
- Improves perceived performance

### Why Green Color Scheme?
- Associated with health and wellness
- Calming and approachable
- Differentiates from competitors
- Works well with AI/tech accents (teal)

## Accessibility Considerations

- Use semantic HTML elements
- Provide ARIA labels for interactive elements
- Ensure sufficient color contrast (WCAG AA)
- Support keyboard navigation
- Provide text alternatives for icons
- Use focus indicators for interactive elements

## Browser Compatibility

Target browsers:
- Chrome 90+ (primary demo browser)
- Safari 14+
- Firefox 88+
- Edge 90+

Required features:
- CSS Grid
- CSS Flexbox
- CSS Custom Properties
- Fetch API
- ES6+ JavaScript
