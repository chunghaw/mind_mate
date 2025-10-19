# ML Integration Quick Start

## 🚀 5-Minute Integration

### 1. Deploy Backend (2 min)
```bash
./infrastructure/deploy-ml-lambdas.sh
./infrastructure/add-ml-routes.sh
```

### 2. Integrate Frontend (1 min)
```bash
./scripts/integrate-ml-widget.sh
```

### 3. Deploy Frontend (1 min)
```bash
# Copy files to your hosting
cp frontend/mind-mate-ml.html YOUR_HOSTING_PATH/
cp frontend/ml-wellness-widget.* YOUR_HOSTING_PATH/
```

### 4. Test (1 min)
```bash
# Replace with your API URL
API="https://YOUR_API.execute-api.us-east-1.amazonaws.com/prod"

# Test risk calculation
curl -X POST "$API/calculate-risk" \
  -H "Content-Type: application/json" \
  -d '{"userId":"demo-user"}'
```

## 📦 What You Get

### Backend
- ✅ Real-time risk scoring
- ✅ Proactive interventions
- ✅ Feature extraction pipeline
- ✅ Crisis resource delivery

### Frontend
- ✅ Wellness status widget
- ✅ Auto-refresh every 5 min
- ✅ Color-coded risk levels
- ✅ Intervention alerts

## 🎯 Key Endpoints

```bash
# Calculate risk
POST /calculate-risk
Body: {"userId": "user123"}

# Get risk score
GET /risk-score?userId=user123
```

## 🎨 Widget Display

| Risk Level | Color  | Icon | Message |
|-----------|--------|------|---------|
| Minimal   | Green  | 😊   | Doing Great |
| Low       | Blue   | 🙂   | Doing Well |
| Moderate  | Yellow | 😐   | Check In |
| High      | Orange | 😟   | Need Support |
| Critical  | Red    | 💙   | Reach Out |

## 🔧 Quick Customization

### Change Refresh Interval
Edit `ml-wellness-widget.js` line 18:
```javascript
5 * 60 * 1000  // Change 5 to desired minutes
```

### Change Colors
Edit `ml-wellness-widget.css`:
```css
.status-minimal { background: #YOUR_COLOR; }
```

## 🐛 Quick Fixes

### Widget Not Showing
```javascript
// Check in browser console
console.log(mlWidget);
```

### No Risk Data
```bash
# Trigger manual assessment
curl -X POST "$API/calculate-risk" \
  -d '{"userId":"YOUR_USER_ID"}'
```

### CORS Error
```bash
# Re-deploy API Gateway
./infrastructure/add-ml-routes.sh
```

## 📊 Quick Test

```bash
# 1. Log some moods
curl -X POST "$API/mood" \
  -d '{"userId":"test","mood":3,"notes":"Low"}'

# 2. Calculate risk
curl -X POST "$API/calculate-risk" \
  -d '{"userId":"test"}'

# 3. Check result
curl "$API/risk-score?userId=test"
```

## 📚 Full Docs

- Complete Guide: `ML_FULL_INTEGRATION_GUIDE.md`
- Architecture: `docs/ML_INTEGRATION_COMPLETE.md`
- API Reference: `docs/API_REFERENCE.md`

## ✅ Checklist

- [ ] Backend deployed
- [ ] Routes added
- [ ] Frontend integrated
- [ ] Tested endpoints
- [ ] Widget showing
- [ ] Auto-refresh working

---

**Need Help?** Check CloudWatch logs:
```bash
aws logs tail /aws/lambda/calculateRiskScore --follow
```
