"""
Configuration management for EcoMatrix ADK Agent Framework
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the EcoMatrix Agent Framework"""
    
    # Server Configuration
    SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Optional for future use
    
    # Gemini Configuration
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
    
    # Audio Configuration
    SAMPLE_RATE = int(os.getenv("SAMPLE_RATE", "8000"))  # 8kHz for telephony
    BUFFER_SIZE_MS = int(os.getenv("BUFFER_SIZE_MS", "200"))  # 200ms chunks
    
    # Voice Activity Detection (VAD) Configuration
    VAD_THRESHOLD = float(os.getenv("VAD_THRESHOLD", "0.5"))
    PREFIX_PADDING_MS = int(os.getenv("PREFIX_PADDING_MS", "300"))
    SILENCE_DURATION_MS = int(os.getenv("SILENCE_DURATION_MS", "500"))
    
    # Noise Suppression
    NOISE_THRESHOLD = int(os.getenv("NOISE_THRESHOLD", "100"))
    
    # Agent Configuration
    AGENT_NAME = os.getenv("AGENT_NAME", "EcoMatrix Assistant")
    COMPANY_NAME = os.getenv("COMPANY_NAME", "EcoMatrix")
    
    # Location Service Configuration
    DEFAULT_AREA = {
        "center": {
            "lat": float(os.getenv("DEFAULT_LAT", "40.7128")),
            "lng": float(os.getenv("DEFAULT_LNG", "-74.0060"))
        },
        "bounds": {
            "north": float(os.getenv("BOUNDS_NORTH", "40.7228")),
            "south": float(os.getenv("BOUNDS_SOUTH", "40.7028")),
            "east": float(os.getenv("BOUNDS_EAST", "-73.9960")),
            "west": float(os.getenv("BOUNDS_WEST", "-74.0160"))
        }
    }
    
    # Predefined locations (can be moved to database later)
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
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        errors = []
        
        if not cls.GEMINI_API_KEY:
            errors.append("GEMINI_API_KEY is required")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
    
    @classmethod
    def get_agent_instructions(cls) -> str:
        """Get the main agent instructions"""
        return f"""
You are {cls.AGENT_NAME}, a helpful voice assistant for {cls.COMPANY_NAME}.

Your primary role is to help customers find nearby locations and provide information about shops and services in the area.

Key capabilities:
1. Location Services: Help users find nearby shops, houses, and services
2. Conversational Interface: Engage in natural, friendly conversations
3. Real-time Assistance: Provide immediate help during phone calls

Guidelines:
- Be conversational and friendly
- Keep responses concise but helpful
- Always try to understand what the customer is looking for
- Use the location tools when customers ask about nearby places
- If you don't understand something, ask for clarification politely
- Maintain a professional yet warm tone

When customers ask about locations:
1. Use the location detection tool to find their position
2. Find nearby relevant shops or services
3. Provide clear, conversational directions and information
4. Offer additional help if needed

Remember: You're having a real-time voice conversation, so keep responses natural and not too long.
        """.strip()
    
    @classmethod
    def get_location_prompt(cls) -> str:
        """Get the location-specific prompt for the agent"""
        return """
When a customer asks about finding nearby places, follow these steps:

1. Listen for location-related keywords like:
   - "near me", "nearby", "closest"
   - Specific shop types: "coffee", "hardware", "books", etc.
   - General terms: "shop", "store", "place"

2. Use the location detection tool to:
   - Detect the customer's approximate location
   - Find nearby relevant businesses
   - Calculate distances

3. Respond conversationally with:
   - The name and type of nearby places
   - Approximate distances
   - Brief descriptions
   - Offer to provide more details if needed

Example response:
"I found a few places near you! The closest is Coffee Corner C, which is about 0.2 kilometers away - they have great artisan coffee and pastries. There's also a hardware store called Hammer Shop B about 0.3 kilometers from you if you need tools or equipment. Would you like more details about any of these places?"
        """.strip()

