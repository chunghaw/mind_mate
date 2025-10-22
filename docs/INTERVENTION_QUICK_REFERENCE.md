# Intervention System - Quick Reference

## 🚀 Quick Commands

### Test Intervention
```bash
aws lambda invoke \
  --function-name mindmate-executeIntervention \
  --cli-binary-format raw-in-base64-out \
  --payload file://test/intervention-test-payload.json \
  /tmp/response.json && cat /tmp/response.json
```

### View Logs
```bash
aws logs tail /aws/lambda/mindmate-executeIntervention --follow
```

### Query Interventions
```bash
# Get all interventions for a user
aws dynamodb query \
  --table-name MindMate-Interventions \
  --index-name UserInterventionsIndex \
  --key-condition-expression "userId = :uid" \
  --expression-attribute-values '{":uid":{"S":"test-user"}}'
```

### Redeploy Lambda
```bash
./infrastructure/deploy-intervention-lambda.sh
```

---

## 📊 Risk Levels

| Level | Score | Frequency | Action |
|-------|-------|-----------|--------|
| Minimal | 0.0-0.19 | None | No intervention |
| Low | 0.2-0.39 | Weekly | Encouragement |
| Moderate | 0.4-0.59 | 3 days | Check-in |
| High | 0.6-0.79 | Daily | Proactive support |
| Critical | 0.8-1.0 | 6 hours | Crisis intervention |

---

## 🔄 Flow

```
Risk Detected → Check Frequency → Gather Context → 
Generate Message → Store in Chat → Log Intervention → 
Alert if Critical → User Sees Message
```

---

## 📁 Key Files

- **Lambda**: `backend/lambdas/executeIntervention/lambda_function.py`
- **Deploy**: `infrastructure/deploy-intervention-lambda.sh`
- **Test**: `test/intervention-test-payload.json`
- **Docs**: `docs/INTERVENTION_SYSTEM_EXPLAINED.md`

---

## 🗄️ Tables

### EmoCompanion (Chat History)
- **PK**: `USER#{userId}`
- **SK**: `CHAT#{timestamp}`
- **Fields**: message, sender, messageType, sessionId

### MindMate-Interventions
- **PK**: interventionId
- **Fields**: userId, riskLevel, riskScore, riskFactors, messageGenerated, userResponded

---

## 🎯 Test Payloads

### High Risk
```json
{
  "userId": "test-user",
  "riskLevel": "high",
  "riskScore": 0.75,
  "riskFactors": ["Declining mood", "Negative sentiment"]
}
```

### Critical Risk
```json
{
  "userId": "test-user",
  "riskLevel": "critical",
  "riskScore": 0.92,
  "riskFactors": ["Crisis keywords", "Hopelessness", "Isolation"]
}
```

---

## 💰 Costs

- **Lambda**: $0.000001 per invocation
- **Bedrock**: $0.003 per message
- **DynamoDB**: $0.000001 per write
- **Total**: ~$0.003 per intervention

---

## 🔧 Troubleshooting

### Intervention not sending
1. Check frequency rules (may be too soon)
2. Verify IAM permissions
3. Check CloudWatch logs

### Message not appearing
1. Verify EmoCompanion table write
2. Check PK/SK format
3. Refresh chat interface

### Bedrock errors
1. Verify model access
2. Check region (us-east-1)
3. Review prompt format

---

## 📞 Crisis Resources

Always included in high/critical interventions:
- **988**: Suicide & Crisis Lifeline
- **741741**: Crisis Text Line (text HOME)
- **911**: Emergency services

