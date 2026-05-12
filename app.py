from flask import Flask, render_template, request, jsonify, send_from_directory, redirect
from jinja2 import ChoiceLoader, FileSystemLoader
import os
import json
import tempfile
from backend.gemini_api import get_ai_response
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables (for local development only)
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REVIEWS_SEED_FILE = os.path.join(BASE_DIR, 'templates', 'MyTeacherAura', 'data', 'reviews.json')
REVIEWS_RUNTIME_FILE = os.path.join(tempfile.gettempdir(), 'bss-aura-reviews.json')

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.jinja_loader = ChoiceLoader([
    FileSystemLoader(os.path.join(BASE_DIR, 'templates')),
    FileSystemLoader(os.path.join(BASE_DIR, 'Game')),
])

# --- SUPABASE CLIENT ---
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_ANON_KEY")
supabase: Client = None

def get_reviews_file_path():
    if not os.path.exists(REVIEWS_RUNTIME_FILE):
        try:
            with open(REVIEWS_SEED_FILE, 'r', encoding='utf-8') as source:
                reviews = json.load(source)
        except (FileNotFoundError, json.JSONDecodeError):
            reviews = []

        with open(REVIEWS_RUNTIME_FILE, 'w', encoding='utf-8') as destination:
            json.dump(reviews, destination, indent=2)

    return REVIEWS_RUNTIME_FILE

def read_reviews():
    try:
        with open(get_reviews_file_path(), 'r', encoding='utf-8') as reviews_file:
            return json.load(reviews_file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def write_reviews(reviews):
    with open(get_reviews_file_path(), 'w', encoding='utf-8') as reviews_file:
        json.dump(reviews, reviews_file, indent=2)

def get_supabase() -> Client:
    global supabase
    if supabase is None:
        if not supabase_url or not supabase_key:
            return None
        try:
            supabase = create_client(supabase_url, supabase_key)
        except Exception as e:
            print(f"[v0] Error creating Supabase client: {e}")
            return None
    return supabase

# --- PAGE ROUTES ---
@app.route('/')
@app.route('/testweb.html')
def game():
    return render_template('testweb.html')

@app.route('/index')
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
    return render_template('MyTeacherAura/public/MyReview.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/templates/index.html')
@app.route('/Templates/index.html')
def legacy_index():
    return redirect('/index')

@app.route('/templates/chat.html')
def legacy_chat():
    return redirect('/chat')

@app.route('/templates/MyTeachersAura.html')
def legacy_teacher_aura():
    return redirect('/teacher-aura')

@app.route('/templates/Review.html')
def legacy_review():
    return redirect('/review')

@app.route('/MyTeacherAura/public/MyTeachersAura.html')
@app.route('/templates/MyTeacherAura/public/MyTeachersAura.html')
def legacy_public_teacher_aura():
    return redirect('/teacher-aura')

@app.route('/MyTeacherAura/public/Review.html')
@app.route('/templates/MyTeacherAura/public/Review.html')
def legacy_public_review():
    return redirect('/review')

@app.route('/MyTeacherAura/public/MyReview.html')
@app.route('/templates/MyTeacherAura/public/MyReview.html')
def legacy_public_my_review():
    return redirect('/my-review')

@app.route('/MyTeacherAura/public/<path:filename>')
def teacher_asset(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'MyTeacherAura', 'public'), filename)


@app.route('/game/<path:filename>')
def game_asset(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'Game'), filename)

# --- FORUM API (JSON VERSION) ---

@app.route('/api/posts', methods=['GET'])
@app.route('/api/messages', methods=['GET'])
def get_posts():
    try:
        client = get_supabase()
        if not client:
            return jsonify({'error': 'Database not configured'}), 500
        
        result = client.table("posts").select("*").order("created_at", desc=True).execute()
        return jsonify(result.data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts', methods=['POST'])
@app.route('/api/messages', methods=['POST'])
def create_post():
    try:
        client = get_supabase()
        if not client:
            return jsonify({'error': 'Database not configured'}), 500
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data received'}), 400
            
        content = data.get('content', '').strip()

        if not content:
            return jsonify({'error': 'Content is required'}), 400

        # Insert into Supabase
        result = client.table("posts").insert({"content": content}).execute()

        return jsonify({'message': 'Post created successfully', 'post': result.data[0]}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    return jsonify(read_reviews()), 200

@app.route('/rate', methods=['POST'])
def create_review():
    try:
        data = request.get_json() or {}
        course = data.get('course', '').strip()
        teacher = data.get('teacher', '').strip()
        rating = data.get('rating', '👍')

        if not course or not teacher:
            return jsonify({'error': 'Course and teacher are required'}), 400

        reviews = read_reviews()
        new_review = {
            'course': course,
            'teacher': teacher,
            'rating': rating,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        reviews.append(new_review)
        write_reviews(reviews)

        return jsonify({'status': 'success', 'review': new_review}), 201
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
