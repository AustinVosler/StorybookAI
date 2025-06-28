import shutil
from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from model import generate_story
from transcriber import transcribe_audio
from tts import generate_tts

def clear_generated_files():
    folders_to_clear = ['static/images', 'static/audio']

    for folder in folders_to_clear:
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f'Failed to delete {file_path}: {e}')
            print(f"Cleared {folder}")
        else:
            os.makedirs(folder, exist_ok=True)
            print(f"Created {folder}")


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
        clear_generated_files()
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
    
    image_dir = "static/images"
    image_count = 0
    
    if os.path.exists(image_dir):
        image_count = len([f for f in os.listdir(image_dir) if f.endswith(".png")])
    
    image_count = image_count / 5
    
    global is_generating
    if not is_generating:
        return jsonify(status="done", result={"image_count": image_count})
    return jsonify(status="pending", result={"image_count": image_count})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=False)