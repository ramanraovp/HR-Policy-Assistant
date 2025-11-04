from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import tempfile
from PyPDF2 import PdfReader
from docx import Document as DocxDocument
import google.generativeai as genai
from functools import wraps

# Determine correct paths for templates and static files located in the workspace
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
FRONTEND_DIR = os.path.join(BASE_DIR, 'Frontend Files')
TEMPLATE_FOLDER = os.path.join(FRONTEND_DIR, 'templates')
STATIC_FOLDER = os.path.join(FRONTEND_DIR, 'static')

# Create Flask app pointing to the Frontend Files folders
app = Flask(__name__, template_folder=TEMPLATE_FOLDER, static_folder=STATIC_FOLDER)
app.secret_key = 'your-secret-key-change-this-in-production'

# Configure Gemini API (Free tier available)
# Get your free API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
genai.configure(api_key=GEMINI_API_KEY)

# Simple user database (in production, use a proper database)
users = {
    "abhay": "yourpassword"
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def extract_text(file_path):
    """Extract text from PDF, DOCX, or TXT files"""
    ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if ext == '.pdf':
            reader = PdfReader(file_path)
            text = ''
            for page in reader.pages:
                try:
                    text += page.extract_text() or ''
                except Exception:
                    continue
            return text
        elif ext == '.docx':
            doc = DocxDocument(file_path)
            return '\n'.join([para.text for para in doc.paragraphs])
        elif ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception as e:
        return f"Error extracting text: {str(e)}"
    
    return ''

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users and users[username] == password:
            session['username'] = username
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'})
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'})
    
    # Save file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
        file.save(tmp_file.name)
        temp_file_path = tmp_file.name
    
    # Extract text
    document_text = extract_text(temp_file_path)
    os.remove(temp_file_path)
    
    if not document_text.strip():
        return jsonify({'success': False, 'message': 'No text could be extracted from the document'})
    
    # Store in session
    session['document_text'] = document_text
    
    return jsonify({
        'success': True,
        'text': document_text,
        'length': len(document_text)
    })

@app.route('/ask', methods=['POST'])
@login_required
def ask_question():
    question = request.json.get('question')
    document_text = session.get('document_text', '')
    
    if not question:
        return jsonify({'success': False, 'message': 'No question provided'})
    
    if not document_text:
        return jsonify({'success': False, 'message': 'No document uploaded'})
    
    try:
        # Use Gemini API (Free tier)
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""You are a helpful assistant for HR Policy documents.

Document Text:
{document_text}

Question: {question}

Please provide a clear and concise answer based on the document."""

        response = model.generate_content(prompt)
        answer = response.text
        
        return jsonify({'success': True, 'answer': answer})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

if __name__ == '__main__':
    # Startup info to help debugging template/static path issues
    print('Starting Flask app')
    print(f'Base dir: {BASE_DIR}')
    print(f'Frontend dir: {FRONTEND_DIR}')
    print(f'Template folder: {TEMPLATE_FOLDER}')
    print(f'Static folder: {STATIC_FOLDER}')
    # Verify that expected template files exist
    for tpl in ('login.html', 'dashboard.html'):
        tpl_path = os.path.join(TEMPLATE_FOLDER, tpl)
        print(f"Template {tpl}: {'FOUND' if os.path.exists(tpl_path) else 'MISSING'} -> {tpl_path}")

    app.run(debug=True, port=5000)