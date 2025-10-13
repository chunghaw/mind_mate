# Mind Mate – Setup & Deployment Guide (AWS, low-cost & serverless)

This README walks you **step‑by‑step** from a blank AWS account to a working demo of **Mind Mate** — an AI pet companion that tracks mood, analyzes selfies/surroundings, emails daily recaps, and raises early‑warning signals for prevention.

> **What’s the outcome?**  
> A **web app** (hosted on **AWS Amplify**) that calls a **serverless backend** (API Gateway + Lambda + DynamoDB + S3).  
> No EC2 is required. Users can log mood, upload photos, and receive **daily email recaps** and **risk alerts**.  
> Optionally add a small **QuickSight dashboard** and an **avatar generator** (Titan Image).

> **Region:** Use **us‑east‑1 (N. Virginia)** to keep all services/models available. Keep *everything* in the same region unless noted.  
> **Budget:** Fits inside ~$100 with light usage. Set a budget alarm (below).


---

## 0) Prereqs & Safety Rails

- ✅ AWS account with ~$100 credit
- ✅ IAM user (not root) with AdministratorAccess for setup (fine for hackathon)
- ✅ AWS CLI v2 installed (`aws --version`) and configured (`aws configure`) – optional but useful
- ✅ Basic comfort in the AWS Console

**Recommended:**  
Create a **Cost Budget** at **$20/month** (email alerts at 50/80/100%) → Console → *Billing* → *Budgets* → *Create*.


---

## 1) Enable Amazon Bedrock Models (once)

Console → **Amazon Bedrock** → **Model access** → Request/enable at least:
- **Text**: Anthropic **Claude** or Amazon **Nova** (for recaps/coach)
- **Image**: **Titan Image Generator G1** (for the pet avatar — optional)

> Tip: Approvals are usually instant. Keep region = **us‑east‑1**.


---

## 2) Create Core Data Stores

### 2.1 DynamoDB (operational data)
Console → **DynamoDB** → *Create table*
- **Table name:** `EmoCompanion`  _(you can keep this name even if branding is Mind Mate)_
- **Partition key:** `PK` (String)
- **Sort key:** `SK` (String)
- Capacity mode: **On‑Demand** (easy, cheap for small traffic)

### 2.2 S3 Bucket (images/exports)
Console → **S3** → *Create bucket*
- **Name:** `mindmate-uploads-<random>`
- Block public access: **ON** (keep private)
- Default encryption: **ON** (SSE‑S3 is fine; KMS optional)


---

## 3) Create the Lambda Execution Role

Console → **IAM** → *Roles* → *Create role*
- **Trusted entity:** AWS service → **Lambda**
- **Name:** `MindMateLambdaRole`

Attach:
- AWS managed policy **AWSLambdaBasicExecutionRole** (CloudWatch logs)

Add **inline policy** (edit `<YOUR_BUCKET_NAME>` as needed):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DynamoRW",
      "Effect": "Allow",
      "Action": ["dynamodb:PutItem","dynamodb:GetItem","dynamodb:Query","dynamodb:UpdateItem"],
      "Resource": [
        "arn:aws:dynamodb:us-east-1:*:table/EmoCompanion",
        "arn:aws:dynamodb:us-east-1:*:table/EmoCompanion/index/*"
      ]
    },
    {
      "Sid": "S3RW",
      "Effect": "Allow",
      "Action": ["s3:PutObject","s3:GetObject"],
      "Resource": "arn:aws:s3:::<YOUR_BUCKET_NAME>/*"
    },
    {
      "Sid": "RekognitionDetect",
      "Effect": "Allow",
      "Action": ["rekognition:DetectFaces","rekognition:DetectLabels"],
      "Resource": "*"
    },
    {
      "Sid": "BedrockInvoke",
      "Effect": "Allow",
      "Action": ["bedrock:InvokeModel","bedrock:InvokeModelWithResponseStream"],
      "Resource": "*"
    },
    {
      "Sid": "SESSend",
      "Effect": "Allow",
      "Action": ["ses:SendEmail","ses:SendRawEmail"],
      "Resource": "*"
    }
  ]
}
```

> For production, scope ARNs more tightly and use KMS CMKs. For hackathon, this is intentionally simple.


---

## 4) Create Lambda Functions (the “Agent Tools”)

Create each function in **us‑east‑1** with **Runtime = Python 3.12** and **Role = MindMateLambdaRole**.  
Set **Memory 256 MB** and **Timeout 10s** (defaults are fine).

### 4.1 `logMood`
**Environment variables:** `TABLE_NAME = EmoCompanion`

```python
import json, os, datetime
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def _resp(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST"
        },
        "body": json.dumps(body)
    }

