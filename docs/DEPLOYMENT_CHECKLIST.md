# Mind Mate Deployment Checklist

## Pre-Deployment

- [ ] AWS account created
- [ ] IAM user created (not root)
- [ ] AWS CLI installed (`aws --version`)
- [ ] AWS CLI configured (`aws configure`)
- [ ] Region set to **us-east-1**
- [ ] Budget alert created ($20/month)

## Step 1: Enable Bedrock Models

- [ ] Go to AWS Console → Bedrock → Model access
- [ ] Enable **Anthropic Claude 3 Haiku**
- [ ] Enable **Amazon Titan Image Generator G1**
- [ ] Wait for approval (usually instant)

## Step 2: Deploy Infrastructure

- [ ] Deploy CloudFormation stack
- [ ] Verify DynamoDB table created: `EmoCompanion`
- [ ] Verify S3 bucket created: `mindmate-uploads-*`
- [ ] Verify IAM role created: `MindMateLambdaRole`
- [ ] Verify API Gateway created: `MindMateAPI`
- [ ] Copy API Gateway Invoke URL

## Step 3: Deploy Lambda Functions

- [ ] Run `deploy-lambdas.sh` script
- [ ] Verify all 6 functions deployed:
  - [ ] logMood
  - [ ] analyzeSelfie
  - [ ] analyzeScene
  - [ ] generateAvatar
  - [ ] dailyRecap
  - [ ] riskScan
- [ ] Check environment variables set correctly

## Step 4: Configure API Gateway

- [ ] Create route: `POST /mood` → logMood
- [ ] Create route: `POST /selfie` → analyzeSelfie
- [ ] Create route: `POST /scene` → analyzeScene
- [ ] Create route: `POST /avatar` → generateAvatar
- [ ] Enable CORS for all routes
- [ ] Test API with curl

## Step 5: Set Up SES

- [ ] Verify sender email address
- [ ] Verify recipient email address (if sandbox)
- [ ] Check inbox for verification emails
- [ ] Click verification links
- [ ] Test sending email manually

## Step 6: Create EventBridge Rules

- [ ] Create rule: `DailyRecap7am` (cron: `0 20 * * ? *`)
- [ ] Add Lambda permission for dailyRecap
- [ ] Add target: dailyRecap function
- [ ] Create rule: `RiskScanDaily` (cron: `0 11 * * ? *`)
- [ ] Add Lambda permission for riskScan
- [ ] Add target: riskScan function

## Step 7: Deploy Frontend

- [ ] Edit `frontend/index.html`
- [ ] Replace API URL with your API Gateway URL
- [ ] Go to AWS Amplify → Host web app
- [ ] Deploy without Git
- [ ] Upload index.html
- [ ] Copy Amplify app URL

## Step 8: Testing

- [ ] Open Amplify URL in browser
- [ ] Test mood logging
- [ ] Test selfie upload
- [ ] Test avatar generation
- [ ] Check DynamoDB for stored data
- [ ] Manually trigger dailyRecap
- [ ] Check email inbox
- [ ] Log low moods (3-4 days)
- [ ] Manually trigger riskScan
- [ ] Verify risk alert email received

## Step 9: Monitoring

- [ ] Check CloudWatch Logs for Lambda errors
- [ ] Monitor DynamoDB item count
- [ ] Check S3 bucket for uploaded images
- [ ] Review AWS Cost Explorer

## Optional Enhancements

- [ ] Add Cognito authentication
- [ ] Create QuickSight dashboard
- [ ] Set up Athena for analytics
- [ ] Add Bedrock Guardrails
- [ ] Request SES production access
- [ ] Add custom domain to Amplify

## Demo Preparation

- [ ] Create demo user account
- [ ] Log 7 days of varied moods
- [ ] Upload 2-3 selfies
- [ ] Generate pet avatar
- [ ] Trigger daily recap
- [ ] Trigger risk scan
- [ ] Take screenshots
- [ ] Record video walkthrough

## Cleanup (Post-Hackathon)

- [ ] Delete EventBridge rules
- [ ] Empty S3 bucket
- [ ] Delete CloudFormation stack
- [ ] Delete Lambda functions
- [ ] Delete API Gateway
- [ ] Delete Amplify app
- [ ] Remove SES verified identities
- [ ] Delete IAM role
