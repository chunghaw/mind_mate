#!/usr/bin/env python3
"""
Merge onboarding flow from onboarding.html into mind-mate-hackathon.html
Following PRODUCT_VISION.md: Welcome → Pet Selection → Name → Intro → Main App
"""

import re

# Read source files
with open('frontend/onboarding.html', 'r') as f:
    onboarding = f.read()

with open('frontend/mind-mate-hackathon.html', 'r') as f:
    main_app = f.read()

# Extract onboarding CSS (between <style> tags, after line 10)
onboarding_css_match = re.search(r'<style>(.*?)</style>', onboarding, re.DOTALL)
onboarding_css = onboarding_css_match.group(1) if onboarding_css_match else ''

# Extract onboarding screens (between <div class="container"> and </div>)
onboarding_html_match = re.search(r'<div class="container">(.*?)</div>\s*<script>', onboarding, re.DOTALL)
onboarding_html = onboarding_html_match.group(1) if onboarding_html_match else ''

# Extract onboarding JavaScript (between <script> and </script>, the main logic)
onboarding_js_match = re.search(r'<script>\s*// Cognito Configuration(.*?)</script>', onboarding, re.DOTALL)
onboarding_js = onboarding_js_match.group(1) if onboarding_js_match else ''

# Simplify onboarding (remove OAuth, keep simple flow per PRODUCT_VISION.md)
simplified_css = """
        /* ===== ONBOARDING STYLES ===== */
        #onboardingOverlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, var(--bg) 0%, #e0f2e9 100%);
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        #onboardingOverlay.hidden {
            display: none;
        }
        
        .onboarding-screen {
            display: none;
            max-width: 480px;
            width: 90%;
            animation: fadeIn 0.5s ease-out;
        }
        
        .onboarding-screen.active {
            display: block;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .welcome-card, .personality-card, .conversation-card {
            background: white;
            border-radius: 24px;
            padding: 40px;
            border: 2px solid var(--border);
            box-shadow: 0 4px 20px var(--shadow);
            text-align: center;
        }
        
        .onboarding-logo {
            width: 120px;
            height: 120px;
            margin: 0 auto 20px;
            border-radius: 20px;
        }
        
        .onboarding-title {
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 12px;
        }
        
        .onboarding-subtitle {
            font-size: 16px;
            color: var(--text-light);
            margin-bottom: 30px;
        }
        
        .personality-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin: 24px 0;
        }
        
        .personality-option {
            padding: 20px;
            border: 2px solid var(--border);
            border-radius: 16px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .personality-option:hover {
            border-color: var(--primary);
            transform: translateY(-2px);
        }
        
        .personality-option.selected {
            border-color: var(--primary);
            background: var(--primary-light);
        }
        
        .personality-emoji {
            font-size: 48px;
            margin-bottom: 8px;
        }
        
        .personality-name {
            font-weight: 600;
            margin-bottom: 4px;
        }
        
        .personality-desc {
            font-size: 12px;
            color: var(--text-light);
        }
        
        .pet-avatar-large {
            font-size: 80px;
            margin-bottom: 20px;
        }
        
        .pet-message {
            font-size: 18px;
            line-height: 1.6;
            margin-bottom: 24px;
            color: var(--text);
        }
        
        .user-input {
            width: 100%;
            padding: 16px;
            border: 2px solid var(--border);
            border-radius: 12px;
            font-size: 16px;
            margin-bottom: 16px;
        }
        
        .onboarding-btn {
            width: 100%;
            padding: 16px;
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .onboarding-btn:hover {
            background: var(--primary-dark);
            transform: translateY(-2px);
        }
        
        .onboarding-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
"""

simplified_html = """
    <!-- Onboarding Overlay -->
    <div id="onboardingOverlay">
        <!-- Welcome Screen -->
        <div id="welcomeScreen" class="onboarding-screen active">
            <div class="welcome-card">
                <img src="Mind_Mate.jpeg" alt="Mind Mate" class="onboarding-logo">
                <h1 class="onboarding-title">Mind Mate</h1>
                <p class="onboarding-subtitle">Your AI Pet Companion for Mental Wellness</p>
                <button class="onboarding-btn" onclick="startOnboarding()">🌟 Get Started</button>
            </div>
        </div>
        
        <!-- Pet Selection Screen -->
        <div id="petSelectionScreen" class="onboarding-screen">
            <div class="personality-card">
                <h2 class="onboarding-title">Choose Your Companion</h2>
                <p class="onboarding-subtitle">Each personality has a unique way of supporting you!</p>
                
                <div class="personality-grid">
                    <div class="personality-option" onclick="selectPet('🐶', 'Gentle Guardian')">
                        <div class="personality-emoji">🐶</div>
                        <div class="personality-name">Gentle Guardian</div>
                        <div class="personality-desc">Nurturing, supportive, patient</div>
                    </div>
                    
                    <div class="personality-option" onclick="selectPet('🐱', 'Playful Pal')">
                        <div class="personality-emoji">🐱</div>
                        <div class="personality-name">Playful Pal</div>
                        <div class="personality-desc">Energetic, fun, motivating</div>
                    </div>
                    
                    <div class="personality-option" onclick="selectPet('🐉', 'Focused Friend')">
                        <div class="personality-emoji">🐉</div>
                        <div class="personality-name">Focused Friend</div>
                        <div class="personality-desc">Calm, direct, mindful</div>
                    </div>
                    
                    <div class="personality-option" onclick="selectPet('🦊', 'Sensitive Soul')">
                        <div class="personality-emoji">🦊</div>
                        <div class="personality-name">Sensitive Soul</div>
                        <div class="personality-desc">Empathetic, understanding, validating</div>
                    </div>
                </div>
                
                <button class="onboarding-btn" id="continuePetBtn" onclick="confirmPet()" disabled>Continue</button>
            </div>
        </div>
        
        <!-- Name Input Screen -->
        <div id="nameScreen" class="onboarding-screen">
            <div class="conversation-card">
                <div class="pet-avatar-large" id="petAvatar">🐶</div>
                <div class="pet-message">
                    Hi there! I'm so excited to be your companion!<br>
                    What should I call you?
                </div>
                <input type="text" id="userName" class="user-input" placeholder="Your name..." onkeypress="if(event.key==='Enter') saveName()">
                <button class="onboarding-btn" onclick="saveName()">Continue</button>
            </div>
        </div>
        
        <!-- Intro Screen -->
        <div id="introScreen" class="onboarding-screen">
            <div class="conversation-card">
                <div class="pet-avatar-large" id="introPetAvatar">🐶</div>
                <div class="pet-message" id="introMessage">
                    Nice to meet you! I'm here to support your mental wellness journey.<br><br>
                    I'll check in with you, listen to how you're feeling, and suggest activities that might help.<br><br>
                    Ready to start?
                </div>
                <button class="onboarding-btn" onclick="completeOnboarding()">Let's Go!</button>
            </div>
        </div>
    </div>
"""

