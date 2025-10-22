#!/bin/bash

# Prepare Mind Mate frontend for Amplify ZIP upload
set -e

echo "📦 Preparing Mind Mate for Amplify deployment"
echo "============================================="

# Create deployment directory
DEPLOY_DIR="mindmate-amplify-deploy"
ZIP_FILE="mindmate-frontend.zip"

# Clean up previous builds
rm -rf "$DEPLOY_DIR" "$ZIP_FILE" 2>/dev/null || true

# Create deployment directory
mkdir -p "$DEPLOY_DIR"

echo "📁 Copying frontend files..."

# Copy all frontend files
cp -r frontend/* "$DEPLOY_DIR/"

# Copy amplify.yml to root of deployment
cp amplify.yml "$DEPLOY_DIR/"

# Ensure main app file is accessible
if [ -f "$DEPLOY_DIR/mind-mate-hackathon.html" ]; then
    echo "✅ Main app file found: mind-mate-hackathon.html"
fi

# List files being deployed
echo ""
echo "📋 Files to be deployed:"
find "$DEPLOY_DIR" -type f | sort

# Create ZIP file
echo ""
echo "🗜️  Creating ZIP file for upload..."
cd "$DEPLOY_DIR"
zip -r "../$ZIP_FILE" . -x "*.DS_Store" "*.git*"
cd ..

# Get file size
FILE_SIZE=$(du -h "$ZIP_FILE" | cut -f1)

echo ""
echo "✅ Deployment package ready!"
echo "📦 File: $ZIP_FILE"
echo "📏 Size: $FILE_SIZE"
echo ""
echo "🚀 Next steps:"
echo "1. Go to AWS Amplify Console: https://console.aws.amazon.com/amplify/"
echo "2. Click 'New app' → 'Host web app'"
echo "3. Choose 'Deploy without Git provider'"
echo "4. Upload the file: $ZIP_FILE"
echo "5. Set app name: 'mindmate-ai-companion'"
echo "6. Deploy!"
echo ""
echo "🌐 Your app will be available at: https://[random-id].amplifyapp.com"

# Cleanup deployment directory
rm -rf "$DEPLOY_DIR"

echo ""
echo "🎉 Ready for deployment!"