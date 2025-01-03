
# Chat Application with PDF Upload and Question Answering

This FastAPI-based chat application allows users to upload PDF files and ask questions about the content. The app uses a front-end interface styled with Html,CSS and JavaScript, providing an interactive and user-friendly experience. For question answering, the application leverages Langchain for text processing, FAISS for efficient similarity search, and integrates Google generative AI embeddings along with LLaMA 3 and Groq for enhanced responses. The PDF content is extracted, embedded, and stored in a FAISS index, enabling quick and accurate retrieval of relevant information when users ask questions. This system uses Retrieval-Augmented Generation (RAG), where the relevant content is first retrieved through FAISS and embeddings, then passed to the LLaMA 3 with Groq model for response generation. The Groq AI accelerates inference for the models, ensuring faster and more efficient query processing. This integration provides a seamless and intelligent experience for answering queries based on PDF documents.

## Features

- Upload PDF files for processing.
- Ask questions about the content in uploaded PDFs.
- Dynamic chat interface with user and assistant responses.

## Requirements

- Python 3.9 or later.
- A virtual environment set up (recommended).
- API keys for:
  - Groq API from https://groq.com/
  - Google API from https://ai.google.dev/

## Setup
- Clone the repository 
```
git clone <repository-url>
cd <repository-directory>

```
- Set Up the Virtual Environment
```
python3 -m venv venv
.\venv\Scripts\activate


```
-Install Python Dependencies 
```
pip install -r requirements.txt
```
- Configure Environment Variables Create a .env file in the root directory and add your API keys:
```
.env
GROQ_API_KEY="#########"
GOOGLE_API_KEY="#########"


```
- Run the Backend Server
```
uvicorn main:app --reload
```
## Usage
1-Upload PDFs:
- Click the upload button to select pdf file
-  Wait for the server to process the files. A success message will be displayed.
2-Ask questions:
- Type your question into the input box.
- Click the "Ask" button to send the question.
- The assistant's response will appear in the chat history.
3-Chat Interface:
- User messages are shown on the left in blue bubbles.
- Assistant responses are shown on the right in green bubbles.
## Directory Structure
```
.
├── main.py                 # FastAPI entry point
├── index.html              # The main HTML file for the chat app
├── static/                 # Front-end assets
│   ├── style.css           # CSS for the front-end
│   ├── script.js           # JavaScript for front-end functionality
│   ├── logo.png            # Logo image
├── .env                    # Environment variables
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
```

## API Endpoints
## POST `/upload-pdf/`
- **Description**: Upload PDF files for processing.
- **Request**: FormData containing one or more PDF files.
- **Response**: Success message.
## POST `/ask-question/`
- **Description**:Ask a question about the uploaded PDFs.
- **Request**:FormData containing the question.
- **Response**:Assistant's answer or an error message.
## Notes
- Ensure you have the correct API keys in your .env file for proper functionality.



## Troubleshooting
**PDF Upload Fails**: Ensure the backend server is running and accessible.
**Questions Not Responded To**: Verify that the API keys are correctly configured and valid.






