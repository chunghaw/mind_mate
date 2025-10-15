# Voice Agent - Technical Specification

## 🎤 Overview

Real-time voice conversation with AI pet, similar to ChatGPT voice function. Users can speak naturally and get immediate voice responses from their pet companion.

## 🏗️ Architecture

```
User speaks
    ↓
WebSocket (API Gateway)
    ↓
Amazon Transcribe (Streaming)
    ↓
Lambda (processVoiceInput)
    ↓
Bedrock Claude (generate response)
    ↓
Amazon Polly (text-to-speech)
    ↓
WebSocket (stream audio back)
    ↓
User hears pet response
```

## 🔧 Technical Implementation

### **1. WebSocket API Gateway**

**Purpose**: Real-time bidirectional communication

```yaml
# CloudFormation
VoiceWebSocketAPI:
  Type: AWS::ApiGatewayV2::Api
  Properties:
    Name: MindMateVoiceAPI
    ProtocolType: WEBSOCKET
    RouteSelectionExpression: "$request.body.action"

ConnectRoute:
  Type: AWS::ApiGatewayV2::Route
  Properties:
    ApiId: !Ref VoiceWebSocketAPI
    RouteKey: $connect
    Target: !Sub "integrations/${ConnectIntegration}"

DisconnectRoute:
  Type: AWS::ApiGatewayV2::Route
  Properties:
    ApiId: !Ref VoiceWebSocketAPI
    RouteKey: $disconnect
    Target: !Sub "integrations/${DisconnectIntegration}"

VoiceRoute:
  Type: AWS::ApiGatewayV2::Route
  Properties:
    ApiId: !Ref VoiceWebSocketAPI
    RouteKey: voice
    Target: !Sub "integrations/${VoiceIntegration}"
```

### **2. Frontend WebSocket Client**

```javascript
// Frontend: voice-client.js
class VoiceAgent {
    constructor(apiUrl, userId) {
        this.apiUrl = apiUrl;
        this.userId = userId;
        this.ws = null;
        this.mediaRecorder = null;
        this.audioContext = null;
        this.isRecording = false;
        this.isConnected = false;
    }

    async connect() {
        this.ws = new WebSocket(`${this.apiUrl}?userId=${this.userId}`);
        
        this.ws.onopen = () => {
            console.log('Voice agent connected');
            this.isConnected = true;
            this.onConnectionChange(true);
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };

        this.ws.onclose = () => {
            console.log('Voice agent disconnected');
            this.isConnected = false;
            this.onConnectionChange(false);
        };
    }

    async startRecording() {
        if (!this.isConnected) {
            throw new Error('Not connected to voice service');
        }

        const stream = await navigator.mediaDevices.getUserMedia({ 
            audio: {
                sampleRate: 16000,
                channelCount: 1,
                echoCancellation: true,
                noiseSuppression: true
            }
        });

        this.audioContext = new AudioContext({ sampleRate: 16000 });
        const source = this.audioContext.createMediaStreamSource(stream);
        
        // Create audio processor for real-time streaming
        const processor = this.audioContext.createScriptProcessor(4096, 1, 1);
        
        processor.onaudioprocess = (event) => {
            if (this.isRecording) {
                const audioData = event.inputBuffer.getChannelData(0);
                const int16Array = this.float32ToInt16(audioData);
                
                // Send audio chunks to WebSocket
                this.ws.send(JSON.stringify({
                    action: 'audio-chunk',
                    data: Array.from(int16Array),
                    userId: this.userId
                }));
            }
        };

        source.connect(processor);
        processor.connect(this.audioContext.destination);
        
        this.isRecording = true;
        this.onRecordingChange(true);
        
        // Send start recording signal
        this.ws.send(JSON.stringify({
            action: 'start-recording',
            userId: this.userId
        }));
    }

    stopRecording() {
        this.isRecording = false;
        this.onRecordingChange(false);
        
        if (this.audioContext) {
            this.audioContext.close();
        }
        
        // Send stop recording signal
        this.ws.send(JSON.stringify({
            action: 'stop-recording',
            userId: this.userId
        }));
    }

    handleMessage(data) {
        switch (data.type) {
            case 'transcription':
                this.onTranscription(data.text);
                break;
            case 'pet-response':
                this.onPetResponse(data.text);
                break;
            case 'audio-response':
                this.playAudioResponse(data.audioData);
                break;
            case 'error':
                this.onError(data.message);
                break;
        }
    }

    playAudioResponse(audioData) {
        // Convert base64 audio to playable format
        const audioBuffer = this.base64ToArrayBuffer(audioData);
        const blob = new Blob([audioBuffer], { type: 'audio/mp3' });
        const audioUrl = URL.createObjectURL(blob);
        
        const audio = new Audio(audioUrl);
        audio.play();
        
        audio.onended = () => {
            URL.revokeObjectURL(audioUrl);
            this.onAudioPlaybackComplete();
        };
    }

    float32ToInt16(float32Array) {
        const int16Array = new Int16Array(float32Array.length);
        for (let i = 0; i < float32Array.length; i++) {
            int16Array[i] = Math.max(-32768, Math.min(32767, float32Array[i] * 32768));
        }
        return int16Array;
    }

    base64ToArrayBuffer(base64) {
        const binaryString = window.atob(base64);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }
        return bytes.buffer;
    }

    // Event handlers (to be overridden)
    onConnectionChange(connected) {}
    onRecordingChange(recording) {}
    onTranscription(text) {}
    onPetResponse(text) {}
    onAudioPlaybackComplete() {}
    onError(message) {}
}
```

