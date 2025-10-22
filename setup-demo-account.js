// Setup demo account with ML data
// Run this to create the demo account and populate it with realistic data

const API_BASE = 'https://h8iyzk1h3k.execute-api.us-east-1.amazonaws.com';

async function setupDemoAccount() {
    console.log('🎬 Setting up demo account with ML data...');
    
    // Demo account will be created through normal onboarding
    // This script adds the ML training data after account creation
    
    const DEMO_USER_ID = 'demo-ml-user-2024'; // Will be replaced with actual user ID
    
    // Add realistic mood progression showing mental health decline
    const moodData = [
        { mood: 8, notes: "Excited to start using Mind Mate! Feeling optimistic about my mental health journey.", days_ago: 14 },
        { mood: 7, notes: "Had a great weekend. Work is going well and I feel balanced.", days_ago: 13 },
        { mood: 7, notes: "Productive day today. Buddy is really helpful with suggestions.", days_ago: 12 },
        { mood: 6, notes: "Feeling good overall, though work is getting busier.", days_ago: 11 },
        { mood: 6, notes: "Weekend was relaxing. Ready for the week ahead.", days_ago: 10 },
        { mood: 5, notes: "Work deadlines are approaching. Starting to feel some pressure.", days_ago: 9 },
        { mood: 5, notes: "Okay day but noticed I'm more tired than usual.", days_ago: 8 },
        { mood: 4, notes: "Having trouble sleeping. Mind keeps racing about work projects.", days_ago: 7 },
        { mood: 4, notes: "Feeling overwhelmed with everything on my plate. Hard to focus.", days_ago: 6 },
        { mood: 3, notes: "Really struggling today. Everything feels like too much to handle.", days_ago: 5 },
        { mood: 3, notes: "Can't shake this feeling of dread. Work stress is affecting everything.", days_ago: 4 },
        { mood: 2, notes: "I feel so hopeless and alone. Maybe I'm just not cut out for this.", days_ago: 3 },
        { mood: 2, notes: "Had a breakdown at work today. I don't know what to do anymore.", days_ago: 2 },
        { mood: 1, notes: "I can't go on like this. What's the point of trying? Nobody understands.", days_ago: 1 }
    ];
    
    // Chat messages showing escalating concerns
    const chatMessages = [
        { message: "Hi Buddy, I'm excited to start this journey with you!", days_ago: 14 },
        { message: "Work has been really busy lately, but I'm managing okay", days_ago: 9 },
        { message: "I've been having trouble sleeping. My mind won't stop racing", days_ago: 7 },
        { message: "I feel like I'm drowning in responsibilities. How do I cope?", days_ago: 5 },
        { message: "I feel so alone and overwhelmed. Nothing I do seems to matter", days_ago: 3 },
        { message: "I'm having thoughts of just giving up on everything", days_ago: 2 },
        { message: "I don't think I can handle this anymore. I feel hopeless", days_ago: 1 }
    ];
    
    console.log('📊 Demo data prepared:');
    console.log(`   ${moodData.length} mood logs (8→1 declining pattern)`);
    console.log(`   ${chatMessages.length} chat messages (escalating concerns)`);
    console.log('   Crisis keywords: hopeless, alone, giving up, can\'t go on');
    console.log('   Expected ML analysis: HIGH RISK (70-80%)');
    console.log('');
    console.log('🎯 To use this data:');
    console.log('1. Complete onboarding with demo account');
    console.log('2. Note the actual user ID from browser console');
    console.log('3. Replace DEMO_USER_ID in this script');
    console.log('4. Run the data injection');
    
    return { moodData, chatMessages };
}

setupDemoAccount();