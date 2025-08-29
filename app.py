import os
import json
import math
import random
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import folium
import base64
import io
from google import genai
from google.genai import types
import pyttsx3
import speech_recognition as sr
import threading
from datetime import datetime
from dotenv import load_dotenv
import sys
import uuid
from werkzeug.utils import secure_filename

# Add caller-agent to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'caller-agent'))

try:
    from speech_to_text import SpeechToTextService
    from text_to_speech import TextToSpeechService
except ImportError as e:
    print(f"Warning: Could not import speech services: {e}")
    SpeechToTextService = None
    TextToSpeechService = None

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize TTS engine with error handling
tts_engine = None
try:
    tts_engine = pyttsx3.init()
    tts_engine.setProperty('rate', 150)
    tts_engine.setProperty('volume', 0.9)
    print("TTS engine initialized successfully")
except Exception as e:
    print(f"Warning: TTS engine initialization failed: {e}")
    print("Voice output will be disabled")

# Initialize SarvamAI speech services
stt_service = None
tts_service = None
try:
    if SpeechToTextService and TextToSpeechService:
        stt_service = SpeechToTextService()
        tts_service = TextToSpeechService()
        print("SarvamAI speech services initialized successfully")
    else:
        print("Warning: SarvamAI speech services not available")
except Exception as e:
    print(f"Warning: SarvamAI speech services initialization failed: {e}")

# Configure upload folder for audio files
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'flac', 'm4a', 'ogg', 'webm'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Fixed area coordinates (example: downtown area)
FIXED_AREA = {
    "center": {"lat": 40.7128, "lng": -74.0060},  # New York City center
    "bounds": {
        "north": 40.7228,
        "south": 40.7028,
        "east": -73.9960,
        "west": -74.0160
    }
}

# Predefined locations in the fixed area
LOCATIONS = [
    {"id": 1, "name": "Butter Shop A", "type": "shop", "lat": 40.7140, "lng": -74.0070, "description": "Fresh dairy and butter products"},
    {"id": 2, "name": "Hammer Shop B", "type": "shop", "lat": 40.7160, "lng": -74.0050, "description": "Hardware tools and equipment"},
    {"id": 3, "name": "House Alpha", "type": "house", "lat": 40.7120, "lng": -74.0080, "description": "Residential building with modern amenities"},
    {"id": 4, "name": "House Beta", "type": "house", "lat": 40.7180, "lng": -74.0040, "description": "Cozy family home"},
    {"id": 5, "name": "Coffee Corner C", "type": "shop", "lat": 40.7100, "lng": -74.0100, "description": "Artisan coffee and pastries"},
    {"id": 6, "name": "Book Haven D", "type": "shop", "lat": 40.7200, "lng": -74.0020, "description": "Books, magazines, and stationery"},
    {"id": 7, "name": "House Gamma", "type": "house", "lat": 40.7150, "lng": -74.0110, "description": "Historic townhouse"},
    {"id": 8, "name": "Tech Store E", "type": "shop", "lat": 40.7190, "lng": -74.0090, "description": "Electronics and gadgets"}
]

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def calculate_distance(lat1, lng1, lat2, lng2):
    """Calculate distance between two points using Haversine formula"""
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

def get_gemini_analysis(user_location, nearby_locations, query):
    """Get intelligent analysis from Gemini AI"""
    try:
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        
        location_data = json.dumps({
            "user_location": user_location,
            "nearby_locations": nearby_locations,
            "query": query
        }, indent=2)
        
        prompt = f"""
        Analyze the following location data and provide helpful insights:
        
        {location_data}
        
        Please provide:
        1. A summary of the nearest locations
        2. Recommendations based on the user's query
        3. Any additional helpful information about the area
        
        Keep the response conversational and helpful.
        """
        
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            ),
        ]
        
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=contents,
        )
        
        return response.text
    except Exception as e:
        return f"AI analysis unavailable: {str(e)}"

