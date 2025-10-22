#!/bin/bash

# Test ML/AI Integration
echo "🧠 Testing AI/ML Integration..."

# Test 1: Risk Calculation API
echo "📊 Testing Risk Calculation API..."
curl -X POST "${API_BASE}/calculate-risk" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "demo_ml_user"
  }' | jq '.'

echo ""

# Test 2: Real-time Message Analysis
echo "💭 Testing Real-time Message Analysis..."
curl -X POST "${API_BASE}/calculate-risk" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "test_user",
    "realtimeMessage": "I feel hopeless and alone today"
  }' | jq '.'

echo ""

# Test 3: Emotion Analysis with Bedrock
echo "🤖 Testing Bedrock Emotion Analysis..."
curl -X POST "${API_BASE}/analyze-emotions" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "test_user",
    "message": "I am struggling with anxiety and feel overwhelmed"
  }' | jq '.'

echo ""

# Test 4: Feature Extraction
echo "📈 Testing Feature Extraction..."
curl -X POST "${API_BASE}/extract-mood-features" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "demo_ml_user",
    "days": 30
  }' | jq '.'

echo ""

# Test 5: Sentiment Features
echo "💭 Testing Sentiment Feature Extraction..."
curl -X POST "${API_BASE}/extract-sentiment-features" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "demo_ml_user",
    "days": 30
  }' | jq '.'

echo ""

# Test 6: Behavioral Features
echo "🎯 Testing Behavioral Feature Extraction..."
curl -X POST "${API_BASE}/extract-behavioral-features" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "demo_ml_user",
    "days": 30
  }' | jq '.'

echo ""
echo "✅ ML/AI Integration Tests Complete!"
echo ""
echo "🔍 Key Features Tested:"
echo "  ✓ Multi-service ML analysis"
echo "  ✓ Real-time risk assessment"
echo "  ✓ Bedrock AI emotion analysis"
echo "  ✓ Comprehensive feature extraction"
echo "  ✓ Enhanced risk calculation"
echo ""
echo "📊 Expected Results:"
echo "  • Risk scores between 0-100%"
echo "  • Multiple ML insights per analysis"
echo "  • Confidence scores 60-95%"
echo "  • 40+ extracted features for demo user"
echo "  • Real-time crisis detection"