def lambda_handler(event, context):
    body = json.loads(event.get("body", "{}")) if isinstance(event.get("body"), str) else (event.get("body") or {})
    user_id = body.get("userId", "demo-user")
    mood = int(body["mood"])  # 1–10
    tags = body.get("tags", [])
    notes = body.get("notes", "")
    ts = datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"

    item = {
        "PK": f"USER#{user_id}",
        "SK": f"MOOD#{ts}",
        "type": "MOOD",
        "userId": user_id,
        "mood": mood,
        "tags": tags,
        "notes": notes,
        "ts": ts
    }
    table.put_item(Item=item)
    return _resp(200, {"ok": True, "ts": ts})
```

### 4.2 `analyzeSelfie`
**Env:** `TABLE_NAME = EmoCompanion`, `BUCKET = <YOUR_BUCKET_NAME>`

```python
import json, os, base64, uuid, datetime
import boto3

s3 = boto3.client('s3')
rek = boto3.client('rekognition')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])
BUCKET = os.environ['BUCKET']

def _resp(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST"
        },
        "body": json.dumps(body)
    }

def lambda_handler(event, context):
    body = json.loads(event.get("body", "{}")) if isinstance(event.get("body"), str) else (event.get("body") or {})
    user_id = body.get("userId", "demo-user")
    img_b64 = body["imageBase64"]  # data URL or raw base64
    if "," in img_b64:
        img_b64 = img_b64.split(",", 1)[1]
    img_bytes = base64.b64decode(img_b64)

    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    key = f"selfies/{user_id}/{ts}-{uuid.uuid4().hex}.jpg"
    s3.put_object(Bucket=BUCKET, Key=key, Body=img_bytes, ContentType="image/jpeg")

    faces = rek.detect_faces(Image={"S3Object": {"Bucket": BUCKET, "Name": key}}, Attributes=["ALL"])
    emotions = []
    if faces.get("FaceDetails"):
        emotions = sorted(faces["FaceDetails"][0].get("Emotions", []), key=lambda e: e["Confidence"], reverse=True)[:3]

    # Store derived scores only (privacy-friendly)
    table.put_item(Item={
        "PK": f"USER#{user_id}",
        "SK": f"SELFIE#{ts}",
        "type": "SELFIE",
        "userId": user_id,
        "s3Key": key,
        "emotions": [{"Type": e["Type"], "Confidence": round(e["Confidence"], 2)} for e in emotions],
        "ts": ts
    })
    return _resp(200, {"ok": True, "s3Key": key, "topEmotions": emotions})
```

### 4.3 (Optional) `analyzeScene`
**Env:** `TABLE_NAME = EmoCompanion`, `BUCKET = <YOUR_BUCKET_NAME>`  
Same pattern as `analyzeSelfie` but call `rek.detect_labels(...)` and store top 3 labels as a `SCENE#...` item.

### 4.4 (Optional) `generateAvatar`
Calls **Bedrock Titan Image** to create the pet avatar and saves to S3. Store URL on `PROFILE` item.

### 4.5 `dailyRecap` (email user a recap; add prevention message if needed)
**Env:** `TABLE_NAME = EmoCompanion`, `SENDER_EMAIL = you@domain.com`, `RECIPIENT_EMAIL = you@domain.com`

Skeleton (replace summary with a Bedrock call later):

