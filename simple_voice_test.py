#!/usr/bin/env python3
"""
Simple Voice Test Client for EcoMatrix ADK Agent Framework
Command-line interface for quick voice testing
"""

import asyncio
import websockets
import json
import logging
import base64
import time
from datetime import datetime
import speech_recognition as sr
import pyttsx3

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleVoiceTest:
    """Simple command-line voice test client"""
    
    def __init__(self):
        self.stream_id = f"simple_test_{int(time.time())}"
        self.websocket = None
        self.is_connected = False
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Initialize TTS
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)
            self.tts_engine.setProperty('volume', 0.9)
            logger.info("✅ TTS engine initialized")
        except Exception as e:
            logger.error(f"❌ TTS initialization failed: {e}")
            self.tts_engine = None
        
        # Adjust for ambient noise
        print("🎤 Adjusting for ambient noise... Please wait.")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
        print("✅ Microphone calibrated!")
    
    async def connect_to_server(self):
        """Connect to the WebSocket server"""
        try:
            uri = "ws://localhost:8000/media"
            print(f"🔗 Connecting to {uri}...")
            
            self.websocket = await websockets.connect(uri)
            self.is_connected = True
            
            print("✅ Connected to EcoMatrix Agent!")
            
            # Send connected event
            await self.send_message({
                "event": "connected",
                "streamSid": self.stream_id,
                "timestamp": datetime.now().isoformat()
            })
            
            # Send start event
            await self.send_message({
                "event": "start",
                "streamSid": self.stream_id,
                "timestamp": datetime.now().isoformat()
            })
            
            # Listen for responses in background
            asyncio.create_task(self.listen_for_responses())
            
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    async def send_message(self, message: dict):
        """Send a message to the WebSocket server"""
        if self.websocket and self.is_connected:
            try:
                await self.websocket.send(json.dumps(message))
                logger.info(f"📤 Sent: {message.get('event', 'message')}")
            except Exception as e:
                logger.error(f"❌ Error sending message: {e}")
    
    async def listen_for_responses(self):
        """Listen for responses from the server"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self.handle_response(data)
                except json.JSONDecodeError as e:
                    logger.error(f"❌ JSON decode error: {e}")
        except websockets.exceptions.ConnectionClosed:
            print("🔌 Connection closed")
            self.is_connected = False
        except Exception as e:
            logger.error(f"❌ Error listening: {e}")
    
    async def handle_response(self, data: dict):
        """Handle server response"""
        event = data.get("event", "")
        
        if event == "media":
            # Agent's audio response
            print("🤖 Agent is responding...")
            
            # For demo, simulate different agent responses
            demo_responses = [
                "Hi there! I'm EcoMatrix Assistant. How can I help you find what you're looking for today?",
                "I found Coffee Corner C about 200 meters from you. They serve artisan coffee and pastries. Would you like directions?",
                "The closest hardware store is Hammer Shop B, just 300 meters away. They have tools and equipment.",
                "I found several bookstores near you! The closest is Book Haven D, about 400 meters away.",
                "I found a few options for you! Would you like me to tell you about the nearest ones?",
                "I'm sorry, I don't see any matching places in your immediate area. Would you like me to expand the search?"
            ]
            
            import random
            response_text = random.choice(demo_responses)
            print(f"🗣️  Agent: {response_text}")
            
            # Speak the response
            if self.tts_engine:
                try:
                    self.tts_engine.say(response_text)
                    self.tts_engine.runAndWait()
                except Exception as e:
                    logger.error(f"❌ TTS error: {e}")
    
    def listen_for_speech(self) -> str:
        """Listen for speech from microphone"""
        try:
            print("🎤 Listening... Speak now!")
            
            with self.microphone as source:
                # Listen for audio with a timeout
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=10)
            
            print("🔄 Processing speech...")
            
            # Recognize speech using Google Speech Recognition
            text = self.recognizer.recognize_google(audio)
            print(f"🎤 You said: {text}")
            
            return text
            
        except sr.WaitTimeoutError:
            print("⏱️  Timeout - no speech detected")
            return ""
        except sr.UnknownValueError:
            print("❓ Could not understand speech, please try again")
            return ""
        except sr.RequestError as e:
            print(f"❌ Speech recognition error: {e}")
            return ""
        except Exception as e:
            print(f"❌ Error: {e}")
            return ""
    
    async def send_voice_message(self, text: str):
        """Send voice message to the agent"""
        if not text.strip():
            return
        
        print(f"📤 Sending to agent: {text}")
        
        # Simulate audio data (in real implementation, this would be actual audio)
        demo_audio = b"simulated_audio_data" * 50
        audio_b64 = base64.b64encode(demo_audio).decode()
        
        message = {
            "event": "media",
            "streamSid": self.stream_id,
            "media": {
                "payload": audio_b64,
                "timestamp": str(int(time.time() * 1000)),
                "sequenceNumber": str(int(time.time()))
            }
        }
        
        await self.send_message(message)
    
    async def run_conversation(self):
        """Run the main conversation loop"""
        print("\n" + "="*60)
        print("🎙️  EcoMatrix Voice Test - Ready!")
        print("="*60)
        print("\nInstructions:")
        print("- Press Enter to start speaking")
        print("- Type 'quit' or 'exit' to stop")
        print("- Type a message to send text instead of voice")
        print("\nExample queries:")
        print("- 'Hi, can you help me find a coffee shop nearby?'")
        print("- 'Where is the nearest hardware store?'")
        print("- 'I'm looking for a bookstore in the area.'")
        print("\n" + "="*60)
        
        while self.is_connected:
            try:
                user_input = input("\n🎤 Press Enter to speak (or type message): ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                
                if user_input:
                    # User typed a message
                    await self.send_voice_message(user_input)
                else:
                    # User wants to speak
                    speech_text = self.listen_for_speech()
                    if speech_text:
                        await self.send_voice_message(speech_text)
                
                # Wait a moment for the agent to respond
                await asyncio.sleep(2)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print("\n👋 Conversation ended!")
    
    async def run(self):
        """Main run method"""
        print("🚀 Starting Simple Voice Test Client")
        
        # Connect to server
        if not await self.connect_to_server():
            print("❌ Failed to connect to server. Make sure it's running:")
            print("   python main.py")
            return
        
        try:
            # Run conversation
            await self.run_conversation()
        finally:
            # Cleanup
            if self.websocket:
                await self.websocket.close()
            print("🧹 Cleaned up resources")

async def main():
    """Main function"""
    print("""
🎤 EcoMatrix Simple Voice Test

Prerequisites:
1. Start the EcoMatrix server: python main.py
2. Make sure you have a working microphone
3. Ensure GEMINI_API_KEY is configured in .env

Starting voice test client...
    """)
    
    client = SimpleVoiceTest()
    await client.run()

if __name__ == "__main__":
    asyncio.run(main())

