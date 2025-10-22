# AWS Amplify Deployment Guide for Mind Mate

## 🚀 Quick Deployment Steps

### Option 1: Manual Deployment (Recommended for Demo)

1. **Prepare the Frontend**
   ```bash
   # Ensure all files are in the frontend directory
   ls frontend/
   ```

2. **Create Amplify App via AWS Console**
   - Go to [AWS Amplify Console](https://console.aws.amazon.com/amplify/)
   - Click "New app" → "Host web app"
   - Choose "Deploy without Git provider"
   - Upload the `frontend` folder as a ZIP file

3. **Configure Build Settings**
   - Use the provided `amplify.yml` configuration
   - Set build command: `echo "Static site - no build needed"`
   - Set output directory: `.` (current directory)

### Option 2: Git-based Deployment

1. **Initialize Git Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Mind Mate AI Companion"
   ```

2. **Push to GitHub/CodeCommit**
   ```bash
   # For GitHub
   git remote add origin https://github.com/your-username/mindmate-ai.git
   git push -u origin main
   ```

3. **Connect to Amplify**
   - Go to AWS Amplify Console
   - Click "New app" → "Host web app"
   - Connect your Git repository
   - Select the main branch
   - Use the existing `amplify.yml` configuration

### Option 3: AWS CLI Deployment

```bash
# Run the deployment script
./deploy-amplify.sh
```

## 📁 File Structure for Deployment

```
frontend/
├── index.html                    # Landing page
├── mind-mate-hackathon.html     # Main app (rename to app.html if needed)
├── onboarding.html              # User onboarding
├── check-auth.html              # Authentication check
├── test-auth.html               # Auth testing
├── ml-wellness-widget.js        # ML widget functionality
├── ml-wellness-widget.css       # ML widget styles
├── *.jpeg, *.png               # Pet avatars and assets
└── amplify.yml                  # Build configuration
```

## ⚙️ Environment Configuration

### Required Environment Variables (if using backend APIs)
```bash
# API Endpoints
API_BASE=https://h8iyzk1h3k.execute-api.us-east-1.amazonaws.com
CHAT_API=https://7ctr3cdwnfuy2at5qt36mdziee0ugypx.lambda-url.us-east-1.on.aws
CHAT_HISTORY_API=https://4tybbjkqlkwewxgawzcjjhdzty0hygwv.lambda-url.us-east-1.on.aws

# Cognito Configuration
COGNITO_USER_POOL_ID=us-east-1_YourPoolId
COGNITO_CLIENT_ID=YourClientId
COGNITO_DOMAIN=mindmate-403745271636.auth.us-east-1.amazoncognito.com
```

## 🔧 Build Configuration

The `amplify.yml` file is already configured for static site deployment:

```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - echo "Pre-build phase started"
        - echo "Checking frontend files..."
        - ls -la frontend/
    build:
      commands:
        - echo "Build phase started"
        - echo "Mind Mate - AI Mental Health Companion"
        - echo "Preparing frontend assets..."
        - echo "✅ Frontend build complete"
    postBuild:
      commands:
        - echo "Post-build phase"
        - echo "Deployment ready!"
  artifacts:
    baseDirectory: frontend
    files:
      - '**/*'
    name: mindmate-frontend
  cache:
    paths: []
```

## 🌐 Custom Domain (Optional)

1. **Purchase/Configure Domain**
   - Buy domain through Route 53 or use existing domain
   - Configure DNS settings

2. **Add Custom Domain in Amplify**
   - Go to App Settings → Domain management
   - Add your custom domain
   - Follow SSL certificate setup

## 🔒 Security Considerations

1. **CORS Configuration**
   - Ensure API endpoints allow requests from Amplify domain
   - Update CORS settings in API Gateway

2. **Authentication**
   - Configure Cognito redirect URLs to include Amplify domain
   - Update OAuth settings

3. **Content Security Policy**
   - Add CSP headers if needed for enhanced security

## 📊 Monitoring & Analytics

1. **Enable Amplify Monitoring**
   - Go to App Settings → Monitoring
   - Enable access logs and performance monitoring

2. **CloudWatch Integration**
   - Monitor deployment metrics
   - Set up alerts for failures

## 🚨 Troubleshooting

### Common Issues:

1. **Build Failures**
   ```bash
   # Check build logs in Amplify console
   # Verify amplify.yml syntax
   ```

2. **API Connection Issues**
   ```bash
   # Verify API endpoints are accessible
   # Check CORS configuration
   # Validate authentication tokens
   ```

3. **Asset Loading Issues**
   ```bash
   # Ensure all images are in frontend directory
   # Check file paths are relative
   # Verify file extensions match
   ```

## 📱 Post-Deployment Checklist

- [ ] App loads successfully
- [ ] Authentication works
- [ ] Chat functionality operational
- [ ] ML analysis features working
- [ ] Pet avatars display correctly
- [ ] Mobile responsiveness verified
- [ ] API endpoints responding
- [ ] Clear chat button functional

## 🎯 Performance Optimization

1. **Image Optimization**
   - Compress pet avatar images
   - Use WebP format if supported

2. **Caching**
   - Configure CloudFront caching rules
   - Set appropriate cache headers

3. **Minification**
   - Minify CSS and JavaScript if needed
   - Enable gzip compression

## 📞 Support

If you encounter issues:
1. Check AWS Amplify console logs
2. Verify all API endpoints are accessible
3. Test authentication flow
4. Check browser console for errors

---

**Ready to deploy? Choose your preferred method above and follow the steps!** 🚀