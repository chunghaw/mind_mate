# 🚀 Deploy Mind Mate to AWS Amplify

## Quick Deployment (5 minutes)

### Option 1: Amplify Console (Easiest)

1. **Go to AWS Amplify Console**
   - Open: https://console.aws.amazon.com/amplify/home?region=us-east-1
   - Click "New app" → "Host web app"

2. **Deploy without Git**
   - Select "Deploy without Git provider"
   - Click "Continue"

3. **Upload Files**
   - App name: `MindMate`
   - Environment name: `production`
   - Drag and drop: `frontend/app-v2.html`
   - Click "Save and deploy"

4. **Get URL**
   - Wait 1-2 minutes for deployment
   - Copy the Amplify URL (e.g., `https://production.xxxxx.amplifyapp.com`)
   - Open in browser and test!

---

### Option 2: AWS CLI

```bash
# Create Amplify app
aws amplify create-app \
  --name MindMate \
  --region us-east-1

# Note the appId from output

# Create a branch
aws amplify create-branch \
  --app-id YOUR_APP_ID \
  --branch-name main

# Deploy (manual upload via console)
# Go to Amplify Console and upload frontend/app-v2.html
```

---

### Option 3: Local Testing (No Deployment)

```bash
# Serve locally with Python
cd frontend
python3 -m http.server 8000

# Open in browser
open http://localhost:8000/app-v2.html
```

---

## Testing Your Deployment

Once deployed, test these features:

1. **Personality Selection**
   - Click on each personality card
   - Verify avatar and colors change

2. **Mood Logging**
   - Select a mood emoji
   - Add a note
   - Click "Save Mood"
   - Verify coin notification appears

3. **Stats Dashboard**
   - Click "Stats" tab
   - Verify streak, check-ins, coins display
   - Check 7-day mood trend

4. **Profile Update**
   - Click "Personality" tab
   - Change personality
   - Verify header updates

---

## Troubleshooting

### CORS Errors
If you see CORS errors in browser console:
- API Gateway already has CORS enabled
- Try hard refresh (Cmd+Shift+R on Mac)

### API Not Responding
- Verify API URL in frontend: `https://h8iyzk1h3k.execute-api.us-east-1.amazonaws.com`
- Check Lambda logs: `aws logs tail /aws/lambda/logMood --follow`

### Coins Not Updating
- Check browser console for errors
- Verify DynamoDB table has data: `aws dynamodb scan --table-name EmoCompanion --limit 5`

---

## Current Status

✅ **Backend**: Fully deployed and operational  
✅ **API**: All endpoints working  
✅ **Frontend**: Ready to deploy  
⏳ **Hosting**: Choose option above  

**API Endpoint**: `https://h8iyzk1h3k.execute-api.us-east-1.amazonaws.com`

---

## Next Steps After Deployment

1. **Test all features** in deployed app
2. **Generate pet avatars** (optional): `python3 scripts/generate-pet-avatars.py`
3. **Set up SES** for daily recap emails
4. **Create EventBridge rules** for scheduled tasks
5. **Prepare demo** using `docs/DEMO_SCRIPT.md`

---

## Demo URLs

Once deployed, you'll have:
- **Frontend**: `https://production.xxxxx.amplifyapp.com`
- **API**: `https://h8iyzk1h3k.execute-api.us-east-1.amazonaws.com`
- **S3 Bucket**: `mindmate-uploads-403745271636`
- **DynamoDB**: `EmoCompanion`

Share the Amplify URL for your demo! 🎉
