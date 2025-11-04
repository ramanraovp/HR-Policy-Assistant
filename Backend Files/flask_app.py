from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import tempfile
from PyPDF2 import PdfReader
from docx import Document as DocxDocument
import google.generativeai as genai
from functools import wraps
from datetime import datetime

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
# NOTE: In a production app, you should load this from an environment variable for security.
GEMINI_API_KEY = "AIzaSyCz45MdZbcVS4uz1iay-TRvpdz-WXM1sSI"
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
            # PyPDF2 usage for text extraction
            reader = PdfReader(file_path)
            text = ''
            for page in reader.pages:
                try:
                    text += page.extract_text() or ''
                except Exception:
                    continue
            return text
        elif ext == '.docx':
            # docx usage for text extraction
            doc = DocxDocument(file_path)
            return '\n'.join([para.text for para in doc.paragraphs])
        elif ext == '.txt':
            # Plain text file reading
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception as e:
        # Log the error for debugging
        print(f"Extraction Error: {e}")
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
    
    # Assuming 'login.html' exists in the template folder
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Assuming 'dashboard.html' exists in the template folder
    return render_template('dashboard.html', username=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('document_text', None)
    session.pop('chat_history', None)
    session.pop('file_metadata', None)
    return redirect(url_for('login'))

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'})
    
    # Save file temporarily to disk
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            file.save(tmp_file.name)
            temp_file_path = tmp_file.name
        
        # Extract text
        document_text = extract_text(temp_file_path)
        file_size = os.path.getsize(temp_file_path)
    finally:
        # Clean up the temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
    
    if not document_text.strip():
        return jsonify({'success': False, 'message': 'No text could be extracted from the document'})
    
    # Store in session with metadata
    session['document_text'] = document_text
    session['chat_history'] = []  # Reset chat history for new document
    session['file_metadata'] = {
        'filename': file.filename,
        'file_size': file_size,
        'upload_time': datetime.now().isoformat(),
        'char_count': len(document_text),
        'word_count': len(document_text.split()),
        'file_type': os.path.splitext(file.filename)[1].upper()
    }
    
    return jsonify({
        'success': True,
        'text': document_text,
        'length': len(document_text),
        'metadata': session['file_metadata']
    })

@app.route('/ask', methods=['POST'])
@login_required
def ask_question():
    question = request.json.get('question')
    document_text = session.get('document_text', '')
    chat_history = session.get('chat_history', [])
    file_metadata = session.get('file_metadata', {})
    
    if not question:
        return jsonify({'success': False, 'message': 'No question provided'})
    
    if not document_text:
        return jsonify({'success': False, 'message': 'No document uploaded'})
    
    try:
        # Switching to the current, highly available 'gemini-2.5-flash'.
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Build conversation context from history
        context = ""
        if chat_history:
            context = "\n\nPrevious conversation:\n"
            # Last 5 exchanges for context to maintain focus
            for i, msg in enumerate(chat_history[-5:]):
                context += f"Q{i+1}: {msg.get('question', '')}\nA{i+1}: {msg.get('answer', '')}\n\n"
        
        # Add file metadata context
        metadata_context = f"\n\nFile Information:\n"
        metadata_context += f"Filename: {file_metadata.get('filename', 'Unknown')}\n"
        metadata_context += f"File Type: {file_metadata.get('file_type', 'Unknown')}\n"
        metadata_context += f"Characters: {file_metadata.get('char_count', 0)}\n"
        metadata_context += f"Words: {file_metadata.get('word_count', 0)}\n"
        
        prompt = f"""You are a helpful assistant for HR Policy documents. You can answer questions about the document content, provide summaries, and give information about the document itself.
All your responses MUST be formatted using Markdown (e.g., bolding, bullet points, headers) for maximum clarity and readability.

{metadata_context}

Document Text:
{document_text}
{context}
Current Question: {question}

Please provide a clear and concise answer based on the document and the conversation context. If the user asks about the file itself (like filename, size, type), use the file information provided above."""

        response = model.generate_content(prompt)
        answer = response.text
        
        # Add to chat history
        chat_history.append({
            'question': question,
            'answer': answer,
            'timestamp': datetime.now().isoformat()
        })
        session['chat_history'] = chat_history
        
        return jsonify({
            'success': True, 
            'answer': answer,
            'chat_history': chat_history
        })
    
    except Exception as e:
        # Log the error
        print(f"Gemini API Error: {e}")
        return jsonify({'success': False, 'message': f'Error processing request: {str(e)}'})

@app.route('/clear_chat', methods=['POST'])
@login_required
def clear_chat():
    """Clear chat history while keeping the document"""
    session['chat_history'] = []
    return jsonify({'success': True, 'message': 'Chat history cleared'})

@app.route('/get_chat_history', methods=['GET'])
@login_required
def get_chat_history():
    """Retrieve current chat history"""
    chat_history = session.get('chat_history', [])
    return jsonify({'success': True, 'chat_history': chat_history})

if __name__ == '__main__':
    # Startup info to help debugging template/static path issues
    print('Starting Flask app with Chat Feature')
    print(f'Base dir: {BASE_DIR}')
    print(f'Frontend dir: {FRONTEND_DIR}')
    print(f'Template folder: {TEMPLATE_FOLDER}')
    print(f'Static folder: {STATIC_FOLDER}')
    # Verify that expected template files exist
    for tpl in ('login.html', 'dashboard.html'):
        tpl_path = os.path.join(TEMPLATE_FOLDER, tpl)
        print(f"Template {tpl}: {'FOUND' if os.path.exists(tpl_path) else 'MISSING'} -> {tpl_path}")

    app.run(debug=True, port=5000)
