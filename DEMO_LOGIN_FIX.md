# 🔧 Demo Login Fix Guide

## Problem
The demo credentials `demo_user` / `DemoML2024!` are not working due to Cognito authentication issues.

## 🚀 Quick Solutions

### Option 1: Demo Bypass (Recommended for Demo)
1. **Open the demo bypass page:**
   ```
   open demo-bypass.html
   ```
2. **Click "Enter Demo Mode"**
3. **Access the full app with demo data**

### Option 2: URL Parameter Access
1. **Open the main app with demo parameter:**
   ```
   open frontend/mind-mate-hackathon.html?demo=true
   ```
2. **App will automatically run in demo mode**

### Option 3: Create Real Demo User
1. **Run the fix script:**
   ```bash
   ./fix-demo-login.sh
   ```
2. **Then try logging in with:**
   - Username: `demo_user`
   - Password: `DemoML2024!`

### Option 4: Manual Browser Setup
1. **Open browser console (F12)**
2. **Paste this code:**
   ```javascript
   localStorage.setItem('demoMode', 'true');
   localStorage.setItem('userId', 'demo-user-123');
   localStorage.setItem('userEmail', 'demo@mindmate.ai');
   localStorage.setItem('userName', 'Demo User');
   window.location.reload();
   ```

## 🎯 For Your Demo Presentation

### Recommended Flow:
1. **Start with demo-bypass.html** - Shows professional demo entry
2. **Click "Enter Demo Mode"** - Seamless transition
3. **Show the full ML analysis** - All features work
4. **Mention authentication** - "In production, users would login normally"

### Demo Script Update:
```markdown
> "For this demo, I'll use our demo access portal..."
[Open demo-bypass.html]
> "In production, users would authenticate through Google OAuth or username/password..."
[Click Enter Demo Mode]
> "Now we're in the full application with two weeks of demo data..."
```

## 🔍 What's Working Now

✅ **Demo Mode Access** - Bypass authentication completely
✅ **Full ML Analysis** - All 40+ features extracted
✅ **AI Report** - Complete risk assessment
✅ **Chat Interface** - Interactive companion
✅ **Clear Chat Button** - Reset functionality
✅ **Wellness Dashboard** - Real-time updates

## 🛠️ Technical Details

The authentication bypass works by:
1. Setting demo mode in localStorage
2. Providing demo user ID for API calls
3. Skipping Cognito authentication
4. Using the same ML analysis pipeline

This gives you a fully functional demo without authentication issues.

## 🎬 Demo Ready!

Your demo is now ready with multiple access methods. Use **demo-bypass.html** for the cleanest presentation experience.