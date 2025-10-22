#!/usr/bin/env node

/**
 * Create Demo User with Rich ML Features
 * 
 * This script creates a comprehensive demo user profile with:
 * - 14 days of mood data showing declining trend
 * - Chat messages with varying sentiment
 * - Behavioral patterns for ML analysis
 * - Risk factors that trigger interventions
 */

const AWS = require('aws-sdk');
const { v4: uuidv4 } = require('uuid');

// Configure AWS
const dynamodb = new AWS.DynamoDB.DocumentClient({
    region: process.env.AWS_REGION || 'us-east-1'
});

const TABLE_NAME = process.env.DYNAMODB_TABLE || 'EmoCompanion';

// Demo user configuration
const DEMO_USER = {
    userId: 'demo_ml_user',
    email: 'demo@mindmate.ai',
    name: 'Alex Chen',
    petName: 'Buddy',
    personality: 'gentle_guardian',
    createdAt: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString() // 14 days ago
};

/**
 * Generate realistic mood data showing declining trend
 */
function generateMoodData() {
    const moods = [];
    const baseDate = new Date(Date.now() - 14 * 24 * 60 * 60 * 1000);
    
    // Start with moderate mood, decline over time
    let currentMood = 7;
    
    for (let i = 0; i < 14; i++) {
        const date = new Date(baseDate.getTime() + i * 24 * 60 * 60 * 1000);
        
        // Gradual decline with some volatility
        if (i < 5) {
            currentMood = 7 + Math.random() * 2 - 1; // 6-8 range
        } else if (i < 10) {
            currentMood = 5 + Math.random() * 2 - 1; // 4-6 range
        } else {
            currentMood = 3 + Math.random() * 2 - 1; // 2-4 range
        }
        
        // Ensure bounds
        currentMood = Math.max(1, Math.min(10, currentMood));
        
        moods.push({
            PK: `USER#${DEMO_USER.userId}`,
            SK: `MOOD#${date.toISOString().split('T')[0]}`,
            userId: DEMO_USER.userId,
            date: date.toISOString().split('T')[0],
            mood: Math.round(currentMood * 10) / 10,
            timestamp: date.toISOString(),
            notes: i > 10 ? 'Feeling overwhelmed lately' : i > 7 ? 'Struggling a bit' : 'Doing okay'
        });
    }
    
    return moods;
}

/**
 * Generate chat messages with varying sentiment
 */
function generateChatMessages() {
    const messages = [];
    const baseDate = new Date(Date.now() - 14 * 24 * 60 * 60 * 1000);
    
    const messageTemplates = [
        // Week 1 - More positive
        { day: 1, content: "Hi Buddy! Had a good day at work today. Feeling pretty optimistic.", sentiment: 0.7 },
        { day: 2, content: "Thanks for checking in. I'm doing alright, just the usual stress.", sentiment: 0.3 },
        { day: 3, content: "Went for a walk today. Fresh air helped clear my mind.", sentiment: 0.6 },
        { day: 4, content: "Feeling a bit anxious about the presentation tomorrow.", sentiment: -0.2 },
        
        // Week 2 - Declining sentiment
        { day: 6, content: "Not sleeping well lately. Mind keeps racing at night.", sentiment: -0.4 },
        { day: 7, content: "Everything feels overwhelming. Can't seem to catch a break.", sentiment: -0.6 },
        { day: 8, content: "I don't know if I can handle this anymore. Feeling hopeless.", sentiment: -0.8 },
        { day: 9, content: "What's the point? Nothing I do seems to matter.", sentiment: -0.9 },
        { day: 10, content: "I feel so alone. Nobody understands what I'm going through.", sentiment: -0.7 },
        { day: 11, content: "Can't get out of bed today. Everything hurts.", sentiment: -0.8 },
        { day: 12, content: "Maybe everyone would be better off without me.", sentiment: -0.95 },
        { day: 13, content: "I'm scared of these thoughts I'm having.", sentiment: -0.85 }
    ];
    
    messageTemplates.forEach((template, index) => {
        const messageDate = new Date(baseDate.getTime() + template.day * 24 * 60 * 60 * 1000);
        
        // User message
        messages.push({
            PK: `USER#${DEMO_USER.userId}`,
            SK: `CHAT#${messageDate.getTime()}#USER`,
            userId: DEMO_USER.userId,
            messageId: uuidv4(),
            content: template.content,
            sender: 'user',
            timestamp: messageDate.toISOString(),
            sentiment: template.sentiment,
            analysisComplete: true
        });
        
        // AI response
        const aiResponse = generateAIResponse(template.content, template.sentiment);
        messages.push({
            PK: `USER#${DEMO_USER.userId}`,
            SK: `CHAT#${messageDate.getTime() + 1000}#AI`,
            userId: DEMO_USER.userId,
            messageId: uuidv4(),
            content: aiResponse,
            sender: 'ai',
            timestamp: new Date(messageDate.getTime() + 1000).toISOString()
        });
    });
    
    return messages;
}

