"""
EcoMatrix Agent Implementation with Gemini 2.0 Flash
Handles voice conversations and location queries
"""

import asyncio
import json
import logging
import base64
import struct
import time
from typing import Dict, Any, Optional, List
from datetime import datetime

from google import genai
from google.genai import types

from config import Config
from .prompt import AgentPrompt

logger = logging.getLogger(__name__)

class EcoMatrixAgent:
    """Main agent class for handling voice conversations"""
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.client = None
        self.prompt_manager = AgentPrompt()
        
        # Initialize Gemini client
        self._initialize_gemini()
        
        logger.info("🤖 EcoMatrix Agent initialized with Gemini 2.0 Flash")
    
    def _initialize_gemini(self):
        """Initialize Gemini AI client"""
        try:
            if not Config.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY is required")
                
            self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
            logger.info("✅ Gemini client initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini client: {e}")
            raise
    
    async def create_session(self, stream_id: str) -> Dict[str, Any]:
        """Create a new agent session for a stream"""
        try:
            session = {
                "stream_id": stream_id,
                "start_time": time.time(),
                "conversation_history": [],
                "context": {
                    "user_location": None,
                    "recent_queries": [],
                    "preferences": {}
                },
                "state": "greeting"  # greeting, listening, responding, ended
            }
            
            self.sessions[stream_id] = session
            logger.info(f"🎯 Created agent session for {stream_id}")
            
            return session
            
        except Exception as e:
            logger.error(f"❌ Error creating session: {e}")
            raise
    
    async def cleanup_session(self, stream_id: str):
        """Clean up agent session"""
        try:
            if stream_id in self.sessions:
                session = self.sessions[stream_id]
                duration = time.time() - session["start_time"]
                
                logger.info(f"🧹 Cleaning up session {stream_id} (duration: {duration:.1f}s)")
                del self.sessions[stream_id]
                
        except Exception as e:
            logger.error(f"❌ Error cleaning up session: {e}")
    
    async def generate_greeting(self, stream_id: str) -> Optional[bytes]:
        """Generate initial greeting audio"""
        try:
            greeting_text = self.prompt_manager.get_greeting()
            
            # Add to conversation history
            if stream_id in self.sessions:
                self.sessions[stream_id]["conversation_history"].append({
                    "role": "assistant",
                    "content": greeting_text,
                    "timestamp": datetime.now().isoformat()
                })
            
            # Convert text to audio (simplified - you might want to use a TTS service)
            audio_data = self._text_to_audio(greeting_text)
            
            logger.info(f"👋 Generated greeting for {stream_id}")
            return audio_data
            
        except Exception as e:
            logger.error(f"❌ Error generating greeting: {e}")
            return None
    
    async def process_audio(self, stream_id: str, audio_data: bytes, location_tool) -> Optional[bytes]:
        """Process incoming audio and generate response"""
        try:
            if stream_id not in self.sessions:
                logger.warning(f"⚠️ No session found for {stream_id}")
                return None
            
            session = self.sessions[stream_id]
            
            # Convert audio to text (simplified - you might want to use STT service)
            user_text = self._audio_to_text(audio_data)
            
            if not user_text or user_text.strip() == "":
                return None
            
            logger.info(f"🎤 User said: {user_text}")
            
            # Add user message to conversation history
            session["conversation_history"].append({
                "role": "user",
                "content": user_text,
                "timestamp": datetime.now().isoformat()
            })
            
            # Process with Gemini
            response_text = await self._generate_response(stream_id, user_text, location_tool)
            
            if response_text:
                # Add assistant response to conversation history
                session["conversation_history"].append({
                    "role": "assistant",
                    "content": response_text,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Convert response to audio
                response_audio = self._text_to_audio(response_text)
                
                logger.info(f"🗣️ Agent responded: {response_text[:100]}...")
                return response_audio
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error processing audio: {e}")
            return None
    
    async def _generate_response(self, stream_id: str, user_text: str, location_tool) -> Optional[str]:
        """Generate response using Gemini AI"""
        try:
            session = self.sessions[stream_id]
            
            # Check if user is asking about locations
            location_keywords = ["near", "nearby", "closest", "find", "where", "shop", "store", "coffee", "hardware", "book"]
            is_location_query = any(keyword.lower() in user_text.lower() for keyword in location_keywords)
            
            # Build context for Gemini
            context = self._build_context(session, user_text, is_location_query)
            
            # If it's a location query, use the location tool
            location_info = ""
            if is_location_query and location_tool:
                try:
                    # For demo, use a random location within bounds
                    import random
                    bounds = Config.DEFAULT_AREA["bounds"]
                    user_lat = random.uniform(bounds["south"], bounds["north"])
                    user_lng = random.uniform(bounds["west"], bounds["east"])
                    
                    # Find nearby locations
                    location_result = await location_tool.find_nearby_locations(user_lat, user_lng, user_text)
                    location_info = f"\n\nLocation Information:\n{json.dumps(location_result, indent=2)}"
                    
                    # Update session context
                    session["context"]["user_location"] = {"lat": user_lat, "lng": user_lng}
                    
                except Exception as e:
                    logger.error(f"❌ Error using location tool: {e}")
            
            # Create the prompt
            full_prompt = f"""
{self.prompt_manager.get_system_prompt()}

{context}
{location_info}

User: {user_text}

Please respond conversationally and helpfully. If location information is provided, use it to give specific recommendations with distances and descriptions. Keep your response natural and not too long since this is a voice conversation.
            """
            
            # Generate response with Gemini
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=full_prompt)],
                ),
            ]
            
            response = self.client.models.generate_content(
                model=Config.GEMINI_MODEL,
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=200,  # Keep responses concise for voice
                    top_p=0.9
                )
            )
            
            response_text = response.text.strip()
            
            # Update session state
            session["context"]["recent_queries"].append(user_text)
            if len(session["context"]["recent_queries"]) > 5:
                session["context"]["recent_queries"] = session["context"]["recent_queries"][-5:]
            
            return response_text
            
        except Exception as e:
            logger.error(f"❌ Error generating Gemini response: {e}")
            return "I'm sorry, I'm having trouble processing that right now. Could you please try again?"
    
    def _build_context(self, session: Dict[str, Any], user_text: str, is_location_query: bool) -> str:
        """Build context for the AI model"""
        context_parts = []
        
        # Add conversation history (last 3 exchanges)
        history = session["conversation_history"][-6:]  # Last 3 exchanges (6 messages)
        if history:
            context_parts.append("Recent conversation:")
            for msg in history:
                role = "User" if msg["role"] == "user" else "Assistant"
                context_parts.append(f"{role}: {msg['content']}")
        
        # Add user location if available
        if session["context"]["user_location"]:
            loc = session["context"]["user_location"]
            context_parts.append(f"User location: Lat {loc['lat']:.4f}, Lng {loc['lng']:.4f}")
        
        # Add recent queries context
        if session["context"]["recent_queries"]:
            context_parts.append(f"Recent queries: {', '.join(session['context']['recent_queries'][-3:])}")
        
        return "\n".join(context_parts)
    
    async def handle_interruption(self, stream_id: str):
        """Handle user interruption"""
        try:
            if stream_id in self.sessions:
                self.sessions[stream_id]["state"] = "listening"
                logger.info(f"🛑 Handled interruption for {stream_id}")
                
        except Exception as e:
            logger.error(f"❌ Error handling interruption: {e}")
    
    def _text_to_audio(self, text: str) -> bytes:
        """Convert text to audio (simplified implementation)"""
        # This is a placeholder implementation
        # In a real system, you would use a TTS service like:
        # - Google Cloud Text-to-Speech
        # - Azure Speech Services
        # - Amazon Polly
        # - OpenAI TTS API
        
        try:
            # Generate a simple sine wave as placeholder audio
            # In production, replace this with actual TTS
            import math
            
            sample_rate = Config.SAMPLE_RATE
            duration = min(len(text) * 0.1, 5.0)  # Roughly 0.1s per character, max 5s
            samples = int(sample_rate * duration)
            frequency = 440  # A4 note
            amplitude = 5000
            
            audio_data = []
            for i in range(samples):
                t = i / sample_rate
                # Add some variation to make it less monotonous
                freq_mod = frequency + (math.sin(t * 2) * 50)
                sample = int(amplitude * math.sin(2 * math.pi * freq_mod * t) * math.exp(-t * 0.5))
                sample = max(-32767, min(32767, sample))
                audio_data.append(sample)
            
            # Convert to 16-bit PCM bytes
            return struct.pack(f'<{len(audio_data)}h', *audio_data)
            
        except Exception as e:
            logger.error(f"❌ Error in TTS: {e}")
            return b""
    
    def _audio_to_text(self, audio_data: bytes) -> str:
        """Convert audio to text (simplified implementation)"""
        # This is a placeholder implementation
        # In a real system, you would use an STT service like:
        # - Google Cloud Speech-to-Text
        # - Azure Speech Services
        # - Amazon Transcribe
        # - OpenAI Whisper API
        
        try:
            # For demo purposes, return some sample queries based on audio length
            audio_length = len(audio_data)
            
            sample_queries = [
                "Hi, can you help me find a coffee shop nearby?",
                "Where is the nearest hardware store?",
                "I'm looking for a bookstore in the area.",
                "Can you tell me about shops near me?",
                "Is there a good place to get coffee around here?",
                "I need to find a hardware store.",
                "What shops are nearby?",
                "Can you help me find something?",
                "Hello, I need some assistance.",
                "Where can I find a good restaurant?"
            ]
            
            # Use audio length to simulate different queries
            query_index = (audio_length // 1000) % len(sample_queries)
            return sample_queries[query_index]
            
        except Exception as e:
            logger.error(f"❌ Error in STT: {e}")
            return ""
