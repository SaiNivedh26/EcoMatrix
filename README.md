# EcoMatrix
## Application made as part of ICSRF 2025 Hackathon final round

<br>

<img width="729" height="895" alt="image" src="https://github.com/user-attachments/assets/ed1f69cd-aee5-40ae-854f-68b13e35afdb" />

# EcoMatrix - Smart Location Finder

A Flask-based backend application that provides intelligent location analysis with mapping, voice interaction, and AI-powered insights using Gemini 2.0 Flash.

## Features

- 🗺️ **Interactive Map**: Leafmap-powered visualization with predefined locations
- 📍 **Location Analysis**: Find nearby locations with distance calculations
- 🤖 **AI Insights**: Gemini 2.0 Flash integration for intelligent location analysis
- 🎤 **Voice Input**: Speech-to-Text for hands-free queries
- 🔊 **Voice Output**: Text-to-Speech for audio responses
- 🏠 **Predefined Locations**: Fixed area with houses and shops (Butter Shop, Hammer Shop, etc.)

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Environment**:
   ```bash
   cp env_example.txt .env
   # Edit .env and add your GEMINI_API_KEY
   ```

3. **Run the Application**:
   ```bash
   python app.py
   ```

4. **Access the App**:
   Open your browser and go to `http://localhost:5000`

## API Endpoints

- `GET /` - Main web interface
- `GET /api/map` - Get interactive map HTML
- `GET /api/locations` - Get all predefined locations
- `POST /api/find-nearby` - Find nearby locations (requires lat, lng, optional query)
- `POST /api/voice/listen` - Voice input (Speech-to-Text)
- `POST /api/voice/speak` - Voice output (Text-to-Speech)
- `GET /api/random-location` - Get random coordinates within fixed area

## Usage Examples

### Find Nearby Locations
```bash
curl -X POST http://localhost:5000/api/find-nearby \
  -H "Content-Type: application/json" \
  -d '{"lat": 40.7128, "lng": -74.0060, "query": "looking for shops"}'
```

### Voice Interaction
- Use the microphone button in the web interface for voice input
- Click "Speak Analysis" to hear AI insights

## Configuration

The application uses a fixed area around New York City (configurable in `app.py`):
- Center: 40.7128, -74.0060
- Bounds: Approximately 2km x 2km area
- 8 predefined locations (houses and shops)

## Dependencies

- **Flask**: Web framework
- **Folium**: Map generation
- **Google GenAI**: Gemini 2.0 Flash integration
- **pyttsx3**: Text-to-Speech
- **SpeechRecognition**: Speech-to-Text
- **Flask-CORS**: Cross-origin support

## Troubleshooting

1. **Voice Input Issues**: Ensure microphone permissions are granted
2. **TTS Not Working**: Check audio output settings
3. **Gemini API Errors**: Verify your API key in the .env file
4. **Map Not Loading**: Check internet connection for map tiles

## License

MIT License - feel free to use and modify as needed.