### **3. Backend Lambda Functions**

#### **Connection Handler**
```python
# Lambda: voiceConnect
import json
import boto3
import time
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('EmoCompanion')

def lambda_handler(event, context):
    connection_id = event['requestContext']['connectionId']
    user_id = event.get('queryStringParameters', {}).get('userId')
    
    # Store connection
    table.put_item(Item={
        'PK': f'CONNECTION#{connection_id}',
        'SK': 'VOICE',
        'userId': user_id,
        'connectionId': connection_id,
        'connectedAt': datetime.utcnow().isoformat(),
        'ttl': int(time.time()) + 3600  # 1 hour TTL
    })
    
    return {'statusCode': 200}
```

#### **Voice Processing Handler**
```python
# Lambda: processVoiceInput
import json
import boto3
import base64
from io import BytesIO

transcribe = boto3.client('transcribe-streaming')
bedrock = boto3.client('bedrock-runtime')
polly = boto3.client('polly')
apigateway = boto3.client('apigatewaymanagementapi')
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    connection_id = event['requestContext']['connectionId']
    body = json.loads(event['body'])
    action = body['action']
    user_id = body['userId']
    
    if action == 'start-recording':
        return start_recording_session(connection_id, user_id)
    elif action == 'audio-chunk':
        return process_audio_chunk(connection_id, user_id, body['data'])
    elif action == 'stop-recording':
        return stop_recording_session(connection_id, user_id)

def generate_audio_response(text, user_id):
    # Get user's preferred voice
    profile = get_user_profile(user_id)
    voice_id = get_voice_for_personality(profile['personality'])
    
    # Generate speech with Polly
    response = polly.synthesize_speech(
        Text=text,
        OutputFormat='mp3',
        VoiceId=voice_id,
        Engine='neural'
    )
    
    # Convert to base64 for WebSocket transmission
    audio_data = response['AudioStream'].read()
    return base64.b64encode(audio_data).decode('utf-8')

def get_voice_for_personality(personality):
    voice_mapping = {
        'gentle': 'Joanna',    # Warm, nurturing female voice
        'playful': 'Emma',     # Energetic, friendly female voice
        'focused': 'Matthew',  # Calm, steady male voice
        'sensitive': 'Amy'     # Soft, empathetic female voice
    }
    return voice_mapping.get(personality, 'Joanna')
```

## 🎨 UI Components

### **Voice Button**
```html
<div class="voice-container">
    <button id="voiceBtn" class="voice-btn" onclick="toggleVoice()">
        <span class="voice-icon">🎤</span>
        <span class="voice-text">Hold to Talk</span>
    </button>
    
    <div id="voiceStatus" class="voice-status">
        <div class="transcription" id="transcription"></div>
        <div class="pet-speaking" id="petSpeaking" style="display: none;">
            🐶 Speaking...
        </div>
    </div>
</div>

<style>
.voice-btn {
    background: linear-gradient(135deg, #10b981, #059669);
    color: white;
    border: none;
    border-radius: 50px;
    padding: 15px 30px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
    display: flex;
    align-items: center;
    gap: 10px;
}

.voice-btn.recording {
    background: linear-gradient(135deg, #ef4444, #dc2626);
    animation: pulse 1s infinite;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
}
</style>
```

## 🔊 Voice Personality Mapping

```python
VOICE_PERSONALITIES = {
    'gentle': {
        'voice': 'Joanna',
        'speed': 'medium',
        'pitch': '+5%',
        'style': 'Warm and nurturing'
    },
    'playful': {
        'voice': 'Emma', 
        'speed': 'fast',
        'pitch': '+10%',
        'style': 'Energetic and upbeat'
    },
    'focused': {
        'voice': 'Matthew',
        'speed': 'slow',
        'pitch': '0%',
        'style': 'Calm and steady'
    },
    'sensitive': {
        'voice': 'Amy',
        'speed': 'medium',
        'pitch': '+3%',
        'style': 'Soft and empathetic'
    }
}
```

## 📊 Performance Considerations

### **Latency Optimization**
- **Streaming transcription**: Process audio chunks in real-time
- **Parallel processing**: Generate text and audio responses simultaneously
- **Connection pooling**: Reuse WebSocket connections
- **Regional deployment**: Deploy close to users

### **Cost Optimization**
- **Transcribe**: ~$0.024 per minute
- **Polly**: ~$4 per 1M characters
- **WebSocket**: ~$1 per 1M messages
- **Estimated cost**: ~$0.10 per 5-minute conversation

### **Error Handling**
- **Network issues**: Automatic reconnection
- **Audio failures**: Fallback to text input
- **Transcription errors**: Show "Didn't catch that" message
- **Timeout handling**: 30-second max recording

---

**Status**: Specification complete ✅
**Complexity**: High (real-time streaming)
**Timeline**: 2-3 weeks for full implementation
**Priority**: Phase 2 (after core chat is working)
