from flask import Flask, render_template, request, send_from_directory, jsonify
from werkzeug.utils import secure_filename
import os
import json
import time

app = Flask(__name__, static_folder='static')
UPLOAD_FOLDER = "uploads"
DATA_FILE = "project_data.json"
ALLOWED_EXT = {"pdf", "docx", "zip", "png", "jpg", "jpeg", "pptx", "txt"}

# ensure folders / data file
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    """Handle project upload with validation"""
    try:
        # Get and strip form inputs
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()
        github_link = request.form.get("github_link", "").strip()
        file = request.files.get("file")

        # Validate all required fields
        if not title or not description or not category or not file:
            return "Please fill all required fields and select a file.", 400

        # Validate file type
        if not allowed_file(file.filename):
            return "File type not allowed.", 400

        # Secure filename and avoid collisions with timestamp
        filename = secure_filename(file.filename)
        base, ext = os.path.splitext(filename)
        timestamp = int(time.time())
        filename = f"{base}_{timestamp}{ext}"
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        
        # Save file
        file.save(save_path)

        # Load existing projects
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            projects = json.load(f)

        # Append new project metadata
        projects.append({
            "title": title,
            "description": description,
            "category": category,
            "github_link": github_link,
            "file": filename,
            "uploaded_at": time.strftime("%Y-%m-%d %H:%M:%S")
        })

        # Save updated projects
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(projects, f, indent=2, ensure_ascii=False)

        return "OK", 200
    
    except Exception as e:
        return f"Error processing upload: {str(e)}", 500

@app.route("/projects_json")
def projects_json():
    """Return all projects as JSON"""
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            projects = json.load(f)
        return jsonify(projects)
    except Exception as e:
        return jsonify({"error": f"Failed to load projects: {str(e)}"}), 500

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    """Serve uploaded files for download"""
    try:
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
    except Exception as e:
        return f"File not found: {str(e)}", 404

if __name__ == "__main__":
    app.run(debug=True)