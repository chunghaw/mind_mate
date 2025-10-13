# Mind Mate - Quick Setup Guide

## Prerequisites
- AWS Account with ~$100 credit
- AWS CLI v2 installed and configured
- Region: **us-east-1** (recommended)

## Step-by-Step Setup

### 1. Enable Bedrock Models
```bash
# Go to AWS Console → Bedrock → Model access
# Enable:
# - Anthropic Claude 3 Haiku
# - Amazon Titan Image Generator G1
```

### 2. Deploy Infrastructure
```bash
# Option A: Using CloudFormation
cd infrastructure
aws cloudformation create-stack \
  --stack-name mindmate-stack \
  --template-body file://cloudformation-template.yaml \
  --parameters ParameterKey=SenderEmail,ParameterValue=your@email.com \
               ParameterKey=RecipientEmail,ParameterValue=user@email.com \
  --capabilities CAPABILITY_NAMED_IAM

# Wait for stack creation
aws cloudformation wait stack-create-complete --stack-name mindmate-stack

# Get outputs
aws cloudformation describe-stacks --stack-name mindmate-stack --query 'Stacks[0].Outputs'
```

### 3. Deploy Lambda Functions
```bash
cd infrastructure
chmod +x deploy-lambdas.sh

# Replace with your values
./deploy-lambdas.sh EmoCompanion mindmate-uploads-ACCOUNT_ID your@email.com user@email.com
```

### 4. Set Up API Gateway Routes

**Console → API Gateway → MindMateAPI → Routes**

Create these routes and integrations:
- `POST /mood` → Lambda: `logMood`
- `POST /selfie` → Lambda: `analyzeSelfie`
- `POST /scene` → Lambda: `analyzeScene`
- `POST /avatar` → Lambda: `generateAvatar`

Copy the **Invoke URL** (e.g., `https://abc123.execute-api.us-east-1.amazonaws.com`)

### 5. Verify SES Email Addresses

```bash
# Verify sender email
aws ses verify-email-identity --email-address your@email.com

# Verify recipient email (if in sandbox)
aws ses verify-email-identity --email-address user@email.com

# Check verification status
aws ses get-identity-verification-attributes --identities your@email.com
```

Check your inbox and click verification links.

### 6. Create EventBridge Rules

**Daily Recap (7 AM daily)**
```bash
aws events put-rule \
  --name DailyRecap7am \
  --schedule-expression "cron(0 20 * * ? *)" \
  --state ENABLED

aws lambda add-permission \
  --function-name dailyRecap \
  --statement-id DailyRecapEvent \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn arn:aws:events:us-east-1:ACCOUNT_ID:rule/DailyRecap7am

aws events put-targets \
  --rule DailyRecap7am \
  --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:ACCOUNT_ID:function:dailyRecap"
```

**Risk Scan (Daily at 8 PM)**
```bash
aws events put-rule \
  --name RiskScanDaily \
  --schedule-expression "cron(0 11 * * ? *)" \
  --state ENABLED

aws lambda add-permission \
  --function-name riskScan \
  --statement-id RiskScanEvent \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn arn:aws:events:us-east-1:ACCOUNT_ID:rule/RiskScanDaily

aws events put-targets \
  --rule RiskScanDaily \
  --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:ACCOUNT_ID:function:riskScan"
```

### 7. Deploy Frontend to Amplify

**Console → AWS Amplify → Host web app → Deploy without Git**

1. Upload `frontend/index.html`
2. Edit the file and replace `API` constant with your API Gateway URL
3. Save and deploy
4. Copy the Amplify app URL

### 8. Test the Application

**Test mood logging:**
```bash
curl -X POST "https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/mood" \
  -H "Content-Type: application/json" \
  -d '{"userId":"demo-user","mood":7,"tags":["happy"],"notes":"Great day!"}'
```

**Test via web app:**
1. Open Amplify URL
2. Log a mood
3. Upload a selfie
4. Check DynamoDB for stored data

### 9. Manual Testing

**Trigger daily recap manually:**
```bash
aws lambda invoke \
  --function-name dailyRecap \
  --payload '{"userId":"demo-user"}' \
  response.json

cat response.json
```

**Trigger risk scan manually:**
```bash
aws lambda invoke \
  --function-name riskScan \
  --payload '{"userId":"demo-user"}' \
  response.json

cat response.json
```

## Troubleshooting

**Lambda errors:**
```bash
# Check logs
aws logs tail /aws/lambda/logMood --follow
```

**SES not sending:**
- Verify both sender and recipient emails
- Check SES sending limits (sandbox = 200 emails/day)
- Request production access if needed

**Bedrock errors:**
- Ensure models are enabled in us-east-1
- Check IAM permissions for bedrock:InvokeModel

**API Gateway CORS:**
- Ensure CORS is enabled for all origins (*)
- Check OPTIONS method is configured

## Cost Monitoring

```bash
# Set up budget alert
aws budgets create-budget \
  --account-id ACCOUNT_ID \
  --budget file://budget.json
```

## Cleanup

```bash
# Delete stack
aws cloudformation delete-stack --stack-name mindmate-stack

# Empty S3 bucket first
aws s3 rm s3://mindmate-uploads-ACCOUNT_ID --recursive
```

## Next Steps

- Add Cognito authentication
- Build mobile app with React Native
- Add voice input with Transcribe
- Create QuickSight dashboard
- Implement Bedrock Guardrails
