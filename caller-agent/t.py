from sarvamai import SarvamAI
from sarvamai.play import save
import os
from dotenv import load_dotenv

load_dotenv()

client = SarvamAI(api_subscription_key=os.getenv("sarvam_api_key"))
# Convert text to speech
audio = client.text_to_speech.convert(
  target_language_code="ta-IN",
  text="Indha location Building Block A Pakathil ulladhu",
  model="bulbul:v2",
  speaker="vidya"
)
save(audio, "output1.wav")
