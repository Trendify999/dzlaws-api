import os
import requests
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Allows all external origins, methods, and headers

# Enforce HTTPS when behind Cloudflare Flexible SSL
@app.before_request
def before_request():
    """Force HTTPS when behind Cloudflare Flexible SSL"""
    if request.headers.get("X-Forwarded-Proto") == "http":
        return "Redirecting to HTTPS", 301

# Load MongoDB Connection
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_DB = os.getenv("MONGO_DB")

mongo_uri = f"mongodb+srv://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}/{MONGO_DB}?retryWrites=true&w=majority"
client = MongoClient(mongo_uri)
db = client[MONGO_DB]

# Load Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=" + GEMINI_API_KEY

# Check if API Key is Loaded
if not GEMINI_API_KEY:
    raise ValueError("❌ ERROR: Missing GEMINI_API_KEY. Please add it to your environment variables.")

# Debugging: Print API Key partially (only for deployment testing, remove in production)
print(f"🔍 DEBUG: Loaded GEMINI_API_KEY: {GEMINI_API_KEY[:5]}*****")

# ✅ Homepage Route
@app.route("/")
def home():
    return "<h1>Welcome to Algerian AI Lawyer - Powered by Gemini & MongoDB</h1>"

# ✅ Test Route to Confirm API Works
@app.route("/test")
def test():
    return "This is a test route!"

# ✅ Gemini API Route
@app.route("/gemini-api", methods=["POST", "GET"])
def gemini_api():
    if request.method == "GET":
        return jsonify({"message": "✅ Gemini API is working! Use POST to send data."})

    data = request.json
    prompt = data.get("prompt", "")

    if not prompt:
        return jsonify({"error": "❌ Missing 'prompt' field in request body."}), 400

    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=payload)
        response_json = response.json()

        if response.status_code == 200:
            return jsonify(response_json)
        else:
            return jsonify({"error": f"Gemini API error {response.status_code}: {response_json}"}), response.status_code

    except Exception as e:
        return jsonify({"error": f"Request failed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
