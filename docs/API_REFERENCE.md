# Mind Mate API Reference

Base URL: `https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com`

## Endpoints

### POST /mood
Log a mood entry.

**Request:**
```json
{
  "userId": "string",
  "mood": 1-10,
  "tags": ["string"],
  "notes": "string"
}
```

**Response:**
```json
{
  "ok": true,
  "ts": "2025-01-15T10:30:00Z",
  "mood": 7
}
```

**Example:**
```bash
curl -X POST "$API_URL/mood" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "demo-user",
    "mood": 7,
    "tags": ["happy", "work"],
    "notes": "Productive day!"
  }'
```

---

### POST /selfie
Analyze emotions from a selfie.

**Request:**
```json
{
  "userId": "string",
  "imageBase64": "data:image/jpeg;base64,..."
}
```

**Response:**
```json
{
  "ok": true,
  "s3Key": "selfies/demo-user/20250115T103000Z-abc123.jpg",
  "topEmotions": [
    {"Type": "HAPPY", "Confidence": 98.5},
    {"Type": "CALM", "Confidence": 85.2},
    {"Type": "SURPRISED", "Confidence": 12.3}
  ]
}
```

**Example:**
```bash
# Convert image to base64
IMAGE_B64=$(base64 -i photo.jpg)

curl -X POST "$API_URL/selfie" \
  -H "Content-Type: application/json" \
  -d "{\"userId\":\"demo-user\",\"imageBase64\":\"data:image/jpeg;base64,$IMAGE_B64\"}"
```

---

### POST /scene
Analyze surroundings/context from a photo.

**Request:**
```json
{
  "userId": "string",
  "imageBase64": "data:image/jpeg;base64,..."
}
```

**Response:**
```json
{
  "ok": true,
  "s3Key": "scenes/demo-user/20250115T103000Z-def456.jpg",
  "topLabels": [
    {"Name": "Office", "Confidence": 95.2},
    {"Name": "Desk", "Confidence": 89.7},
    {"Name": "Computer", "Confidence": 87.3}
  ]
}
```

---

### POST /avatar
Generate AI pet avatar.

**Request:**
```json
{
  "userId": "string",
  "description": "string"
}
```

**Response:**
```json
{
  "ok": true,
  "avatarUrl": "https://mindmate-uploads.s3.amazonaws.com/avatars/demo-user/xyz789.png",
  "s3Key": "avatars/demo-user/xyz789.png"
}
```

**Example:**
```bash
curl -X POST "$API_URL/avatar" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "demo-user",
    "description": "a fluffy orange cat with green eyes"
  }'
```

---

## Lambda Functions (Internal)

### dailyRecap
Triggered by EventBridge daily.

**Input:**
```json
{
  "userId": "demo-user"
}
```

**Output:**
```json
{
  "ok": true,
  "recap": "Daily recap text..."
}
```

**Manual Trigger:**
```bash
aws lambda invoke \
  --function-name dailyRecap \
  --payload '{"userId":"demo-user"}' \
  response.json
```

---

### riskScan
Triggered by EventBridge daily.

**Input:**
```json
{
  "userId": "demo-user"
}
```

**Output:**
```json
{
  "ok": true,
  "risk": true,
  "reason": "Low average mood (3.8/10) over 7 days",
  "avgMood": 3.8,
  "slope": -1.2
}
```

**Manual Trigger:**
```bash
aws lambda invoke \
  --function-name riskScan \
  --payload '{"userId":"demo-user"}' \
  response.json
```

---

## Error Responses

**400 Bad Request:**
```json
{
  "error": "Missing required field: mood"
}
```

**500 Internal Server Error:**
```json
{
  "error": "DynamoDB error: ..."
}
```

---

## Rate Limits

- No hard limits (serverless scales automatically)
- Recommended: Limit Rekognition to 2 images/day per user for cost control
- SES sandbox: 200 emails/day

---

## CORS

All endpoints support CORS with:
- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Methods: OPTIONS,POST`
- `Access-Control-Allow-Headers: *`

---

## Authentication

Currently uses `userId` in request body (demo mode).

**For production:**
- Add Amazon Cognito
- Use JWT tokens
- Extract userId from token claims
