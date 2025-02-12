import os
import requests
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allows all external requests

# Enforce HTTPS when behind Cloudflare Flexible SSL
@app.before_request
def before_request():
    """Force HTTPS when behind Cloudflare Flexible SSL"""
    if request.headers.get("X-Forwarded-Proto") == "http":
        return "Redirecting to HTTPS", 301

# Load OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

# Check if API Key is Loaded
if not OPENAI_API_KEY:
    raise ValueError("❌ ERROR: Missing OPENAI_API_KEY. Please add it to your environment variables.")

# ✅ Homepage Route
@app.route("/")
def home():
    return "<h1>Welcome to Algerian AI Lawyer - Powered by OpenAI GPT</h1>"

# ✅ Test Route to Confirm API Works
@app.route("/test")
def test():
    return "This is a test route!"

# ✅ OpenAI GPT Route
@app.route("/openai-api", methods=["POST", "GET"])
def openai_api():
    if request.method == "GET":
        return jsonify({"message": "✅ OpenAI API is working! Use POST to send data."})

    data = request.json
    prompt = data.get("prompt", "")

    if not prompt:
        return jsonify({"error": "❌ Missing 'prompt' field in request body."}), 400

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    payload = {
        "model": "gpt-4",
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(OPENAI_API_URL, headers=headers, json=payload)
        response_json = response.json()

        if response.status_code == 200:
            return jsonify(response_json)
        else:
            return jsonify({"error": f"OpenAI API error {response.status_code}: {response_json}"}), response.status_code

    except Exception as e:
        return jsonify({"error": f"Request failed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)