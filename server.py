import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv("C:/value.env")

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allows all external requests

# Enforce HTTPS when behind Cloudflare Flexible SSL
@app.before_request
def before_request():
    """Force HTTPS when behind Cloudflare Flexible SSL"""
    if request.headers.get("X-Forwarded-Proto") == "http":
        return "Redirecting to HTTPS", 301

# Load Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"

# Check if API Key is Loaded
if not GEMINI_API_KEY:
    raise ValueError("❌ ERROR: Missing GEMINI_API_KEY. Please add it to your .env file.")

# ✅ Homepage Route (Fix for 'Not Found' issue)
@app.route("/")
def home():
    return "<h1>Welcome to Algerian AI Lawyer</h1>"

# ✅ Test Route to Confirm API Works
@app.route("/test")
def test():
    return "This is a test route!"

# ✅ Ensure This Route Exists with GET & POST Support
@app.route("/gemini-api", methods=["POST", "GET"])
def gemini_api():
    if request.method == "GET":
        return jsonify({"message": "✅ API is working! Use POST to send data."})
    
    data = request.json
    prompt = data.get("prompt", "")

    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(GEMINI_API_URL, json=payload, headers=headers)
        response_json = response.json()

        print("DEBUG: API Response:", response_json)  # Debugging line

        if response.status_code == 200:
            return jsonify(response_json)
        else:
            return jsonify({"error": f"Gemini API error {response.status_code}: {response_json}"}), response.status_code

    except Exception as e:
        return jsonify({"error": f"Request failed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
