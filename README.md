
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
  - Groq API from https://groq.com/ ,This is a complete comprehensive video that you can follow to have this api key (link:https://drive.google.com/file/d/1HfmG-WfeusmoXIC4Ki0u3dXkh1hSPGFN/view?usp=sharing)
  - Google API from https://ai.google.dev/, this is also a comprehensive video shared from my drive to have this api key (link :https://drive.google.com/file/d/1HfmG-WfeusmoXIC4Ki0u3dXkh1hSPGFN/view?usp=sharing)

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
- 
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
         "message": "Pdf(s) processed successfully!",
         "processing_time": "1.87 seconds"
      }
      ```
  - **Error (400)**:
    - Returns an error if the file uploaded is not a pdf file .
     ```json
      {
       "message": "Some files were not PDFs and could not be processed.",
       "processing_time": "0.00 seconds",
       "invalid_files": [
        "presentation_projet_big_data.pptx"
    ]
      }
      ```
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
        "response": "Based on the provided context, the objectives of this project are:\n\n1. Detect fraudulent credit card transactions.\n2. Compare the performance of Isolation Forest and DBSCAN algorithms.",
        "response_time": "5.48 seconds",
       "history": [
        {
            "question": "what is this project is about",
            "answer": "Based on the provided context, the project is about:\n\n**Credit card fraud detection using Isolation Forest and DBSCAN algorithms for anomaly detection.**",
            "response_time": "1.73 seconds"
        },
        {
            "question": "give me objectives of this project",
            "answer": "According to the provided context, the objectives of this project are:\n\n1. Detect fraudulent credit card transactions.\n2. Compare the performance of Isolation Forest and DBSCAN algorithms.",
            "response_time": "1.45 seconds"
        },
        {
            "question": "what is this project about?",
            "answer": "Based on the provided context, the project is about detecting fraudulent credit card transactions and comparing the performance of Isolation Forest and DBSCAN algorithms for anomaly detection.",
            "response_time": "0.94 seconds"
        },
        {
            "question": "give me the dimensions of datset used in this project",
            "answer": "According to the provided context, the dataset used in this project has:\n\n* ~284,807 rows\n* 31 columns\n\nNote that the target variable is a binary class label (0 = Normal, 1 = Fraud), which is not included in the count of columns.",
            "response_time": "1.94 seconds"
        },
        {
            "question": "give me the objectives of this project",
            "answer": "Based on the provided context, the objectives of this project are:\n\n1. Detect fraudulent credit card transactions.\n2. Compare the performance of Isolation Forest and DBSCAN algorithms.",
            "response_time": "5.48 seconds"
        }
    ]
      }
- **Error (400)**:
    - Bad Request: No PDF files uploaded.
    - **Example**:
      ```json
      {
        "error": "No PDFs uploaded. Please upload PDF files before asking questions."
      }
      
- **Processing Steps**:
  - Retrieve relevant content from the FAISS vector store using similarity search.
  - Pass the retrieved content and question to the `ChatGroq` model (`LLaMA 3`) to generate the answer.
  - Append the response to the session’s chat history.

---


### **4. POST `/upload-status/`**
- **Description**: Provides the current status of PDF upload and processing.
- **Request**:
  - **Method**: `POST`
  - **Response after uploading a pdf**:
    - Returns the current processing status as a JSON object after uploading a pdf file
    - **Example in my app**:
      ```json
      {
      "current_file": "Black and Purple Gradient Modern Artificial Intelligence Presentation.pdf",
      "total_files": 1,
      "processed_files": 1,
      "status": "completed"
      }
    
   - **Response after uploading files different from pdf:**
     - This is shows the result of upload-status api while uploading files different from pdf(exemple:powerpoint file) .
    - **Example**:
      ```json
      {
        "current_file": "presentation_projet_big_data.pptx",
       "total_files": 1,
       "processed_files": 0,
       "status": "completed_with_errors"
      }

-You can follow the video link below shared in my drive to view my backend apis demo.I've used postman to test my apis.

Link:https://drive.google.com/file/d/1Frzn-fdmhlq-4omfkuRzsExsxp2W2qKw/view?usp=sharing






