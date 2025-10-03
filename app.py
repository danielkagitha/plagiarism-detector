from flask import Flask, request, jsonify, render_template
import os
from plagiarism import check_plagiarism  # Import the plagiarism check function

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Home route serving the frontend
@app.route("/")
def index():
    return render_template("index.html")

# Route to handle file upload and plagiarism check
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)

    # Call plagiarism check function
    results = check_plagiarism(file_path)

    return jsonify({"results": results})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  
    app.run(host="0.0.0.0", port=port, debug=True)
