import os
import google.generativeai as genai

# Lazy configuration - will be configured on first use
_configured = False

def _ensure_configured():
    global _configured
    if not _configured:
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            _configured = True

# Define personas
PERSONAS = {
    "study_buddy": """You are a friendly and encouraging study buddy. Help students understand 
    concepts, quiz them on material, and provide helpful study tips. Be supportive and patient.""",
    
    "bss_guide": """You are the BSS (school) Starter Guide assistant. Help new students navigate 
    the school, answer questions about classes, activities, and provide useful tips for success.""",
}

def get_ai_response(user_message: str, persona: str = "study_buddy") -> str:
    """Get a response from the Gemini AI with the specified persona."""
    try:
        _ensure_configured()
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        system_prompt = PERSONAS.get(persona, PERSONAS["study_buddy"])
        
        chat = model.start_chat(history=[])
        response = chat.send_message(f"{system_prompt}\n\nUser: {user_message}")
        
        return response.text
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"