def speak_text(text):
    """Convert text to speech"""
    if tts_engine is None:
        print("TTS not available - would speak:", text)
        return
    
    try:
        tts_engine.say(text)
        tts_engine.runAndWait()
    except Exception as e:
        print(f"TTS Error: {e}")

def listen_for_speech():
    """Convert speech to text"""
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    
    try:
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            print("Listening...")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
        
        text = recognizer.recognize_google(audio)
        return text
    except sr.WaitTimeoutError:
        return "Listening timeout"
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError as e:
        return f"Speech recognition error: {e}"

@app.route('/api/speech-to-text', methods=['POST'])
def speech_to_text():
    """Convert uploaded audio file to text using SarvamAI"""
    if stt_service is None:
        return jsonify({"error": "Speech-to-text service not available"}), 500
    
    # Check if file was uploaded
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    
    file = request.files['audio']
    
    # Check if file is selected
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if file and allowed_file(file.filename):
        try:
            # Save uploaded file temporarily
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            
            # Process with speech-to-text service
            result = stt_service.transcribe_audio(filepath)
            
            # Clean up uploaded file
            try:
                os.remove(filepath)
            except:
                pass  # Ignore cleanup errors
            
            if result["success"]:
                return jsonify({
                    "success": True,
                    "request_id": result["request_id"],
                    "transcript": result["transcript"],
                    "language_code": result["language_code"],
                    "diarized_transcript": result["diarized_transcript"],
                    "timestamp": datetime.now().isoformat()
                })
            else:
                return jsonify({
                    "success": False,
                    "error": result["error"]
                }), 500
                
        except Exception as e:
            # Clean up uploaded file in case of error
            try:
                if 'filepath' in locals():
                    os.remove(filepath)
            except:
                pass
            return jsonify({"error": f"Processing failed: {str(e)}"}), 500
    
    return jsonify({"error": "Invalid file type. Allowed: wav, mp3, flac, m4a, ogg, webm"}), 400

@app.route('/api/text-to-speech', methods=['POST'])
def text_to_speech():
    """Convert text to speech using SarvamAI"""
    if tts_service is None:
        return jsonify({"error": "Text-to-speech service not available"}), 500
    
    data = request.json
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    
    text = data.get('text', '').strip()
    language_code = data.get('language_code', 'ta-IN')
    speaker = data.get('speaker', 'vidya')
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    try:
        # Convert text to speech
        result = tts_service.convert_text_to_speech(
            text=text,
            language_code=language_code,
            speaker=speaker
        )
        
        if result["success"]:
            return jsonify({
                "success": True,
                "file_path": result["file_path"],
                "filename": result["filename"],
                "text": result["text"],
                "language_code": result["language_code"],
                "speaker": result["speaker"],
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "success": False,
                "error": result["error"]
            }), 500
            
    except Exception as e:
        return jsonify({"error": f"TTS processing failed: {str(e)}"}), 500

