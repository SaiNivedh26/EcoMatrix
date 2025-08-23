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
    
    # Get AI analysis
    ai_analysis = get_gemini_analysis(
        {"lat": user_lat, "lng": user_lng},
        nearest_locations,
        query
    )
    
    response = {
        "user_location": {"lat": user_lat, "lng": user_lng},
        "nearest_locations": nearest_locations,
        "ai_analysis": ai_analysis,
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
