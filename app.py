from flask import Flask, request, render_template, jsonify, send_from_directory
import os
import shutil
from datetime import datetime

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = "uploads"
ORGANIZED_FOLDER = "organized"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ORGANIZED_FOLDER, exist_ok=True)

FILE_TYPES = {
    "Documents": [".pdf", ".docx", ".txt"],
    "Images": [".jpg", ".jpeg", ".png", ".gif"],
    "Videos": [".mp4", ".avi", ".mkv"],
    "Music": [".mp3", ".wav"],
    "Archives": [".zip", ".rar", ".tar"],
}

# Create folders for each type
def create_folders():
    for folder in FILE_TYPES.keys():
        folder_path = os.path.join(ORGANIZED_FOLDER, folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

# Move files to corresponding folders
def sort_files(source_folder):
    results = {"moved": []}
    for file_name in os.listdir(source_folder):
        file_path = os.path.join(source_folder, file_name)
        if os.path.isfile(file_path):
            file_extension = os.path.splitext(file_name)[1].lower()
            for folder, extensions in FILE_TYPES.items():
                if file_extension in extensions:
                    dest_folder = os.path.join(ORGANIZED_FOLDER, folder)
                    shutil.move(file_path, os.path.join(dest_folder, file_name))
                    results["moved"].append({"file": file_name, "folder": folder})
                    break
    return results

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    uploaded_file = request.files["file"]
    if uploaded_file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
    uploaded_file.save(file_path)
    return jsonify({"success": True, "filename": uploaded_file.filename})

@app.route("/organize", methods=["POST"])
def organize_files():
    create_folders()
    results = sort_files(UPLOAD_FOLDER)
    return jsonify(results)

@app.route("/download/<folder>/<filename>", methods=["GET"])
def download_file(folder, filename):
    folder_path = os.path.join(ORGANIZED_FOLDER, folder)
    return send_from_directory(folder_path, filename)

if __name__ == "__main__":
    app.run(debug=True)
