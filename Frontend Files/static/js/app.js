// Document Upload Handling
const uploadBox = document.getElementById('uploadBox');
const fileInput = document.getElementById('fileInput');
const uploadStatus = document.getElementById('uploadStatus');
const documentPreview = document.getElementById('documentPreview');
const documentText = document.getElementById('documentText');
const documentStats = document.getElementById('documentStats');
const qaSection = document.getElementById('qaSection');
const clearDocument = document.getElementById('clearDocument');

// Question & Answer Handling
const questionInput = document.getElementById('questionInput');
const askButton = document.getElementById('askButton');
const answerSection = document.getElementById('answerSection');
const answerText = document.getElementById('answerText');
const loadingIndicator = document.getElementById('loadingIndicator');

// Upload box click handler
uploadBox.addEventListener('click', () => {
    fileInput.click();
});

// Drag and drop handlers
uploadBox.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadBox.style.borderColor = '#667eea';
    uploadBox.style.background = '#f0f4ff';
});

uploadBox.addEventListener('dragleave', (e) => {
    e.preventDefault();
    uploadBox.style.borderColor = '#e0e0e0';
    uploadBox.style.background = 'white';
});

uploadBox.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadBox.style.borderColor = '#e0e0e0';
    uploadBox.style.background = 'white';
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileUpload(files[0]);
    }
});

// File input change handler
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileUpload(e.target.files[0]);
    }
});

// Handle file upload
async function handleFileUpload(file) {
    // Validate file type
    const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    const validExtensions = ['.pdf', '.docx', '.txt'];
    const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    
    if (!validExtensions.includes(fileExtension)) {
        showUploadStatus('Please upload a PDF, DOCX, or TXT file.', 'error');
        return;
    }
    
    // Show loading
    uploadStatus.className = 'upload-status';
    uploadStatus.textContent = 'Uploading and processing...';
    uploadStatus.style.display = 'block';
    uploadStatus.style.background = '#d1ecf1';
    uploadStatus.style.color = '#0c5460';
    uploadStatus.style.border = '1px solid #bee5eb';
    
    // Create form data
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            showUploadStatus(`✓ Successfully uploaded "${file.name}" (${data.length} characters)`, 'success');
            
            // Show document preview
            documentText.value = data.text;
            documentStats.textContent = `Document size: ${data.length} characters`;
            documentPreview.style.display = 'block';
            qaSection.style.display = 'block';
            
            // Scroll to preview
            documentPreview.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else {
            showUploadStatus(`✗ Error: ${data.message}`, 'error');
        }
    } catch (error) {
        showUploadStatus(`✗ Error uploading file: ${error.message}`, 'error');
    }
}

function showUploadStatus(message, type) {
    uploadStatus.textContent = message;
    uploadStatus.className = `upload-status ${type}`;
    uploadStatus.style.display = 'block';
}

// Clear document handler
clearDocument.addEventListener('click', () => {
    if (confirm('Are you sure you want to clear the document?')) {
        fileInput.value = '';
        documentText.value = '';
        documentPreview.style.display = 'none';
        qaSection.style.display = 'none';
        answerSection.style.display = 'none';
        uploadStatus.style.display = 'none';
        questionInput.value = '';
    }
});

// Ask question handler
askButton.addEventListener('click', askQuestion);
questionInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        askQuestion();
    }
});

async function askQuestion() {
    const question = questionInput.value.trim();
    
    if (!question) {
        alert('Please enter a question.');
        return;
    }
    
    // Show loading
    loadingIndicator.style.display = 'block';
    answerSection.style.display = 'none';
    askButton.disabled = true;
    
    try {
        const response = await fetch('/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question: question })
        });
        
        const data = await response.json();
        
        loadingIndicator.style.display = 'none';
        askButton.disabled = false;
        
        if (data.success) {
            answerText.textContent = data.answer;
            answerSection.style.display = 'block';
            
            // Scroll to answer
            answerSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        } else {
            alert(`Error: ${data.message}`);
        }
    } catch (error) {
        loadingIndicator.style.display = 'none';
        askButton.disabled = false;
        alert(`Error: ${error.message}`);
    }
}

// Add smooth scrolling for all anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});