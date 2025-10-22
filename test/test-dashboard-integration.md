# Dashboard & AI Report Integration Test

## Quick Test Steps

### 1. Test Dashboard Loading
1. Open the app: `frontend/mind-mate-hackathon.html`
2. Should see Dashboard tab (default)
3. Check that it shows:
   - Wellness Score (should calculate from API)
   - Risk Level (should be from real data)
   - Features Analyzed (should be 49 or actual count)
   - ML Confidence (should be from calculation)

### 2. Test Crisis Keyword Detection
1. Go to Chat tab
2. Send message: "I feel hopeless and want to die"
3. Wait for Bedrock Agent response
4. Wait 2 seconds for auto-refresh
5. Go back to Dashboard tab
6. Should see:
   - Higher risk score
   - Risk level changed to HIGH or CRITICAL
   - Updated metrics

### 3. Test AI Report
1. Click "AI Report" tab
2. Should see:
   - Risk score with color indicator
   - Features analyzed count
   - ML confidence percentage
   - Risk factors list (if any detected)
   - Recommendations section
   - Crisis resources (if high risk)

### 4. Test Tab Switching
1. Switch between tabs multiple times
2. Each time you switch to Dashboard → should refresh data
3. Each time you switch to AI Report → should update report
4. Data should be consistent across both views

## Expected API Calls

### On Page Load
```
GET /risk/calculate
→ Returns current risk assessment
→ Updates Dashboard
```

### On Crisis Message
```
1. Message sent to Bedrock Agent
2. Wait 2 seconds
3. GET /risk/calculate (auto-triggered)
→ Returns updated risk with crisis keywords
→ Updates Dashboard automatically
```

### On Tab Switch to Dashboard
```
GET /risk/calculate
→ Refreshes current data
```

### On Tab Switch to AI Report
```
Uses cached data from AppState.wellness
→ Renders report immediately
```

## Verification Points

✅ Dashboard shows real data (not static 49, 94%, LOW)  
✅ AI Report displays detailed analysis  
✅ Crisis keywords trigger refresh  
✅ Risk factors list populated  
✅ Crisis resources shown when risk is high  
✅ Tab switching works smoothly  
✅ No console errors  
✅ Data consistent across views  

## Troubleshooting

### Dashboard shows "--" or "N/A"
- Check browser console for API errors
- Verify API endpoint is accessible
- Check that calculateRiskScore Lambda is deployed
- Ensure user has some data (mood logs or chat history)

### AI Report is empty
- Check that `updateAIReport()` is being called
- Verify `AppState.wellness` has data
- Check browser console for errors

### Crisis keywords don't trigger refresh
- Check browser console for "Crisis keyword detected" message
- Verify 2-second delay is working
- Check that `loadWellnessData()` is being called

### Risk level doesn't change
- Verify chat messages are being stored in DynamoDB
- Check that sentiment analysis is detecting keywords
- Run risk calculation manually to test

## Manual API Test

```bash
# Test risk calculation directly
curl -X POST https://h8iyzk1h3k.execute-api.us-east-1.amazonaws.com/risk/calculate \
  -H "Content-Type: application/json" \
  -d '{"userId":"YOUR_USER_ID"}'
```

Expected response:
```json
{
  "ok": true,
  "riskScore": 0.75,
  "riskLevel": "high",
  "riskFactors": [
    "Crisis keywords detected (2)",
    "High negative sentiment"
  ],
  "features": { ... },
  "confidence": 87
}
```

