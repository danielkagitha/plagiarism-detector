import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from docx import Document
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'docx'}

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)

class DocumentModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(120), unique=True, nullable=False)
    summary = db.Column(db.Text)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_docx(filepath):
    doc = Document(filepath)
    text = '\n'.join([para.text for para in doc.paragraphs])
    return text

def summarize_text(text, sentence_count=5):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, sentence_count)
    summarized_text = ' '.join(str(sentence) for sentence in summary)
    return summarized_text

def compare_with_online(summary):
    # Replace below with actual scraping or API for online docs (examples only!)
    online_texts = [
        "This is a sample online document for comparison.",
        "Another online source text to be used.",
        # add more meaningful texts from external sources/APIs
    ]
    vectorizer = TfidfVectorizer().fit_transform([summary] + online_texts)
    vectors = vectorizer.toarray()
    cosine_matrix = cosine_similarity([vectors[0]], vectors[1:])
    results = [{"text": online_texts[i], "score": round(float(cosine_matrix[0][i]) * 100, 2)} for i in range(len(online_texts))]
    top5 = sorted(results, key=lambda x: -x['score'])[:5]
    return top5

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file.filename == '' or not allowed_file(file.filename):
            return redirect(request.url)
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        text = read_docx(filepath)
        summary = summarize_text(text)
        # Save the uploaded doc in DB
        new_doc = DocumentModel(filename=filename, summary=summary)
        db.session.add(new_doc)
        db.session.commit()
        # Compare
        results = compare_with_online(summary)
        return render_template('results.html', summary=summary, results=results)
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)

