import os
import json
import boto3
import datetime
from boto3.dynamodb.conditions import Key

"""
Lambda: riskScan
Purpose:
- Scan the last 7 days of mood logs for a user
- Compute 7-day average and simple slope
- If risk (avg <= THRESHOLD_AVG or slope <= THRESHOLD_SLOPE), send a gentle prevention email
- Optionally use Bedrock to craft empathetic wording

Env vars required:
- TABLE_NAME            (DynamoDB table name, e.g., EmoCompanion)
- SENDER_EMAIL          (SES verified sender)
- RECIPIENT_EMAIL       (SES verified recipient; for multi-user, look up per user)
- THRESHOLD_AVG         (default "4.0")
- THRESHOLD_SLOPE       (default "-0.8")
- USE_BEDROCK           ("true" | "false", default "false")
- BEDROCK_MODEL_ID      (e.g., "anthropic.claude-3-haiku-20240307-v1:0")  # optional if USE_BEDROCK=true
"""

dynamodb = boto3.resource('dynamodb')
ses = boto3.client('ses')
bedrock = boto3.client('bedrock-runtime', region_name=os.getenv('AWS_REGION', 'us-east-1'))

TABLE_NAME = os.environ['TABLE_NAME']
SENDER = os.environ['SENDER_EMAIL']
RECIPIENT = os.environ['RECIPIENT_EMAIL']
THRESHOLD_AVG = float(os.getenv('THRESHOLD_AVG', '4.0'))
THRESHOLD_SLOPE = float(os.getenv('THRESHOLD_SLOPE', '-0.8'))
USE_BEDROCK = os.getenv('USE_BEDROCK', 'false').lower() == 'true'
BEDROCK_MODEL_ID = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-haiku-20240307-v1:0')

table = dynamodb.Table(TABLE_NAME)

def iso_utc(dt: datetime.datetime) -> str:
    return dt.replace(microsecond=0).isoformat() + 'Z'

def _daterange_strings(days_back=7):
    end = datetime.datetime.utcnow()
    start = end - datetime.timedelta(days=days_back)
    return iso_utc(start), iso_utc(end)

def fetch_last7_moods(user_id: str):
    start_iso, end_iso = _daterange_strings(7)
    pk = f"USER#{user_id}"
    sk_start = f"MOOD#{start_iso}"
    sk_end = f"MOOD#{end_iso}"
    resp = table.query(
        KeyConditionExpression=Key('PK').eq(pk) & Key('SK').between(sk_start, sk_end)
    )
    items = resp.get('Items', [])
    out = []
    for it in items:
        if it.get('type') == 'MOOD':
            ts = it.get('ts')
            mood = it.get('mood')
            if ts and isinstance(mood, (int, float)):
                out.append((ts, float(mood)))
    out.sort(key=lambda x: x[0])
    return out

def compute_stats(points):
    if not points:
        return {'avg': None, 'slope': None}
    moods = [m for _, m in points]
    avg = sum(moods) / len(moods)
    n = len(moods)
    xs = list(range(n))
    x_mean = sum(xs)/n
    y_mean = avg
    num = sum((x - x_mean)*(y - y_mean) for x, y in zip(xs, moods))
    den = sum((x - x_mean)**2 for x in xs) or 1.0
    slope = num/den
    return {'avg': avg, 'slope': slope}

def bedrock_copy(points, stats):
    history_str = "\n".join([f"- {ts}: mood {m}" for ts, m in points[-7:]])
    prompt = (
        "You are Mind Mate, a supportive AI pet.\n"
        "Write a brief (<=120 words) empathetic prevention message based on the last 7 mood entries.\n"
        "Acknowledge effort, normalize seeking help, and suggest 2 short coping strategies.\n"
        "Avoid medical advice and diagnosis; keep tone warm and encouraging.\n\n"
        f"Mood history:\n{history_str}\n\n"
        f"Stats: avg={stats['avg']:.2f}, slope={stats['slope']:.2f}\n"
    )
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 250,
        "messages": [
            {"role": "user", "content": [{"type":"text", "text": prompt}]}
        ]
    }
    resp = bedrock.invoke_model(
        modelId=BEDROCK_MODEL_ID,
        accept="application/json",
        contentType="application/json",
        body=json.dumps(body)
    )
    out = json.loads(resp['body'].read())
    try:
        return out["content"][0]["text"]
    except Exception:
        return "You're doing your best. Consider a short breathing break and a brief walk. If low mood persists, reach out to someone you trust."

def send_email(subject: str, body_text: str):
    ses.send_email(
        Source=SENDER,
        Destination={"ToAddresses": [RECIPIENT]},
        Message={
            "Subject": {"Data": subject},
            "Body": {"Text": {"Data": body_text}}
        }
    )

def lambda_handler(event, context):
    user_id = event.get("userId", "demo-user")
    points = fetch_last7_moods(user_id)
    if not points:
        return {"ok": True, "msg": "No mood data in the last 7 days."}

    stats = compute_stats(points)
    avg = stats['avg']
    slope = stats['slope']

    risk = False
    reasons = []
    if avg is not None and avg <= THRESHOLD_AVG:
        risk = True
        reasons.append(f"7-day avg ({avg:.2f}) <= {THRESHOLD_AVG}")
    if slope is not None and slope <= THRESHOLD_SLOPE:
        risk = True
        reasons.append(f"slope ({slope:.2f}) <= {THRESHOLD_SLOPE}")

    if risk:
        if USE_BEDROCK:
            message = bedrock_copy(points, stats)
        else:
            message = (
                "You've logged a run of tougher days — thank you for checking in.\n"
                "Try a 2‑minute breathing exercise and a 10‑minute light walk today.\n"
                "If low mood continues, consider talking to a friend or professional support.\n"
                f"(Signals: {', '.join(reasons)})"
            )
        send_email("Mind Mate — gentle check‑in 💛", message)
        return {"ok": True, "risk": True, "reasons": reasons}
    else:
        return {"ok": True, "risk": False, "avg": avg, "slope": slope}
