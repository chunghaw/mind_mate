# Google OAuth Setup Guide

This guide walks you through setting up Google OAuth for Mind Mate authentication.

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter project name: "Mind Mate"
4. Click "Create"

## Step 2: Enable Google+ API

1. In your project, go to "APIs & Services" → "Library"
2. Search for "Google+ API"
3. Click "Enable"

## Step 3: Configure OAuth Consent Screen

1. Go to "APIs & Services" → "OAuth consent screen"
2. Select "External" user type
3. Click "Create"
4. Fill in the form:
   - **App name**: Mind Mate
   - **User support email**: Your email
   - **App logo**: (optional)
   - **App domain**: Your domain or leave blank for testing
   - **Developer contact**: Your email
5. Click "Save and Continue"
6. **Scopes**: Click "Add or Remove Scopes"
   - Select: `email`, `profile`, `openid`
   - Click "Update"
7. Click "Save and Continue"
8. **Test users** (for development):
   - Add your email address
   - Click "Save and Continue"
9. Click "Back to Dashboard"

## Step 4: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Select "Web application"
4. Fill in the form:
   - **Name**: Mind Mate Web App
   - **Authorized JavaScript origins**:
     - `http://localhost:8000`
     - `https://your-amplify-url.amplifyapp.com` (add later)
   - **Authorized redirect URIs**:
     - `http://localhost:8000`
     - `https://mindmate-ACCOUNT_ID.auth.us-east-1.amazoncognito.com/oauth2/idpresponse`
     
     (Replace `ACCOUNT_ID` with your AWS account ID after deploying Cognito)

5. Click "Create"
6. **Save the credentials**:
   - Copy "Client ID"
   - Copy "Client secret"
   - Keep these safe!

## Step 5: Set Environment Variables

```bash
# Add to your shell profile (~/.zshrc or ~/.bashrc)
export GOOGLE_CLIENT_ID="your-client-id-here.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="your-client-secret-here"

# Reload shell
source ~/.zshrc  # or source ~/.bashrc
```

## Step 6: Deploy Cognito with Google OAuth

```bash
cd infrastructure
./deploy-cognito.sh
```

The script will:
- Deploy Cognito User Pool
- Configure Google as identity provider
- Output the Cognito domain URL

## Step 7: Update Google OAuth Redirect URIs

After deploying Cognito, you'll get a domain like:
```
mindmate-123456789.auth.us-east-1.amazoncognito.com
```

1. Go back to Google Cloud Console → Credentials
2. Click on your OAuth 2.0 Client ID
3. Add the Cognito redirect URI:
   ```
   https://mindmate-123456789.auth.us-east-1.amazoncognito.com/oauth2/idpresponse
   ```
4. Click "Save"

## Step 8: Test Google Sign-In

1. Open your app
2. Click "Sign in with Google"
3. You should see Google's OAuth consent screen
4. Sign in with your Google account
5. You should be redirected back to your app

## Troubleshooting

### Error: "redirect_uri_mismatch"
- Check that the redirect URI in Google Console exactly matches the Cognito domain
- Make sure there are no trailing slashes
- Wait a few minutes after updating URIs (Google caches them)

### Error: "Access blocked: This app's request is invalid"
- Make sure you've enabled Google+ API
- Check that OAuth consent screen is configured
- Add your email as a test user

### Error: "invalid_client"
- Check that Client ID and Client Secret are correct
- Make sure they're properly set in environment variables
- Redeploy Cognito stack if you changed credentials

## Production Checklist

Before going to production:

- [ ] Verify OAuth consent screen
- [ ] Add production domain to authorized origins
- [ ] Add production Cognito domain to redirect URIs
- [ ] Remove test users (make app public)
- [ ] Set up proper app logo and branding
- [ ] Review scopes (only request what you need)
- [ ] Set up proper error handling in app

## Security Best Practices

1. **Never commit credentials to Git**
   - Use environment variables
   - Add `.env` to `.gitignore`

2. **Rotate secrets regularly**
   - Generate new client secret every 90 days
   - Update in AWS Secrets Manager

3. **Limit redirect URIs**
   - Only add URIs you actually use
   - Remove development URIs in production

4. **Monitor usage**
   - Check Google Cloud Console for unusual activity
   - Set up alerts for quota limits

## Cost

Google OAuth is **free** for most use cases:
- Up to 10,000 requests/day: Free
- Above that: Contact Google for pricing

## Support

- [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2)
- [AWS Cognito with Google](https://docs.aws.amazon.com/cognito/latest/developerguide/google.html)
- [Mind Mate Issues](https://github.com/chunghaw/mind_mate/issues)
