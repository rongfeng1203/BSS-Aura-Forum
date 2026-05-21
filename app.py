# ============================================================
# app.py  --  BSS Aura Forum, main Flask application
# ------------------------------------------------------------
# This is the "receptionist" of the project. Every browser
# request -- whether it's a page load, an AI chat message,
# or a forum post -- lands here first and gets routed to the
# correct Python function.
#
# Major responsibilities:
#   1. Serve HTML pages (chat, forum, kudos, etc.)
#   2. Expose JSON API endpoints for the frontend's fetch() calls
#   3. Connect to Supabase (cloud Postgres) for persistent storage
#   4. Bridge the frontend to the Gemini AI via gemini_api.py
#
# Deployed on Vercel as a serverless function. Vercel imports
# this module and treats `app` as the WSGI entry point.
# ============================================================

# ---- IMPORTS -------------------------------------------------
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect
from jinja2 import ChoiceLoader, FileSystemLoader
import os                                          # env vars + file paths
import json                                        # read/write JSON files
import tempfile                                    # safe temp folder on Vercel
from backend.gemini_api import get_ai_response     # our Gemini wrapper
from datetime import datetime                      # timestamps for reviews
from dotenv import load_dotenv                     # load .env locally
from supabase import create_client, Client         # Supabase Python client

# Pull values from .env into os.environ. On Vercel this is a no-op
# because Vercel injects env vars directly; locally it lets us keep
# secrets in a gitignored .env file instead of hard-coding them.
load_dotenv()

# ---- FILE PATH CONSTANTS ------------------------------------
# BASE_DIR resolves to the absolute path of this file's folder so
# we can build paths that work both locally and on Vercel's server.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Reviews are stored in a JSON file. The "seed" file ships with the
# repo (default reviews). On Vercel the filesystem is read-only,
# so at runtime we copy the seed into the OS temp directory where
# we CAN write to it.
REVIEWS_SEED_FILE = os.path.join(BASE_DIR, 'templates', 'MyTeacherAura', 'data', 'reviews.json')
REVIEWS_RUNTIME_FILE = os.path.join(tempfile.gettempdir(), 'bss-aura-reviews.json')

# Create the Flask app. static_folder/static_url_path tell Flask to
# serve files from /static/... directly (CSS, JS, images).
app = Flask(__name__, static_folder='static', static_url_path='/static')

# Tell Jinja (Flask's template engine) to look for HTML templates
# in TWO folders: /templates and /Game. This lets us keep the game
# files separate from the main site templates.
app.jinja_loader = ChoiceLoader([
    FileSystemLoader(os.path.join(BASE_DIR, 'templates')),
    FileSystemLoader(os.path.join(BASE_DIR, 'Game')),
])

# ---- SUPABASE CLIENT (lazy-initialised) ---------------------
# Read DB credentials from environment variables -- never hard-coded.
# The actual client object isn't built until get_supabase() is called,
# which avoids wasted connections when a request doesn't need the DB.
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_ANON_KEY")
supabase: Client = None   # module-level cache; populated on first use

# ---- REVIEW STORAGE HELPERS ---------------------------------
# The reviews feature uses a JSON file rather than Supabase. These
# three helpers handle the read/write/initialise flow so the route
# handlers below stay clean.

def get_reviews_file_path():
    """
    Return the path to the writable reviews file.
    If the runtime copy doesn't exist yet (first request after a
    fresh deploy), copy the seed file into the temp folder so we
    have a writable starting point.
    """
    if not os.path.exists(REVIEWS_RUNTIME_FILE):
        # Try to copy the seeded reviews. If the seed is missing or
        # corrupt, start with an empty list so the app still runs.
        try:
            with open(REVIEWS_SEED_FILE, 'r', encoding='utf-8') as source:
                reviews = json.load(source)
        except (FileNotFoundError, json.JSONDecodeError):
            reviews = []

        # Write the (seeded or empty) list to the runtime location.
        with open(REVIEWS_RUNTIME_FILE, 'w', encoding='utf-8') as destination:
            json.dump(reviews, destination, indent=2)

    return REVIEWS_RUNTIME_FILE

