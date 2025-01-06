const pdfUpload = document.getElementById('pdf-upload');
const questionInput = document.getElementById('question-input');
const askButton = document.getElementById('ask-btn');
const chatHistory = document.getElementById('chat-history');
const chatContainer = document.querySelector('.chat-container');
let pdfUploaded = false;

// Create loading indicator
const loadingDiv = document.createElement('div');
loadingDiv.className = 'loading-indicator';
loadingDiv.innerHTML = `
    <div class="spinner"></div>
    <div class="loading-text">Processing: <span id="current-file"></span></div>
    <div class="progress-text">Processed <span id="processed-files">0</span> of <span id="total-files">0</span> files</div>
`;
document.querySelector('.chat-app').appendChild(loadingDiv);

// Function to poll upload status
async function checkUploadStatus() {
    const response = await fetch("/upload-status", {
        method: "POST"
    });
    const status = await response.json();
    
    document.getElementById('current-file').textContent = status.current_file;
    document.getElementById('processed-files').textContent = status.processed_files;
    document.getElementById('total-files').textContent = status.total_files;
    
    return status.status === "completed" || status.status === "error";
}

// Handle PDF upload
pdfUpload.addEventListener('change', async () => {
    const files = pdfUpload.files;
    if (files.length > 0) {
        // Show loading indicator
        loadingDiv.style.display = 'flex';
        
        const formData = new FormData();
        for (let file of files) {
            formData.append("files", file);
        }
        
        try {
            // Start upload
            const uploadPromise = fetch("/upload-pdf/", {
                method: "POST",
                body: formData
            });
            
            // Poll status while uploading
            const pollInterval = setInterval(async () => {
                const isComplete = await checkUploadStatus();
                if (isComplete) {
                    clearInterval(pollInterval);
                }
            }, 1000);
            
            const response = await uploadPromise;
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Add success message to chat
            addMessage(`PDFs processed in ${data.processing_time}. Ready for questions!`, 'system');
            pdfUploaded = true;
            
        } catch (error) {
            addMessage(`Error: ${error.message}`, 'error');
        } finally {
            loadingDiv.style.display = 'none';
        }
    }
});

// Handle question submission
askButton.addEventListener('click', async () => {
    const question = questionInput.value.trim();
    if (!pdfUploaded) {
        addMessage("Please upload PDF before asking a question.", 'error');
        return;
    }
    if (question) {
        addMessage(question, 'user');
        questionInput.value = '';
        
        try {
            const formData = new FormData();
            formData.append("question", question);
            
            // Show thinking indicator
            const thinkingMsg = addMessage('Thinking...', 'assistant');
            
            const response = await fetch("/ask-question/", {
                method: "POST",
                body: formData
            });
            const data = await response.json();
            
            // Remove thinking indicator and show response
            thinkingMsg.remove();
            
            if (data.response) {
                addMessage(`${data.response}\n\nResponse time: ${data.response_time}`, 'assistant');
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            addMessage(`Error: ${error.message}`, 'error');
        }
    }
});

// Add new message to chat history
function addMessage(message, type) {
    const messageBubble = document.createElement('div');
    messageBubble.classList.add('chat-message', `${type}-message`);
    messageBubble.innerHTML = `<p>${message}</p>`;
    chatHistory.appendChild(messageBubble);
    
    // Ensure chat history scrolls to the bottom
    setTimeout(() => {
        chatHistory.scrollTo({
            top: chatHistory.scrollHeight,
            behavior: 'smooth'
        });
    }, 100);
    
    return messageBubble;
}

// Adjust the chat container's height dynamically
window.addEventListener('resize', adjustChatHeight);
adjustChatHeight();

function adjustChatHeight() {
    const chatControlsHeight = document.querySelector('.chat-controls').offsetHeight;
    chatHistory.style.maxHeight = `calc(100% - ${chatControlsHeight}px)`;
}
