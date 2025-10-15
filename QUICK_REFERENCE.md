# Mind Mate - Quick Reference Card

## 🔗 Essential URLs

**API Endpoint**
```
https://h8iyzk1h3k.execute-api.us-east-1.amazonaws.com
```

**AWS Console Links**
- Amplify: https://console.aws.amazon.com/amplify/home?region=us-east-1
- Lambda: https://console.aws.amazon.com/lambda/home?region=us-east-1
- DynamoDB: https://console.aws.amazon.com/dynamodbv2/home?region=us-east-1
- API Gateway: https://console.aws.amazon.com/apigateway/home?region=us-east-1

---

## 🧪 Quick Test Commands

```bash
# Test profile
curl "https://h8iyzk1h3k.execute-api.us-east-1.amazonaws.com/profile?userId=demo"

# Test mood logging
curl -X POST "https://h8iyzk1h3k.execute-api.us-east-1.amazonaws.com/mood" \
  -H "Content-Type: application/json" \
  -d '{"userId":"demo","mood":8,"note":"Testing!"}'

# Test stats
curl "https://h8iyzk1h3k.execute-api.us-east-1.amazonaws.com/stats?userId=demo"
```

---

## 🚀 Deploy Frontend

**Amplify (5 min)**
1. Go to Amplify Console
2. New app → Deploy without Git
3. Upload `frontend/app-v2.html`
4. Done!

**Local (30 sec)**
```bash
cd frontend
python3 -m http.server 8000
open http://localhost:8000/app-v2.html
```

---

## 📊 System Status

**Lambda Functions**: 9 deployed ✅
- logMood, analyzeSelfie, analyzeScene
- generateAvatar, dailyRecap, riskScan
- getProfile, updateProfile, getStats

**Database**: EmoCompanion (DynamoDB) ✅

**Storage**: mindmate-uploads-403745271636 (S3) ✅

**API**: MindMateAPI (h8iyzk1h3k) ✅

**AI Models**: Claude 3 Haiku + Titan Image ✅

---

## 🎬 Demo Script (5 min)

1. **Personality** (30s) - Show 4 types, select one
2. **Mood Log** (1m) - Select emoji, earn coins
3. **Stats** (30s) - Show dashboard, trends
4. **Change Personality** (30s) - Switch, show adaptation
5. **Technical** (2m) - AWS Console, architecture

---

## 💰 Costs

**Demo**: ~$3.55/month  
**Production (10K users)**: ~$180/month

---

## 🎯 Key Features

- 🎭 4 personalities (Gentle, Playful, Focused, Sensitive)
- 💰 Coin rewards (10-20 per mood, 15 per selfie)
- 📊 Stats dashboard with 7-day trends
- 🤖 AI responses (Claude)
- 🎨 AI avatars (Titan)
- 😊 Emotion detection (Rekognition)

---

## 🆘 Troubleshooting

**API not responding?**
```bash
aws logs tail /aws/lambda/logMood --follow
```

**CORS errors?**
- Hard refresh (Cmd+Shift+R)

**Coins not updating?**
```bash
aws dynamodb scan --table-name EmoCompanion --limit 5
```

---

## 📚 Key Documents

- `DEPLOYMENT_COMPLETE.md` - Full summary
- `READY_TO_DEPLOY.md` - Deployment guide
- `deploy-to-amplify.md` - Amplify steps
- `docs/DEMO_SCRIPT.md` - Detailed demo
- `PRODUCT_VISION.md` - Product vision

---

## ✅ Checklist

- [x] Backend deployed
- [x] API tested
- [x] Frontend ready
- [ ] Deploy to Amplify
- [ ] Test in browser
- [ ] Review demo script
- [ ] Win hackathon! 🏆

---

**Status**: ✅ READY  
**Time to deploy**: 5 minutes  
**Time to demo**: 10 minutes
