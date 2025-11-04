// Document Upload Handling
const uploadBox = document.getElementById('uploadBox');
const fileInput = document.getElementById('fileInput');
const uploadStatus = document.getElementById('uploadStatus');
const documentPreview = document.getElementById('documentPreview');
const documentText = document.getElementById('documentText');
const fileMetadata = document.getElementById('fileMetadata');
const chatSection = document.getElementById('chatSection');
const clearChatBtn = document.getElementById('clearChatBtn');

// Chat Handling
const chatMessages = document.getElementById('chatMessages');
const questionInput = document.getElementById('questionInput');
const askButton = document.getElementById('askButton');
const loadingIndicator = document.getElementById('loadingIndicator');

// Metadata elements
const metaFilename = document.getElementById('metaFilename');
const metaFileType = document.getElementById('metaFileType');
const metaFileSize = document.getElementById('metaFileSize');
const metaWordCount = document.getElementById('metaWordCount');
const togglePreview = document.getElementById('togglePreview');
const closePreview = document.getElementById('closePreview');

// Quick action buttons
const quickActionButtons = document.querySelectorAll('.quick-action-btn');

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
            showUploadStatus(`✓ Successfully uploaded "${file.name}"`, 'success');
            
            // Store document text
            documentText.value = data.text;
            
            // Show file metadata
            displayFileMetadata(data.metadata);
            
            // Show chat section
            chatSection.style.display = 'block';
            clearChatBtn.style.display = 'block';
            
            // Clear previous chat
            clearChatMessages();
            
            // Scroll to chat
            chatSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else {
            showUploadStatus(`✗ Error: ${data.message}`, 'error');
        }
    } catch (error) {
        showUploadStatus(`✗ Error uploading file: ${error.message}`, 'error');
    }
}

function displayFileMetadata(metadata) {
    fileMetadata.style.display = 'block';
    metaFilename.textContent = metadata.filename;
    metaFileType.textContent = metadata.file_type;
    metaFileSize.textContent = formatFileSize(metadata.file_size);
    metaWordCount.textContent = metadata.word_count.toLocaleString();
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function showUploadStatus(message, type) {
    uploadStatus.textContent = message;
    uploadStatus.className = `upload-status ${type}`;
    uploadStatus.style.display = 'block';
}

// Toggle preview
togglePreview.addEventListener('click', () => {
    if (documentPreview.style.display === 'none') {
        documentPreview.style.display = 'block';
        togglePreview.textContent = 'Hide Full Text';
    } else {
        documentPreview.style.display = 'none';
        togglePreview.textContent = 'Show Full Text';
    }
});

closePreview.addEventListener('click', () => {
    documentPreview.style.display = 'none';
    togglePreview.textContent = 'Show Full Text';
});

// Clear chat handler
clearChatBtn.addEventListener('click', async (e) => {
    e.preventDefault();
    if (confirm('Clear all chat history? Your document will remain uploaded.')) {
        try {
            const response = await fetch('/clear_chat', {
                method: 'POST'
            });
            const data = await response.json();
            if (data.success) {
                clearChatMessages();
                showNotification('Chat history cleared', 'success');
            }
        } catch (error) {
            showNotification('Error clearing chat', 'error');
        }
    }
});

// Ask question handler
askButton.addEventListener('click', () => askQuestion());
questionInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        askQuestion();
    }
});

// Quick action buttons
quickActionButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        const question = btn.getAttribute('data-question');
        questionInput.value = question;
        askQuestion();
    });
});

async function askQuestion() {
    const question = questionInput.value.trim();
    
    if (!question) {
        showNotification('Please enter a question.', 'error');
        return;
    }
    
    // Add user message to chat
    addMessageToChat('user', question);
    
    // Clear input
    questionInput.value = '';
    
    // Show loading
    loadingIndicator.style.display = 'flex';
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
            // Add AI response to chat
            addMessageToChat('ai', data.answer);
            
            // Scroll to bottom
            chatMessages.scrollTop = chatMessages.scrollHeight;
        } else {
            showNotification(`Error: ${data.message}`, 'error');
        }
    } catch (error) {
        loadingIndicator.style.display = 'none';
        askButton.disabled = false;
        showNotification(`Error: ${error.message}`, 'error');
    }
}

function addMessageToChat(sender, message) {
    // Remove welcome message if it exists
    const welcomeMsg = chatMessages.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}-message`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = sender === 'user' ? '👤' : '🤖';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    
    const text = document.createElement('div');
    text.className = 'message-text';
    text.textContent = message;
    
    const time = document.createElement('div');
    time.className = 'message-time';
    time.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    content.appendChild(text);
    content.appendChild(time);
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function clearChatMessages() {
    chatMessages.innerHTML = `
        <div class="welcome-message">
            <div class="welcome-icon">🤖</div>
            <p>Hello! I'm ready to answer questions about your document. You can ask me to:</p>
            <ul>
                <li>Summarize the document</li>
                <li>Explain specific policies</li>
                <li>Find information about specific topics</li>
                <li>Get details about the file itself</li>
            </ul>
        </div>
    `;
}

function showNotification(message, type) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#d4edda' : '#f8d7da'};
        color: ${type === 'success' ? '#155724' : '#721c24'};
        border: 1px solid ${type === 'success' ? '#c3e6cb' : '#f5c6cb'};
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 1000;
        animation: slideInRight 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Load chat history on page load if document exists
window.addEventListener('load', async () => {
    try {
        const response = await fetch('/get_chat_history');
        const data = await response.json();
        
        if (data.success && data.chat_history && data.chat_history.length > 0) {
            // Document exists, restore chat
            clearChatMessages();
            data.chat_history.forEach(msg => {
                addMessageToChat('user', msg.question);
                addMessageToChat('ai', msg.answer);
            });
        }
    } catch (error) {
        console.log('No previous chat history');
    }
});