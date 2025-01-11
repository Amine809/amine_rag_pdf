
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

## Backend API Documentation

The backend is implemented using FastAPI and provides RESTful endpoints for handling PDF uploads, processing, and question answering. Below is the detailed documentation for the backend APIs.

---

### **API Endpoints**

#### **1. GET `/`**
- **Description**: Serves the home route.
- **Response**:
  - Returns the index.html page for the front-end interface.

---

#### **2. POST `/upload-pdf/`**
- **Description**: Handles the upload and processing of one or more PDF files.
- **Request**:
  - **Method**: `POST`
  - **Content-Type**: `multipart/form-data`
  - **Body Parameters**:
    - `files`: A list of PDF files to be uploaded.
- **Response**:
  - **Success (200)**:
    - Returns a success message, the time taken to process the files, and the number of documents processed.
      ```json
      {
       "message": "PDF uploaded and processed successfully!",
       "processing_time": "X.XX seconds",
       "documents_processed": X
      }
      ```
  - **Error (400/500)**:
    - Returns an error message if file upload or processing fails.
    
- **Processing Steps**:
  - Save the uploaded files temporarily.
  - Extract text from the PDFs using `PyPDFDirectoryLoader`.
  - Chunk the text for embedding using `RecursiveCharacterTextSplitter`.
  - Embed the text and store it in a FAISS vector database for similarity search.

---

#### **3. POST `/ask-question/`**
- **Description**: Processes a question related to the content of uploaded PDFs and generates an answer.
- **Request**:
  - **Method**: `POST`
  - **Content-Type**: `application/json`
  - **Body Parameters**:
    - `question` (string): The question asked by the user.
- **Response**:
  - **Success (200)**:
    - Returns the answer to the question, the response time, and the full chat history.
    - **Example**:
      ```json
      {
        "response": "The document discusses advanced AI techniques.",
        "response_time": "2.15 seconds",
        "history": [
          {
            "question": "What is the document about?",
            "answer": "The document discusses advanced AI techniques.",
            "response_time": "2.15 seconds"
          }
        ]
      }
      
- **Processing Steps**:
  - Retrieve relevant content from the FAISS vector store using similarity search.
  - Pass the retrieved content and question to the `ChatGroq` model (`LLaMA 3`) to generate the answer.
  - Append the response to the session’s chat history.

---






## Troubleshooting
**PDF Upload Fails**: Ensure the backend server is running and accessible.
**Questions Not Responded To**: Verify that the API keys are correctly configured and valid.






