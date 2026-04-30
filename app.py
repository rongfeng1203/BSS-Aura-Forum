from flask import Flask, render_template, request, jsonify
from backend.gemini_api import get_ai_response
import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv('api.env')

app = Flask(__name__)

# Database configuration
db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

# Initialize database on startup
init_db()

# --- ADD THIS NEW ROUTE ---
# This tells Flask: "When someone visits the home page, show the HTML file"
@app.route('/')
def index():
    # Flask looks for this inside your 'templates' folder automatically
    return render_template('chat.html')

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

# Forum routes
@app.route('/api/posts', methods=['POST'])
def create_post():
    try:
        data = request.get_json()
        content = data.get('content', '').strip()

        if not content:
            return jsonify({'error': 'Content is required'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO posts (content) VALUES (%s)', (content,))
        conn.commit()

        post_id = cursor.lastrowid
        cursor.close()
        conn.close()

        return jsonify({'message': 'Post created successfully', 'id': post_id}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts', methods=['GET'])
def get_posts():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT id, content, created_at FROM posts ORDER BY created_at DESC')
        posts = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify(posts), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- ADD THIS AT THE VERY BOTTOM ---
if __name__ == '__main__':
    app.run(debug=True, port=5001) # Change 5000 to 5001