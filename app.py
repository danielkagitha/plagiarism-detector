from flask import Flask, request, render_template, redirect, url_for
import os
from plagiarism import check_plagiarism  # Import plagiarism logic

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return redirect(url_for('index'))

    file = request.files["file"]
    if file.filename == "":
        return redirect(url_for('index'))

    filename = file.filename
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    results = check_plagiarism(file_path)  # Run plagiarism detection

    return render_template("results.html", results=results, filename=filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000) 

