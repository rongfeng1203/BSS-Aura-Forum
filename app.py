from flask import Flask, render_template, request, jsonify
from backend.gemini_api import get_ai_response  # <--- Import your AI function

app = Flask(__name__)

# Route for the AI Boyfriend / Study Buddy page
@app.route('/study-buddy', methods=['POST'])
def study_buddy():
    user_message = request.json.get('message')
    # Call the function with the "study_buddy" persona
    response = get_ai_response(user_message, "study_buddy")
    return jsonify({"reply": response})


# Route for the BSS Starter Guide
@app.route('/bss-guide', methods=['POST'])
def bss_guide():
    user_message = request.json.get('message')
    # Call the function with the "bss_guide" persona
    response = get_ai_response(user_message, "bss_guide")
    return jsonify({"reply": response})