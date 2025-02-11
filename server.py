import os
import requests
import zipfile
import wave
import json
from flask import Flask, request, jsonify
from vosk import Model, KaldiRecognizer

# Vosk Model Configuration
VOSK_MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-ar-0.22.zip"
MODEL_PATH = "vosk-model-ar"

def download_vosk_model():
    """Download and extract Vosk model if not already present."""
    if not os.path.exists(MODEL_PATH):
        print("Downloading Vosk Arabic model... ⏳")
        response = requests.get(VOSK_MODEL_URL, stream=True)
        with open("vosk-model.zip", "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)

        print("Extracting model... ⏳")
        with zipfile.ZipFile("vosk-model.zip", "r") as zip_ref:
            zip_ref.extractall(".")

        os.rename("vosk-model-ar-0.22", MODEL_PATH)
        os.remove("vosk-model.zip")
        print("Vosk model ready! ✅")

# Download the model at server startup
download_vosk_model()

# Initialize Flask App
app = Flask(__name__)

# Load Vosk Model
model = Model(MODEL_PATH)

@app.route("/test", methods=["GET"])
def test():
    return "✅ Vosk-powered API is running!"

@app.route("/voice-to-text", methods=["POST"])
def voice_to_text():
    """Process uploaded audio and return transcribed text."""
    if "audio" not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    audio_file = request.files["audio"]
    wf = wave.open(audio_file, "rb")

    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        return jsonify({"error": "Invalid audio format"}), 400

    rec = KaldiRecognizer(model, wf.getframerate())
    data = wf.readframes(wf.getnframes())

    if rec.AcceptWaveform(data):
        result = json.loads(rec.Result())
        return jsonify({"text": result.get("text", "")})
    else:
        return jsonify({"error": "Could not process audio"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
