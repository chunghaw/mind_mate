# Mind Mate - Cost Breakdown

## Monthly Cost Estimate (Light Demo Usage)

### Assumptions
- 1 user
- 2 mood logs per day
- 1 selfie per day
- 1 daily recap email
- 1 risk scan per day

---

## Service-by-Service Breakdown

### 1. AWS Lambda
**Usage:**
- 60 mood logs/month × 100ms = 6 seconds
- 30 selfie analyses/month × 500ms = 15 seconds
- 30 daily recaps/month × 2s = 60 seconds
- 30 risk scans/month × 2s = 60 seconds
- **Total: 141 seconds = 0.039 hours**

**Cost:**
- Compute: 0.039 hours × 256MB × $0.0000166667 = $0.0001
- Requests: 150 requests × $0.20/1M = $0.00003
- **Lambda Total: ~$0.00 (Free Tier)**

### 2. DynamoDB
**Usage:**
- 150 writes/month (moods, selfies, recaps)
- 200 reads/month (queries for recaps/risk)
- Storage: <1GB

**Cost:**
- Writes: 150 × $1.25/1M = $0.0002
- Reads: 200 × $0.25/1M = $0.00005
- Storage: 1GB × $0.25 = $0.25
- **DynamoDB Total: ~$0.25/month**

### 3. Amazon S3
**Usage:**
- 30 selfies × 500KB = 15MB
- 5 avatars × 200KB = 1MB
- **Total: 16MB storage**

**Cost:**
- Storage: 0.016GB × $0.023 = $0.0004
- PUT requests: 35 × $0.005/1000 = $0.0002
- GET requests: 100 × $0.0004/1000 = $0.00004
- **S3 Total: ~$0.001/month**

### 4. Amazon Rekognition
**Usage:**
- 30 selfies/month (DetectFaces)

**Cost:**
- 30 images × $0.001 = $0.03
- **Rekognition Total: ~$0.03/month**

### 5. Amazon Bedrock
**Usage:**
- Daily recaps: 30 × 350 tokens = 10,500 tokens
- Risk alerts: 5 × 500 tokens = 2,500 tokens
- **Total: 13,000 tokens**

**Cost (Claude 3 Haiku):**
- Input: 8,000 tokens × $0.25/1M = $0.002
- Output: 5,000 tokens × $1.25/1M = $0.006
- **Bedrock Total: ~$0.008/month**

### 6. Amazon Bedrock (Titan Image)
**Usage:**
- 2 avatar generations/month

**Cost:**
- 2 images × $0.008 = $0.016
- **Titan Total: ~$0.016/month**

### 7. Amazon SES
**Usage:**
- 30 daily recaps
- 5 risk alerts
- **Total: 35 emails**

**Cost:**
- 35 emails × $0.0001 = $0.0035
- **SES Total: ~$0.004/month**

### 8. API Gateway (HTTP API)
**Usage:**
- 150 API calls/month

**Cost:**
- 150 × $1/1M = $0.00015
- **API Gateway Total: ~$0.00 (Free Tier)**

### 9. AWS Amplify
**Usage:**
- Static hosting
- <1GB served/month

**Cost:**
- Build minutes: 0 (manual deploy)
- Hosting: Free tier
- **Amplify Total: ~$0.00 (Free Tier)**

### 10. EventBridge
**Usage:**
- 2 rules × 30 invocations = 60 events

**Cost:**
- Free for scheduled rules
- **EventBridge Total: ~$0.00**

### 11. CloudWatch Logs
**Usage:**
- ~50MB logs/month

**Cost:**
- Ingestion: 0.05GB × $0.50 = $0.025
- Storage: 0.05GB × $0.03 = $0.0015
- **CloudWatch Total: ~$0.027/month**

---

## Total Monthly Cost

| Service | Cost |
|---------|------|
| Lambda | $0.00 |
| DynamoDB | $0.25 |
| S3 | $0.00 |
| Rekognition | $0.03 |
| Bedrock (Claude) | $0.01 |
| Bedrock (Titan) | $0.02 |
| SES | $0.00 |
| API Gateway | $0.00 |
| Amplify | $0.00 |
| EventBridge | $0.00 |
| CloudWatch | $0.03 |
| **TOTAL** | **~$0.34/month** |

---

## Scaling Scenarios

### 10 Users
- Lambda: $0.00 (still free tier)
- DynamoDB: $2.50
- Rekognition: $0.30
- Bedrock: $0.10
- SES: $0.04
- **Total: ~$3.00/month**

### 100 Users
- Lambda: $0.50
- DynamoDB: $25.00
- Rekognition: $3.00
- Bedrock: $1.00
- SES: $0.35
- **Total: ~$30.00/month**

### 1,000 Users
- Lambda: $5.00
- DynamoDB: $250.00
- Rekognition: $30.00
- Bedrock: $10.00
- SES: $3.50
- **Total: ~$300.00/month**

---

## Cost Optimization Tips

### 1. Limit Rekognition Usage
- Max 2 selfies per day per user
- Cache emotion results for 1 hour
- **Savings: 50%**

### 2. Use Shorter Bedrock Prompts
- Reduce max_tokens from 300 to 200
- Use more concise system prompts
- **Savings: 30%**

### 3. DynamoDB On-Demand → Provisioned
- If usage is predictable, switch to provisioned capacity
- **Savings: 20-40%**

### 4. S3 Lifecycle Policies
- Delete selfies after 30 days
- Move old data to Glacier
- **Savings: 50% on storage**

### 5. CloudWatch Log Retention
- Set retention to 7 days instead of indefinite
- **Savings: 80%**

### 6. Use Nova Instead of Claude
- Amazon Nova may be cheaper
- Test quality vs cost tradeoff
- **Potential savings: 20-30%**

---

## Free Tier Benefits (First 12 Months)

- Lambda: 1M requests + 400,000 GB-seconds/month
- DynamoDB: 25GB storage + 25 WCU + 25 RCU
- S3: 5GB storage + 20,000 GET + 2,000 PUT
- API Gateway: 1M requests/month (HTTP API)
- Amplify: 1,000 build minutes + 15GB served

**With free tier: ~$0.10/month for demo usage**

---

## Budget Alerts

Set up alerts at:
- $5 (50% of $10 budget)
- $8 (80% of $10 budget)
- $10 (100% of $10 budget)

```bash
aws budgets create-budget \
  --account-id YOUR_ACCOUNT_ID \
  --budget file://infrastructure/budget-alert.json
```

---

## Cost Monitoring

**Daily:**
```bash
aws ce get-cost-and-usage \
  --time-period Start=2025-01-01,End=2025-01-31 \
  --granularity DAILY \
  --metrics BlendedCost
```

**By Service:**
```bash
aws ce get-cost-and-usage \
  --time-period Start=2025-01-01,End=2025-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE
```
