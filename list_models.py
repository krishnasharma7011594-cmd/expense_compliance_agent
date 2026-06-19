import os
from google import genai
from config.settings import settings

key = settings.google_api_key.get_secret_value()
client = genai.Client(api_key=key)

try:
    print("Listing models...")
    for model in client.models.list():
        print(f"- {model.name}")
except Exception as e:
    print(f"FAILED to list models: {e}")
