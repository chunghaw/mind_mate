# 🚀 Get Started with Mind Mate

Welcome! This guide will get you from zero to deployed in 30 minutes.

## 📋 What You Need

- [ ] AWS Account (with ~$100 credit)
- [ ] AWS CLI installed ([Install Guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html))
- [ ] 30 minutes of time

## 🎯 Quick Path (Choose One)

### Path A: I Want to Deploy NOW (30 min)
→ Follow **README_QUICKSTART.md**

### Path B: I Want to Understand Everything (1 hour)
→ Follow **docs/SETUP_GUIDE.md**

### Path C: I'm New to AWS (2 hours)
1. Read **docs/AWS_SERVICES_EXPLAINED.md** (15 min)
2. Follow **docs/DEPLOYMENT_CHECKLIST.md** (1.5 hours)

## 🏃 Super Quick Start (5 Commands)

```bash
# 1. Enable Bedrock models in AWS Console first!
# Go to: Bedrock → Model access → Enable Claude & Titan

# 2. Deploy infrastructure
cd infrastructure
aws cloudformation create-stack \
  --stack-name mindmate \
  --template-body file://cloudformation-template.yaml \
  --parameters ParameterKey=SenderEmail,ParameterValue=YOUR_EMAIL@example.com \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1

# 3. Wait for stack (2-3 minutes)
aws cloudformation wait stack-create-complete --stack-name mindmate

# 4. Get outputs
aws cloudformation describe-stacks --stack-name mindmate \
  --query 'Stacks[0].Outputs' --output table

# 5. Deploy Lambda functions
./deploy-lambdas.sh EmoCompanion mindmate-uploads-ACCOUNT_ID YOUR_EMAIL@example.com
```

Then:
- Configure API Gateway routes in Console
- Verify SES email
- Deploy frontend to Amplify
- Test!

## 📚 Documentation Map

**Start Here:**
- `README_QUICKSTART.md` - 5-minute setup
- `SUMMARY.md` - Project overview

**Setup & Deployment:**
- `docs/SETUP_GUIDE.md` - Detailed setup
- `docs/DEPLOYMENT_CHECKLIST.md` - Step-by-step checklist
- `infrastructure/deploy-lambdas.sh` - Deployment script

**Learning:**
- `docs/AWS_SERVICES_EXPLAINED.md` - AWS basics
- `docs/BEDROCK_PROMPTS.md` - AI prompt engineering
- `docs/COST_BREAKDOWN.md` - Cost analysis

**Reference:**
- `docs/API_REFERENCE.md` - API documentation
- `PROJECT_STRUCTURE.md` - File structure
- `agent.md` - Original requirements

**Help:**
- `docs/TROUBLESHOOTING.md` - Common issues
- `docs/DEMO_SCRIPT.md` - Hackathon demo guide

## 🎬 Demo Preparation

1. Deploy everything (30 min)
2. Test all features (10 min)
3. Read `docs/DEMO_SCRIPT.md` (5 min)
4. Practice demo (15 min)
5. Record backup video (10 min)

**Total: 70 minutes to demo-ready**

## 💡 Key Features to Highlight

1. **Predictive Prevention** - Detects mental health risks early
2. **Multi-Modal AI** - Text + Vision + Image Generation
3. **Privacy-First** - No raw facial data stored
4. **Fully Serverless** - Scales automatically
5. **Cost-Effective** - <$1/month for demo

## 🆘 Stuck?

1. Check `docs/TROUBLESHOOTING.md`
2. Review CloudWatch Logs
3. Test with curl commands
4. Verify AWS Console settings

## 🎯 Success Checklist

- [ ] All Lambda functions deployed
- [ ] API Gateway routes configured
- [ ] SES emails verified
- [ ] Frontend deployed to Amplify
- [ ] Mood logging works
- [ ] Selfie analysis works
- [ ] Avatar generation works
- [ ] Daily recap email received
- [ ] Risk scan detects low moods

## 🏆 You're Ready!

Once you complete the checklist above, you have a **production-ready AWS AI Agent** that:
- Tracks moods
- Analyzes emotions
- Generates AI avatars
- Sends daily recaps
- Predicts mental health risks
- Sends prevention alerts

**Now go win that hackathon! 🚀**

---

## Next Steps After Deployment

1. **Test Everything** - Use `test/test-api.sh`
2. **Monitor Costs** - Check AWS Cost Explorer
3. **Prepare Demo** - Follow `docs/DEMO_SCRIPT.md`
4. **Add Features** - See `CONTRIBUTING.md`
5. **Scale Up** - Add Cognito, QuickSight, mobile app

---

## Quick Links

- [AWS Console](https://console.aws.amazon.com/)
- [Bedrock Model Access](https://console.aws.amazon.com/bedrock/home#/modelaccess)
- [Lambda Functions](https://console.aws.amazon.com/lambda/home)
- [API Gateway](https://console.aws.amazon.com/apigateway/home)
- [DynamoDB Tables](https://console.aws.amazon.com/dynamodbv2/home)
- [S3 Buckets](https://console.aws.amazon.com/s3/home)
- [Amplify Apps](https://console.aws.amazon.com/amplify/home)
- [SES Email Verification](https://console.aws.amazon.com/ses/home)