simplified_js = """
        // ===== ONBOARDING LOGIC =====
        let selectedPet = { emoji: '🐶', name: 'Gentle Guardian' };
        
        function startOnboarding() {
            showOnboardingScreen('petSelectionScreen');
        }
        
        function selectPet(emoji, name) {
            selectedPet = { emoji, name };
            document.querySelectorAll('.personality-option').forEach(el => el.classList.remove('selected'));
            event.target.closest('.personality-option').classList.add('selected');
            document.getElementById('continuePetBtn').disabled = false;
        }
        
        function confirmPet() {
            document.getElementById('petAvatar').textContent = selectedPet.emoji;
            showOnboardingScreen('nameScreen');
        }
        
        function saveName() {
            const name = document.getElementById('userName').value.trim();
            if (!name) {
                alert('Please enter your name');
                return;
            }
            
            localStorage.setItem('mindmate_username', name);
            localStorage.setItem('mindmate_pet_emoji', selectedPet.emoji);
            localStorage.setItem('mindmate_pet_name', selectedPet.name);
            
            document.getElementById('introPetAvatar').textContent = selectedPet.emoji;
            document.getElementById('introMessage').innerHTML = 
                `Nice to meet you, ${name}! I'm here to support your mental wellness journey.<br><br>` +
                `I'll check in with you, listen to how you're feeling, and suggest activities that might help.<br><br>` +
                `Ready to start?`;
            
            showOnboardingScreen('introScreen');
        }
        
        function completeOnboarding() {
            localStorage.setItem('mindmate_onboarding_complete', 'true');
            document.getElementById('onboardingOverlay').classList.add('hidden');
            
            // Update main app with pet selection
            const petEmoji = localStorage.getItem('mindmate_pet_emoji') || '🐶';
            AppState.chat.companion.emoji = petEmoji;
            document.getElementById('companionAvatar').textContent = petEmoji;
        }
        
        function showOnboardingScreen(screenId) {
            document.querySelectorAll('.onboarding-screen').forEach(s => s.classList.remove('active'));
            document.getElementById(screenId).classList.add('active');
        }
        
        function checkOnboarding() {
            const completed = localStorage.getItem('mindmate_onboarding_complete');
            if (completed === 'true') {
                document.getElementById('onboardingOverlay').classList.add('hidden');
                // Load saved pet
                const petEmoji = localStorage.getItem('mindmate_pet_emoji') || '🐶';
                AppState.chat.companion.emoji = petEmoji;
                document.getElementById('companionAvatar').textContent = petEmoji;
            }
        }
"""

# Insert into main app
# 1. Add CSS before closing </style>
main_app = main_app.replace('</style>', simplified_css + '\n    </style>')

# 2. Add HTML after <body> tag
main_app = main_app.replace('<body>', '<body>\n' + simplified_html)

# 3. Add JavaScript before window.onload
main_app = main_app.replace('// ===== INITIALIZATION =====', simplified_js + '\n        // ===== INITIALIZATION =====')

# 4. Add checkOnboarding() call in window.onload
main_app = main_app.replace(
    "console.log('🧠 Mind Mate Hackathon Demo initialized');",
    "console.log('🧠 Mind Mate Hackathon Demo initialized');\n            checkOnboarding();"
)

# Write merged file
with open('frontend/mind-mate-hackathon.html', 'w') as f:
    f.write(main_app)

print("✅ Onboarding merged successfully!")
print("📝 Changes:")
print("  - Added onboarding CSS styles")
print("  - Added 4 onboarding screens (Welcome, Pet Selection, Name, Intro)")
print("  - Added onboarding JavaScript logic")
print("  - Integrated with existing app state")
print("  - Pet selection persists in localStorage")
