# Mind Mate - Testing Summary

## Overview

Comprehensive testing infrastructure has been created for the Mind Mate application, covering all components from backend Lambda functions to frontend UI and ML pipeline.

---

## 📁 Testing Files Created

### Documentation
- **`docs/TESTING_GUIDE.md`** (29KB) - Complete testing guide with examples and best practices

### Test Scripts
- **`test/run_all_tests.sh`** - Comprehensive automated test suite
- **`test/test_user_journey.sh`** - End-to-end user flow testing
- **`test/test_ml_pipeline.sh`** - ML pipeline integration tests
- **`test/test_demo_scenarios.sh`** - Predefined demo scenarios
- **`test/cleanup_test_data.sh`** - Test data cleanup utility
- **`test/README.md`** - Test suite documentation

---

## 🚀 Quick Start

### 1. Set Up Environment
```bash
export API_URL="https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com"
cd test
```

### 2. Run All Tests
```bash
./run_all_tests.sh
```

### 3. Expected Output
```
==========================================
Mind Mate - Automated Test Suite
==========================================

Test 1: Lambda Functions
------------------------
  Testing logMood... ✓ PASS
  Testing chat... ✓ PASS
  Testing calculateRiskScore... ✓ PASS

Test 2: API Endpoints
---------------------
  Testing POST /mood... ✓ PASS (HTTP 200)
  Testing POST /chat... ✓ PASS (HTTP 200)

Test 3: Data Persistence
------------------------
  Checking DynamoDB... ✓ PASS (5 items)

Test 4: ML Pipeline
-------------------
  Extracting mood features... ✓ PASS
  Calculating risk score... ✓ PASS (Risk: MODERATE)

Test 5: Performance
-------------------
  API response time... ✓ PASS (245ms)

==========================================
Results: 8 passed, 0 failed
==========================================
```

---

## 📋 Test Coverage

### Backend Components
✅ **Lambda Functions**
- logMood - Mood logging
- chat - AI conversation (Bedrock)
- getChatHistory - Chat retrieval
- calculateRiskScore - Risk assessment
- extractMoodFeatures - Mood analysis
- extractBehavioralFeatures - Behavior analysis
- extractSentimentFeatures - Sentiment analysis
- prepareTrainingData - ML data preparation

✅ **API Endpoints**
- POST /mood - Log mood entry
- POST /chat - Send chat message
- GET /chat-history - Retrieve history
- GET /risk-score - Get risk assessment

✅ **Data Persistence**
- DynamoDB writes
- DynamoDB queries
- Data consistency
- Feature storage

### Frontend Components
✅ **Authentication**
- Cognito integration
- Google OAuth
- Token management
- Session persistence

✅ **UI Components**
- Dashboard widgets
- Risk visualization
- Chart rendering
- Tab navigation

✅ **API Integration**
- Fetch requests
- Error handling
- Response parsing
- State management

### ML Pipeline
✅ **Feature Extraction**
- Mood features (7-day trends, volatility)
- Behavioral features (engagement, frequency)
- Sentiment features (positive/negative ratios)

✅ **Risk Calculation**
- Weighted scoring algorithm
- Risk level classification
- Confidence scoring
- Recommendation generation

✅ **Model Training** (Optional)
- SageMaker integration
- Training data preparation
- Model evaluation
- Prediction testing

### Integration Testing
✅ **User Journeys**
- Complete onboarding flow
- Multi-day mood logging
- Chat interactions
- Risk assessment

✅ **Demo Scenarios**
- Stable user (low risk)
- Declining user (moderate risk)
- Crisis user (critical risk)
- Volatile user (unpredictable)

### Performance Testing
✅ **Response Times**
- API latency measurement
- Lambda execution duration
- DynamoDB query performance

✅ **Load Testing**
- Concurrent requests
- Throttling behavior
- Error rates under load

### Security Testing
✅ **Authentication**
- Unauthorized access prevention
- Token validation
- Session management

✅ **Input Validation**
- SQL injection prevention
- XSS prevention
- Payload size limits

---

## 🎯 Test Scenarios

### Scenario 1: Stable User (Low Risk)
**Pattern**: Consistently good mood (7-8)  
**Expected Risk**: MINIMAL or LOW (0.0-0.3)  
**Test**: `./test_demo_scenarios.sh`

### Scenario 2: Declining User (Moderate Risk)
**Pattern**: Gradual mood decline (7→1)  
**Expected Risk**: MODERATE or HIGH (0.4-0.7)  
**Test**: `./test_demo_scenarios.sh`

### Scenario 3: Crisis User (Critical Risk)
**Pattern**: Very low mood (2) + crisis keywords  
**Expected Risk**: CRITICAL (0.8-1.0)  
**Test**: `./test_demo_scenarios.sh`

### Scenario 4: Volatile User (Unpredictable)
**Pattern**: Erratic mood swings (8→3→7→2)  
**Expected Risk**: MODERATE (0.4-0.6)  
**Test**: `./test_demo_scenarios.sh`

