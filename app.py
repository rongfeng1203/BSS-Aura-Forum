from flask import Flask, render_template, request, jsonify
from backend.gemini_api import get_ai_response 

app = Flask(__name__)

# --- ADD THIS NEW ROUTE ---
# This tells Flask: "When someone visits the home page, show the HTML file"
@app.route('/')
def index():
    # Flask looks for this inside your 'templates' folder automatically
    return render_template('GeminiStudyBuddy.html')

# Route for the AI Boyfriend / Study Buddy API logic
@app.route('/study-buddy', methods=['POST'])
def study_buddy():
    user_message = request.json.get('message')
    response = get_ai_response(user_message, "study_buddy")
    return jsonify({"reply": response})

# Route for the BSS Starter Guide API logic
@app.route('/bss-guide', methods=['POST'])
def bss_guide():
    user_message = request.json.get('message')
    response = get_ai_response(user_message, "bss_guide")
    return jsonify({"reply": response})

# --- ADD THIS AT THE VERY BOTTOM ---
if __name__ == '__main__':
    app.run(debug=True)