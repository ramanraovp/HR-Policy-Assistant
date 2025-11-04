#!/usr/bin/env python3
"""
Setup script for HR Policy Assistant
Helps you choose and configure a free AI service
"""

import sys
import os

def print_header():
    print("\n" + "="*60)
    print("  HR Policy Assistant - Free AI Setup")
    print("="*60 + "\n")

def print_option(number, name, pros, cons, difficulty):
    print(f"\n{number}. {name}")
    print(f"   Difficulty: {difficulty}")
    print(f"   Pros: {pros}")
    print(f"   Cons: {cons}")

def main():
    print_header()
    
    print("Choose your FREE AI service:\n")
    
    print_option(
        1,
        "Google Gemini (Recommended)",
        "Fast, high quality, easy setup, generous free tier",
        "Requires Google account",
        "⭐ Easy"
    )
    
    print_option(
        2,
        "Hugging Face Inference API",
        "Many models to choose from, good for experimentation",
        "Rate limits on free tier, variable quality",
        "⭐⭐ Medium"
    )
    
    print_option(
        3,
        "Ollama (Local)",
        "100% free, unlimited, private, no internet needed",
        "Requires downloading models (~4GB+), slower on CPU",
        "⭐⭐⭐ Advanced"
    )
    
    print("\n" + "-"*60)
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        setup_gemini()
    elif choice == "2":
        setup_huggingface()
    elif choice == "3":
        setup_ollama()
    else:
        print("Invalid choice. Please run the script again.")
        sys.exit(1)

def setup_gemini():
    print("\n" + "="*60)
    print("  Setting up Google Gemini")
    print("="*60)
    
    print("\nSteps:")
    print("1. Go to: https://makersuite.google.com/app/apikey")
    print("2. Sign in with your Google account")
    print("3. Click 'Create API Key' or 'Get API Key'")
    print("4. Copy your API key")
    
    api_key = input("\nPaste your Gemini API key here: ").strip()
    
    if not api_key or not api_key.startswith("AIza"):
        print("\n⚠️  Warning: This doesn't look like a valid Gemini API key.")
        print("   Gemini keys usually start with 'AIza'")
        confirm = input("   Continue anyway? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Setup cancelled.")
            sys.exit(1)
    
    # Update flask_app.py
    try:
        with open('flask_app.py', 'r') as f:
            content = f.read()
        
        content = content.replace(
            'GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"',
            f'GEMINI_API_KEY = "{api_key}"'
        )
        
        with open('flask_app.py', 'w') as f:
            f.write(content)
        
        print("\n✓ Configuration updated successfully!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements_flask.txt")
        print("2. Run the app: python flask_app.py")
        print("3. Open browser: http://localhost:5000")
        print("\nDefault login:")
        print("  Username: abhay")
        print("  Password: yourpassword")
        
    except FileNotFoundError:
        print("\n❌ Error: flask_app.py not found in current directory")
        print("   Make sure you're running this from the project directory.")
        sys.exit(1)

def setup_huggingface():
    print("\n" + "="*60)
    print("  Setting up Hugging Face")
    print("="*60)
    
    print("\nSteps:")
    print("1. Go to: https://huggingface.co/settings/tokens")
    print("2. Sign up or log in")
    print("3. Click 'New token'")
    print("4. Give it a name and select 'read' access")
    print("5. Copy your token")
    
    api_key = input("\nPaste your Hugging Face token here: ").strip()
    
    if not api_key or len(api_key) < 20:
        print("\n⚠️  Warning: This doesn't look like a valid HF token.")
        confirm = input("   Continue anyway? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Setup cancelled.")
            sys.exit(1)
    
    try:
        with open('flask_app_huggingface.py', 'r') as f:
            content = f.read()
        
        content = content.replace(
            'HF_API_KEY = "YOUR_HUGGINGFACE_API_KEY_HERE"',
            f'HF_API_KEY = "{api_key}"'
        )
        
        with open('flask_app_huggingface.py', 'w') as f:
            f.write(content)
        
        print("\n✓ Configuration updated successfully!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements_flask.txt")
        print("2. Install HF: pip install huggingface_hub")
        print("3. Run the app: python flask_app_huggingface.py")
        print("4. Open browser: http://localhost:5000")
        
    except FileNotFoundError:
        print("\n❌ Error: flask_app_huggingface.py not found")
        sys.exit(1)

def setup_ollama():
    print("\n" + "="*60)
    print("  Setting up Ollama (Local)")
    print("="*60)
    
    print("\nOllama runs AI models locally on your computer.")
    print("This means:")
    print("  ✓ 100% free and unlimited")
    print("  ✓ Complete privacy (no data sent online)")
    print("  ✓ Works offline")
    print("  ✗ Requires downloading ~4GB model")
    print("  ✗ May be slow without a good GPU")
    
    print("\nSteps:")
    print("1. Download Ollama from: https://ollama.ai")
    print("2. Install Ollama on your system")
    print("3. Open terminal and run: ollama run llama2")
    print("4. Wait for model to download (~4GB)")
    print("5. Once ready, run the Flask app")
    
    print("\nI'll create an Ollama-compatible Flask app for you...")
    
    # Create Ollama version
    ollama_code = '''from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import tempfile
from PyPDF2 import PdfReader
from docx import Document as DocxDocument
import requests
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Ollama runs locally on port 11434 by default
OLLAMA_URL = "http://localhost:11434/api/generate"

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
            return '\\n'.join([para.text for para in doc.paragraphs])
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
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
        file.save(tmp_file.name)
        temp_file_path = tmp_file.name
    document_text = extract_text(temp_file_path)
    os.remove(temp_file_path)
    if not document_text.strip():
        return jsonify({'success': False, 'message': 'No text could be extracted'})
    session['document_text'] = document_text
    return jsonify({'success': True, 'text': document_text, 'length': len(document_text)})

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
        prompt = f"""You are a helpful assistant for HR Policy documents.

Document Text:
{document_text}

Question: {question}

Please provide a clear and concise answer based on the document."""

        response = requests.post(OLLAMA_URL, json={
            "model": "llama2",
            "prompt": prompt,
            "stream": False
        })
        
        if response.status_code == 200:
            answer = response.json()['response']
            return jsonify({'success': True, 'answer': answer})
        else:
            return jsonify({'success': False, 'message': 'Ollama is not running. Start it with: ollama run llama2'})
    except requests.exceptions.ConnectionError:
        return jsonify({'success': False, 'message': 'Cannot connect to Ollama. Make sure it is running: ollama run llama2'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
'''
    
    try:
        with open('flask_app_ollama.py', 'w') as f:
            f.write(ollama_code)
        
        print("\n✓ Created flask_app_ollama.py")
        print("\nNext steps:")
        print("1. Install Ollama: https://ollama.ai")
        print("2. Run: ollama run llama2 (downloads model)")
        print("3. Install Flask: pip install -r requirements_flask.txt")
        print("4. Run app: python flask_app_ollama.py")
        print("5. Open browser: http://localhost:5000")
        
    except Exception as e:
        print(f"\n❌ Error creating file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()