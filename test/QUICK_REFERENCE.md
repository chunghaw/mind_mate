# Mind Mate Testing - Quick Reference Card

## 🚀 Setup (One-Time)

```bash
# 1. Set API URL
export API_URL="https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com"

# 2. Make scripts executable
chmod +x test/*.sh

# 3. Verify AWS CLI
aws sts get-caller-identity
```

---

## ⚡ Quick Commands

### Run All Tests
```bash
cd test && ./run_all_tests.sh
```

### Test Specific Component
```bash
# User journey
./test_user_journey.sh

# ML pipeline
./test_ml_pipeline.sh

# Demo scenarios
./test_demo_scenarios.sh
```

### Manual Tests
```bash
# Test mood logging
curl -X POST "$API_URL/mood" \
  -H "Content-Type: application/json" \
  -d '{"userId":"test","mood":7,"notes":"Testing"}'

# Test chat
curl -X POST "$API_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{"userId":"test","message":"Hello!"}'

# Test risk score
aws lambda invoke \
  --function-name calculateRiskScore \
  --payload '{"userId":"test"}' \
  response.json && cat response.json
```

---

## 🔍 Debugging

### Check Logs
```bash
# Lambda logs
aws logs tail /aws/lambda/logMood --follow

# Recent errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/chat \
  --filter-pattern "ERROR" \
  --start-time $(date -u -d '1 hour ago' +%s)000
```

### Check Data
```bash
# DynamoDB items
aws dynamodb query \
  --table-name EmoCompanion \
  --key-condition-expression "PK = :pk" \
  --expression-attribute-values '{":pk":{"S":"USER#test"}}'

# S3 objects
aws s3 ls s3://YOUR_BUCKET/ --recursive
```

---

## 🧹 Cleanup

```bash
# Remove test data
./cleanup_test_data.sh

# Remove test files
rm -f *.json response.json
```

---

## 📊 Expected Results

### Successful Test
```
✓ PASS - Lambda functions responding
✓ PASS - API endpoints working
✓ PASS - Data persisting
✓ PASS - ML pipeline functioning
✓ PASS - Performance acceptable
```

### Risk Levels
- **MINIMAL** (0.0-0.2): Stable, good mood
- **LOW** (0.2-0.4): Minor concerns
- **MODERATE** (0.4-0.6): Attention needed
- **HIGH** (0.6-0.8): Intervention recommended
- **CRITICAL** (0.8-1.0): Immediate support

---

## 🚨 Common Issues

| Issue | Solution |
|-------|----------|
| Lambda timeout | `aws lambda update-function-configuration --function-name NAME --timeout 30` |
| API 403 | Check API_URL environment variable |
| DynamoDB not found | Run `./deploy-ml-stack.sh` |
| Bedrock error | Enable models in AWS Console |

---

## 📚 Full Documentation

- **[TESTING_GUIDE.md](../docs/TESTING_GUIDE.md)** - Complete guide
- **[README.md](README.md)** - Test suite docs
- **[TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md)** - Common issues

---

## 💡 Pro Tips

1. **Always check CloudWatch logs first** when debugging
2. **Use demo scenarios** for quick validation
3. **Clean up test data** regularly to avoid clutter
4. **Monitor performance** to catch regressions early
5. **Run tests before deployment** to catch issues

---

**Print this card and keep it handy!** 📋