@app.route('/api/speech-pipeline', methods=['POST'])
def speech_pipeline():
    """Complete speech-to-text then text-to-speech pipeline"""
    if stt_service is None or tts_service is None:
        return jsonify({"error": "Speech services not available"}), 500
    
    # Check if file was uploaded
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    
    file = request.files['audio']
    
    # Optional parameters
    response_text = request.form.get('response_text', '')
    target_language = request.form.get('target_language', '')
    speaker = request.form.get('speaker', 'vidya')
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if file and allowed_file(file.filename):
        try:
            # Step 1: Speech to Text
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            
            # Process with speech-to-text service
            stt_result = stt_service.transcribe_audio(filepath)
            
            # Clean up uploaded file
            try:
                os.remove(filepath)
            except:
                pass
            
            if not stt_result["success"]:
                return jsonify({
                    "success": False,
                    "step": "speech_to_text",
                    "error": stt_result["error"]
                }), 500
            
            # Step 2: Determine response text and language
            if response_text:
                # Use provided response text
                text_to_convert = response_text
                tts_language = target_language or stt_result["language_code"] or 'ta-IN'
            else:
                # Echo back the transcript (for testing)
                text_to_convert = stt_result["transcript"]
                tts_language = stt_result["language_code"] or 'ta-IN'
            
            # Step 3: Text to Speech
            tts_result = tts_service.convert_text_to_speech(
                text=text_to_convert,
                language_code=tts_language,
                speaker=speaker
            )
            
            if not tts_result["success"]:
                return jsonify({
                    "success": False,
                    "step": "text_to_speech",
                    "error": tts_result["error"],
                    "stt_result": {
                        "transcript": stt_result["transcript"],
                        "language_code": stt_result["language_code"]
                    }
                }), 500
            
            # Return complete pipeline result
            return jsonify({
                "success": True,
                "stt_result": {
                    "request_id": stt_result["request_id"],
                    "transcript": stt_result["transcript"],
                    "language_code": stt_result["language_code"],
                    "diarized_transcript": stt_result["diarized_transcript"]
                },
                "tts_result": {
                    "file_path": tts_result["file_path"],
                    "filename": tts_result["filename"],
                    "text": tts_result["text"],
                    "language_code": tts_result["language_code"],
                    "speaker": tts_result["speaker"]
                },
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            # Clean up uploaded file in case of error
            try:
                if 'filepath' in locals():
                    os.remove(filepath)
            except:
                pass
            return jsonify({"error": f"Pipeline processing failed: {str(e)}"}), 500
    
    return jsonify({"error": "Invalid file type. Allowed: wav, mp3, flac, m4a, ogg, webm"}), 400

@app.route('/api/speech-with-location', methods=['POST'])
def speech_with_location():
    """
    Complete speech pipeline: STT -> Gemini (with location context) -> TTS
    This matches your workflow: cal_r.py -> Gemini processing -> t.py
    """
    if stt_service is None or tts_service is None:
        return jsonify({"error": "Speech services not available"}), 500
    
    # Check if file was uploaded
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    
    file = request.files['audio']
    
    # Get location parameters
    user_lat = request.form.get('lat', type=float)
    user_lng = request.form.get('lng', type=float)
    speaker = request.form.get('speaker', 'vidya')
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not file or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Allowed: wav, mp3, flac, m4a, ogg, webm"}), 400
    
    try:
        # Step 1: Speech to Text (cal_r.py equivalent)
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        # Process with speech-to-text service
        stt_result = stt_service.transcribe_audio(filepath)
        
        # Clean up uploaded file
        try:
            os.remove(filepath)
        except:
            pass
        
        if not stt_result["success"]:
            return jsonify({
                "success": False,
                "step": "speech_to_text",
                "error": stt_result["error"]
            }), 500
        
        # Extract the key information (like your cal_r.py output)
        request_id = stt_result["request_id"]
        transcript = stt_result["transcript"]
        language_code = stt_result["language_code"]
        diarized_transcript = stt_result["diarized_transcript"]
        
        print(f"STT Results - Language: {language_code}, Transcript: {transcript}")
        print(f"Cal_r.py equivalent output: request_id='{request_id}' transcript='{transcript}' language_code='{language_code}' diarized_transcript={diarized_transcript}")
        
        # Step 2: Get location context if coordinates provided
        location_context = ""
        nearest_locations = []
        
        if user_lat and user_lng:
            # Check if user location is within service area
            if is_within_bounds(user_lat, user_lng):
                # Calculate distances to all locations
                locations_with_distance = []
                for location in LOCATIONS:
                    distance = calculate_distance(user_lat, user_lng, location['lat'], location['lng'])
                    location_copy = location.copy()
                    location_copy['distance'] = round(distance, 3)
                    locations_with_distance.append(location_copy)
                
                # Sort by distance and get top 3
                locations_with_distance.sort(key=lambda x: x['distance'])
                nearest_locations = locations_with_distance[:3]
                
                # Create location context for Gemini
                location_context = f"\nUser Location: Lat {user_lat}, Lng {user_lng}\n"
                location_context += "Nearby locations:\n"
                for loc in nearest_locations:
                    location_context += f"- {loc['name']} ({loc['type']}) - {loc['distance']}km away: {loc['description']}\n"
        
        # Step 3: Process with Gemini AI
        gemini_response = get_gemini_response_for_speech(transcript, language_code, location_context)
        
        if not gemini_response:
            # Fallback response
            gemini_response = f"I heard you say: {transcript}. How can I help you with location services?"
        
        # Step 4: Text to Speech (t.py equivalent)
        # Use the detected language from STT for TTS
        print(f"Using language_code from STT for TTS: {language_code}")
        tts_result = tts_service.convert_text_to_speech(
            text=gemini_response,
            language_code=language_code,  # This comes from STT result
            speaker=speaker
        )
        
        if not tts_result["success"]:
            return jsonify({
                "success": False,
                "step": "text_to_speech",
                "error": tts_result["error"],
                "stt_result": {
                    "request_id": request_id,
                    "transcript": transcript,
                    "language_code": language_code
                },
                "gemini_response": gemini_response
            }), 500
        
        # Return complete pipeline result
        return jsonify({
            "success": True,
            "cal_r_output": f"request_id='{request_id}' transcript='{transcript}' language_code='{language_code}' diarized_transcript={diarized_transcript}",
            "stt_result": {
                "request_id": request_id,
                "transcript": transcript,
                "language_code": language_code,
                "diarized_transcript": diarized_transcript
            },
            "location_context": {
                "user_location": {"lat": user_lat, "lng": user_lng} if user_lat and user_lng else None,
                "nearest_locations": nearest_locations,
                "within_service_area": is_within_bounds(user_lat, user_lng) if user_lat and user_lng else None
            },
            "gemini_response": gemini_response,
            "tts_result": {
                "file_path": tts_result["file_path"],
                "filename": tts_result["filename"],
                "text": tts_result["text"],
                "language_code": tts_result["language_code"],
                "speaker": tts_result["speaker"]
            },
            "audio_url": f"/api/audio/{tts_result['filename']}",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        # Clean up uploaded file in case of error
        try:
            if 'filepath' in locals():
                os.remove(filepath)
        except:
            pass
        return jsonify({"error": f"Pipeline processing failed: {str(e)}"}), 500

def get_gemini_response_for_speech(transcript, language_code, location_context=""):
    """Generate response using Gemini AI with location context"""
    try:
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        
        # Map language codes to language names for better Gemini understanding
        language_map = {
            'en-IN': 'English',
            'hi-IN': 'Hindi (हिंदी)',
            'bn-IN': 'Bengali (বাংলা)',
            'ta-IN': 'Tamil (தமிழ்)',
            'te-IN': 'Telugu (తెలుగు)',
            'kn-IN': 'Kannada (ಕನ್ನಡ)',
            'ml-IN': 'Malayalam (മലയാളം)',
            'mr-IN': 'Marathi (मराठी)',
            'gu-IN': 'Gujarati (ગુજરાતી)',
            'pa-IN': 'Punjabi (ਪੰਜਾਬੀ)',
            'or-IN': 'Odia (ଓଡ଼ିଆ)'
        }
        
        language_name = language_map.get(language_code, f'the language with code {language_code}')
        
        # Create a prompt that incorporates the speech input and location context
        prompt = f"""
        You are a helpful location-based assistant. A user has spoken to you in {language_name} and you need to respond helpfully.
        
        User's speech transcript: "{transcript}"
        Detected language: {language_name} ({language_code})
        
        {location_context}
        
        IMPORTANT: You MUST respond in {language_name} ({language_code}) - the same language the user spoke in.
        
        Please provide a helpful response that:
        1. Acknowledges what the user said in {language_name}
        2. Provides relevant information based on their location (if available)
        3. Offers assistance with location-based services
        4. Keep the response conversational and concise (suitable for speech)
        5. Use natural, native expressions in {language_name}
        
        If the user is asking about locations, directions, or nearby places, use the location context provided.
        
        Remember: Your entire response must be in {language_name} ({language_code}).
        """
        
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            ),
        ]
        
        print(f"Sending Gemini prompt for language {language_code} ({language_name})")
        
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=contents,
        )
        
        gemini_text = response.text.strip()
        print(f"Gemini response in {language_code}: {gemini_text}")
        
        return gemini_text
        
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        # Fallback response in the detected language
        if language_code == 'hi-IN':
            return f"मैंने सुना कि आपने कहा: {transcript}. मैं आपकी कैसे सहायता कर सकता हूं?"
        elif language_code == 'ta-IN':
            return f"நீங்கள் சொன்னதை நான் கேட்டேன்: {transcript}. நான் உங்களுக்கு எப்படி உதவ முடியும்?"
        elif language_code == 'ml-IN':
            return f"നിങ്ങൾ പറഞ്ഞത് ഞാൻ കേട്ടു: {transcript}. എനിക്ക് നിങ്ങളെ എങ്ങനെ സഹായിക്കാൻ കഴിയും?"
        elif language_code == 'te-IN':
            return f"మీరు చెప్పింది నేను విన్నాను: {transcript}. నేను మీకు ఎలా సహాయపడగలను?"
        elif language_code == 'kn-IN':
            return f"ನೀವು ಹೇಳಿದ್ದನ್ನು ನಾನು ಕೇಳಿದೆ: {transcript}. ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?"
        elif language_code == 'bn-IN':
            return f"আপনি যা বলেছেন তা আমি শুনেছি: {transcript}. আমি কীভাবে আপনাকে সাহায্য করতে পারি?"
        elif language_code == 'gu-IN':
            return f"તમે જે કહ્યું તે મેં સાંભળ્યું: {transcript}. હું તમારી કેવી રીતે મદદ કરી શકું?"
        elif language_code == 'mr-IN':
            return f"तुम्ही जे सांगितले ते मी ऐकले: {transcript}. मी तुम्हाला कशी मदत करू शकतो?"
        elif language_code == 'pa-IN':
            return f"ਤੁਸੀਂ ਜੋ ਕਿਹਾ ਮੈਂ ਸੁਣਿਆ: {transcript}. ਮੈਂ ਤੁਹਾਡੀ ਕਿਵੇਂ ਮਦਦ ਕਰ ਸਕਦਾ ਹਾਂ?"
        elif language_code == 'or-IN':
            return f"ଆପଣ ଯାହା କହିଲେ ମୁଁ ଶୁଣିଲି: {transcript}. ମୁଁ ଆପଣଙ୍କୁ କିପରି ସାହାଯ୍ୟ କରିପାରିବି?"
        else:
            return f"I heard you say: {transcript}. How can I help you today?"

@app.route('/api/audio/<path:filename>')
def serve_audio(filename):
    """Serve generated audio files"""
    try:
        audio_dir = os.path.join('caller-agent', 'audio_output')
        return send_file(os.path.join(audio_dir, filename))
    except Exception as e:
        return jsonify({"error": f"File not found: {str(e)}"}), 404

@app.route('/api/speech-services/info')
def speech_services_info():
    """Get information about available speech services"""
    if tts_service is None:
        return jsonify({
            "available": False,
            "error": "Speech services not initialized"
        })
    
    return jsonify({
        "available": True,
        "supported_languages": tts_service.get_supported_languages(),
        "supported_speakers": tts_service.get_supported_speakers(),
        "allowed_audio_formats": list(ALLOWED_EXTENSIONS)
    })

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/map')
def get_map():
    """Generate and return the map with all locations"""
    # Create a folium map centered on the fixed area
    m = folium.Map(
        location=[FIXED_AREA["center"]["lat"], FIXED_AREA["center"]["lng"]],
        zoom_start=15,
        tiles='OpenStreetMap'
    )
    
    # Add markers for all locations
    for location in LOCATIONS:
        icon_color = 'red' if location['type'] == 'house' else 'blue'
        folium.Marker(
            [location['lat'], location['lng']],
            popup=f"<b>{location['name']}</b><br>{location['description']}",
            tooltip=location['name'],
            icon=folium.Icon(color=icon_color, icon='home' if location['type'] == 'house' else 'shopping-cart')
        ).add_to(m)
    
    # Add area boundary with better visibility
    folium.Rectangle(
        bounds=[
            [FIXED_AREA["bounds"]["south"], FIXED_AREA["bounds"]["west"]],
            [FIXED_AREA["bounds"]["north"], FIXED_AREA["bounds"]["east"]]
        ],
        color="red",
        fill=True,
        fillColor="red",
        fillOpacity=0.1,
        weight=3,
        popup="<b>Fixed Area Boundary</b><br>All locations and random points are within this area",
        tooltip="EcoMatrix Service Area"
    ).add_to(m)
    
    # Add center marker
    folium.Marker(
        [FIXED_AREA["center"]["lat"], FIXED_AREA["center"]["lng"]],
        popup="<b>Area Center</b><br>Fixed service area center point",
        tooltip="Service Area Center",
        icon=folium.Icon(color='green', icon='star')
    ).add_to(m)
    
    # Save map to string
    map_html = m._repr_html_()
    return map_html

@app.route('/api/locations')
def get_locations():
    """Get all locations"""
    return jsonify(LOCATIONS)

def is_within_bounds(lat, lng):
    """Check if coordinates are within the fixed area bounds"""
    return (FIXED_AREA["bounds"]["south"] <= lat <= FIXED_AREA["bounds"]["north"] and
            FIXED_AREA["bounds"]["west"] <= lng <= FIXED_AREA["bounds"]["east"])

@app.route('/api/find-nearby', methods=['POST'])
def find_nearby():
    """Find nearby locations based on user coordinates"""
    data = request.json
    user_lat = data.get('lat')
    user_lng = data.get('lng')
    query = data.get('query', '')
    
    if not user_lat or not user_lng:
        return jsonify({"error": "Latitude and longitude required"}), 400
    
    # Check if user location is within service area
    if not is_within_bounds(user_lat, user_lng):
        return jsonify({
            "error": "Location is outside the service area",
            "service_area": FIXED_AREA["bounds"],
            "user_location": {"lat": user_lat, "lng": user_lng}
        }), 400
    
    # Calculate distances to all locations (all locations are already within bounds)
    locations_with_distance = []
    for location in LOCATIONS:
        distance = calculate_distance(user_lat, user_lng, location['lat'], location['lng'])
        location_copy = location.copy()
        location_copy['distance'] = round(distance, 3)
        locations_with_distance.append(location_copy)
    
    # Sort by distance
    locations_with_distance.sort(key=lambda x: x['distance'])
    
    # Get top 5 nearest locations
    nearest_locations = locations_with_distance[:5]
    
    response = {
        "user_location": {"lat": user_lat, "lng": user_lng},
        "nearest_locations": nearest_locations,
        "service_area": FIXED_AREA["bounds"],
        "timestamp": datetime.now().isoformat()
    }
    
    return jsonify(response)

@app.route('/api/voice/listen', methods=['POST'])
def voice_listen():
    """Listen to voice input and convert to text"""
    try:
        text = listen_for_speech()
        return jsonify({"text": text, "success": True})
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/voice/speak', methods=['POST'])
def voice_speak():
    """Convert text to speech"""
    data = request.json
    text = data.get('text', '')
    
    if not text:
        return jsonify({"error": "Text required"}), 400
    
    if tts_engine is None:
        return jsonify({"error": "TTS engine not available", "success": False}), 500
    
    try:
        # Run TTS in a separate thread to avoid blocking
        thread = threading.Thread(target=speak_text, args=(text,))
        thread.start()
        return jsonify({"success": True, "message": "Speaking..."})
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/test')
def test_endpoint():
    """Simple test endpoint to verify server is working"""
    return jsonify({
        "status": "ok",
        "message": "Server is running",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/random-location')
def get_random_location():
    """Get a random location from the fixed area for testing"""
    try:
        # Generate random coordinates within the fixed area bounds
        lat = random.uniform(FIXED_AREA["bounds"]["south"], FIXED_AREA["bounds"]["north"])
        lng = random.uniform(FIXED_AREA["bounds"]["west"], FIXED_AREA["bounds"]["east"])
        
        # Verify the generated point is within bounds (should always be true)
        if not is_within_bounds(lat, lng):
            # Fallback to center if somehow out of bounds
            lat = FIXED_AREA["center"]["lat"]
            lng = FIXED_AREA["center"]["lng"]
        
        print(f"Generated random point: lat={lat}, lng={lng}")
        
        return jsonify({
            "lat": lat, 
            "lng": lng,
            "message": "Random location within service area",
            "service_area": FIXED_AREA["bounds"],
            "is_within_bounds": is_within_bounds(lat, lng)
        })
    except Exception as e:
        print(f"Error in get_random_location: {str(e)}")
        return jsonify({"error": f"Failed to generate random location: {str(e)}"}), 500

@app.route('/api/map-with-point')
def get_map_with_point():
    """Generate map with a specific point marked (for random location display)"""
    data = request.args
    point_lat = data.get('lat', type=float)
    point_lng = data.get('lng', type=float)
    
    # Create a folium map centered on the fixed area
    m = folium.Map(
        location=[FIXED_AREA["center"]["lat"], FIXED_AREA["center"]["lng"]],
        zoom_start=15,
        tiles='OpenStreetMap'
    )
    
    # Add markers for all locations
    for location in LOCATIONS:
        icon_color = 'red' if location['type'] == 'house' else 'blue'
        folium.Marker(
            [location['lat'], location['lng']],
            popup=f"<b>{location['name']}</b><br>{location['description']}",
            tooltip=location['name'],
            icon=folium.Icon(color=icon_color, icon='home' if location['type'] == 'house' else 'shopping-cart')
        ).add_to(m)
    
    # Add area boundary with better visibility
    folium.Rectangle(
        bounds=[
            [FIXED_AREA["bounds"]["south"], FIXED_AREA["bounds"]["west"]],
            [FIXED_AREA["bounds"]["north"], FIXED_AREA["bounds"]["east"]]
        ],
        color="red",
        fill=True,
        fillColor="red",
        fillOpacity=0.1,
        weight=3,
        popup="<b>Fixed Area Boundary</b><br>All locations and random points are within this area",
        tooltip="EcoMatrix Service Area"
    ).add_to(m)
    
    # Add center marker
    folium.Marker(
        [FIXED_AREA["center"]["lat"], FIXED_AREA["center"]["lng"]],
        popup="<b>Area Center</b><br>Fixed service area center point",
        tooltip="Service Area Center",
        icon=folium.Icon(color='green', icon='star')
    ).add_to(m)
    
    # Add the specific point marker if coordinates are provided
    if point_lat is not None and point_lng is not None:
        # Verify the point is within bounds
        if is_within_bounds(point_lat, point_lng):
            folium.Marker(
                [point_lat, point_lng],
                popup=f"<b>Random Point</b><br>Lat: {point_lat:.6f}<br>Lng: {point_lng:.6f}<br><i>Generated within service area</i>",
                tooltip="Random Point (Within Area)",
                icon=folium.Icon(color='purple', icon='map-marker')
            ).add_to(m)
        else:
            # If point is outside bounds, show it in a different color and add warning
            folium.Marker(
                [point_lat, point_lng],
                popup=f"<b>Point Outside Service Area</b><br>Lat: {point_lat:.6f}<br>Lng: {point_lng:.6f}<br><i style='color: red;'>WARNING: Outside service area!</i>",
                tooltip="Point Outside Service Area",
                icon=folium.Icon(color='orange', icon='exclamation-triangle')
            ).add_to(m)
    
    # Save map to string
    map_html = m._repr_html_()
    return map_html

if __name__ == '__main__':
    print("Starting EcoMatrix Location Service...")
    print(f"Fixed area center: {FIXED_AREA['center']}")
    print(f"Total locations: {len(LOCATIONS)}")
    app.run(debug=True, host='0.0.0.0', port=5000)
