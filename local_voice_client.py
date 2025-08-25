#!/usr/bin/env python3
"""
Local Voice Client for EcoMatrix ADK Agent Framework
Test voice interactions locally before Exotel integration
"""

import asyncio
import websockets
import json
import logging
import base64
import pyaudio
import wave
import threading
import time
from datetime import datetime
import speech_recognition as sr
import pyttsx3
import tkinter as tk
from tkinter import ttk, scrolledtext
import queue

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocalVoiceClient:
    """Local voice client for testing the EcoMatrix agent"""
    
    def __init__(self):
        # Audio configuration
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 8000  # 8kHz to match server
        self.record_seconds = 5  # Maximum recording length
        
        # Initialize audio
        self.audio = pyaudio.PyAudio()
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
        
        # WebSocket connection
        self.websocket = None
        self.stream_id = f"local_test_{int(time.time())}"
        
        # GUI components
        self.root = None
        self.text_area = None
        self.status_label = None
        self.is_recording = False
        self.is_connected = False
        
        # Message queues for thread communication
        self.message_queue = queue.Queue()
        self.response_queue = queue.Queue()
        
        logger.info("🎤 Local Voice Client initialized")
    
    def create_gui(self):
        """Create the GUI for the voice client"""
        self.root = tk.Tk()
        self.root.title("EcoMatrix Voice Client - Local Testing")
        self.root.geometry("600x500")
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="🤖 EcoMatrix Voice Agent Tester", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Status
        self.status_label = ttk.Label(main_frame, text="❌ Disconnected", font=("Arial", 12))
        self.status_label.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        # Connection controls
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=2, pady=(0, 20))
        
        self.connect_btn = ttk.Button(control_frame, text="🔗 Connect to Agent", command=self.connect_to_server)
        self.connect_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.disconnect_btn = ttk.Button(control_frame, text="🔌 Disconnect", command=self.disconnect_from_server, state="disabled")
        self.disconnect_btn.grid(row=0, column=1, padx=(0, 10))
        
        # Voice controls
        voice_frame = ttk.Frame(main_frame)
        voice_frame.grid(row=3, column=0, columnspan=2, pady=(0, 20))
        
        self.record_btn = ttk.Button(voice_frame, text="🎤 Hold to Talk", state="disabled")
        self.record_btn.grid(row=0, column=0, padx=(0, 10))
        self.record_btn.bind('<ButtonPress-1>', self.start_recording)
        self.record_btn.bind('<ButtonRelease-1>', self.stop_recording)
        
        self.quick_test_btn = ttk.Button(voice_frame, text="⚡ Quick Test", command=self.quick_test, state="disabled")
        self.quick_test_btn.grid(row=0, column=1)
        
        # Text input for testing
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=4, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))
        
        ttk.Label(text_frame, text="Or type a message:").grid(row=0, column=0, sticky=tk.W)
        self.text_input = ttk.Entry(text_frame, width=40)
        self.text_input.grid(row=1, column=0, padx=(0, 10), sticky=(tk.W, tk.E))
        self.text_input.bind('<Return>', self.send_text_message)
        
        self.send_btn = ttk.Button(text_frame, text="📤 Send", command=self.send_text_message, state="disabled")
        self.send_btn.grid(row=1, column=1)
        
        # Conversation area
        ttk.Label(main_frame, text="Conversation:").grid(row=5, column=0, sticky=tk.W, pady=(20, 5))
        
        self.text_area = scrolledtext.ScrolledText(main_frame, width=70, height=15, state="disabled")
        self.text_area.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        text_frame.columnconfigure(0, weight=1)
        
        # Instructions
        instructions = """
Instructions:
1. Click 'Connect to Agent' to connect to the WebSocket server
2. Hold 'Hold to Talk' button and speak your question
3. Or type a message and press Enter or click Send
4. The agent will respond with location information

Example queries:
- "Hi, can you help me find a coffee shop nearby?"
- "Where is the nearest hardware store?"
- "I'm looking for a bookstore in the area."
        """
        
        self.log_message("SYSTEM", instructions.strip())
        
        logger.info("🖥️ GUI created successfully")
    
    def log_message(self, sender: str, message: str):
        """Add a message to the conversation area"""
        if self.text_area:
            self.text_area.config(state="normal")
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.text_area.insert(tk.END, f"[{timestamp}] {sender}: {message}\n\n")
            self.text_area.see(tk.END)
            self.text_area.config(state="disabled")
    
    def update_status(self, status: str, color: str = "black"):
        """Update the status label"""
        if self.status_label:
            self.status_label.config(text=status, foreground=color)
    
    async def connect_websocket(self):
        """Connect to the WebSocket server"""
        try:
            uri = "ws://localhost:8000/media"
            logger.info(f"🔗 Connecting to WebSocket: {uri}")
            
            self.websocket = await websockets.connect(uri)
            self.is_connected = True
            
            self.log_message("SYSTEM", "✅ Connected to EcoMatrix Agent")
            self.update_status("✅ Connected to Agent", "green")
            
            # Send connected event
            await self.send_websocket_message({
                "event": "connected",
                "streamSid": self.stream_id,
                "timestamp": datetime.now().isoformat()
            })
            
            # Send start event
            await self.send_websocket_message({
                "event": "start",
                "streamSid": self.stream_id,
                "timestamp": datetime.now().isoformat()
            })
            
            # Listen for responses
            asyncio.create_task(self.listen_for_responses())
            
            logger.info("✅ WebSocket connected successfully")
            
        except Exception as e:
            logger.error(f"❌ WebSocket connection failed: {e}")
            self.log_message("ERROR", f"Connection failed: {e}")
            self.update_status("❌ Connection Failed", "red")
            self.is_connected = False
    
    async def send_websocket_message(self, message: dict):
        """Send a message to the WebSocket server"""
        if self.websocket and self.is_connected:
            try:
                await self.websocket.send(json.dumps(message))
                logger.info(f"📤 Sent: {message.get('event', 'message')}")
            except Exception as e:
                logger.error(f"❌ Error sending message: {e}")
    
    async def listen_for_responses(self):
        """Listen for responses from the WebSocket server"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self.handle_server_response(data)
                except json.JSONDecodeError as e:
                    logger.error(f"❌ JSON decode error: {e}")
        except websockets.exceptions.ConnectionClosed:
            logger.info("🔌 WebSocket connection closed")
            self.is_connected = False
            self.update_status("❌ Disconnected", "red")
        except Exception as e:
            logger.error(f"❌ Error listening for responses: {e}")
    
    async def handle_server_response(self, data: dict):
        """Handle response from the server"""
        event = data.get("event", "")
        
        if event == "media":
            # This would be audio response from the agent
            media = data.get("media", {})
            audio_payload = media.get("payload", "")
            
            if audio_payload:
                # In a real implementation, you would decode and play the audio
                # For now, we'll simulate the agent's text response
                self.log_message("AGENT", "🔊 [Audio response received - would play audio here]")
                
                # For demo, let's also show a text version
                demo_responses = [
                    "I found Coffee Corner C about 200 meters from you. They serve artisan coffee and pastries. Would you like directions?",
                    "The closest hardware store is Hammer Shop B, just 300 meters away. They have tools and equipment.",
                    "I found several bookstores near you! The closest is Book Haven D, about 400 meters away.",
                    "Hi there! I'm EcoMatrix Assistant. How can I help you find what you're looking for today?",
                    "I found a few options for you! Would you like me to tell you about the nearest ones?"
                ]
                
                import random
                demo_response = random.choice(demo_responses)
                self.log_message("AGENT", f"💬 {demo_response}")
                
                # Speak the response if TTS is available
                if self.tts_engine:
                    threading.Thread(target=self.speak_text, args=(demo_response,), daemon=True).start()
        
        logger.info(f"📥 Received: {event}")
    
    def speak_text(self, text: str):
        """Speak text using TTS"""
        if self.tts_engine:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                logger.error(f"❌ TTS error: {e}")
    
    def record_audio(self) -> bytes:
        """Record audio from microphone"""
        try:
            logger.info("🎤 Recording audio...")
            
            stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            
            frames = []
            
            # Record for a maximum time or until stopped
            for i in range(0, int(self.rate / self.chunk * self.record_seconds)):
                if not self.is_recording:
                    break
                data = stream.read(self.chunk)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            
            # Convert to bytes
            audio_data = b''.join(frames)
            logger.info(f"🎤 Recorded {len(audio_data)} bytes of audio")
            
            return audio_data
            
        except Exception as e:
            logger.error(f"❌ Recording error: {e}")
            return b""
    
    def transcribe_audio(self, audio_data: bytes) -> str:
        """Transcribe audio to text using speech recognition"""
        try:
            # Save audio data to a temporary wav file
            with wave.open("/tmp/temp_audio.wav", "wb") as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.format))
                wf.setframerate(self.rate)
                wf.writeframes(audio_data)
            
            # Use speech recognition
            with sr.AudioFile("/tmp/temp_audio.wav") as source:
                audio = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio)
                logger.info(f"🎤 Transcribed: {text}")
                return text
                
        except sr.UnknownValueError:
            logger.warning("⚠️ Could not understand audio")
            return ""
        except sr.RequestError as e:
            logger.error(f"❌ Speech recognition error: {e}")
            return ""
        except Exception as e:
            logger.error(f"❌ Transcription error: {e}")
            return ""
    
    async def send_voice_message(self, text: str):
        """Send a voice message to the agent"""
        if not self.is_connected:
            self.log_message("ERROR", "Not connected to agent")
            return
        
        self.log_message("YOU", text)
        
        # For demo purposes, we'll simulate audio data
        # In a real implementation, you would send the actual audio
        demo_audio = b"demo_audio_data" * 100  # Simulate some audio data
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
        
        await self.send_websocket_message(message)
    
    def connect_to_server(self):
        """Connect to the WebSocket server (GUI callback)"""
        if not self.is_connected:
            self.update_status("🔄 Connecting...", "orange")
            self.connect_btn.config(state="disabled")
            
            # Run connection in background
            threading.Thread(target=self.run_connection, daemon=True).start()
    
    def run_connection(self):
        """Run WebSocket connection in a separate thread"""
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.connect_websocket())
        except Exception as e:
            logger.error(f"❌ Connection thread error: {e}")
            self.update_status("❌ Connection Failed", "red")
        finally:
            # Re-enable connect button
            self.root.after(0, lambda: self.connect_btn.config(state="normal"))
    
    def disconnect_from_server(self):
        """Disconnect from the WebSocket server"""
        if self.is_connected and self.websocket:
            asyncio.create_task(self.websocket.close())
            self.is_connected = False
            self.update_status("❌ Disconnected", "red")
            self.log_message("SYSTEM", "🔌 Disconnected from agent")
        
        # Update button states
        self.connect_btn.config(state="normal")
        self.disconnect_btn.config(state="disabled")
        self.record_btn.config(state="disabled")
        self.quick_test_btn.config(state="disabled")
        self.send_btn.config(state="disabled")
    
    def start_recording(self, event):
        """Start recording audio (mouse press)"""
        if not self.is_connected:
            return
        
        self.is_recording = True
        self.record_btn.config(text="🔴 Recording... (Release to send)")
        self.log_message("SYSTEM", "🎤 Recording started...")
        
        # Start recording in background thread
        threading.Thread(target=self.handle_recording, daemon=True).start()
    
    def stop_recording(self, event):
        """Stop recording audio (mouse release)"""
        self.is_recording = False
        self.record_btn.config(text="🎤 Hold to Talk")
    
    def handle_recording(self):
        """Handle the recording process"""
        try:
            # Record audio
            audio_data = self.record_audio()
            
            if audio_data:
                # Transcribe audio
                text = self.transcribe_audio(audio_data)
                
                if text:
                    # Send to agent
                    asyncio.run_coroutine_threadsafe(
                        self.send_voice_message(text),
                        asyncio.get_event_loop()
                    )
                else:
                    self.log_message("SYSTEM", "⚠️ Could not understand speech, please try again")
            
        except Exception as e:
            logger.error(f"❌ Recording handling error: {e}")
            self.log_message("ERROR", f"Recording error: {e}")
    
    def send_text_message(self, event=None):
        """Send a text message to the agent"""
        if not self.is_connected:
            self.log_message("ERROR", "Not connected to agent")
            return
        
        text = self.text_input.get().strip()
        if text:
            self.text_input.delete(0, tk.END)
            
            # Send message in background
            threading.Thread(
                target=lambda: asyncio.run(self.send_voice_message(text)),
                daemon=True
            ).start()
    
    def quick_test(self):
        """Send a quick test message"""
        test_messages = [
            "Hi, can you help me find a coffee shop nearby?",
            "Where is the nearest hardware store?",
            "I'm looking for a bookstore in the area.",
            "Can you tell me about shops near me?",
            "Hello, I need some assistance."
        ]
        
        import random
        message = random.choice(test_messages)
        self.text_input.delete(0, tk.END)
        self.text_input.insert(0, message)
        self.send_text_message()
    
    def on_connection_change(self):
        """Update GUI when connection status changes"""
        if self.is_connected:
            self.connect_btn.config(state="disabled")
            self.disconnect_btn.config(state="normal")
            self.record_btn.config(state="normal")
            self.quick_test_btn.config(state="normal")
            self.send_btn.config(state="normal")
        else:
            self.connect_btn.config(state="normal")
            self.disconnect_btn.config(state="disabled")
            self.record_btn.config(state="disabled")
            self.quick_test_btn.config(state="disabled")
            self.send_btn.config(state="disabled")
    
    def run(self):
        """Run the voice client"""
        logger.info("🚀 Starting Local Voice Client")
        
        # Create and run GUI
        self.create_gui()
        
        # Start GUI main loop
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            logger.info("👋 Voice client stopped by user")
        finally:
            # Cleanup
            if self.is_connected and self.websocket:
                asyncio.run(self.websocket.close())
            
            if self.audio:
                self.audio.terminate()

if __name__ == "__main__":
    print("""
🎤 EcoMatrix Local Voice Client

This tool allows you to test voice interactions with the EcoMatrix Agent locally.

Prerequisites:
1. Make sure the EcoMatrix server is running:
   python main.py

2. Ensure you have a microphone connected and working

3. Make sure your .env file has GEMINI_API_KEY configured

Starting the voice client...
    """)
    
    client = LocalVoiceClient()
    client.run()

