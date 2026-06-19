import os
from google import genai
from config.settings import settings

key = settings.google_api_key.get_secret_value()
client = genai.Client(api_key=key, http_options={'api_version': 'v1beta'})

try:
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents='Hello, speak 1 word.',
    )
    print(f"SUCCESS: {response.text}")
except Exception as e:
    print(f"FAILED with error: {e}")
