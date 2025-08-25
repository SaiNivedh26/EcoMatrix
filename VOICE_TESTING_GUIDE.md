# 🎤 Voice Testing Guide for EcoMatrix ADK Agent

This guide will help you test your voice agent locally before connecting it to Exotel.

## 🚀 Quick Start

### 1. Setup Audio Dependencies

```bash
# Install audio system dependencies
./setup_audio.sh

# Or install manually:
sudo apt-get install portaudio19-dev python3-pyaudio espeak flac
pip install pyaudio speechrecognition pyttsx3
```

### 2. Start the EcoMatrix Server

```bash
# Make sure your .env file has GEMINI_API_KEY
python main.py
```

You should see:
```
🚀 Starting EcoMatrix ADK Agent Framework
🔗 WebSocket endpoint: ws://0.0.0.0:8000/media
📥 Passthru endpoint: http://0.0.0.0:8000/passthru
```

### 3. Test with Voice

Choose one of the voice testing options:

#### Option A: Simple Command-Line Interface
```bash
python simple_voice_test.py
```

#### Option B: GUI Interface
```bash
python local_voice_client.py
```

## 🎯 Testing Options

### 1. Simple Voice Test (`simple_voice_test.py`)

**Features:**
- ✅ Command-line interface
- ✅ Real-time speech recognition
- ✅ Text-to-speech responses
- ✅ WebSocket connection to agent
- ✅ No GUI dependencies

**Usage:**
1. Run the script
2. Press Enter to start speaking
3. Say your query (e.g., "Find a coffee shop nearby")
4. Listen to the agent's response
5. Type 'quit' to exit

**Example Session:**
```
🎤 Press Enter to speak (or type message): 
🎤 Listening... Speak now!
🎤 You said: Hi, can you help me find a coffee shop nearby?
📤 Sending to agent: Hi, can you help me find a coffee shop nearby?
🤖 Agent is responding...
🗣️  Agent: I found Coffee Corner C about 200 meters from you. They serve artisan coffee and pastries. Would you like directions?
```

### 2. GUI Voice Client (`local_voice_client.py`)

**Features:**
- ✅ User-friendly GUI interface
- ✅ Hold-to-talk button
- ✅ Text input option
- ✅ Conversation history
- ✅ Connection status display
- ✅ Quick test buttons

**Usage:**
1. Run the script to open the GUI
2. Click "Connect to Agent"
3. Hold "Hold to Talk" button and speak
4. Or type a message and press Enter
5. View conversation in the text area

## 🧪 Test Scenarios

### Location Queries
Test these voice commands:

1. **Coffee Shops:**
   - "Hi, can you help me find a coffee shop nearby?"
   - "Where's the nearest cafe?"
   - "I need coffee, what's around here?"

2. **Hardware Stores:**
   - "Where is the nearest hardware store?"
   - "I need tools, where can I go?"
   - "Find me a place to buy a hammer"

3. **Bookstores:**
   - "I'm looking for a bookstore in the area"
   - "Where can I buy books nearby?"
   - "Find me a place with magazines"

4. **General Queries:**
   - "What shops are near me?"
   - "Can you help me find something?"
   - "Show me nearby businesses"

### Expected Agent Responses

The agent should respond conversationally with:
- Location names and distances
- Brief descriptions of places
- Offers for more information
- Natural, friendly tone

**Example Good Response:**
> "I found Coffee Corner C about 200 meters from you. They serve artisan coffee and pastries. Would you like directions or more information?"

## 🔧 Troubleshooting

### Audio Issues

**Problem:** Microphone not working
```bash
# Test microphone access
python -c "import speech_recognition as sr; print('Mic test:', sr.Microphone.list_microphone_names())"
```

**Problem:** No audio output
```bash
# Test speakers/TTS
python -c "import pyttsx3; engine = pyttsx3.init(); engine.say('Test'); engine.runAndWait()"
```

**Problem:** Permission denied for audio
```bash
# Add user to audio group (Linux)
sudo usermod -a -G audio $USER
# Then logout and login again
```

### Connection Issues

**Problem:** Can't connect to WebSocket
- ✅ Make sure the server is running (`python main.py`)
- ✅ Check if port 8000 is available
- ✅ Verify no firewall blocking localhost:8000

**Problem:** Agent not responding
- ✅ Check server logs for errors
- ✅ Verify GEMINI_API_KEY in .env file
- ✅ Check internet connection for Gemini API

### Speech Recognition Issues

**Problem:** "Could not understand speech"
- 🎤 Speak clearly and not too fast
- 🎤 Reduce background noise
- 🎤 Check microphone volume levels
- 🎤 Try typing the message instead

**Problem:** Recognition timeout
- ⏱️ Start speaking immediately after "Listening..."
- ⏱️ Keep sentences reasonably short
- ⏱️ Avoid long pauses while speaking

## 📊 Monitoring and Logs

### Server Logs
Watch the server logs while testing:
```bash
# In the server terminal, you'll see:
📞 NEW CALL from Exotel: ('127.0.0.1', 54321)
🆔 STREAM ID: simple_test_1234567890
🎯 EVENT: 'connected' for simple_test_1234567890
🎤 User said: Hi, can you help me find a coffee shop nearby?
🗣️ Agent responded: I found Coffee Corner C about 200 meters...
```

### Client Logs
The voice clients also provide detailed logging:
```bash
# Enable debug logging if needed
export PYTHONPATH=.
python -c "import logging; logging.basicConfig(level=logging.DEBUG)"
python simple_voice_test.py
```

## 🚀 Next Steps: Exotel Integration

Once local testing works well:

1. **Deploy Server:**
   ```bash
   # Deploy to a server with public IP
   # Update SERVER_HOST in .env to 0.0.0.0
   # Ensure port 8000 is accessible from internet
   ```

2. **Configure Exotel:**
   - WebSocket URL: `ws://your-server-ip:8000/media`
   - Passthru URL: `http://your-server-ip:8000/passthru`

3. **Test with Real Calls:**
   - Call your Exotel number
   - Verify audio streaming works
   - Check passthru webhook receives data

## 📞 Production Considerations

### Audio Quality
- Use proper TTS service (Google Cloud TTS, Azure Speech, etc.)
- Implement proper STT service (Google Speech-to-Text, Whisper, etc.)
- Add noise cancellation and audio enhancement

### Performance
- Add connection pooling
- Implement proper error handling
- Add rate limiting and throttling
- Monitor memory usage during long calls

### Security
- Use HTTPS/WSS in production
- Implement proper authentication
- Add input validation and sanitization
- Monitor for abuse and unusual patterns

---

## 🎉 Happy Testing!

Your EcoMatrix voice agent is now ready for local testing. Start with the simple command-line interface, then move to the GUI for more advanced testing. Once everything works locally, you'll be ready to integrate with Exotel for real phone calls! 🚀

