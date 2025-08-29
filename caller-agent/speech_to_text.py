from sarvamai import SarvamAI
from dotenv import load_dotenv
import os 
import re
import subprocess
import tempfile

load_dotenv()

class SpeechToTextService:
    def __init__(self):
        self.client = SarvamAI(
            api_subscription_key=os.getenv("sarvam_api_key"),
        )
    
    def convert_to_wav_if_needed(self, audio_file_path):
        """
        Convert audio file to WAV format if it's not already WAV
        Returns path to WAV file (original or converted)
        """
        file_extension = os.path.splitext(audio_file_path)[1].lower()
        
        if file_extension == '.wav':
            return audio_file_path
        
        try:
            # Create temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                temp_wav_path = temp_wav.name
            
            # Convert using ffmpeg (if available)
            try:
                subprocess.run([
                    'ffmpeg', '-i', audio_file_path, 
                    '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1',
                    '-y', temp_wav_path
                ], check=True, capture_output=True)
                
                return temp_wav_path
                
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback: try with different parameters or return original
                print(f"Warning: Could not convert {file_extension} to WAV. Trying original file...")
                os.unlink(temp_wav_path)  # Clean up temp file
                return audio_file_path
                
        except Exception as e:
            print(f"Error in audio conversion: {e}")
            return audio_file_path

    def transcribe_audio(self, audio_file_path):
        """
        Transcribe audio file and return transcript and language code
        Returns dict with request_id, transcript, language_code, diarized_transcript
        """
        wav_file_path = None
        try:
            # Convert to WAV if needed
            wav_file_path = self.convert_to_wav_if_needed(audio_file_path)
            
            response = self.client.speech_to_text.translate(
                file=open(wav_file_path, "rb"),
                model="saaras:v2.5"
            )
            
            # Parse the response string to extract information
            response_str = str(response)
            
            # Extract request_id
            request_id_match = re.search(r"request_id='([^']+)'", response_str)
            request_id = request_id_match.group(1) if request_id_match else None
            
            # Extract transcript
            transcript_match = re.search(r"transcript='([^']+)'", response_str)
            transcript = transcript_match.group(1) if transcript_match else None
            
            # Extract language_code
            language_code_match = re.search(r"language_code='([^']+)'", response_str)
            language_code = language_code_match.group(1) if language_code_match else None
            
            # Extract diarized_transcript
            diarized_match = re.search(r"diarized_transcript=([^\s]+)", response_str)
            diarized_transcript = diarized_match.group(1) if diarized_match else None
            
            return {
                "success": True,
                "request_id": request_id,
                "transcript": transcript,
                "language_code": language_code,
                "diarized_transcript": diarized_transcript,
                "raw_response": response_str
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "request_id": None,
                "transcript": None,
                "language_code": None,
                "diarized_transcript": None
            }
        finally:
            # Clean up temporary WAV file if it was created
            if wav_file_path and wav_file_path != audio_file_path:
                try:
                    os.unlink(wav_file_path)
                except:
                    pass

def main():
    """Test function - can be called directly"""
    service = SpeechToTextService()
    result = service.transcribe_audio("mala.wav")
    print(f"Request ID: {result['request_id']}")
    print(f"Transcript: {result['transcript']}")
    print(f"Language Code: {result['language_code']}")
    print(f"Diarized Transcript: {result['diarized_transcript']}")
    
if __name__ == "__main__":
    main()
