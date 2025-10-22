#!/bin/bash

# Deploy Mind Mate to AWS Amplify
set -e

echo "🚀 Deploying Mind Mate to AWS Amplify"
echo "======================================"

# Configuration
REGION="us-east-1"
APP_NAME="mindmate-ai-companion"
BRANCH_NAME="main"
REPO_URL="https://github.com/your-username/mindmate-repo"  # Update this with your actual repo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    print_error "AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if user is authenticated
print_status "Checking AWS authentication..."
if ! aws sts get-caller-identity &> /dev/null; then
    print_error "AWS CLI is not configured. Please run 'aws configure' first."
    exit 1
fi

print_success "AWS CLI is configured"

# Check if Amplify CLI is installed
if ! command -v amplify &> /dev/null; then
    print_warning "Amplify CLI is not installed. Installing..."
    npm install -g @aws-amplify/cli
fi

# Function to create Amplify app
create_amplify_app() {
    print_status "Creating Amplify app: $APP_NAME"
    
    # Create the app
    APP_ID=$(aws amplify create-app \
        --name "$APP_NAME" \
        --description "Mind Mate - AI-powered mental health companion" \
        --repository "$REPO_URL" \
        --platform "WEB" \
        --iam-service-role-arn "arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/amplifyconsole-backend-role" \
        --region "$REGION" \
        --query 'app.appId' \
        --output text 2>/dev/null || echo "")
    
    if [ -z "$APP_ID" ]; then
        print_warning "App might already exist or role not found. Trying to find existing app..."
        APP_ID=$(aws amplify list-apps --region "$REGION" --query "apps[?name=='$APP_NAME'].appId" --output text)
        
        if [ -z "$APP_ID" ]; then
            print_error "Could not create or find Amplify app. Please create it manually in the AWS Console."
            exit 1
        fi
    fi
    
    print_success "Amplify app ID: $APP_ID"
    echo "$APP_ID" > .amplify-app-id
}

# Function to create branch
create_branch() {
    print_status "Creating branch: $BRANCH_NAME"
    
    aws amplify create-branch \
        --app-id "$APP_ID" \
        --branch-name "$BRANCH_NAME" \
        --description "Main production branch" \
        --enable-auto-build \
        --region "$REGION" 2>/dev/null || print_warning "Branch might already exist"
    
    print_success "Branch created/updated: $BRANCH_NAME"
}

# Function to start deployment
start_deployment() {
    print_status "Starting deployment..."
    
    JOB_ID=$(aws amplify start-job \
        --app-id "$APP_ID" \
        --branch-name "$BRANCH_NAME" \
        --job-type "RELEASE" \
        --region "$REGION" \
        --query 'jobSummary.jobId' \
        --output text)
    
    print_success "Deployment started with Job ID: $JOB_ID"
    
    # Wait for deployment to complete
    print_status "Waiting for deployment to complete..."
    
    while true; do
        STATUS=$(aws amplify get-job \
            --app-id "$APP_ID" \
            --branch-name "$BRANCH_NAME" \
            --job-id "$JOB_ID" \
            --region "$REGION" \
            --query 'job.summary.status' \
            --output text)
        
        case $STATUS in
            "SUCCEED")
                print_success "Deployment completed successfully!"
                break
                ;;
            "FAILED")
                print_error "Deployment failed!"
                exit 1
                ;;
            "RUNNING"|"PENDING")
                echo -n "."
                sleep 10
                ;;
            *)
                print_warning "Unknown status: $STATUS"
                sleep 10
                ;;
        esac
    done
}

# Function to get app URL
get_app_url() {
    APP_URL=$(aws amplify get-app \
        --app-id "$APP_ID" \
        --region "$REGION" \
        --query 'app.defaultDomain' \
        --output text)
    
    BRANCH_URL="https://$BRANCH_NAME.$APP_URL"
    
    print_success "App deployed successfully!"
    echo ""
    echo "🌐 App URL: $BRANCH_URL"
    echo "📱 App ID: $APP_ID"
    echo "🌿 Branch: $BRANCH_NAME"
    echo ""
    echo "You can also access the Amplify console at:"
    echo "https://console.aws.amazon.com/amplify/home?region=$REGION#/$APP_ID"
}

# Main deployment process
main() {
    print_status "Starting Mind Mate deployment process..."
    
    # Check if app ID exists
    if [ -f ".amplify-app-id" ]; then
        APP_ID=$(cat .amplify-app-id)
        print_status "Using existing app ID: $APP_ID"
    else
        create_amplify_app
    fi
    
    create_branch
    start_deployment
    get_app_url
    
    print_success "Deployment complete! 🎉"
}

# Run main function
main "$@"