from flask import Flask, render_template, request, jsonify
import os
import base64
import requests
from dotenv import load_dotenv
from google.genai import types
from model import generate_story
from transcriber import transcribe_audio
from google import genai
from pathlib import Path
# from transcriber import transcribe
# from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)

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

@app.route("/reading")
def reading():
    return render_template('reading.html')

@app.route("/generate", methods=['POST'])
def generate():
    print("DJSFKLSDLKFDKLFJKSLDJFSLKDJFSLKJFLJFKLDSFJLKF")
    try:
        data = request.get_json()
        print("working query: ",data["query"])
        generate_story(1, data["query"])
        return jsonify({"message": "Story generated successfully!"}), 200
    except Exception as e:
        print("EXCEPTPTTTTION",e)
        return jsonify({"error": str(e)}), 500

@app.route("/transcribe", methods=["POST"])
def transcribe_audio_route():
    return transcribe_audio(request)

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