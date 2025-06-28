from flask import Flask, render_template, request, jsonify
import os
import base64
import requests
from dotenv import load_dotenv
from google.genai import types

# from transcriber import transcribe
# from werkzeug.utils import secure_filename

load_dotenv()

from pathlib import Path

# print("✅ .env file exists?", Path(".env").exists())
# print("🔑 GEMINI_API_KEY:", os.getenv("GEMINI_API_KEY"))
# print("🌍 GEMINI_ENDPOINT:", os.getenv("GEMINI_ENDPOINT"))

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

# Gemini API:
def transcribe_audio():
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

        # Create the payload in the inline format with raw binary data
        payload = {
            "contents": [
                "Describe this audio clip",  # Optional prompt
                {
                    "inline_data": {
                        "mime_type": mime_type,  # Use the correct mime type based on the file type
                        "data": base64.b64encode(audio_bytes).decode("utf-8")  # Base64 encode the audio
                    }
                }
            ]
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GEMINI_API_KEY}"
        }

        # Make the API request to Gemini
        response = requests.post(GEMINI_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()

        # Parse the Gemini API response
        gemini_response = response.json()

        # Extract the transcription (if available)
        text = gemini_response.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")

        return jsonify({"transcription": text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        os.remove(audio_path)  # Clean up the uploaded file after processing



# @app.route("/transcribe", methods=["POST"])
# def transcribe_audio():
#     if "audio" not in request.files:
#         return jsonify({"error": "No audio file uploaded"}), 400
# 
#     audio_file = request.files["audio"]
#     audio_path = os.path.join(UPLOAD_FOLDER, "temp_audio.webm")
#     audio_file.save(audio_path)
# 
#     try:
#         # Convert audio to base64 inline format
#         with open(audio_path, "rb") as f:
#             encoded_audio = base64.b64encode(f.read()).decode("utf-8")
# 
#         payload = {
#             "contents": [{
#                 "role": "user",
#                 "parts": [{
#                     "inline_data": {
#                         "mime_type": "audio/webm",
#                         "data": encoded_audio
#                     }
#                 }]
#             }]
#         }
# 
#         headers = {
#             "Content-Type": "application/json",
#             "Authorization": f"Bearer {GEMINI_API_KEY}"
#         }
# 
#         response = requests.post(GEMINI_ENDPOINT, headers=headers, json=payload)
#         response.raise_for_status()
#         gemini_response = response.json()
# 
#         # Extract transcription (best effort parsing)
#         text = gemini_response.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
#         return jsonify({"transcription": text})
# 
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#     finally:
#         os.remove(audio_path)

# Hugging Face Local Model:
# @app.route("/transcribe", methods=["POST"])
# def transcribe_audio():
#     if "audio" not in request.files:
#         return jsonify({"error": "No audio file uploaded"}), 400
# 
#     file = request.files["audio"]
#     filename = secure_filename(file.filename)
#     filepath = os.path.join(UPLOAD_FOLDER, filename)
#     file.save(filepath)
# 
#     try:
#         text = transcribe(filepath)
#         return jsonify({"transcription": text})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#     finally:
#         os.remove(filepath)  # Clean up uploaded file

if __name__ == "__main__":
    app.run(debug=True)