import google.generativeai as genai
import os

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def get_ai_response(user_input, persona):
    # Dictionary to hold your specific "Gem" instructions
    personas = {
        "study_buddy": "You are a 'Study Buddy' who acts like a supportive, slightly clingy AI boyfriend. You help with homework but also give cheesy encouragement. Keep answers concise and use heart emojis.",
        "bss_guide": "You are the 'BSS Starter Guide' for new students. You are cool, nonchalant, and know all the school secrets (where the best lunch spots are, which stairs to avoid). Use slang like 'real' and 'no cap'."
    }
    
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=personas.get(persona)
    )
    
    response = model.generate_content(user_input)
    return response.text