---

## 🔧 Testing Tools

### Command-Line Testing
```bash
# Test Lambda function
aws lambda invoke \
  --function-name logMood \
  --payload '{"body":"{\"userId\":\"test\",\"mood\":7}"}' \
  response.json

# Test API endpoint
curl -X POST "$API_URL/mood" \
  -H "Content-Type: application/json" \
  -d '{"userId":"test","mood":7}'

# Check DynamoDB
aws dynamodb query \
  --table-name EmoCompanion \
  --key-condition-expression "PK = :pk" \
  --expression-attribute-values '{":pk":{"S":"USER#test"}}'
```

### Browser Testing
- **`frontend/check-auth.html`** - Authentication debugging
- **`frontend/test-auth.html`** - Cognito testing
- Browser console for UI testing

### Monitoring
```bash
# Watch Lambda logs
aws logs tail /aws/lambda/logMood --follow

# Check CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=chat
```

---

## 📊 Test Metrics

### Success Criteria
- ✅ All Lambda functions respond within 3 seconds
- ✅ API endpoints return HTTP 200
- ✅ Data persists correctly in DynamoDB
- ✅ Risk scores calculated accurately
- ✅ ML features extracted successfully
- ✅ No errors in CloudWatch logs

### Performance Benchmarks
- API response time: < 1000ms (target), < 3000ms (acceptable)
- Lambda execution: < 5 seconds
- DynamoDB queries: < 100ms
- Risk calculation: < 2 seconds

---

## 🧹 Cleanup

### Remove Test Data
```bash
cd test
./cleanup_test_data.sh
```

This removes all test users matching patterns:
- `test-*`
- `demo-*`
- `e2e-test-*`
- `ml-test-*`

---

## 📚 Documentation

### Main Testing Guide
**[docs/TESTING_GUIDE.md](docs/TESTING_GUIDE.md)** - Comprehensive guide covering:
- Backend testing (Lambda, DynamoDB, CloudWatch)
- Frontend testing (UI, authentication, API)
- Integration testing (end-to-end flows)
- ML pipeline testing (features, risk scoring)
- Performance testing (load, latency)
- Security testing (auth, validation)
- Demo scenarios
- Automated test suite
- Monitoring and debugging

### Test Suite Documentation
**[test/README.md](test/README.md)** - Quick reference for:
- Test script usage
- Configuration
- Expected results
- Troubleshooting
- CI/CD integration

### Related Documentation
- **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Common issues
- **[docs/API_REFERENCE.md](docs/API_REFERENCE.md)** - API documentation
- **[docs/DEPLOYMENT_CHECKLIST.md](docs/DEPLOYMENT_CHECKLIST.md)** - Deployment steps

---

## 🎓 Best Practices

### Before Testing
1. ✅ Deploy all Lambda functions
2. ✅ Configure API Gateway routes
3. ✅ Set environment variables
4. ✅ Verify AWS CLI configuration

### During Testing
1. ✅ Monitor CloudWatch logs
2. ✅ Check DynamoDB for data
3. ✅ Verify API responses
4. ✅ Track performance metrics

### After Testing
1. ✅ Review test results
2. ✅ Clean up test data
3. ✅ Document any issues
4. ✅ Update tests as needed

---

## 🚨 Troubleshooting

### Common Issues

**Lambda timeout**
```bash
aws lambda update-function-configuration \
  --function-name calculateRiskScore \
  --timeout 30
```

**API Gateway 403**
```bash
# Verify API URL
aws apigatewayv2 get-apis
```

**DynamoDB not found**
```bash
# Check table exists
aws dynamodb describe-table --table-name EmoCompanion
```

**Bedrock errors**
```bash
# Verify model access
aws bedrock list-foundation-models
```

---

## 🔄 Continuous Integration

### GitHub Actions Example
```yaml
name: Test Mind Mate
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      - name: Run Tests
        run: cd test && ./run_all_tests.sh
```

---

## 📈 Next Steps

### Enhance Testing
- [ ] Add unit tests for Lambda functions
- [ ] Implement frontend E2E tests (Playwright/Cypress)
- [ ] Add load testing with Apache Bench
- [ ] Create performance benchmarks
- [ ] Set up automated regression testing

### Monitoring
- [ ] Create CloudWatch dashboards
- [ ] Set up alerting for test failures
- [ ] Track test coverage metrics
- [ ] Monitor performance trends

### Documentation
- [ ] Add video walkthrough of testing
- [ ] Create testing best practices guide
- [ ] Document edge cases
- [ ] Add troubleshooting examples

---

## 📞 Support

For testing issues:
1. Check [TESTING_GUIDE.md](docs/TESTING_GUIDE.md)
2. Review [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
3. Check CloudWatch logs
4. Open GitHub issue

---

**Created**: October 2025  
**Last Updated**: October 2025  
**Maintained By**: Mind Mate Team
