import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_ai_response(user_input, persona):
    api_key = os.getenv("GEMINI_API_KEY")
    
    # We are using the v1beta endpoint with the 2.0-flash model from your list
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    
    # Setting the vibes
    system_instruction = "You are a supportive AI boyfriend named Aura. Use heart emojis."
    if persona == "bss_guide":
        # Add your school's actual info here!
        school_facts = """
        - Cafeteria: Border's dining hall is always busy around 12:00, try the hub down stairs.
        - Theatre: Best place to lock in, but it's always locked and rumour has it people 💋💋 in there.
        - Skipping class: The best way to skip is to say you have a headache, but the nurse is pretty chill if you just want to hang out in the office. 
        - Community time: No one cares about community time, but it's a good chance to catch up on homework or just vibe with friends. (find a washroom and hide well)
        - Chapel: Teachers will haunt you if you skip one of these, infraction warning!
        - Uniform: 3 in above your knee and BSS socks, who know why they stare at your foot
        - Washroom: Smelliest bathroom is always beside student center, the best one is beside think tank / art room. 
        """
        system_instruction = f"""
        You are the 'BSS Aura Guide'. You are a cool, older student. 
        Use slang like 'real', 'no cap', 'mid', 'cracked', and 'lock in'.
        Keep it helpful but funny. 
        Here is the school info: {school_facts}
        """
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