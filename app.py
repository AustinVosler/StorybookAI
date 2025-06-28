from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from model import generate_story
from transcriber import transcribe_audio
from tts import generate_tts

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
    image_dir = os.path.join(app.static_folder, "images")
    images = [f"images/{f}" for f in os.listdir(image_dir) if f.endswith(".png")]
    return render_template('reading.html', images=images)

is_generating = False

@app.route("/generate", methods=['POST'])
def generate():
    global is_generating
    try:
        is_generating = True
        data = request.get_json()
        print("working query: ",data["query"])
        page_texts = generate_story(1, data["query"])
        generate_tts(1, page_texts)
        is_generating = False
        return jsonify({"message": "Story generated successfully!", "page_texts": page_texts}), 200
    except Exception as e:
        is_generating = False
        print("EXCEPTPTTTTION",e)
        return jsonify({"error": str(e)}), 500

@app.route("/transcribe", methods=["POST"])
def transcribe_audio_route():
    return transcribe_audio(request)

@app.route('/status')
def check_status():
    # import random
    global is_generating
    print("is generating ", is_generating)
    if not is_generating:
        return jsonify(status="done", result={"RAHH" : "rahhhhh"})
    return jsonify(status="pending")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)