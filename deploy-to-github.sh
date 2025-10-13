#!/bin/bash
# Deploy Mind Mate to GitHub

set -e

echo "🚀 Deploying Mind Mate to GitHub..."
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
  echo "📦 Initializing Git repository..."
  git init
  git branch -M main
fi

# Create .gitignore if it doesn't exist
if [ ! -f .gitignore ]; then
  echo "�o Creating .gitignore..."
  cat > .gitignore << 'EOF'
# AWS
.aws/
*.pem
api-endpoint.txt

# Environment
.env
.env.local

# Python
__pycache__/
*.py[cod]
venv/
*.egg-info/

# Node
node_modules/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Deployment
function.zip
*.zip
EOF
fi

# Add all files
echo "📦 Adding files to Git..."
git add .

# Commit
echo "💾 Committing changes..."
git commit -m "Deploy Mind Mate - AWS AI Agent Hackathon" || echo "No changes to commit"

# Check if remote exists
if ! git remote | grep -q origin; then
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "📝 Next steps:"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  echo "1. Create a new repository on GitHub:"
  echo "   https://github.com/new"
  echo ""
  echo "2. Name it: mind-mate or aws-ai-agent-hackathon"
  echo ""
  echo "3. Run these commands:"
  echo ""
  echo "   git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git"
  echo "   git push -u origin main"
  echo ""
  echo "4. Then connect to Amplify:"
  echo "   https://console.aws.amazon.com/amplify/home?region=us-east-1"
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
else
  echo "🚀 Pushing to GitHub..."
  git push -u origin main
  
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "✅ Deployed to GitHub!"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  echo "📝 Next: Connect to Amplify"
  echo "   https://console.aws.amazon.com/amplify/home?region=us-east-1"
  echo ""
  echo "   1. Click 'New app' → 'Host web app'"
  echo "   2. Select 'GitHub'"
  echo "   3. Authorize AWS Amplify"
  echo "   4. Select your repository"
  echo "   5. Build settings:"
  echo "      - Base directory: frontend"
  echo "      - Build command: (leave empty)"
  echo "      - Publish directory: ."
  echo "   6. Click 'Save and deploy'"
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi
