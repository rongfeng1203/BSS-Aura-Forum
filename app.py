from flask import Flask, render_template, request, jsonify
import os
from Backend.gemini_api import get_ai_response
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
load_dotenv('api.env', override=True)

app = Flask(__name__, static_folder='static', static_url_path='/static')

# --- IN-MEMORY POSTS STORAGE ---
# Serverless functions don't have persistent filesystem, so we use in-memory storage
# For production, consider using a database like Supabase or Neon
posts_storage = []

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
        return jsonify(posts_storage), 200
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

        # Add to in-memory storage
        posts_storage.insert(0, new_post)  # Newest posts at the top

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

# Vercel requires 'app' to be exported for WSGI
# For local development
if __name__ == '__main__':
    app.run(debug=True, port=5001)


