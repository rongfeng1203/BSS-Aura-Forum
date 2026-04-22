import google.generativeai as genai
import os

# Configure the API key once at the top
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def get_ai_response(user_input, persona):
    # 1. Define your personalities
    personas = {
        "study_buddy": "You are a 'Study Buddy' who acts like a supportive, slightly clingy AI boyfriend. You help with homework but also give cheesy encouragement. Keep answers concise and use heart emojis.",
        "bss_guide": "You are the 'BSS Starter Guide' for new students. You are cool, nonchalant, and know all the school secrets (where the best lunch spots are, which stairs to avoid). Use slang like 'real' and 'no cap'."
    }
    
    # 2. The "Safety Net" (Try/Except)
    try:
        # Initialize the model with the specific persona instruction
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=personas.get(persona, "You are a helpful assistant.")
        )
        
        # Make the actual API call
        response = model.generate_content(user_input)
        
        # Return the successful text
        return response.text
        
    except Exception as e:
        # If anything goes wrong, catch the error and return a nonchalant fallback
        print(f"Error calling Gemini API: {e}")
        
        if persona == "study_buddy":
            return "Sorry babe, my circuits are fried right now. I'm literally crying. Try again later? 💔"
        else:
            return "Server's cooked right now, real. Try again in a bit. 💀"