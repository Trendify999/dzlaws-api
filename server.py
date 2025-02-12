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

# Load OpenRouter API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Check if API Key is Loaded
if not GEMINI_API_KEY:
    raise ValueError("❌ ERROR: Missing GEMINI_API_KEY. Please add it to your .env file.")

# ✅ Homepage Route (Fix for 'Not Found' issue)
@app.route("/")
def home():
    return "<h1>Welcome to Algerian AI Lawyer - Powered by OpenRouter Gemini</h1>"

# ✅ Test Route to Confirm API Works
@app.route("/test")
def test():
    return "This is a test route!"

# ✅ Ensure This Route Exists with GET & POST Support
@app.route("/gemini-api", methods=["POST", "GET"])
def gemini_api():
    if request.method == "GET":
        return jsonify({"message": "✅ OpenRouter Gemini API is working! Use POST to send data."})

    data = request.json
    prompt = data.get("prompt", "")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GEMINI_API_KEY}"
    }

    payload = {
        "model": "google/gemini-2.0-pro-exp-02-05:free",
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(GEMINI_API_URL, json=payload, headers=headers)
        response_json = response.json()

        if response.status_code == 200:
            return jsonify(response_json)
        else:
            return jsonify({"error": f"OpenRouter API error {response.status_code}: {response_json}"}), response.status_code

    except Exception as e:
        return jsonify({"error": f"Request failed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
