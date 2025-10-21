# Mind Mate - Test Suite

Automated testing scripts for the Mind Mate application.

## Quick Start

### Run All Tests
```bash
# Set your API URL
export API_URL="https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com"

# Run complete test suite
./run_all_tests.sh
```

## Test Scripts

### 1. `run_all_tests.sh`
**Comprehensive test suite covering all components**

Tests:
- Lambda function invocations
- API endpoint responses
- Data persistence in DynamoDB
- ML pipeline (feature extraction + risk scoring)
- Performance metrics

Usage:
```bash
./run_all_tests.sh
```

### 2. `test_user_journey.sh`
**End-to-end user flow testing**

Simulates complete user journey:
1. User onboarding
2. First mood log
3. Chat interaction
4. Multiple mood logs over 7 days
5. Chat history retrieval
6. Risk assessment

Usage:
```bash
./test_user_journey.sh
```

### 3. `test_ml_pipeline.sh`
**ML pipeline integration testing**

Tests:
- Synthetic data generation (30 days)
- Mood feature extraction
- Behavioral feature extraction
- Sentiment feature extraction
- Risk score calculation
- Feature storage verification

Usage:
```bash
# Test with auto-generated user ID
./test_ml_pipeline.sh

# Test with specific user ID
./test_ml_pipeline.sh my-test-user
```

### 4. `test_demo_scenarios.sh`
**Predefined demo scenarios**

Tests 4 user patterns:
1. **Stable User**: Consistently good mood → LOW risk
2. **Declining User**: Gradual mood decline → MODERATE/HIGH risk
3. **Crisis User**: Severe low mood + crisis keywords → CRITICAL risk
4. **Volatile User**: Erratic mood swings → MODERATE risk

Usage:
```bash
./test_demo_scenarios.sh
```

### 5. `cleanup_test_data.sh`
**Remove all test data**

Cleans up test users from DynamoDB:
- Removes users matching patterns: `test-*`, `demo-*`, `e2e-test-*`, `ml-test-*`
- Deletes from both EmoCompanion and MoodFeatures tables
- Interactive confirmation before deletion

Usage:
```bash
./cleanup_test_data.sh
```

## Test Data Files

### `sample-payloads.json`
Example payloads for manual Lambda testing:
- logMood
- analyzeSelfie
- generateAvatar
- dailyRecap
- riskScan

Usage:
```bash
aws lambda invoke \
  --function-name logMood \
  --cli-input-json file://sample-payloads.json \
  response.json
```

## Configuration

### Environment Variables

```bash
# Required
export API_URL="https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com"

# Optional
export AWS_REGION="us-east-1"
export TABLE_NAME="EmoCompanion"
```

### AWS CLI Configuration

Ensure AWS CLI is configured:
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Default region: us-east-1
```

## Expected Results

### Successful Test Run
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
Test Suite Complete
==========================================
Results: 8 passed, 0 failed
==========================================
```

## Troubleshooting

### Lambda Function Not Found
```bash
# Check if function exists
aws lambda list-functions --query 'Functions[?contains(FunctionName, `logMood`)].FunctionName'

# Deploy functions if missing
cd ../infrastructure
./deploy-lambdas.sh
```

### API Gateway 403 Error
```bash
# Check API Gateway URL
aws apigatewayv2 get-apis --query 'Items[?Name==`MindMateAPI`].ApiEndpoint'

# Update API_URL environment variable
export API_URL="https://YOUR_CORRECT_API_ID.execute-api.us-east-1.amazonaws.com"
```

### DynamoDB Table Not Found
```bash
# Check if table exists
aws dynamodb describe-table --table-name EmoCompanion

# Create table if missing
cd ../infrastructure
./deploy-ml-stack.sh
```

### Slow Performance
- Check Lambda memory allocation (increase if needed)
- Verify DynamoDB is not throttling
- Check CloudWatch logs for errors

## CI/CD Integration

### GitHub Actions
```yaml
# .github/workflows/test.yml
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

## Additional Resources

- [TESTING_GUIDE.md](../docs/TESTING_GUIDE.md) - Comprehensive testing documentation
- [TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md) - Common issues and solutions
- [API_REFERENCE.md](../docs/API_REFERENCE.md) - API endpoint documentation

## Support

For issues or questions:
1. Check [TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md)
2. Review CloudWatch logs
3. Open an issue on GitHub
