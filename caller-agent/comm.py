from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
import requests
import json
import uuid
import time
import logging
import urllib.parse
from google import genai
from google.genai import types

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration from environment variables
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID', 'pNInz6obpgDQGcFmaJgB')  # Default to "Rachel" voice
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
BASE_URL = os.getenv('BASE_URL', 'https://c65b-2409-40f4-2054-d890-bb59-d09d-e4ca-6b00.ngrok-free.app')  # Change to your public URL

# Initialize Flask app
app = Flask(__name__)

# Initialize Twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Initialize Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)
gemini_model = "gemini-2.0-flash"  # You can use other models like "gemini-2.0-pro"

# Store conversation histories
conversation_histories = {}

@app.route("/health", methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({"status": "healthy", "message": "Service is running"}), 200

@app.route("/make_call", methods=['POST'])
def initiate_call():
    """API endpoint to start an outbound call"""
    try:
        data = request.get_json()
        
        # Validate request
        if not data:
            return jsonify({"error": "Missing request body"}), 400
        
        phone_number = data.get('phone_number')
        initial_message = data.get('initial_message', "Hello, this is an AI assistant calling to follow up on your project which you took, can you provide some update?")
        
        if not phone_number:
            return jsonify({"error": "Missing required parameter: phone_number"}), 400
            
        # Ensure phone number has international format
        if not phone_number.startswith('+'):
            return jsonify({"error": "Phone number must include country code (e.g., +1...)"}), 400
            
        # Create a call SID to track this conversation
        call_id = str(uuid.uuid4())
        
        # Initialize conversation history for this call
        conversation_histories[call_id] = [
            {"role": "model", "content": "You are a helpful AI voice assistant making a phone call. Keep responses conversational and concise since they'll be spoken aloud. Avoid long explanations or complex formatting."},
            {"role": "model", "content": initial_message}
        ]
        
        # Make the call with Twilio
        encoded_message = urllib.parse.quote(initial_message)

        call = twilio_client.calls.create(
            to=phone_number,
            from_=TWILIO_PHONE_NUMBER,
            url=f"{BASE_URL}/voice?call_id={call_id}&initial_message={encoded_message}",
            status_callback=f"{BASE_URL}/call_status?call_id={call_id}",
            status_callback_method='POST',
            method='GET'
        )
        
        logger.info(f"Initiated call to {phone_number} with SID: {call.sid}")
        
        return jsonify({
            "success": True,
            "message": "Call initiated successfully",
            "call_sid": call.sid,
            "call_id": call_id
        }), 200
        
    except Exception as e:
        logger.error(f"Error initiating call: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/call_status", methods=['POST'])
def call_status():
    """Handle Twilio call status callbacks"""
    call_id = request.args.get('call_id')
    call_status = request.values.get('CallStatus')
    
    logger.info(f"Call status update for {call_id}: {call_status}")
    
    # If the call has completed, log the full conversation
    if call_status in ['completed', 'failed', 'busy', 'no-answer', 'canceled']:
        log_conversation(call_id, call_status)
        
    return '', 204

def log_conversation(call_id, status):
    """Log the complete conversation when a call ends"""
    if call_id in conversation_histories:
        conversation = conversation_histories[call_id]
        
        logger.info(f"=== CALL {call_id} ENDED WITH STATUS: {status} ===")
        logger.info(f"=== COMPLETE CONVERSATION LOG ===")
        
        user_responses = []
        for msg in conversation:
            if msg["role"] == "user":
                user_responses.append(msg["content"])
                timestamp = msg.get("timestamp", "unknown time")
                logger.info(f"USER [{timestamp}]: {msg['content']}")
            else:
                timestamp = msg.get("timestamp", "unknown time")
                logger.info(f"AI [{timestamp}]: {msg['content']}")
        
        # Log a summary of user responses
        logger.info(f"=== USER RESPONSES SUMMARY ===")
        for i, response in enumerate(user_responses):
            logger.info(f"Response {i+1}: {response}")
        
        logger.info(f"=== END OF CONVERSATION LOG ===")
        
        # Optional: You can also store the conversation in a database or send it to another service
        
        # Clean up the conversation history to free memory
        del conversation_histories[call_id]

        
@app.route("/voice", methods=['GET', 'POST'])
def voice_webhook():
    """Handle the initial Twilio voice webhook"""
    call_id = request.args.get('call_id')
    initial_message = request.args.get('initial_message', "Hello, this is an AI assistant calling. How can I help you today?")
    
    logger.info(f"Voice webhook triggered for call_id: {call_id}")
    
    # Create TwiML response
    response = VoiceResponse()
    
    # Add initial greeting with gather
    gather = Gather(
        input='speech',
        action=f'/handle_response?call_id={call_id}',
        language='en-US',
        speechTimeout='auto',
        timeout=3
    )
    
    # Generate TTS for initial message
    audio_url = generate_elevenlabs_tts(initial_message)
    
    if audio_url:
        gather.play(audio_url)
    else:
        # Fallback to basic Twilio TTS
        gather.say(initial_message)
    
    response.append(gather)
    
    # If no input detected, end the call gracefully
    response.say("I didn't hear a response. Thank you for your time. Goodbye.")
    response.hangup()
    
    return str(response)

@app.route("/handle_response", methods=['POST'])
def handle_response():
    """Process user's speech and generate AI response"""
    call_id = request.args.get('call_id')
    user_speech = request.values.get('SpeechResult')
    
    logger.info(f"Received speech from call {call_id}: {user_speech}")
    
    if not user_speech:
        # If no speech detected, end call gracefully
        response = VoiceResponse()
        response.say("I didn't catch that. Thank you for your time. Goodbye.")
        response.hangup()
        
        # Log that no response was received
        if call_id in conversation_histories:
            conversation_histories[call_id].append({"role": "user", "content": "[NO RESPONSE DETECTED]"})
            
        return str(response)
    
    # Update conversation history
    if call_id in conversation_histories:
        # Log the user's response with timestamp
        conversation_histories[call_id].append({
            "role": "user", 
            "content": user_speech,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        
        # Generate AI response
        ai_response = generate_gemini_response(conversation_histories[call_id])
        
        # Add AI response to history with timestamp
        conversation_histories[call_id].append({
            "role": "model", 
            "content": ai_response,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        
        # Create TwiML for response
        response = VoiceResponse()
        gather = Gather(
            input='speech',
            action=f'/handle_response?call_id={call_id}',
            language='en-US',
            speechTimeout='auto',
            timeout=3
        )
        
        # Generate TTS for AI response
        audio_url = generate_elevenlabs_tts(ai_response)
        
        if audio_url:
            gather.play(audio_url)
        else:
            # Fallback to basic Twilio TTS
            gather.say(ai_response)
        
        response.append(gather)
        
        # If no user response after AI speaks, end call gracefully
        response.say("Thank you for the conversation. Goodbye.")
        response.hangup()
        
        return str(response)
    else:
        # If call_id not found in history
        response = VoiceResponse()
        response.say("I'm having trouble with this call. Goodbye.")
        response.hangup()
        return str(response)

def generate_gemini_response(conversation):
    """Generate AI response using Google Gemini"""
    try:
        # Keep conversation history manageable (last 10 messages)
        if len(conversation) > 12:  # Keep system prompt + last 10 exchanges
            conversation = [conversation[0]] + conversation[-11:]
            
        # Convert conversation history to Gemini format
        gemini_contents = []
        
        # Add system message as a model message
        gemini_contents.append(
            types.Content(
                role="model",
                parts=[types.Part.from_text(text="You are a helpful AI voice assistant making a phone call. Keep responses conversational and concise since they'll be spoken aloud. Avoid long explanations or complex formatting.")]
            )
        )
        
        # Add the conversation history
        for i in range(1, len(conversation)):
            msg = conversation[i]
            role = "user" if msg["role"] == "user" else "model"
            gemini_contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=msg["content"])]
                )
            )
            
        # Set up Gemini client
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # Set response configuration
        generate_content_config = types.GenerateContentConfig(
            response_mime_type="text/plain",
            max_output_tokens=150,  # Keep responses concise for voice
            temperature=0.7
        )
        
        # Generate response
        response = client.models.generate_content(
            model=gemini_model,
            contents=gemini_contents,
            config=generate_content_config,
        )
        
        return response.text.strip()
        
    except Exception as e:
        logger.error(f"Error generating Gemini response: {str(e)}")
        return "I'm having trouble processing your request right now. Could you please repeat that?"

def generate_elevenlabs_tts(text):
    """Generate text-to-speech using ElevenLabs API"""
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}/stream"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0,
                "use_speaker_boost": True
            }
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            # Create unique filename
            audio_dir = os.path.join("static", "audio")
            os.makedirs(audio_dir, exist_ok=True)
            
            filename = f"tts_{uuid.uuid4()}.mp3"
            filepath = os.path.join(audio_dir, filename)
            
            with open(filepath, "wb") as f:
                f.write(response.content)
                
            audio_url = f"{BASE_URL}/static/audio/{filename}"
            logger.info(f"Generated TTS audio: {audio_url}")
            return audio_url
        else:
            logger.error(f"ElevenLabs API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error generating TTS: {str(e)}")
        return None

