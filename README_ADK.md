# EcoMatrix ADK Agent Framework

A sophisticated voice agent framework built with FastAPI and Exotel integration, featuring bidirectional streaming, Gemini 2.0 Flash AI, and location-based services.

## 🚀 Features

- **Bidirectional Streaming**: Real-time voice conversations with Exotel WebSocket integration
- **AI-Powered Agent**: Uses Gemini 2.0 Flash for natural conversation handling
- **Location Services**: Intelligent location detection and nearby business recommendations
- **Exotel Integration**: Complete passthru webhook handling and stream management
- **Conversational Interface**: Natural, friendly voice interactions
- **Scalable Architecture**: Built with FastAPI for high performance

## 🏗️ Architecture

```
ecomatrix/
├── main.py                 # FastAPI application with WebSocket server
├── config.py              # Configuration management
├── agents/
│   ├── agents.py          # Main agent implementation
│   └── prompt.py          # Prompt management and templates
├── tools/
│   └── map.py             # Location detection and mapping tools
├── requirements.txt       # Python dependencies
└── env_example.txt       # Environment variables template
```

## 🔧 Setup Instructions

### 1. Environment Setup

```bash
# Clone or navigate to the project directory
cd ecomatrix

# Copy environment template
cp env_example.txt .env

# Edit .env with your API keys
nano .env
```

### 2. Required API Keys

Add these to your `.env` file:

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional (for future TTS/STT integration)
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt
```

### 4. Run the Server

```bash
# Start the FastAPI server
python main.py

# Or use uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 🌐 API Endpoints

### WebSocket Endpoint
- **URL**: `ws://your-server:8000/media`
- **Purpose**: Handles Exotel media streaming
- **Protocol**: WebSocket with JSON message format

### Passthru Webhook
- **URL**: `http://your-server:8000/passthru`
- **Method**: POST
- **Purpose**: Receives Exotel call metadata and streaming information

### Health Check
- **URL**: `http://your-server:8000/health`
- **Method**: GET
- **Purpose**: Server health monitoring

## 📞 Exotel Integration

### 1. Configure Exotel Applet Flow

In your Exotel dashboard:

1. Create a new Voice Applet flow
2. Add a **Stream Applet** or **Voicebot Applet**
3. Set the WebSocket URL to: `ws://your-server-ip:8000/media`
4. Add a **Passthru Applet** after the streaming applet
5. Set the Passthru URL to: `http://your-server-ip:8000/passthru`
6. Enable "Make Passthru Async" if you don't need real-time flow control

### 2. Stream Configuration

The agent supports both streaming formats:

**Flat Format Parameters:**
- `Stream[StreamSID]` - Unique streaming session ID
- `Stream[Status]` - Status (completed, failed, cancelled)
- `Stream[Duration]` - Stream duration in seconds
- `Stream[StreamUrl]` - WebSocket URL for streaming
- `Stream[RecordingUrl]` - URL to recording (if enabled)
- `Stream[DisconnectedBy]` - Who disconnected (user, bot, NA)

**JSON Format:**
```json
{
  "StreamSID": "abc123...",
  "Status": "completed",
  "Duration": "28",
  "StreamUrl": "ws://your-server:8000/media",
  "DisconnectedBy": "user"
}
```

## 🎯 Agent Capabilities

### Location Services
The agent can help users find:
- Coffee shops and cafes
- Hardware stores
- Bookstores
- Tech stores
- Residential properties
- General shops and services

### Conversation Features
- Natural language understanding
- Context-aware responses
- Location-based recommendations
- Distance calculations
- Conversational clarifications
- Interruption handling

### Example Interactions

**User**: "Hi, can you help me find a coffee shop nearby?"

**Agent**: "I found Coffee Corner C about 200 meters from you. They serve artisan coffee and pastries. Would you like directions or more information?"

**User**: "Where is the nearest hardware store?"

**Agent**: "The closest hardware store is Hammer Shop B, just 300 meters away. They have tools and equipment. Would you like me to give you directions?"

## 🔧 Configuration Options

### Audio Settings
```bash
SAMPLE_RATE=8000          # 8kHz for telephony compatibility
BUFFER_SIZE_MS=200        # 200ms audio chunks
```

### Voice Activity Detection
```bash
VAD_THRESHOLD=0.5         # Speech detection sensitivity
PREFIX_PADDING_MS=300     # Pre-speech padding
SILENCE_DURATION_MS=500   # Silence before response
```

### Location Service
```bash
DEFAULT_LAT=40.7128       # Service area center latitude
DEFAULT_LNG=-74.0060      # Service area center longitude
BOUNDS_NORTH=40.7228      # Northern boundary
BOUNDS_SOUTH=40.7028      # Southern boundary
BOUNDS_EAST=-73.9960      # Eastern boundary
BOUNDS_WEST=-74.0160      # Western boundary
```

## 🚀 Deployment

### Local Development
```bash
python main.py
```

### Production Deployment

#### Using Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Using systemd service
```ini
[Unit]
Description=EcoMatrix ADK Agent
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/ecomatrix
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Cloud Deployment

The application is ready for deployment on:
- **AWS**: EC2, ECS, or Lambda
- **Google Cloud**: Compute Engine or Cloud Run
- **Azure**: App Service or Container Instances
- **DigitalOcean**: Droplets or App Platform

## 📊 Monitoring and Logging

The application provides comprehensive logging:

```bash
# View logs in real-time
tail -f application.log

# Check specific events
grep "EXOTEL" application.log
grep "GEMINI" application.log
grep "ERROR" application.log
```

### Key Log Events
- `📞 NEW CALL` - Incoming Exotel connection
- `🎤 User said` - Transcribed user input
- `🗣️ Agent responded` - AI-generated response
- `📥 PASSTHRU RECEIVED` - Webhook data
- `❌ ERROR` - Error conditions

## 🔐 Security Considerations

1. **API Keys**: Store in environment variables, never in code
2. **HTTPS**: Use SSL/TLS for production deployments
3. **Firewall**: Restrict access to necessary ports only
4. **Rate Limiting**: Implement rate limiting for production use
5. **Input Validation**: All inputs are validated and sanitized

## 🛠️ Development

### Adding New Location Types
Edit `config.py` to add new locations:

```python
LOCATIONS = [
    {
        "id": 9,
        "name": "New Store",
        "type": "shop",
        "lat": 40.7150,
        "lng": -74.0100,
        "description": "Description of the new store"
    }
]
```

### Customizing Agent Responses
Edit `agents/prompt.py` to modify conversation templates:

```python
def get_greeting(self) -> str:
    return "Your custom greeting message"
```

### Adding New Tools
Create new tools in the `tools/` directory following the pattern in `map.py`.

## 📞 Support

For issues or questions:
1. Check the logs for error details
2. Verify API keys and configuration
3. Test with curl commands
4. Review Exotel applet configuration

## 🔄 Updates and Maintenance

Regular maintenance tasks:
1. Update dependencies: `pip install -r requirements.txt --upgrade`
2. Monitor API usage and rate limits
3. Review and rotate API keys periodically
4. Update location data as needed
5. Monitor server resources and performance

---

**Ready to deploy!** 🚀

Your EcoMatrix ADK Agent Framework is now ready for production use with Exotel's bidirectional streaming platform.

