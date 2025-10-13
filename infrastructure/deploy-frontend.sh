#!/bin/bash
# Deploy frontend to S3 + CloudFront

BUCKET="mindmate-uploads-403745271636"
REGION="us-east-1"

echo "🚀 Deploying frontend..."

# Upload file
aws s3 cp frontend/app-v2.html s3://$BUCKET/public/index.html \
  --content-type "text/html" \
  --region $REGION

echo "✅ File uploaded to S3"
echo ""
echo "📝 To access your app, you have 3 options:"
echo ""
echo "Option 1: Use Amplify with GitHub (recommended)"
echo "  - Push your code to GitHub"
echo "  - Connect Amplify to your repo"
echo "  - Auto-deploys on every push"
echo ""
echo "Option 2: Open the file locally"
echo "  - Open frontend/app-v2.html in your browser"
echo "  - Works perfectly for testing!"
echo ""
echo "Option 3: Use a simple HTTP server"
echo "  - cd frontend"
echo "  - python3 -m http.server 8000"
echo "  - Open http://localhost:8000/app-v2.html"
