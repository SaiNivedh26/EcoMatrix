from sarvamai import SarvamAI
from sarvamai.play import save
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

class TextToSpeechService:
    def __init__(self):
        self.client = SarvamAI(api_subscription_key=os.getenv("sarvam_api_key"))
        # Ensure output directory exists
        os.makedirs("caller-agent/audio_output", exist_ok=True)
    
    def convert_text_to_speech(self, text, language_code="ta-IN", speaker="vidya", output_filename=None):
        """
        Convert text to speech and save as audio file
        
        Args:
            text (str): Text to convert to speech
            language_code (str): Target language code (default: ta-IN)
            speaker (str): Voice speaker (default: vidya)
            output_filename (str): Optional custom filename
            
        Returns:
            dict: Result with success status, file_path, and other info
        """
        try:
            # Generate unique filename if not provided
            if output_filename is None:
                output_filename = f"tts_output_{uuid.uuid4().hex[:8]}.wav"
            
            # Ensure the filename has .wav extension
            if not output_filename.endswith('.wav'):
                output_filename += '.wav'
            
            # Full path for the output file
            output_path = os.path.join("caller-agent", "audio_output", output_filename)
            
            # Convert text to speech
            audio = self.client.text_to_speech.convert(
                target_language_code=language_code,
                text=text,
                model="bulbul:v2",
                speaker=speaker
            )
            
            # Save the audio file
            save(audio, output_path)
            
            return {
                "success": True,
                "file_path": output_path,
                "filename": output_filename,
                "text": text,
                "language_code": language_code,
                "speaker": speaker
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": None,
                "filename": None,
                "text": text,
                "language_code": language_code,
                "speaker": speaker
            }
    
    def get_supported_languages(self):
        """Return list of supported language codes"""
        return [
            "hi-IN",  # Hindi
            "ta-IN",  # Tamil
            "te-IN",  # Telugu
            "kn-IN",  # Kannada
            "ml-IN",  # Malayalam
            "bn-IN",  # Bengali
            "gu-IN",  # Gujarati
            "mr-IN",  # Marathi
            "pa-IN",  # Punjabi
            "or-IN",  # Odia
            "as-IN",  # Assamese
            "en-IN"   # English (Indian)
        ]
    
    def get_supported_speakers(self):
        """Return list of supported speakers"""
        return [
            "vidya",
            "meera", 
            "arjun",
            "ananya"
        ]

def main():
    """Test function"""
    service = TextToSpeechService()
    
    # Test with sample text
    result = service.convert_text_to_speech(
        text="Indha location Building Block A Pakathil ulladhu",
        language_code="ta-IN",
        speaker="vidya"
    )
    
    if result["success"]:
        print(f"Audio generated successfully: {result['file_path']}")
    else:
        print(f"Error: {result['error']}")

if __name__ == "__main__":
    main()
