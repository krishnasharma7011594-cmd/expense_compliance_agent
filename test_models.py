import os
from google import genai
from config.settings import settings

key = settings.google_api_key.get_secret_value()
client = genai.Client(api_key=key)

for model in ['gemini-1.5-flash', 'gemini-1.5-flash-8b']:
    print(f"Testing model: {model}")
    try:
        response = client.models.generate_content(
            model=model,
            contents='Hello',
        )
        print(f"SUCCESS with {model}: {response.text}")
        break
    except Exception as e:
        print(f"FAILED with {model}: {e}")