/**
 * Generate appropriate AI responses based on sentiment
 */
function generateAIResponse(userMessage, sentiment) {
    if (sentiment < -0.8) {
        return "I'm really concerned about you, Alex. These feelings are serious, and you don't have to face them alone. Have you considered reaching out to a mental health professional? I'm here to support you, but professional help could make a real difference.";
    } else if (sentiment < -0.5) {
        return "I hear that you're struggling right now, Alex. These difficult feelings are valid, and it's okay to not be okay sometimes. What's one small thing that usually brings you a little comfort?";
    } else if (sentiment < 0) {
        return "It sounds like you're going through a tough time. I'm here to listen and support you. Would it help to talk about what's making you feel this way?";
    } else if (sentiment < 0.5) {
        return "Thanks for sharing how you're feeling, Alex. It's good that you're checking in with yourself. How can I support you today?";
    } else {
        return "I'm glad to hear you're doing well, Alex! It's wonderful when you have those positive moments. What made today feel good for you?";
    }
}

/**
 * Generate ML features based on the data
 */
function generateMLFeatures() {
    const now = new Date();
    const features = {
        PK: `USER#${DEMO_USER.userId}`,
        SK: 'ML_FEATURES#CURRENT',
        userId: DEMO_USER.userId,
        lastUpdated: now.toISOString(),
        
        // Mood Features (16 features)
        mood_trend_7day: -0.6,
        mood_mean_7day: 3.2,
        mood_std_7day: 1.4,
        mood_min_7day: 2.1,
        mood_max_7day: 4.8,
        consecutive_low_days: 3,
        mood_volatility: 0.78,
        weekend_mood_diff: -0.3,
        morning_vs_evening_mood: -0.2,
        mood_decline_rate: -0.43,
        mood_recovery_time: 0,
        mood_baseline_deviation: -2.8,
        seasonal_mood_factor: 0.1,
        mood_consistency_score: 0.3,
        mood_improvement_trend: -0.8,
        mood_stability_index: 0.25,
        
        // Behavioral Features (18 features)
        daily_checkin_frequency: 0.85,
        engagement_decline: 0.65,
        response_time_trend: 1.2,
        activity_completion_rate: 0.4,
        late_night_usage_frequency: 4,
        session_duration_trend: -0.3,
        interaction_depth_score: 0.6,
        help_seeking_frequency: 0.2,
        social_withdrawal_score: 0.8,
        routine_disruption_score: 0.7,
        sleep_pattern_irregularity: 0.75,
        communication_frequency: 0.5,
        goal_completion_rate: 0.3,
        self_care_engagement: 0.25,
        crisis_resource_usage: 0.1,
        support_system_engagement: 0.2,
        coping_strategy_usage: 0.3,
        behavioral_consistency: 0.35,
        
        // Sentiment Features (15 features)
        negative_sentiment_frequency: 0.75,
        positive_sentiment_frequency: 0.15,
        neutral_sentiment_frequency: 0.10,
        sentiment_volatility: 0.85,
        crisis_keywords: 2,
        hopelessness_score: 0.82,
        isolation_keywords: 3,
        anxiety_indicators: 4,
        depression_markers: 5,
        suicidal_ideation_risk: 0.7,
        emotional_numbness_score: 0.6,
        anger_frustration_level: 0.4,
        fear_worry_frequency: 0.8,
        guilt_shame_indicators: 0.5,
        sentiment_trend_7day: -0.7
    };
    
    return features;
}

