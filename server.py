import os
import requests
import zipfile
import wave
import json
from flask import Flask, request, jsonify
from vosk import Model, KaldiRecognizer

app = Flask(__name__)

# Google Drive File IDs for Arabic & French models
VOSK_MODEL_AR_ID = "1bbrhsSJeadP4ssXavleeSOtzF59kqnPl"
VOSK_MODEL_FR_ID = "1qMyI9vvw5TpxyINbMnOMf2WhGhtJh1rE"

MODEL_PATH_AR = "vosk-model-ar"
MODEL_PATH_FR = "vosk-model-fr"

def download_from_google_drive(file_id, destination):
    """Download a large file from Google Drive."""
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()
    response = session.get(URL, params={"id": file_id}, stream=True)
    token = None

    for key, value in response.cookies.items():
        if key.startswith("download_warning"):
            token = value
            break

    if token:
        response = session.get(URL, params={"id": file_id, "confirm": token}, stream=True)

    with open(destination, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

def extract_model(zip_path, model_folder):
    """Extract model from zip file."""
    print(f"Extracting {zip_path}... ⏳")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(".")
    os.rename(zip_path.replace(".zip", ""), model_folder)
    os.remove(zip_path)
    print(f"{model_folder} is ready! ✅")

# Download & Extract Models if Not Present
if not os.path.exists(MODEL_PATH_AR):
    print("Downloading Arabic Vosk model... ⏳")
    download_from_google_drive(VOSK_MODEL_AR_ID, "vosk-model-ar.zip")
    extract_model("vosk-model-ar.zip", MODEL_PATH_AR)

if not os.path.exists(MODEL_PATH_FR):
    print("Downloading French Vosk model... ⏳")
    download_from_google_drive(VOSK_MODEL_FR_ID, "vosk-model-fr.zip")
    extract_model("vosk-model-fr.zip", MODEL_PATH_FR)

# Load Vosk Models
model_ar = Model(MODEL_PATH_AR)
model_fr = Model(MODEL_PATH_FR)

@app.route("/test")
def test():
    return "✅ Vosk-powered API is running!"

@app.route("/voice-to-text", methods=["POST"])
def voice_to_text():
    """Process uploaded audio and return transcribed text."""
    if "audio" not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    language = request.form.get("language", "ar")  # Default to Arabic
    model = model_ar if language == "ar" else model_fr

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
