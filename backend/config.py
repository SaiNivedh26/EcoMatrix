import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    
    SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT = int(os.getenv("SERVER_PORT", 8000))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10485760))  # 10MB
    ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", "jpg,jpeg,png,mp4,mov,avi").split(",")
    
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))
    MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", 1000))
    
    UPLOAD_DIR = "uploads"
    TEMP_DIR = "temp"
