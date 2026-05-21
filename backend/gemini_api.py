# ============================================================
# gemini_api.py
# ------------------------------------------------------------
# Handles all communication between our Flask backend and the
# Google Gemini API. Exposes one function (get_ai_response)
# that takes the user's message + a "persona" flag and returns
# the AI's reply as a plain string.
#
# Two personas share one function:
#   - "study_buddy" (default)  -> Aura, supportive AI companion
#   - "bss_guide"              -> BSS-specific guide with school facts
# Switching personas is done by overwriting the system_instruction
# variable BEFORE the API call. Same function, two AIs.
# ============================================================

import os          # used to read environment variables (API key)
import sys         # imported for future use / debug streams
import requests    # third-party HTTP library; sends POST to Gemini

def get_ai_response(user_input, persona):
    """
    Send the user's message to Google's Gemini API and return the reply.

    Args:
        user_input (str): The raw text the student typed into the chat.
        persona (str): Either "study_buddy" (default Aura) or "bss_guide"
                       (school-context-aware version).

    Returns:
        str: The AI's reply text, OR a friendly fallback message if
             the API call fails for any reason.
    """
    # Load the API key from the environment. Locally it lives in .env;
    # on Vercel it's set in the project's Environment Variables panel.
    # Storing it this way keeps the secret out of the codebase / GitHub.
    api_key = os.getenv("GEMINI_API_KEY")

    # Gemini 2.5 Flash endpoint. We use v1beta because the newer models
    # are only exposed on that path. The API key is appended as a query
    # parameter rather than a header (Google's preferred style for this API).
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite-preview:generateContent?key={api_key}"

    # Gemini expects JSON-encoded bodies, so we declare it in the headers.
    headers = {'Content-Type': 'application/json'}

    # ---- PERSONA SWITCH ----------------------------------------------
    # The default persona is the supportive "AI boyfriend" Aura.
    # If the frontend tells us the user wants the BSS Guide instead,
    # we replace system_instruction with a richer prompt containing
    # school-specific facts. This is the project's "context injection"
    # move: one if-statement = two completely different AI personalities.
    system_instruction = "You are a supportive AI boyfriend named Aura. Use heart emojis."
    if persona == "bss_guide":
        # Hard-coded school knowledge. Edit this block to update what
        # the BSS Guide knows about. The model will quote from these
        # bullet points when answering school-related questions.
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
    # ---- BUILD REQUEST PAYLOAD --------------------------------------
    # Gemini's v1beta API expects a "contents" array of "parts".
    # We concatenate the persona instructions + the user's message into
    # ONE text block so the model treats both as a single prompt.
    data = {
        "contents": [{
            "parts": [{"text": f"Instructions: {system_instruction}\n\nUser: {user_input}"}]
        }]
    }

    # ---- SEND + HANDLE RESPONSE -------------------------------------
    # Everything is wrapped in try/except so a network drop, bad key,
    # or rate-limit error never crashes the page. We always return a
    # string so the frontend can display SOMETHING in the chat window.
    try:
        response = requests.post(url, headers=headers, json=data)

        # A non-200 status means Gemini rejected our request (e.g.
        # invalid model name, quota exceeded, malformed body). We log
        # the raw response for debugging and return a graceful fallback.
        if response.status_code != 200:
            print(f"DEBUG: Status {response.status_code}")
            print(f"DEBUG: Response {response.text}")
            return "Babe, I'm having a moment. Can we try again? 💔"

        # Successful response. Gemini wraps the actual reply text deep
        # inside a nested JSON structure, so we walk down the path:
        # candidates -> [0] -> content -> parts -> [0] -> text
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']

    except Exception as e:
        # Catches network / DNS / timeout errors. Logged to console for
        # debugging; the caller in app.py decides what to display.
        print(f"CONNECTION ERROR: {e}")
        return "Babe, I can't connect right now. Can we try again in a bit? 💔"
