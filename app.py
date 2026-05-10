from flask import Flask, render_template, request, jsonify, send_from_directory
from jinja2 import ChoiceLoader, FileSystemLoader
import os
from backend.gemini_api import get_ai_response
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()
load_dotenv('api.env', override=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.jinja_loader = ChoiceLoader([
    FileSystemLoader(os.path.join(BASE_DIR, 'templates')),
    FileSystemLoader(os.path.join(BASE_DIR, 'Game')),
])

# --- SUPABASE CLIENT ---
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_ANON_KEY")
supabase: Client = None

print(f"[v0] SUPABASE_URL configured: {bool(supabase_url)}")
print(f"[v0] SUPABASE_ANON_KEY configured: {bool(supabase_key)}")

def get_supabase() -> Client:
    global supabase
    if supabase is None:
        if not supabase_url or not supabase_key:
            print(f"[v0] Missing Supabase config - URL: {bool(supabase_url)}, KEY: {bool(supabase_key)}")
            return None
        try:
            supabase = create_client(supabase_url, supabase_key)
            print("[v0] Supabase client created successfully")
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
    return render_template('MyReview.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')


@app.route('/game/<path:filename>')
def game_asset(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'Game'), filename)

# --- FORUM API (JSON VERSION) ---

@app.route('/api/posts', methods=['GET'])
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