@app.route('/static/audio/<filename>')
def serve_audio(filename):
    """Serve audio files"""
    return app.send_static_file(f"audio/{filename}")

@app.route('/cleanup', methods=['GET'])
def cleanup_audio():
    """Clean up old audio files"""
    try:
        audio_dir = os.path.join("static", "audio")
        if not os.path.exists(audio_dir):
            return jsonify({"message": "Audio directory does not exist"}), 404
            
        count = 0
        current_time = time.time()
        
        for filename in os.listdir(audio_dir):
            if filename.endswith('.mp3'):
                file_path = os.path.join(audio_dir, filename)
                # Delete files older than 1 hour
                if current_time - os.path.getmtime(file_path) > 3600:
                    os.remove(file_path)
                    count += 1
                    
        return jsonify({"message": f"Cleaned up {count} audio files"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Ensure audio directory exists
    os.makedirs(os.path.join("static", "audio"), exist_ok=True)
    app.run(debug=True, host="0.0.0.0", port=5000)
# from flask import Flask, request, jsonify
# import os
# from dotenv import load_dotenv
# from twilio.rest import Client
# from twilio.twiml.voice_response import VoiceResponse, Gather
# import requests
# import json
# import uuid
# import time
# import openai
# import logging
# import urllib.parse  # Add this import at the top of your file

# # Set up logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# # Load environment variables
# load_dotenv()

# # Configuration from environment variables
# TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
# TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
# TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
# ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
# ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID', 'pNInz6obpgDQGcFmaJgB')  # Default to "Rachel" voice
# OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
# BASE_URL = os.getenv('BASE_URL', 'https://c65b-2409-40f4-2054-d890-bb59-d09d-e4ca-6b00.ngrok-free.app')  # Change to your public URL

# # Initialize Flask app
# app = Flask(__name__)

# # Initialize Twilio client
# twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# # Initialize OpenAI client
# openai.api_key = OPENAI_API_KEY

# # Store conversation histories
# conversation_histories = {}

# @app.route("/health", methods=['GET'])
# def health_check():
#     """Simple health check endpoint"""
#     return jsonify({"status": "healthy", "message": "Service is running"}), 200

# @app.route("/make_call", methods=['POST'])
# def initiate_call():
#     """API endpoint to start an outbound call"""
#     try:
#         data = request.get_json()
        
#         # Validate request
#         if not data:
#             return jsonify({"error": "Missing request body"}), 400
        
#         phone_number = data.get('phone_number')
#         initial_message = data.get('initial_message', "Hello, this is an AI assistant calling. How can I help you today?")
        
#         if not phone_number:
#             return jsonify({"error": "Missing required parameter: phone_number"}), 400
            
#         # Ensure phone number has international format
#         if not phone_number.startswith('+'):
#             return jsonify({"error": "Phone number must include country code (e.g., +1...)"}), 400
            
#         # Create a call SID to track this conversation
#         call_id = str(uuid.uuid4())
        
#         # Initialize conversation history for this call
#         conversation_histories[call_id] = [
#             {"role": "system", "content": "You are a helpful AI voice assistant making a phone call. Keep responses conversational and concise since they'll be spoken aloud. Avoid long explanations or complex formatting."},
#             {"role": "assistant", "content": initial_message}
#         ]
        
#         # Make the call with Twilio
#         encoded_message = urllib.parse.quote(initial_message)

#         call = twilio_client.calls.create(
#             to=phone_number,
#             from_=TWILIO_PHONE_NUMBER,
#             url=f"{BASE_URL}/voice?call_id={call_id}&initial_message={encoded_message}",
#             method='GET'
#         )
        
#         logger.info(f"Initiated call to {phone_number} with SID: {call.sid}")
        
#         return jsonify({
#             "success": True,
#             "message": "Call initiated successfully",
#             "call_sid": call.sid,
#             "call_id": call_id
#         }), 200
        
#     except Exception as e:
#         logger.error(f"Error initiating call: {str(e)}")
#         return jsonify({"error": str(e)}), 500

# @app.route("/voice", methods=['GET', 'POST'])
# def voice_webhook():
#     """Handle the initial Twilio voice webhook"""
#     call_id = request.args.get('call_id')
#     initial_message = request.args.get('initial_message', "Hello, this is an AI assistant calling. How can I help you today?")
    
#     logger.info(f"Voice webhook triggered for call_id: {call_id}")
    
#     # Create TwiML response
#     response = VoiceResponse()
    
#     # Add initial greeting with gather
#     gather = Gather(
#         input='speech',
#         action=f'/handle_response?call_id={call_id}',
#         language='en-US',
#         speechTimeout='auto',
#         timeout=3
#     )
    
#     # Generate TTS for initial message
#     audio_url = generate_elevenlabs_tts(initial_message)
    
#     if audio_url:
#         gather.play(audio_url)
#     else:
#         # Fallback to basic Twilio TTS
#         gather.say(initial_message)
    
#     response.append(gather)
    
#     # If no input detected, end the call gracefully
#     response.say("I didn't hear a response. Thank you for your time. Goodbye.")
#     response.hangup()
    
#     return str(response)

# @app.route("/handle_response", methods=['POST'])
# def handle_response():
#     """Process user's speech and generate AI response"""
#     call_id = request.args.get('call_id')
#     user_speech = request.values.get('SpeechResult')
    
#     logger.info(f"Received speech from call {call_id}: {user_speech}")
    
#     if not user_speech:
#         # If no speech detected, end call gracefully
#         response = VoiceResponse()
#         response.say("I didn't catch that. Thank you for your time. Goodbye.")
#         response.hangup()
#         return str(response)
    
#     # Update conversation history
#     if call_id in conversation_histories:
#         conversation_histories[call_id].append({"role": "user", "content": user_speech})
        
#         # Generate AI response
#         ai_response = generate_ai_response(conversation_histories[call_id])
        
#         # Add AI response to history
#         conversation_histories[call_id].append({"role": "assistant", "content": ai_response})
        
#         # Create TwiML for response
#         response = VoiceResponse()
#         gather = Gather(
#             input='speech',
#             action=f'/handle_response?call_id={call_id}',
#             language='en-US',
#             speechTimeout='auto',
#             timeout=3
#         )
        
#         # Generate TTS for AI response
#         audio_url = generate_elevenlabs_tts(ai_response)
        
#         if audio_url:
#             gather.play(audio_url)
#         else:
#             # Fallback to basic Twilio TTS
#             gather.say(ai_response)
        
#         response.append(gather)
        
#         # If no user response after AI speaks, end call gracefully
#         response.say("Thank you for the conversation. Goodbye.")
#         response.hangup()
        
#         return str(response)
#     else:
#         # If call_id not found in history
#         response = VoiceResponse()
#         response.say("I'm having trouble with this call. Goodbye.")
#         response.hangup()
#         return str(response)

# def generate_ai_response(conversation):
#     """Generate AI response using OpenAI"""
#     try:
#         # Keep conversation history manageable (last 10 messages)
#         if len(conversation) > 12:  # Keep system prompt + last 10 exchanges
#             conversation = [conversation[0]] + conversation[-11:]
            
#         response = openai.ChatCompletion.create(
#             model="gpt-4o-mini",  # You can upgrade to gpt-4 for better quality
#             messages=conversation,
#             max_tokens=150,  # Keep responses concise for voice
#             temperature=0.7
#         )
        
#         return response.choices[0].message.content.strip()
        
#     except Exception as e:
#         logger.error(f"Error generating AI response: {str(e)}")
#         return "I'm having trouble processing your request right now. Could you please repeat that?"

# def generate_elevenlabs_tts(text):
#     """Generate text-to-speech using ElevenLabs API"""
#     try:
#         url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}/stream"
        
#         headers = {
#             "Accept": "audio/mpeg",
#             "Content-Type": "application/json",
#             "xi-api-key": ELEVENLABS_API_KEY
#         }
        
#         data = {
#             "text": text,
#             "model_id": "eleven_monolingual_v1",
#             "voice_settings": {
#                 "stability": 0.5,
#                 "similarity_boost": 0.75,
#                 "style": 0,
#                 "use_speaker_boost": True
#             }
#         }
        
#         response = requests.post(url, json=data, headers=headers)
        
#         if response.status_code == 200:
#             # Create unique filename
#             audio_dir = os.path.join("static", "audio")
#             os.makedirs(audio_dir, exist_ok=True)
            
#             filename = f"tts_{uuid.uuid4()}.mp3"
#             filepath = os.path.join(audio_dir, filename)
            
#             with open(filepath, "wb") as f:
#                 f.write(response.content)
                
#             audio_url = f"{BASE_URL}/static/audio/{filename}"
#             logger.info(f"Generated TTS audio: {audio_url}")
#             return audio_url
#         else:
#             logger.error(f"ElevenLabs API error: {response.status_code} - {response.text}")
#             return None
            
#     except Exception as e:
#         logger.error(f"Error generating TTS: {str(e)}")
#         return None

# @app.route('/static/audio/<filename>')
# def serve_audio(filename):
#     """Serve audio files"""
#     return app.send_static_file(f"audio/{filename}")

# @app.route('/cleanup', methods=['GET'])
# def cleanup_audio():
#     """Clean up old audio files"""
#     try:
#         audio_dir = os.path.join("static", "audio")
#         if not os.path.exists(audio_dir):
#             return jsonify({"message": "Audio directory does not exist"}), 404
            
#         count = 0
#         current_time = time.time()
        
#         for filename in os.listdir(audio_dir):
#             if filename.endswith('.mp3'):
#                 file_path = os.path.join(audio_dir, filename)
#                 # Delete files older than 1 hour
#                 if current_time - os.path.getmtime(file_path) > 3600:
#                     os.remove(file_path)
#                     count += 1
                    
#         return jsonify({"message": f"Cleaned up {count} audio files"}), 200
        
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# if __name__ == "__main__":
#     # Ensure audio directory exists
#     os.makedirs(os.path.join("static", "audio"), exist_ok=True)
#     app.run(debug=True, host="0.0.0.0", port=5000)
# # from flask import Flask, request, jsonify
# # from twilio.twiml.voice_response import VoiceResponse, Gather
# # from twilio.rest import Client
# # import requests
# # import os
# # from dotenv import load_dotenv
# # import time
# # import threading
# # import uuid
# # from google import genai
# # from google.genai import types

# # # Load environment variables
# # load_dotenv()

# # # Twilio credentials
# # TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
# # TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
# # TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# # # ElevenLabs API key
# # ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
# # ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID')

# # # Gemini API key
# # GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# # # Initialize Flask app
# # app = Flask(__name__)

# # # Dictionary to store conversation history
# # conversation_history = {}

# # # Initialize Gemini client
# # client = genai.Client(api_key=GEMINI_API_KEY)

# # # Initialize Twilio client for making calls
# # twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# # @app.route("/answer", methods=['POST'])
# # def answer_call():
# #     """Handle incoming calls and provide initial greeting"""
# #     # Get the caller's phone number
# #     caller_id = request.values.get('From', '')
# #     call_sid = request.values.get('CallSid', '')
    
# #     # Initialize conversation history for this caller
# #     if caller_id not in conversation_history:
# #         conversation_history[caller_id] = {
# #             'history': [
# #                 types.Content(
# #                     role="user",
# #                     parts=[types.Part.from_text(text="You are a helpful voice assistant. Keep your responses concise and conversational since they will be spoken aloud over the phone. Avoid long paragraphs and complex formatting.")],
# #                 ),
# #                 types.Content(
# #                     role="model",
# #                     parts=[types.Part.from_text(text="I'll act as a helpful voice assistant with concise, conversational responses suitable for phone conversations.")],
# #                 ),
# #             ],
# #             'current_call_sid': call_sid
# #         }
# #     else:
# #         # Update the current call SID for existing users
# #         conversation_history[caller_id]['current_call_sid'] = call_sid
    
# #     response = VoiceResponse()
    
# #     # Initial greeting
# #     gather = Gather(input='speech', action='/process_speech', language='en-US', 
# #                    speech_timeout='auto', timeout=3)
# #     gather.say("Hello, I'm your AI assistant. How can I help you today?")
# #     response.append(gather)
    
# #     # If no input received, try again
# #     response.redirect('/answer')
    
# #     return str(response)

# # @app.route("/outbound_call_twiml", methods=['POST'])
# # def outbound_call_twiml():
# #     """TwiML for outbound calls - this gets called by Twilio when an outbound call is answered"""
# #     # Get the initial message if provided
# #     initial_message = request.values.get('InitialMessage', 'Hello, this is your AI assistant calling. How can I help you today?')
    
# #     response = VoiceResponse()
    
# #     # Initial greeting for outbound call
# #     gather = Gather(input='speech', action='/process_speech', language='en-US', 
# #                    speech_timeout='auto', timeout=3)
# #     gather.say(initial_message)
# #     response.append(gather)
    
# #     # If no input received, try again
# #     response.redirect('/outbound_call_twiml')
    
# #     return str(response)

# # @app.route("/process_speech", methods=['POST'])
# # def process_speech():
# #     """Process speech from caller and generate a response"""
# #     # Get the caller's phone number and speech input
# #     caller_id = request.values.get('From', '')
# #     call_sid = request.values.get('CallSid', '')
# #     user_input = request.values.get('SpeechResult', '')
    
# #     if user_input:
# #         # Add user input to conversation history
# #         if caller_id in conversation_history:
# #             conversation_history[caller_id]['history'].append(
# #                 types.Content(
# #                     role="user",
# #                     parts=[types.Part.from_text(text=user_input)],
# #                 )
# #             )
        
# #         # Call Gemini API with the conversation history
# #         llm_response = call_gemini_api(user_input, caller_id)
        
# #         # Generate TTS audio with ElevenLabs
# #         audio_url = generate_voice(llm_response)
        
# #         response = VoiceResponse()
        
# #         if audio_url:
# #             # Play the generated audio
# #             response.play(audio_url)
# #         else:
# #             # Fallback if voice generation fails
# #             response.say(llm_response)
        
# #         # Set up for next user input
# #         gather = Gather(input='speech', action='/process_speech', language='en-US', 
# #                        speech_timeout='auto', timeout=2)
# #         response.append(gather)
        
# #         # If no input received, end call after waiting
# #         response.say("Thank you for calling. Goodbye!")
# #         response.hangup()
        
# #         return str(response)
# #     else:
# #         # If no speech was detected
# #         response = VoiceResponse()
# #         response.say("I didn't catch that. Let's try again.")
# #         response.redirect('/answer')
# #         return str(response)

# # @app.route("/make_call", methods=['POST'])
# # def make_call():
# #     """API endpoint to initiate an outbound call"""
# #     try:
# #         data = request.get_json()
        
# #         # Required parameters
# #         to_number = data.get('to_number')
# #         initial_message = data.get('initial_message', 'Hello, this is your AI assistant calling. How can I help you today?')
        
# #         if not to_number:
# #             return jsonify({"error": "Missing required parameter: to_number"}), 400
        
# #         # Validate phone number (basic validation)
# #         if not to_number.startswith('+'):
# #             return jsonify({"error": "Phone number must start with country code (e.g. +1)"}), 400
        
# #         # URL encode the initial message
# #         encoded_message = urllib.parse.quote(initial_message)
        
# #         # Create the call
# #         call = twilio_client.calls.create(
# #             url=f"{request.url_root.rstrip('/')}/outbound_call_twiml?InitialMessage={encoded_message}",
# #             to=to_number,
# #             from_=TWILIO_PHONE_NUMBER,
# #             method='POST'
# #         )
        
# #         return jsonify({
# #             "status": "success",
# #             "call_sid": call.sid,
# #             "to": to_number,
# #             "message": f"Call initiated to {to_number}"
# #         })
        
# #     except Exception as e:
# #         return jsonify({"error": str(e)}), 500

# # def call_gemini_api(user_input, caller_id):
# #     """Call the Gemini API with user input and conversation history"""
# #     try:
# #         # Get conversation history for this caller
# #         history = []
# #         if caller_id in conversation_history:
# #             history = conversation_history[caller_id]['history']
        
# #         # Create Gemini model client
# #         model = genai.GenerativeModel(model_name="gemini-2.0-flash")
        
# #         # Generate response using history
# #         chat = model.start_chat(history=history)
# #         response = chat.send_message(user_input)
        
# #         # Extract response text
# #         response_text = response.text
        
# #         # Add the model's response to conversation history
# #         if caller_id in conversation_history:
# #             conversation_history[caller_id]['history'].append(
# #                 types.Content(
# #                     role="model",
# #                     parts=[types.Part.from_text(text=response_text)],
# #                 )
# #             )
        
# #         # Keep conversation history at a reasonable length
# #         if caller_id in conversation_history and len(conversation_history[caller_id]['history']) > 10:
# #             # Keep the system prompt (first 2 messages) and the last 8 messages
# #             conversation_history[caller_id]['history'] = (
# #                 conversation_history[caller_id]['history'][:2] + 
# #                 conversation_history[caller_id]['history'][-8:]
# #             )
        
# #         print(f"Generated LLM response: {response_text}")
# #         return response_text
    
# #     except Exception as e:
# #         print(f"Error calling Gemini API: {e}")
# #         return "I'm having trouble processing your request right now."

# # def generate_voice(text):
# #     """Generate voice using ElevenLabs API and return URL"""
# #     try:
# #         # ElevenLabs API endpoint for text-to-speech
# #         url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
        
# #         headers = {
# #             "Accept": "audio/mpeg",
# #             "Content-Type": "application/json",
# #             "xi-api-key": ELEVENLABS_API_KEY
# #         }
        
# #         data = {
# #             "text": text,
# #             "model_id": "eleven_monolingual_v1",
# #             "voice_settings": {
# #                 "stability": 0.5,
# #                 "similarity_boost": 0.5
# #             }
# #         }
        
# #         # Generate audio
# #         response = requests.post(url, json=data, headers=headers)
        
# #         if response.status_code == 200:
# #             # Generate a unique filename
# #             filename = f"response_{uuid.uuid4()}.mp3"
# #             filepath = os.path.join("static", "audio", filename)
            
# #             # Ensure directory exists
# #             os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
# #             # Save audio file
# #             with open(filepath, 'wb') as f:
# #                 f.write(response.content)
            
# #             # Return URL to the audio file
# #             # This URL must be publicly accessible to Twilio
# #             base_url = os.getenv('BASE_URL', 'https://your-actual-domain.com')
# #             public_url = f"{base_url}/static/audio/{filename}"
# #             print(f"Generated audio URL: {public_url}")
# #             return public_url
# #         else:
# #             print(f"Error generating voice: {response.status_code}, {response.text}")
# #             return None
            
# #     except Exception as e:
# #         print(f"Error in voice generation: {e}")
# #         return None

# # # Route to clean up old audio files (run periodically)
# # @app.route("/cleanup", methods=['GET'])
# # def cleanup_audio_files():
# #     """Clean up old audio files to prevent disk space issues"""
# #     try:
# #         audio_dir = os.path.join("static", "audio")
# #         if not os.path.exists(audio_dir):
# #             return "Audio directory does not exist"
        
# #         # Get all audio files
# #         audio_files = [os.path.join(audio_dir, f) for f in os.listdir(audio_dir) if f.endswith('.mp3')]
        
# #         # Get current time
# #         current_time = time.time()
        
# #         # Delete files older than 1 hour
# #         deleted_count = 0
# #         for file_path in audio_files:
# #             file_modified_time = os.path.getmtime(file_path)
# #             if current_time - file_modified_time > 3600:  # 3600 seconds = 1 hour
# #                 os.remove(file_path)
# #                 deleted_count += 1
        
# #         return f"Cleaned up {deleted_count} old audio files"
    
# #     except Exception as e:
# #         return f"Error during cleanup: {e}"

# # # Serve static files
# # @app.route('/static/audio/<path:filename>')
# # def serve_audio(filename):
# #     return app.send_static_file(os.path.join('audio', filename))

# # # Helper function to make calls programmatically
# # import urllib.parse

# # def make_outbound_call(to_number, initial_message="Hello, this is your AI assistant calling. How can I help you today?"):
# #     """Helper function to make an outbound call"""
# #     try:
# #         # Create the call
# #         base_url = os.getenv('BASE_URL', 'https://e205-2409-40f4-2054-d890-bb59-d09d-e4ca-6b00.ngrok-free.app')
        
# #         # URL encode the initial message to handle spaces and special characters
# #         encoded_message = urllib.parse.quote(initial_message)
        
# #         # Create the full URL with encoded parameters
# #         callback_url = f"{base_url}/outbound_call_twiml?InitialMessage={encoded_message}"
        
# #         print(f"Using callback URL: {callback_url}")
        
# #         call = twilio_client.calls.create(
# #             url=callback_url,
# #             to=to_number,
# #             from_=TWILIO_PHONE_NUMBER,
# #             method='POST'
# #         )
        
# #         return {
# #             "status": "success",
# #             "call_sid": call.sid,
# #             "to": to_number,
# #             "message": f"Call initiated to {to_number}"
# #         }
        
# #     except Exception as e:
# #         print(f"Error making call: {e}")
# #         return {
# #             "status": "error",
# #             "error": str(e)
# #         }

# # # Example usage code (can be used in other parts of your application)
# # def example_make_call():
# #     """Example of how to use the make_outbound_call function"""
# #     result = make_outbound_call(
# #         to_number="+918300874166",  # Replace with the actual number
# #         initial_message="Hello, this is an Follow up call regarding your Project X"
# #     )
# #     print(result)

# # if __name__ == "__main__":
# #     # Create static/audio directory if it doesn't exist
# #     os.makedirs(os.path.join("static", "audio"), exist_ok=True)
    
# #     # Run the Flask app
# #     app.run(debug=True, port=5000)
