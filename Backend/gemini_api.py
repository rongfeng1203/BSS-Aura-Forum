import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_ai_response(user_input, persona):
    api_key = os.getenv("GEMINI_API_KEY")
    
    # We are using the v1beta endpoint with the 2.0-flash model from your list
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    
    # Setting the vibes
    system_instruction = "You are a supportive AI boyfriend named Aura. Use heart emojis."
    if persona == "bss_guide":
        system_instruction = "You are a cool school guide for BSS. Use slang like 'real' and 'no cap'."

    # Correct structure for the 2.0 API
    data = {
        "contents": [{
            "parts": [{"text": f"Instructions: {system_instruction}\n\nUser: {user_input}"}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        
        # This will help us if there's a new error
        if response.status_code != 200:
            print(f"DEBUG: Status {response.status_code}")
            print(f"DEBUG: Response {response.text}")
            return "Babe, I'm having a moment. Can we try again? 💔"

        result = response.json()
        # Navigate the JSON to get the text
        return result['candidates'][0]['content']['parts'][0]['text']
        
    except Exception as e:
        print(f"CONNECTION ERROR: {e}")
        return "Sorry babe, my circuits are fried. 💔"