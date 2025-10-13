# AWS Services Explained (Beginner-Friendly)

## Core Services Used in Mind Mate

### 1. Amazon Bedrock
**What it is:** AI models as a service  
**What you do:** Call APIs to generate text or images  
**In Mind Mate:** 
- Claude generates empathetic daily recaps
- Titan creates your AI pet avatar
**Cost:** ~$0.001 per 1000 tokens (very cheap for text)

### 2. AWS Lambda
**What it is:** Run code without servers  
**What you do:** Upload Python code, it runs when triggered  
**In Mind Mate:** 6 functions (logMood, analyzeSelfie, etc.)  
**Cost:** Free tier = 1M requests/month, then $0.20 per 1M

### 3. DynamoDB
**What it is:** NoSQL database (key-value store)  
**What you do:** Store JSON-like data with PK/SK keys  
**In Mind Mate:** Stores moods, emotions, recaps  
**Cost:** Free tier = 25GB storage + 25 read/write units

### 4. Amazon S3
**What it is:** Cloud file storage  
**What you do:** Upload/download files via API  
**In Mind Mate:** Stores selfie images  
**Cost:** $0.023 per GB/month (pennies for demo)

### 5. API Gateway (HTTP API)
**What it is:** Creates REST endpoints  
**What you do:** Route URLs to Lambda functions  
**In Mind Mate:** `/mood`, `/selfie` routes  
**Cost:** $1 per million requests (HTTP API is cheaper than REST)

### 6. Amazon Rekognition
**What it is:** Computer vision API  
**What you do:** Send image, get emotions/labels back  
**In Mind Mate:** Detects facial emotions from selfies  
**Cost:** $1 per 1000 images (limit to 2/day = $0.06/month)

### 7. Amazon SES (Simple Email Service)
**What it is:** Programmatic email sending  
**What you do:** Call API to send emails  
**In Mind Mate:** Sends daily recaps and risk alerts  
**Cost:** $0.10 per 1000 emails (1 email/day = $0.003/month)

### 8. Amazon EventBridge
**What it is:** Cron scheduler in the cloud  
**What you do:** Set schedule, trigger Lambda  
**In Mind Mate:** Runs dailyRecap at 7 AM daily  
**Cost:** Free for scheduled rules

### 9. AWS Amplify
**What it is:** Static website hosting  
**What you do:** Upload HTML/React, get a URL  
**In Mind Mate:** Hosts the web app frontend  
**Cost:** Free tier = 1000 build minutes, 15GB served/month

### 10. Amazon Athena (Optional)
**What it is:** SQL queries on S3 files  
**What you do:** Write SQL, query JSON/CSV in S3  
**In Mind Mate:** Analyze mood trends  
**Cost:** $5 per TB scanned (demo = pennies)

### 11. Amazon QuickSight (Optional)
**What it is:** BI dashboard tool  
**What you do:** Connect to data, create charts  
**In Mind Mate:** Visualize mood trends  
**Cost:** $9/month per user (skip for demo)

## How They Connect

```
User Browser (Amplify)
    ↓ POST /mood
API Gateway
    ↓ triggers
Lambda (logMood)
    ↓ writes to
DynamoDB
    ↑ reads from
Lambda (dailyRecap) ← triggered by EventBridge (daily)
    ↓ calls
Bedrock (Claude) → generates text
    ↓ sends via
SES → Email to user
```

## Total Estimated Cost (Demo Usage)
- Lambda: Free tier
- DynamoDB: Free tier
- S3: $0.05/month
- Rekognition: $0.06/month (2 images/day)
- Bedrock: $0.50/month (daily recaps)
- SES: $0.003/month (1 email/day)
- API Gateway: Free tier
- Amplify: Free tier

**Total: ~$1-2/month for light demo usage**

## Key Concepts

### Serverless
No EC2 instances to manage. Services scale automatically and you pay per use.

### IAM (Identity and Access Management)
Controls who/what can access AWS services. Lambda needs a "role" with permissions.

### Region
AWS data centers. Use **us-east-1** (N. Virginia) for best service availability.

### ARN (Amazon Resource Name)
Unique ID for AWS resources. Format: `arn:aws:service:region:account:resource`

### Environment Variables
Config values passed to Lambda (TABLE_NAME, BUCKET, etc.)
