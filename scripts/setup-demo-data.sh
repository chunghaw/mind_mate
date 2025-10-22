#!/bin/bash

echo "🎬 Setting up Mind Mate ML Demo Data"
echo "===================================="

# Demo user ID
DEMO_USER="demo-user-ml-showcase"
API_BASE="https://h8iyzk1h3k.execute-api.us-east-1.amazonaws.com"

echo ""
echo "📊 Creating realistic user journey data..."

# Day 1: Good start
echo "Day 1: Positive start..."
curl -s -X POST "${API_BASE}/log-mood" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "'${DEMO_USER}'",
    "mood": 7,
    "notes": "Excited to try this new mental health app! Feeling optimistic.",
    "tags": ["excited", "optimistic"]
  }' > /dev/null

# Day 2: Still good
echo "Day 2: Maintaining positivity..."
curl -s -X POST "${API_BASE}/log-mood" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "'${DEMO_USER}'",
    "mood": 6,
    "notes": "Had a productive day at work. Buddy is helpful!",
    "tags": ["productive", "work"]
  }' > /dev/null

# Day 3: Starting to decline
echo "Day 3: First signs of stress..."
curl -s -X POST "${API_BASE}/log-mood" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "'${DEMO_USER}'",
    "mood": 5,
    "notes": "Work is getting more stressful. Deadlines approaching.",
    "tags": ["stressed", "work", "deadlines"]
  }' > /dev/null

# Day 4: Noticeable decline
echo "Day 4: Mood declining..."
curl -s -X POST "${API_BASE}/log-mood" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "'${DEMO_USER}'",
    "mood": 4,
    "notes": "Having trouble sleeping. Mind keeps racing about work problems.",
    "tags": ["insomnia", "anxiety", "work"]
  }' > /dev/null

# Day 5: Concerning pattern
echo "Day 5: Concerning patterns emerging..."
curl -s -X POST "${API_BASE}/log-mood" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "'${DEMO_USER}'",
    "mood": 3,
    "notes": "Everything feels overwhelming. I dont know how to handle all this pressure.",
    "tags": ["overwhelmed", "pressure", "struggling"]
  }' > /dev/null

# Day 6: Crisis indicators
echo "Day 6: Crisis indicators detected..."
curl -s -X POST "${API_BASE}/log-mood" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "'${DEMO_USER}'",
    "mood": 2,
    "notes": "I feel so hopeless and alone. Maybe I should just give up on everything.",
    "tags": ["hopeless", "alone", "giving-up"]
  }' > /dev/null

# Day 7: Critical state
echo "Day 7: Critical mental health state..."
curl -s -X POST "${API_BASE}/log-mood" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "'${DEMO_USER}'",
    "mood": 1,
    "notes": "I cant go on like this. Whats the point of trying anymore? Nobody understands.",
    "tags": ["crisis", "despair", "isolated"]
  }' > /dev/null

echo ""
echo "💬 Adding chat conversation data..."

# Add some chat messages to show behavioral patterns
curl -s -X POST "${API_BASE}/agent-chat" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "'${DEMO_USER}'",
    "userMessage": "Hi Buddy, I am feeling really stressed about work lately",
    "timestamp": "'$(date -u -v-2d +%Y-%m-%dT%H:%M:%SZ)'"
  }' > /dev/null

curl -s -X POST "${API_BASE}/agent-chat" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "'${DEMO_USER}'",
    "userMessage": "I cant sleep and my mind keeps racing. What should I do?",
    "timestamp": "'$(date -u -v-1d +%Y-%m-%dT02:%M:%SZ)'"
  }' > /dev/null

curl -s -X POST "${API_BASE}/agent-chat" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "'${DEMO_USER}'",
    "userMessage": "I feel like giving up. Nothing I do matters anymore.",
    "timestamp": "'$(date -u +%Y-%m-%dT01:%M:%SZ)'"
  }' > /dev/null

echo ""
echo "🧠 Triggering ML analysis..."

# Trigger risk calculation to generate ML features
curl -s -X POST "${API_BASE}/calculate-risk" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "'${DEMO_USER}'"
  }' | jq '.'

echo ""
echo "✅ Demo data setup complete!"
echo ""
echo "🎯 Demo Instructions:"
echo "1. Use demo user ID: ${DEMO_USER}"
echo "2. Navigate to the dashboard"
echo "3. Click refresh to see ML analysis"
echo "4. View AI Report to see detailed ML insights"
echo ""
echo "📊 Expected ML Features:"
echo "• Mood trend: Strong decline (-0.857 slope)"
echo "• Consecutive low days: 3+"
echo "• Crisis keywords: 2+ detected"
echo "• Negative sentiment: 75%+"
echo "• Late night usage: Multiple sessions"
echo "• Risk level: HIGH or CRITICAL"