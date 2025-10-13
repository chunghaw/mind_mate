# Mind Mate Troubleshooting Guide

## Common Issues and Solutions

### Lambda Function Errors

**Error: "Unable to import module 'lambda_function'"**
- **Cause:** Missing dependencies or wrong file structure
- **Fix:** Ensure `lambda_function.py` is at root of zip file
```bash
cd backend/lambdas/logMood
zip -r function.zip lambda_function.py
```

**Error: "Task timed out after 3.00 seconds"**
- **Cause:** Default timeout too short
- **Fix:** Increase timeout in Lambda configuration
```bash
aws lambda update-function-configuration \
  --function-name dailyRecap \
  --timeout 30
```

**Error: "An error occurred (AccessDeniedException)"**
- **Cause:** IAM role missing permissions
- **Fix:** Check role has required policies (DynamoDB, S3, Bedrock, etc.)

### DynamoDB Issues

**Error: "The security token included in the request is invalid"**
- **Cause:** AWS CLI not configured or expired credentials
- **Fix:** Run `aws configure` and enter credentials

**No data showing in table**
- **Cause:** Lambda not writing or wrong table name
- **Fix:** Check Lambda environment variable `TABLE_NAME`
```bash
aws lambda get-function-configuration --function-name logMood \
  --query 'Environment.Variables'
```

### API Gateway Issues

**Error: "Missing Authentication Token"**
- **Cause:** Wrong URL or route not configured
- **Fix:** Check API Gateway routes match `/mood`, `/selfie`, etc.

**CORS errors in browser**
- **Cause:** CORS not enabled
- **Fix:** Enable CORS in API Gateway for all origins (*)

**Error: "Internal server error"**
- **Cause:** Lambda function error
- **Fix:** Check CloudWatch Logs
```bash
aws logs tail /aws/lambda/logMood --follow
```

### Bedrock Issues

**Error: "Could not resolve the foundation model"**
- **Cause:** Model not enabled or wrong model ID
- **Fix:** Go to Bedrock → Model access → Enable models

**Error: "AccessDeniedException: User is not authorized"**
- **Cause:** IAM role missing bedrock:InvokeModel permission
- **Fix:** Add Bedrock permissions to Lambda role

**Wrong model ID examples:**
- ❌ `claude-3-haiku`
- ✅ `anthropic.claude-3-haiku-20240307-v1:0`

### Rekognition Issues

**Error: "InvalidImageFormatException"**
- **Cause:** Image not in S3 or wrong format
- **Fix:** Ensure image uploaded to S3 first, then call Rekognition

**Error: "InvalidS3ObjectException"**
- **Cause:** Lambda can't access S3 object
- **Fix:** Check IAM role has s3:GetObject permission

### SES Issues

**Error: "Email address is not verified"**
- **Cause:** Sender/recipient not verified (sandbox mode)
- **Fix:** Verify both emails
```bash
aws ses verify-email-identity --email-address your@email.com
```

**No email received**
- **Cause:** Email in spam or SES sandbox limits
- **Fix:** Check spam folder, request production access

**Error: "Daily sending quota exceeded"**
- **Cause:** Sandbox limit = 200 emails/day
- **Fix:** Request production access via SES console

### EventBridge Issues

**Lambda not triggering on schedule**
- **Cause:** Missing Lambda permission or wrong target
- **Fix:** Add permission for EventBridge to invoke Lambda
```bash
aws lambda add-permission \
  --function-name dailyRecap \
  --statement-id DailyRecapEvent \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com
```

**Wrong timezone**
- **Cause:** EventBridge uses UTC
- **Fix:** Convert your local time to UTC for cron expression

### Frontend Issues

**API calls failing with CORS error**
- **Cause:** API Gateway CORS not configured
- **Fix:** Enable CORS in API Gateway settings

**"Failed to fetch" error**
- **Cause:** Wrong API URL or network issue
- **Fix:** Check API URL in `index.html` matches API Gateway

**Image upload not working**
- **Cause:** File too large or wrong format
- **Fix:** Limit to <5MB, accept only image/*

## Debugging Commands

**Check Lambda logs:**
```bash
aws logs tail /aws/lambda/FUNCTION_NAME --follow
```

**Test Lambda manually:**
```bash
aws lambda invoke \
  --function-name logMood \
  --payload '{"body":"{\"userId\":\"test\",\"mood\":7}"}' \
  response.json
cat response.json
```

**Check DynamoDB items:**
```bash
aws dynamodb scan --table-name EmoCompanion --limit 5
```

**List S3 objects:**
```bash
aws s3 ls s3://mindmate-uploads-ACCOUNT_ID/selfies/ --recursive
```

**Check API Gateway routes:**
```bash
aws apigatewayv2 get-routes --api-id YOUR_API_ID
```

**View CloudFormation stack status:**
```bash
aws cloudformation describe-stacks --stack-name mindmate-stack
```

## Cost Issues

**Unexpected charges**
- Check AWS Cost Explorer
- Look for Rekognition or Bedrock usage spikes
- Set up billing alerts

**How to reduce costs:**
- Limit Rekognition to 2 images/day
- Use shorter Bedrock prompts
- Delete old S3 objects
- Use HTTP API instead of REST API

## Getting Help

1. Check CloudWatch Logs first
2. Search AWS documentation
3. Check AWS forums
4. Use AWS Support (if you have a plan)
5. Ask in AWS Discord/Slack communities
