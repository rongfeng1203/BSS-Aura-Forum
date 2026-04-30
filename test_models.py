import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

try:
    response = requests.get(url)
    models = response.json()
    print("--- AVAILABLE MODELS FOR YOUR KEY ---")
    if 'models' in models:
        for m in models['models']:
            print(f"Model Name: {m['name']} | Supported Methods: {m['supportedGenerationMethods']}")
    else:
        print(f"Error: {models}")
except Exception as e:
    print(f"Connection failed: {e}")