import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv("value.env")

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allows all external requests

# Enforce HTTPS when behind Cloudflare Flexible SSL
@app.before_request
def before_request():
    """Force HTTPS when behind Cloudflare Flexible SSL"""
    if request.headers.get("X-Forwarded-Proto") == "http":
        return "Redirecting to HTTPS", 301

# Load DeepSeek API Key
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Check if API Key is Loaded
if not DEEPSEEK_API_KEY:
    raise ValueError("❌ ERROR: Missing DEEPSEEK_API_KEY. Please add it to value.env in Git.")

# ✅ Homepage Route (Fix for 'Not Found' issue)
@app.route("/")
def home():
    return "<h1>Welcome to Algerian AI Lawyer - Powered by DeepSeek</h1>"

# ✅ Test Route to Confirm API Works
@app.route("/test")
def test():
    return "This is a test route!"

# ✅ Ensure This Route Exists with GET & POST Support
@app.route("/deepseek-api", methods=["POST", "GET"])
def deepseek_api():
    if request.method == "GET":
        return jsonify({"message": "✅ API is working! Use POST to send data."})
    
    data = request.json
    prompt = data.get("prompt", "")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 512
    }

    try:
        response = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers)
        response_json = response.json()

        print("DEBUG: API Response:", response_json)  # Debugging line

        if response.status_code == 200:
            return jsonify(response_json)
        else:
            return jsonify({"error": f"DeepSeek API error {response.status_code}: {response_json}"}), response.status_code

    except Exception as e:
        return jsonify({"error": f"Request failed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)