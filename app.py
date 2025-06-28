from flask import Flask, render_template, request, jsonify
# from transcriber import transcribe
import os
# from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/loading")
def loading():
    return render_template('loading.html')

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