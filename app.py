from flask import Flask, render_template, request, jsonify
import os
import base64
import requests
from dotenv import load_dotenv
from google.genai import types
from model import generate_story

# from transcriber import transcribe
# from werkzeug.utils import secure_filename

load_dotenv()

from pathlib import Path

print("✅ .env file exists?", Path(".env").exists())
print("🔑 GEMINI_API_KEY:", os.getenv("GEMINI_API_KEY"))
print("🌍 GEMINI_ENDPOINT:", os.getenv("GEMINI_ENDPOINT"))

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "MISSING"
GEMINI_ENDPOINT = os.getenv("GEMINI_ENDPOINT") or "MISSING"

if GEMINI_API_KEY == "MISSING":
    raise ValueError("Missing Gemini API key. Did you load the .env file?")


@app.route("/")
def home():
    return render_template('index.html')

@app.route("/loading")
def loading():
    return render_template('loading.html')

@app.route("/generate")
def generate():
    try:
        generate_story(1)
        return jsonify({"message": "Story generated successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Gemini API:
@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    client = genai.Client()

    if "audio" not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    audio_file = request.files["audio"]
    
    # Dynamically use the file extension based on the uploaded file
    file_extension = audio_file.filename.rsplit(".", 1)[-1].lower()
    mime_type = "audio/wav" if file_extension == "wav" else "audio/webm"  # Adjust for other audio types if needed
    
    # Save the file with its original extension
    audio_path = os.path.join(UPLOAD_FOLDER, f"temp_audio.{file_extension}")
    audio_file.save(audio_path)

    try:
        # Open the audio file as raw bytes (without decoding)
        with open(audio_path, "rb") as f:
            audio_bytes = f.read()

        response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[
            'Transcribe only the speech from this audio clip',
            types.Part.from_bytes(
            data=audio_bytes,
            mime_type='audio/mp3',
            )
        ]
        )
        return jsonify({"transcription": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        os.remove(audio_path)  # Clean up the uploaded file after processing


@app.route('/start')
def start():
    print("RAHHH!!!!!!!")
    return "Started"

@app.route('/status')
def check_status():
    import random
    if random.random() < 0.05:
        return jsonify(status="done", result={"RAHH" : "rahhhhh"})
    return jsonify(status="pending")

if __name__ == "__main__":
    app.run(debug=True)