```python
import os, json, datetime, boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])
ses = boto3.client('ses')
# For Bedrock (recap text), later:
# bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

SENDER = os.environ['SENDER_EMAIL']
RECIPIENT = os.environ['RECIPIENT_EMAIL']

def lambda_handler(event, context):
    user_id = event.get("userId", "demo-user")
    today = datetime.date.today()
    yday = (today - datetime.timedelta(days=1)).isoformat()

    # TODO: Query DDB for yesterday’s MOOD/SELFIE/SCENE, compute simple advice, or call Bedrock.
    summary = f"Daily recap for {yday}: keep going! Try a 2‑min breathing break and a 10‑min walk."

    ses.send_email(
        Source=SENDER,
        Destination={"ToAddresses":[RECIPIENT]},
        Message={
            "Subject": {"Data":"Your Mind Mate daily recap"},
            "Body": {"Text": {"Data": summary}}
        }
    )
    return {"ok": True}
```

### 4.6 (Optional) `riskScan` (predictive early‑warning)
Runs once daily to scan last 7 days and create a `RECAP#YYYY‑MM‑DD` with `risk=true` if conditions match.

Pseudo logic:
- Query `MOOD#` items last 7 days → compute 7‑day average and slope → if avg ≤ 4.0 or slope < −0.8 → risk
- If risk → send a kind SES nudge and tag in DynamoDB (or call Bedrock for empathetic wording)


---

## 5) HTTP API (API Gateway, cheaper HTTP API)

Console → **API Gateway** → *Create API* → **HTTP API**  
**Routes → Integrations:**
- `POST /mood` → Lambda: `logMood`
- `POST /selfie` → Lambda: `analyzeSelfie`
- (optional) `POST /scene` → `analyzeScene`
- (optional) `POST /avatar` → `generateAvatar`

**CORS:** Enable for `*` (demo), then restrict in production.  
Copy the **Invoke URL** (e.g., `https://abc123.execute-api.us-east-1.amazonaws.com`).


---

## 6) SES (Simple Email Service) for Recaps

- Console → **SES** → *Verified identities* → Verify **sender** email (and recipient if SES sandbox).  
- Ensure the Lambda role has `ses:SendEmail` (already in inline policy).

**Schedule with EventBridge:**
- Console → **EventBridge** → *Rules* → Create
- Name: `DailyRecap7am`
- Schedule: e.g., `cron(0 20 * * ? *)`  → 7am AEDT approx (adjust to your local TZ)
- Target: Lambda → `dailyRecap`


---

## 7) Frontend (Amplify Hosting) – minimal demo

Create `index.html` (one‑file demo) and deploy without Git.

```html
<!doctype html><meta charset="utf-8">
<title>Mind Mate (demo)</title>
<h1>Mind Mate</h1>
<label>Mood (1-10) <input id="mood" type="number" min="1" max="10" value="6"></label>
<button onclick="sendMood()">Save Mood</button>
<br><br>
<input id="file" type="file" accept="image/*">
<button onclick="sendSelfie()">Analyze Selfie</button>
<pre id="out"></pre>
<script>
const API = "REPLACE_WITH_YOUR_HTTP_API_INVOKE_URL";
async function sendMood(){
  const mood = Number(document.getElementById('mood').value||'5');
  const r = await fetch(API+'/mood',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({userId:'demo-user',mood})});
  document.getElementById('out').textContent = await r.text();
}
async function toBase64(file){return new Promise((res,rej)=>{const r=new FileReader();r.onload=()=>res(r.result);r.onerror=rej;r.readAsDataURL(file);});}
async function sendSelfie(){
  const f = document.getElementById('file').files[0]; if(!f) return alert('Pick a photo');
  const imageBase64 = await toBase64(f);
  const r = await fetch(API+'/selfie',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({userId:'demo-user',imageBase64})});
  document.getElementById('out').textContent = await r.text();
}
</script>
```

Deploy: Console → **AWS Amplify** → *Host web app* → **Deploy without Git** → upload `index.html`.  
Open the Amplify URL and test both buttons.


---

## 8) Bedrock Guardrails (safety by design)

