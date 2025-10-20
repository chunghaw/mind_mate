#!/bin/bash

echo "🧹 Starting comprehensive project cleanup..."

# Remove all temporary status/progress markdown files
echo "📄 Removing temporary documentation files..."
rm -f agent.md
rm -f AI_REPORT_REDESIGN_COMPLETE.md
rm -f AMPLIFY_DEPLOYMENT_READY.md
rm -f APPROVED_REQUIREMENTS.md
rm -f AUTH_REDIRECT_ISSUE.md
rm -f CHAT_CLEANUP_COMPLETE.md
rm -f CHAT_HISTORY_FIX_COMPLETE.md
rm -f DEPLOY_ML_INTEGRATION.md
rm -f deploy-to-amplify.md
rm -f deploy-to-github.sh
rm -f DEPLOYMENT_CHECKLIST.md
rm -f DEPLOYMENT_COMPLETE_ML.md
rm -f DEPLOYMENT_COMPLETE.md
rm -f DEPLOYMENT_FINAL.md
rm -f DEPLOYMENT_STATUS.md
rm -f DEPLOYMENT_SUMMARY.md
rm -f FEATURE_PLAN.md
rm -f FINAL_CHANGES_SUMMARY.md
rm -f FINAL_STATUS.md
rm -f FRONTEND_UPDATE.md
rm -f FULL_INTEGRATION_GUIDE.md
rm -f GET_STARTED.md
rm -f GITHUB_DEPLOYMENT_LOG.md
rm -f HACKATHON_3TAB_LAYOUT.md
rm -f HACKATHON_DEMO_COMPLETE.md
rm -f HACKATHON_DEMO_FINAL.md
rm -f HACKATHON_DEMO_GUIDE.md
rm -f HACKATHON_DEPLOYMENT_COMPLETE.md
rm -f HACKATHON_FINAL_DESIGN.md
rm -f HACKATHON_UI_IMPROVEMENTS.md
rm -f HACKATHON_UI_STATUS.md
rm -f HACKATHON_UI_STRATEGY.md
rm -f HACKATHON_UI_TABS_UPDATE.md
rm -f IMPLEMENTATION_COMPLETE.md
rm -f IMPLEMENTATION_SUMMARY.md
rm -f INTEGRATION_COMPLETE_SUMMARY.md
rm -f LOGIN_FIRST_FIX.md
rm -f ML_API_FIX_COMPLETE.md
rm -f ML_DEPLOYMENT_STATUS.md
rm -f ML_FEATURES_INDIVIDUAL_STATUS.md
rm -f ML_FULL_INTEGRATION_GUIDE.md
rm -f ML_INFRASTRUCTURE_COMPLETE.md
rm -f ML_INTEGRATION_COMPLETE.md
rm -f ML_INTEGRATION_INDEX.md
rm -f ML_INTEGRATION_QUICK_START.md
rm -f ML_INTEGRATION_SUMMARY.md
rm -f ML_SYSTEM_PROGRESS.md
rm -f ML_TASK2_COMPLETE.md
rm -f ML_TASK3_COMPLETE.md
rm -f ML_TASK5_COMPLETE.md
rm -f ML_TASKS_1-4_COMPLETE.md
rm -f ONBOARDING_IMPLEMENTATION_STATUS.md
rm -f ONBOARDING_RESTORED.md
rm -f PHASE2_ENHANCEMENTS.md
rm -f PRODUCT_VISION.md
rm -f PROJECT_COMPLETE.md
rm -f PROJECT_STRUCTURE.md
rm -f PUSH_TO_GITHUB.md
rm -f QUICK_REFERENCE.md
rm -f QUICK_START_PHASE2.md
rm -f README_ML_INTEGRATION.md
rm -f README_QUICKSTART.md
rm -f READY_FOR_HACKATHON.md
rm -f READY_TO_DEPLOY.md
rm -f RESET_CHAT_FEATURE.md
rm -f SUMMARY.md
rm -f UI_REDESIGN_V4.md
rm -f V4_DEPLOYMENT_COMPLETE.md
rm -f WHY_NOT_BEDROCK_AGENTS.md

# Remove old frontend versions
echo "🎨 Removing old frontend versions..."
rm -f frontend/app-v2.html
rm -f frontend/app.html
rm -f frontend/index-old.html
rm -f frontend/index-v2.html
rm -f frontend/mind-mate-complete.html
rm -f frontend/mind-mate-integrated.html
rm -f frontend/mind-mate-ml-integrated.html
rm -f frontend/mind-mate-ml-simple.html
rm -f frontend/mind-mate-ml.html
rm -f frontend/mind-mate-v3.html
rm -f frontend/mind-mate-v4.html
rm -f frontend/ml-integration.html
rm -f frontend/test-chat.html
rm -f frontend/test.html

# Remove unused Lambda functions
echo "⚡ Removing unused Lambda functions..."
rm -rf backend/lambdas/calculateRiskScoreDemo
rm -rf backend/lambdas/executeIntervention
rm -rf backend/lambdas/riskScan
rm -rf backend/lambdas/analyzeScene
rm -rf backend/lambdas/getProfile
rm -rf backend/lambdas/getRiskScore
rm -rf backend/lambdas/getStats
rm -rf backend/lambdas/updateProfile

# Remove old scripts and zip files
echo "📦 Removing old scripts and archives..."
rm -f generateAvatar.py
rm -f generateAvatar.zip
rm -f risk-demo-lambda.zip
rm -f riskScan.py
rm -f setPassword.zip
rm -f deploy-frontend.sh
rm -f test-deployment.sh
rm -f test-hackathon-ui.sh

# Remove old infrastructure scripts
echo "🏗️ Cleaning infrastructure scripts..."
rm -f infrastructure/add-routes.sh
rm -f infrastructure/add-ml-routes.sh
rm -f infrastructure/create-api-gateway.sh
rm -f infrastructure/cognito-simple.yaml
rm -f infrastructure/cloudformation-template.yaml
rm -f infrastructure/verify-ml-stack.sh
rm -f infrastructure/deploy-chat-lambda.sh

# Remove old docs that are duplicates
echo "📚 Cleaning documentation..."
rm -f docs/ML_INTEGRATION_COMPLETE.md
rm -f docs/ML_INTEGRATION_DIAGRAM.md
rm -f docs/ML_APP_INTEGRATION.md

# Remove merge script
rm -f scripts/merge-onboarding.py
rm -f scripts/generate-avatars-simple.sh

echo "✅ Cleanup complete!"
echo ""
echo "📊 Remaining structure:"
echo "  ✓ frontend/ - Core application files only"
echo "  ✓ backend/lambdas/ - Active Lambda functions only"
echo "  ✓ infrastructure/ - Deployment scripts"
echo "  ✓ docs/ - Essential documentation"
echo "  ✓ sagemaker/ - ML training code"
echo "  ✓ scripts/ - Utility scripts"
echo "  ✓ test/ - Test payloads"