def read_reviews():
    """Return the list of all reviews. Falls back to [] on any error."""
    try:
        with open(get_reviews_file_path(), 'r', encoding='utf-8') as reviews_file:
            return json.load(reviews_file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def write_reviews(reviews):
    """Overwrite the reviews file with the given list."""
    with open(get_reviews_file_path(), 'w', encoding='utf-8') as reviews_file:
        json.dump(reviews, reviews_file, indent=2)

def get_supabase() -> Client:
    """
    Return the (cached) Supabase client, building it on first call.

    Lazy initialisation pattern: we don't open the DB connection
    until a request actually needs it. The `global supabase` line
    lets us reuse the same client object across requests instead
    of reconnecting every time -- much faster on Vercel.

    Returns None if Supabase env vars are missing, which lets the
    route handlers respond with a clean error message.
    """
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

# ============================================================
# PAGE ROUTES -- return rendered HTML pages
# ============================================================
# Root URL serves the identity-verification game (Yuwa's module).
# Two routes share one handler so /testweb.html and / both work.
@app.route('/')
@app.route('/testweb.html')
def game():
    return render_template('testweb.html')

# Forum home page (the activity feed where posts appear).
@app.route('/index')
def index():
    return render_template('index.html')

# Generic review page (older entry point, kept for compatibility).
@app.route('/review')
def review():
    return render_template('Review.html')

# Teacher reviews landing page.
@app.route('/teacher-aura')
def teacher_aura():
    return render_template('MyTeachersAura.html')

# The user's own submitted reviews.
@app.route('/my-review')
def my_review():
    return render_template('MyTeacherAura/public/MyReview.html')

# AI chat page -- Aura Study Buddy + BSS Guide live here.
@app.route('/chat')
def chat():
    return render_template('chat.html')

# ---- LEGACY REDIRECTS ---------------------------------------
# Old URLs from earlier project iterations are kept alive as
# redirects so any bookmarks or external links still work.
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

# ---- STATIC ASSET ROUTES ------------------------------------
# Serve raw files (images, JS, etc.) from non-static folders so
# HTML pages can reference them directly.

@app.route('/MyTeacherAura/public/<path:filename>')
def teacher_asset(filename):
    """Stream any file requested from the MyTeacherAura/public folder."""
    return send_from_directory(os.path.join(BASE_DIR, 'MyTeacherAura', 'public'), filename)


@app.route('/game/<path:filename>')
def game_asset(filename):
    """Stream game-related files (sprites, scripts) from /Game."""
    return send_from_directory(os.path.join(BASE_DIR, 'Game'), filename)

# ============================================================
# FORUM API -- JSON endpoints called by the frontend via fetch()
# ============================================================
# Both /api/posts and /api/messages point to the same handlers
# because the route was renamed mid-project; keeping both URLs
# alive prevents the older frontend code from breaking.

@app.route('/api/posts', methods=['GET'])
@app.route('/api/messages', methods=['GET'])
def get_posts():
    """
    Return every forum post as a JSON array, newest first.
    Front-end JS calls this on page load to fill the activity feed.
    """
    try:
        # Lazy-load the Supabase client. If env vars aren't set,
        # return 500 with a clear message instead of crashing.
        client = get_supabase()
        if not client:
            return jsonify({'error': 'Database not configured'}), 500

        # SELECT * FROM posts ORDER BY created_at DESC.
        # .execute() actually fires the request and returns a result
        # object whose .data attribute is a plain Python list.
        result = client.table("posts").select("*").order("created_at", desc=True).execute()
        return jsonify(result.data), 200
    except Exception as e:
        # Any unexpected error is surfaced as JSON so the frontend
        # can display it instead of getting an HTML error page.
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts', methods=['POST'])
@app.route('/api/messages', methods=['POST'])
def create_post():
    """
    Insert a new forum post into Supabase.
    Expects JSON body: {"content": "<message text>"}
    """
    try:
        client = get_supabase()
        if not client:
            return jsonify({'error': 'Database not configured'}), 500

        # Pull the JSON body from the request. .get_json() returns
        # None if the body is missing/invalid, so we check for that.
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data received'}), 400

        # Strip whitespace so blank-but-not-empty submissions
        # (e.g. just spaces) are also rejected.
        content = data.get('content', '').strip()

        if not content:
            return jsonify({'error': 'Content is required'}), 400

        # Insert into Supabase
        result = client.table("posts").insert({"content": content}).execute()

        return jsonify({'message': 'Post created successfully', 'post': result.data[0]}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ---- REVIEWS API ---------------------------------------------
# These endpoints power the "Kudos your Teacher" feature.

@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    """Return all teacher reviews as a JSON array."""
    return jsonify(read_reviews()), 200

@app.route('/rate', methods=['POST'])
def create_review():
    """
    Append a new teacher review to the reviews JSON file.
    Expects JSON body: {"course": str, "teacher": str, "rating": str}
    """
    try:
        # `or {}` makes sure `data` is always a dict, even if the
        # body is empty -- prevents AttributeError on .get().
        data = request.get_json() or {}
        course = data.get('course', '').strip()
        teacher = data.get('teacher', '').strip()
        rating = data.get('rating', '👍')   # default thumbs-up if none given

        # Both course and teacher are required; rating has a default.
        if not course or not teacher:
            return jsonify({'error': 'Course and teacher are required'}), 400

        # Read existing reviews, append the new one, write the list back.
        # Storing a timestamp lets the frontend sort by recency later.
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

# ============================================================
# AI CHAT API -- bridges the chat frontend to gemini_api.py
# ============================================================

# Receives a chat message from the browser, picks a persona, asks
# Gemini for a reply, and sends the reply back as JSON.
@app.route('/study-buddy', methods=['POST'])
def study_buddy():
    data = request.json
    user_message = data.get("message")
    # The frontend tells us which persona is active via the JSON body.
    # Default to "study_buddy" if the field is missing.
    persona = data.get("persona", "study_buddy")
    
    # Delegate the actual API call to gemini_api.py and return
    # whatever string it gives us, wrapped in JSON for the frontend.
    response = get_ai_response(user_message, persona)
    return jsonify({"response": response})

# Legacy endpoint kept for older frontend code that pre-dates the
# persona-switching design. Hard-codes the BSS Guide persona.
@app.route('/bss-guide', methods=['POST'])
def bss_guide():
    user_message = request.json.get('message')
    response = get_ai_response(user_message, "bss_guide")
    return jsonify({"reply": response})

# ============================================================
# ENTRY POINT
# ============================================================
# Vercel imports this file and uses the module-level `app`
# object as the WSGI application -- no extra code needed there.
# The block below ONLY runs when we execute `python app.py`
# directly during local development.
if __name__ == '__main__':
    app.run(debug=True, port=5001)