Console → **Amazon Bedrock** → *Guardrails* → Create
- Enable safety categories (self‑harm, hate, sexual, violence)
- Turn on PII redaction
- Attach guardrail to your Bedrock calls (when you wire Bedrock in `dailyRecap` and copilot prompts)


---

## 9) Add Prediction & Prevention (optional but judge‑winning)

### 9.1 Simple rules (fastest)
- Add a daily `riskScan` Lambda:  
  - Calculate 7‑day avg mood and slope.  
  - If `avg ≤ 4` or slope negative beyond threshold, send a gentle email + mark `risk=true` in DDB.

### 9.2 Analytics pipeline (nicer charts)
- Nightly export to **S3** (`exports/mood/YYYY/MM/DD/...json`).  
- Create an **Athena** table (Glue Data Catalog) to query trends.

**Sample Athena DDL (if exporting newline‑delimited JSON with fields ts, mood, userId):**
```sql
CREATE EXTERNAL TABLE IF NOT EXISTS mindmate_mood (
  ts string,
  mood int,
  userId string
)
PARTITIONED BY (y string, m string, d string)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
LOCATION 's3://<YOUR_BUCKET>/exports/mood/';
```

Then you can compute 7‑day moving averages in SQL or viz in **QuickSight**.


---

## 10) (Optional) Cognito Auth

- Console → **Amazon Cognito** → *User pools* → Create a user pool.  
- Use Hosted UI or Amplify Auth to sign in users and use `sub` as `userId`.  
- Swap `demo-user` in payloads with the logged‑in user’s `sub`.


---

## 11) Test with curl (smoke test)

```bash
# Log a mood
curl -X POST "$API_URL/mood" \
  -H "Content-Type: application/json" \
  -d '{"userId":"demo-user","mood":6,"tags":["work","stress"],"notes":"long day"}'

# Analyze a selfie (put your own small base64 image)
curl -X POST "$API_URL/selfie" \
  -H "Content-Type: application/json" \
  -d '{"userId":"demo-user","imageBase64":"data:image/jpeg;base64,/9j/4AAQSk..."}'
```


---

## 12) Budget Tips

- **HTTP API + Lambda + DynamoDB + S3** are pennies at hackathon scale.  
- **Rekognition**: limit to **1–2 images per day per user**.  
- **Bedrock**: keep prompts short; call only when needed (recap/risk).  
- **SES**: fractions of a cent per recap.  
- Amplify Hosting free tier is generous for tiny demos.


---

## 13) What to Demo (script)

1) Visit Amplify site → **log a mood** and **upload a selfie** → show returned top emotions.  
2) Click **“Send recap now”** button (optional UI) → check inbox for SES email.  
3) Toggle a **bad‑mood streak** (enter low moods) → run `riskScan` manually to show a **gentle prevention email**.  
4) (Optional) Show a **QuickSight chart** of weekly mood trend.  
5) (Optional) Generate a **pet avatar** with a Titan Image prompt.


---

## 14) Clean‑Up (post‑hackathon)

- Delete EventBridge rules, SES identities  
- Empty & delete S3 bucket(s)  
- Delete Lambda functions, API, DynamoDB table  
- Remove Amplify app  
- Remove IAM role/policies if not reused


---

## Outcome Summary

- **Type:** A **web app** hosted on **AWS Amplify** that uses a **serverless backend** on AWS.  
- **User Experience:** Mood check‑ins, photo analysis, daily recap emails, and **predictive prevention** nudges.  
- **Why it’s compelling:** Not “just a chatbot” — it’s an **action‑taking agent** with image understanding, scheduled automation, and safety guardrails, fully built on AWS services.

---

## Repo Structure (suggested)

```
/backend/
  lambdas/
    logMood/
    analyzeSelfie/
    analyzeScene/        (optional)
    generateAvatar/      (optional)
    dailyRecap/
    riskScan/            (optional)
  infra/ (CDK or SAM)    (optional)
/frontend/
  index.html             (or React app)
/docs/
  mindmate_agent.md
  agent.md               (older spec)
README.md
```

**You’re ready.** Deploy the minimum first, then layer in prevention, avatar, and analytics as time allows. Good luck — let’s bring home that first prize 🏆
