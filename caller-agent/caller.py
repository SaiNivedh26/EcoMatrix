from sarvamai import SarvamAI
from dotenv import load_dotenv
import os 
client = SarvamAI(
    api_subscription_key=os.getenv("sarvam_api_key")
)

response = client.text.identify_language(
    input="vanakam da mapla"
)

print(f"Request ID: {response.request_id}")
print(f"Language Code: {response.language_code}")  # Output: en-IN
print(f"Script Code: {response.script_code}")      # Output: Latn
