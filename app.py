from flask import Flask, render_template, request, jsonify
from backend.gemini_api import get_ai_response
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('api.env')

app = Flask(__name__)

# --- JSON FILE CONFIGURATION ---
# This creates posts.json in your root folder if it doesn't exist
POSTS_FILE = 'posts.json'

def init_json():
    if not os.path.exists(POSTS_FILE):
        with open(POSTS_FILE, 'w') as f:
            json.dump([], f)

init_json()

# --- PAGE ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/review')
def review():
    return render_template('Review.html')

@app.route('/teacher-aura')
def teacher_aura():
    return render_template('MyTeachersAura.html')

@app.route('/my-review')
def my_review():
    return render_template('MyReview.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

# --- FORUM API (JSON VERSION) ---

@app.route('/api/posts', methods=['GET'])
def get_posts():
    try:
        with open(POSTS_FILE, 'r') as f:
            posts = json.load(f)
        return jsonify(posts), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts', methods=['POST'])
def create_post():
    try:
        data = request.get_json()
        content = data.get('content', '').strip()

        if not content:
            return jsonify({'error': 'Content is required'}), 400

        # Create the new post object
        new_post = {
            "id": int(datetime.now().timestamp()),
            "content": content,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Read existing, append, and save
        with open(POSTS_FILE, 'r') as f:
            posts = json.load(f)
        
        posts.insert(0, new_post) # Newest posts at the top

        with open(POSTS_FILE, 'w') as f:
            json.dump(posts, f, indent=4)

        return jsonify({'message': 'Post created successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route for the AI Boyfriend / Study Buddy API logic
@app.route('/study-buddy', methods=['POST'])
def study_buddy():
    data = request.json
    user_message = data.get("message")
    persona = data.get("persona", "study_buddy") # Gets the persona from JS
    
    response = get_ai_response(user_message, persona)
    return jsonify({"response": response})

# Route for the BSS Starter Guide API logic
@app.route('/bss-guide', methods=['POST'])
def bss_guide():
    user_message = request.json.get('message')
    response = get_ai_response(user_message, "bss_guide")
    return jsonify({"reply": response})

if __name__ == '__main__':
    app.run(debug=True, port=5001)


