# 🚀 Quick Start - Phase 2 Features

## ⚡ 5-Minute Deployment

### 1. Deploy New Lambda Functions (2 min)
```bash
cd infrastructure
./deploy-lambdas.sh EmoCompanion mindmate-uploads-ACCOUNT_ID YOUR_EMAIL@example.com
```

### 2. Add API Gateway Routes (2 min)
**AWS Console → API Gateway → MindMateAPI → Routes**

Create these 3 new routes:
- `GET /profile` → Integration: `getProfile`
- `POST /profile` → Integration: `updateProfile`
- `GET /stats` → Integration: `getStats`

### 3. Deploy Frontend (1 min)
```bash
# Edit frontend/app-v2.html line 139
# Replace: const API = "YOUR_API_URL"
# With: const API = "https://abc123.execute-api.us-east-1.amazonaws.com"

# Then deploy to Amplify (upload app-v2.html)
```

---

## 🎨 Generate Pet Avatars (Optional)

### Option 1: Python Script (Recommended)
```bash
export BUCKET=mindmate-uploads-YOUR_ACCOUNT_ID
python3 scripts/generate-pet-avatars.py
```

### Option 2: Use Emojis (Fastest)
Skip avatar generation and just use emojis:
- 🐶 Gentle Guardian
- 🐱 Playful Pal
- 🐉 Focused Friend
- 🦊 Sensitive Soul

The frontend already uses emojis by default!

---

## ✅ Test It Works

### 1. Test Profile API
```bash
curl "https://YOUR_API.execute-api.us-east-1.amazonaws.com/profile?userId=demo-user"
# Should return: {"ok":true,"profile":{...}}
```

### 2. Test Stats API
```bash
curl "https://YOUR_API.execute-api.us-east-1.amazonaws.com/stats?userId=demo-user"
# Should return: {"ok":true,"stats":{...}}
```

### 3. Test Frontend
1. Open Amplify URL
2. Select a mood emoji → Save
3. Check coin notification appears
4. Go to Stats tab → see data
5. Go to Personality tab → select one
6. Check header updates with new emoji

---

## 🎯 What's New

### For Users
- 💰 Earn coins for activities
- 🎭 Choose pet personality
- 📊 View progress stats
- 😊 Better mood selection (emojis)
- 🎨 Cleaner, modern UI

### For Demo
- Show personality selection
- Show coin rewards
- Show stats dashboard
- Show personality-based AI responses
- Better visual appeal

---

## 🐛 Troubleshooting

**Coins not updating?**
- Check Lambda logs: `aws logs tail /aws/lambda/logMood --follow`
- Verify profile exists in DynamoDB

**Stats not loading?**
- Check API Gateway route configured
- Verify getStats Lambda deployed
- Check browser console for errors

**Personality not changing avatar?**
- Check updateProfile Lambda deployed
- Verify POST /profile route exists
- Refresh page after saving

**Frontend not loading?**
- Check API URL is correct (line 139)
- Check CORS enabled on API Gateway
- Check browser console for errors

---

## 📝 Quick Reference

### Personality Types
```javascript
gentle   → 🐶 Soft blue   (#93c5fd)
playful  → 🐱 Warm yellow (#fbbf24)
focused  → 🐉 Purple      (#a78bfa)
sensitive → 🦊 Orange      (#fb923c)
```

### Coin Rewards
```
Mood log: 10-20 coins
  Base: 10
  +5 for notes
  +5 for tags
Selfie: 15 coins
```

### API Endpoints
```
GET  /profile?userId=X
POST /profile { userId, personality }
GET  /stats?userId=X
POST /mood { userId, mood, tags, notes } → returns coinsEarned
POST /selfie { userId, imageBase64 } → returns coinsEarned
```

---

## 🎉 You're Done!

**Total time**: 5-10 minutes
**New features**: 5 major enhancements
**Ready to demo**: YES!

Open your Amplify URL and enjoy the enhanced Mind Mate! 🐾
