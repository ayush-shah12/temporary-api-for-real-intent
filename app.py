import json
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import requests
import os
import psycopg2

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app)

DATABASE_URL = os.environ['DATABASE_URL']

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)


def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email VARCHAR(255) UNIQUE NOT NULL,
            api_key UUID UNIQUE NOT NULL
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()

create_table()

@app.route('/getuser/', methods=['GET'])
@cross_origin()
def get_user():
    """Fetch user details by api_key"""
    api_key = request.args.get('api_key')
    if not api_key:
        return jsonify({"error": "api_key is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM users WHERE api_key = %s;", (api_key,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        return jsonify({"email": user[0]}), 200
    else:
        return jsonify({"error": "User not found"}), 404

@app.route('/register', methods=['POST'])
@cross_origin()
def register():
    """Register a new user with email and generated api_key"""
    data = request.get_json()

    email = data.get('email')
    if not email:
        return jsonify({"error": "Email is required"}), 400

    api_key = str(uuid.uuid4())

    # Save the user in the database
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (email, api_key) VALUES (%s, %s);", (email, api_key))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"email": email, "api_key": api_key}), 201
    except Exception as e:
        return jsonify({"error": f"Error occurred: {str(e)}"}), 500

@app.route('/', methods=['GET'])
def home():
    print("Welcome to the API")
    return "Welcome to the API"