/**
 * Generate risk assessment
 */
function generateRiskAssessment() {
    const riskScore = 0.73; // HIGH risk
    
    return {
        PK: `USER#${DEMO_USER.userId}`,
        SK: 'RISK_ASSESSMENT#CURRENT',
        userId: DEMO_USER.userId,
        riskScore: riskScore,
        riskLevel: 'HIGH',
        confidence: 0.89,
        method: 'ml_ensemble',
        lastUpdated: new Date().toISOString(),
        
        riskFactors: [
            'Strong declining mood trend (-0.6 slope over 7 days)',
            'Extended low mood period (3 consecutive days below threshold)',
            'High negative sentiment in communications (75%)',
            'Expressions of hopelessness detected (score: 0.82)',
            'Crisis language detected in recent messages (2 instances)',
            'Increased late-night activity indicating sleep disruption (4 sessions)',
            'Social withdrawal patterns observed (engagement decline: 65%)',
            'Suicidal ideation risk indicators present (score: 0.7)'
        ],
        
        interventions: [
            {
                type: 'immediate',
                action: 'crisis_resources',
                message: 'Provide crisis hotline and emergency resources'
            },
            {
                type: 'proactive',
                action: 'wellness_check',
                message: 'Schedule daily check-ins for next 7 days'
            },
            {
                type: 'therapeutic',
                action: 'coping_strategies',
                message: 'Suggest grounding techniques and breathing exercises'
            }
        ]
    };
}

/**
 * Create user profile
 */
function createUserProfile() {
    return {
        PK: `USER#${DEMO_USER.userId}`,
        SK: 'PROFILE',
        userId: DEMO_USER.userId,
        email: DEMO_USER.email,
        name: DEMO_USER.name,
        petName: DEMO_USER.petName,
        personality: DEMO_USER.personality,
        createdAt: DEMO_USER.createdAt,
        lastActive: new Date().toISOString(),
        onboardingComplete: true,
        preferences: {
            notifications: true,
            dailyReminders: true,
            crisisAlerts: true
        }
    };
}

/**
 * Main function to create all demo data
 */
async function createDemoUser() {
    console.log('🚀 Creating ML-powered demo user...');
    
    try {
        // Prepare all data
        const items = [
            createUserProfile(),
            generateMLFeatures(),
            generateRiskAssessment(),
            ...generateMoodData(),
            ...generateChatMessages()
        ];
        
        console.log(`📊 Generated ${items.length} items for demo user`);
        
        // Batch write to DynamoDB
        const batchSize = 25; // DynamoDB batch limit
        for (let i = 0; i < items.length; i += batchSize) {
            const batch = items.slice(i, i + batchSize);
            
            const params = {
                RequestItems: {
                    [TABLE_NAME]: batch.map(item => ({
                        PutRequest: { Item: item }
                    }))
                }
            };
            
            await dynamodb.batchWrite(params).promise();
            console.log(`✅ Wrote batch ${Math.floor(i/batchSize) + 1}/${Math.ceil(items.length/batchSize)}`);
        }
        
        console.log('🎯 Demo user created successfully!');
        console.log('\n📋 Demo Credentials:');
        console.log(`   User ID: ${DEMO_USER.userId}`);
        console.log(`   Email: ${DEMO_USER.email}`);
        console.log(`   Name: ${DEMO_USER.name}`);
        console.log(`   Pet: ${DEMO_USER.petName} (${DEMO_USER.personality})`);
        console.log('\n📊 ML Features:');
        console.log('   - 49 features extracted');
        console.log('   - Risk Score: 73% (HIGH)');
        console.log('   - 14 days of mood data');
        console.log('   - 26 chat messages');
        console.log('   - 8 risk factors identified');
        
    } catch (error) {
        console.error('❌ Error creating demo user:', error);
        process.exit(1);
    }
}

// Run if called directly
if (require.main === module) {
    createDemoUser();
}

module.exports = { createDemoUser, DEMO_USER };