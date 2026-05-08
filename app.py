from flask import Flask, render_template, request, jsonify, send_from_directory
from jinja2 import ChoiceLoader, FileSystemLoader
import json
import os
from Backend.gemini_api import get_ai_response
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
load_dotenv('api.env', override=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.jinja_loader = ChoiceLoader([
    FileSystemLoader(os.path.join(BASE_DIR, 'templates')),
    FileSystemLoader(os.path.join(BASE_DIR, 'Game')),
    FileSystemLoader(os.path.join(BASE_DIR, 'MyTeacherAura', 'public')),
])

# --- JSON FILE STORAGE ---
posts_storage = []
messages_file = os.path.join(BASE_DIR, 'messages.json')
reviews_file = os.path.join(BASE_DIR, 'MyTeacherAura', 'data', 'reviews.json')


def read_json_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return parse_json_list(file.read())
    except (FileNotFoundError, ValueError):
        return []


def parse_json_list(raw_json):
    data = json.loads(raw_json or '[]')
    return data if isinstance(data, list) else []


def write_json_file(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2)

# --- PAGE ROUTES ---
@app.route('/testweb.html')
@app.route('/')
def game():
    return render_template('testweb.html')

@app.route('/index.html')
@app.route('/index')
def forum():
    return render_template('index.html')

@app.route('/Review.html')
@app.route('/review')
def review():
    return render_template('Review.html')

@app.route('/MyTeachersAura.html')
@app.route('/teacher-aura')
def teacher_aura():
    return render_template('MyTeachersAura.html')

@app.route('/MyReview.html')
@app.route('/my-review')
def my_review():
    return render_template('MyReview.html')

@app.route('/chat.html')
@app.route('/chat')
def chat():
    return render_template('chat.html')


@app.route('/game/<path:filename>')
def game_asset(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'Game'), filename)


@app.route('/teacher-assets/<path:filename>')
def teacher_asset(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'MyTeacherAura', 'public'), filename)

# --- FORUM API (JSON VERSION) ---

@app.route('/api/posts', methods=['GET'])
@app.route('/api/messages', methods=['GET'])
def get_posts():
    try:
        saved_posts = read_json_file(messages_file)
        return jsonify(saved_posts or posts_storage), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts', methods=['POST'])
@app.route('/api/messages', methods=['POST'])
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
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Add to in-memory storage
        posts_storage.insert(0, new_post)  # Newest posts at the top
        saved_posts = read_json_file(messages_file)
        saved_posts.insert(0, new_post)
        write_json_file(messages_file, saved_posts)

        return jsonify({'message': 'Post created successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    try:
        return jsonify(read_json_file(reviews_file)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/rate', methods=['POST'])
def create_review():
    try:
        data = request.get_json()
        course = data.get('course', '').strip()
        teacher = data.get('teacher', '').strip()
        rating = data.get('rating', 'thumbs up')

        if not course or not teacher:
            return jsonify({'error': 'Course and teacher are required'}), 400

        reviews = read_json_file(reviews_file)
        reviews.append({
            "course": course,
            "teacher": teacher,
            "rating": rating,
            "timestamp": datetime.now().isoformat()
        })
        write_json_file(reviews_file, reviews)
        return jsonify({'status': 'success'}), 201

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
