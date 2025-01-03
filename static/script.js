const pdfUpload = document.getElementById('pdf-upload');
const questionInput = document.getElementById('question-input');
const askButton = document.getElementById('ask-btn');
const chatHistory = document.getElementById('chat-history');
const chatContainer = document.querySelector('.chat-container'); // Added for improved scrolling behavior
let pdfUploaded = false;

// Handle PDF upload
pdfUpload.addEventListener('change', async () => {
    const files = pdfUpload.files;
    if (files.length > 0) {
        const formData = new FormData();
        for (let file of files) {
            formData.append("files", file);
        }

        const response = await fetch("/upload-pdf/", {
            method: "POST",
            body: formData
        });
        const data = await response.json();
        alert(data.message);
        pdfUploaded = true;
    }
});

// Handle question submission
askButton.addEventListener('click', async () => {
    const question = questionInput.value.trim();
    if (!pdfUploaded) {
        alert("Please upload PDFs before asking a question.");
        return;
    }
    if (question) {
        addMessage(question, 'user');
        questionInput.value = '';

        const formData = new FormData();
        formData.append("question", question);

        const response = await fetch("/ask-question/", {
            method: "POST",
            body: formData
        });
        const data = await response.json();

        if (data.response) {
            addMessage(data.response, 'assistant');
        } else {
            alert(data.error);
        }
    }
});

// Add new message to chat history
function addMessage(message, type) {
    const messageBubble = document.createElement('div');
    messageBubble.classList.add('chat-message', type === 'user' ? 'user-message' : 'assistant-message');
    messageBubble.innerHTML = `<p>${message}</p>`;
    chatHistory.appendChild(messageBubble);

    // Ensure chat history scrolls to the bottom
    setTimeout(() => {
        chatHistory.scrollTo({
            top: chatHistory.scrollHeight,
            behavior: 'smooth'
        });
    }, 100); // Allow DOM updates before scrolling
}

// Adjust the chat container's height dynamically
window.addEventListener('resize', adjustChatHeight);
adjustChatHeight(); // Initial adjustment on load

function adjustChatHeight() {
    const chatControlsHeight = document.querySelector('.chat-controls').offsetHeight;
    chatHistory.style.maxHeight = `calc(100% - ${chatControlsHeight}px)`;
}
