#!/bin/bash
# Simple script to generate pet avatars using the generateAvatar Lambda

API_URL=${1:-"https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com"}
USER_ID="demo-user"

echo "🐾 Generating Mind Mate Pet Avatars"
echo "===================================="
echo ""

# Gentle Guardian
echo "1️⃣ Generating Gentle Guardian 🐶..."
curl -s -X POST "$API_URL/avatar" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "gentle",
    "description": "a cute cartoon-style friendly dog companion with soft blue colors, gentle expression, warm kind eyes, supportive and nurturing personality, simple clean background, digital art, kawaii style"
  }' | jq -r '.avatarUrl' > gentle_url.txt
echo "✅ Saved to gentle_url.txt"
echo ""

# Playful Pal
echo "2️⃣ Generating Playful Pal 🐱..."
curl -s -X POST "$API_URL/avatar" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "playful",
    "description": "a cute cartoon-style playful cat companion with warm yellow colors, energetic happy expression, bright sparkling eyes, fun-loving personality, simple clean background, digital art, kawaii style"
  }' | jq -r '.avatarUrl' > playful_url.txt
echo "✅ Saved to playful_url.txt"
echo ""

# Focused Friend
echo "3️⃣ Generating Focused Friend 🐉..."
curl -s -X POST "$API_URL/avatar" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "focused",
    "description": "a cute cartoon-style calm dragon companion with purple colors, centered peaceful expression, wise gentle eyes, focused meditative personality, simple clean background, digital art, kawaii style"
  }' | jq -r '.avatarUrl' > focused_url.txt
echo "✅ Saved to focused_url.txt"
echo ""

# Sensitive Soul
echo "4️⃣ Generating Sensitive Soul 🦊..."
curl -s -X POST "$API_URL/avatar" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "sensitive",
    "description": "a cute cartoon-style empathetic fox companion with warm orange colors, understanding caring expression, kind compassionate eyes, sensitive gentle personality, simple clean background, digital art, kawaii style"
  }' | jq -r '.avatarUrl' > sensitive_url.txt
echo "✅ Saved to sensitive_url.txt"
echo ""

echo "🎉 All avatars generated!"
echo ""
echo "URLs saved to:"
echo "  - gentle_url.txt"
echo "  - playful_url.txt"
echo "  - focused_url.txt"
echo "  - sensitive_url.txt"
