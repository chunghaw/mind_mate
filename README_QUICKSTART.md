# Mind Mate - Quick Start (5 Minutes)

Get Mind Mate running with minimal setup.

## 1. Enable Bedrock Models (2 min)
```
AWS Console → Bedrock → Model access → Enable:
- Anthropic Claude 3 Haiku
- Amazon Titan Image Generator G1
```

## 2. Deploy Infrastructure (1 min)
```bash
cd infrastructure
aws cloudformation create-stack \
  --stack-name mindmate \
  --template-body file://cloudformation-template.yaml \
  --parameters \
    ParameterKey=SenderEmail,ParameterValue=YOUR_EMAIL \
    ParameterKey=RecipientEmail,ParameterValue=YOUR_EMAIL \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1

# Wait ~2 minutes
aws cloudformation wait stack-create-complete --stack-name mindmate
```

## 3. Get Stack Outputs
```bash
aws cloudformation describe-stacks --stack-name mindmate \
  --query 'Stacks[0].Outputs' --output table
```

Copy: `ApiEndpoint`, `BucketName`, `TableName`

## 4. Deploy Lambdas (1 min)
```bash
chmod +x deploy-lambdas.sh
./deploy-lambdas.sh <TableName> <BucketName> YOUR_EMAIL YOUR_EMAIL
```

## 5. Configure API Routes (1 min)
```
Console → API Gateway → MindMateAPI → Routes → Create:
- POST /mood → logMood
- POST /selfie → analyzeSelfie
- POST /avatar → generateAvatar
```

## 6. Verify SES Email
Check your inbox for AWS verification email and click the link.

## 7. Deploy Frontend
```bash
# Edit frontend/index.html line 139:
const API = "YOUR_API_ENDPOINT";

# Then:
Console → Amplify → Host web app → Deploy without Git
Upload: frontend/index.html
```

## 8. Test!
Open Amplify URL → Log a mood → Upload a selfie

## Done! 🎉

**Next:** See `docs/SETUP_GUIDE.md` for EventBridge scheduling and advanced features.
