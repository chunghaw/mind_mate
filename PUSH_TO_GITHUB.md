# 🚀 Push Mind Mate to GitHub

## Step 1: Create GitHub Repository

1. Go to: **https://github.com/new**
2. Fill in:
   - **Repository name**: `mind-mate`
   - **Description**: "AI Pet Companion for Mental Wellness - AWS Hackathon"
   - **Public** (recommended for hackathon)
   - **DO NOT** check "Initialize with README"
3. Click **"Create repository"**

---

## Step 2: Push Your Code

After creating the repo, run these commands in your terminal:

```bash
# Add GitHub as remote (replace YOUR_USERNAME with your actual GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/mind-mate.git

# Push to GitHub
git push -u origin main
```

**Example:**
```bash
git remote add origin https://github.com/chunghaw96/mind-mate.git
git push -u origin main
```

When prompted:
- **Username**: Your GitHub username
- **Password**: Your GitHub Personal Access Token (NOT your password!)

---

## Step 3: Get Personal Access Token (If needed)

If you don't have a token:

1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. **Note**: "Mind Mate Deployment"
4. **Expiration**: 30 days
5. **Scopes**: Check `repo` (all repo permissions)
6. Click **"Generate token"**
7. **COPY THE TOKEN** (you won't see it again!)
8. Use this token as your password when pushing

---

## Step 4: Connect to Amplify

1. Go to: https://console.aws.amazon.com/amplify/home?region=us-east-1
2. Click **"New app"** → **"Host web app"**
3. Select **"GitHub"**
4. Authorize AWS Amplify
5. Select repository: `mind-mate`
6. Branch: `main`
7. Build settings:
   - Base directory: `frontend`
   - Build command: (leave empty)
8. Click **"Save and deploy"**

---

## ✅ Done!

You'll get an Amplify URL like:
`https://main.d1234abcd.amplifyapp.com`

Open it and test your app! 🎉
