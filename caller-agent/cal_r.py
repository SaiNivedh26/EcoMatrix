from sarvamai import SarvamAI
from dotenv import load_dotenv
import os 

load_dotenv()

client = SarvamAI(
    api_subscription_key=os.getenv("sarvam_api_key"),
)

response = client.speech_to_text.translate(
    file=open("mala.wav", "rb"),
    model="saaras:v2.5"
)

print(response)
