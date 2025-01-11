from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from langchain_groq import ChatGroq
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import os
import time
import asyncio
from typing import List
import shutil

load_dotenv()

app = FastAPI()

# Initialize the API keys and model
groq_api_key = os.getenv('GROQ_API_KEY')
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

llm = ChatGroq(groq_api_key=groq_api_key, model_name="Llama3-8b-8192")

# Create temporary directory for PDFs
TEMP_DIR = "temp"
if os.path.exists(TEMP_DIR):
    shutil.rmtree(TEMP_DIR)
os.makedirs(TEMP_DIR, exist_ok=True)

# Session storage
history = []
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
vectors = None
final_documents = []

# Processing status
processing_status = {
    "current_file": "",
    "total_files": 0,
    "processed_files": 0,
    "status": "idle"
}

# Define the prompt template
prompt = ChatPromptTemplate.from_template("""
Answer the questions based on the provided context only. 
Provide the most accurate response based on the question.
<context>
{context}
</context>
Questions: {input}
""")

def process_pdf(file_path: str) -> List:
    """Process a single PDF file"""
    try:
        loader = PyPDFDirectoryLoader(os.path.dirname(file_path))
        documents = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=150,
            length_function=len,
            is_separator_regex=False
        )
        
        return text_splitter.split_documents(documents)
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return []

@app.post("/upload-status")
async def get_upload_status():
    return JSONResponse(content=processing_status)

@app.post("/upload-pdf/")
async def upload_pdf(files: list[UploadFile] = File(...)):
    global vectors, final_documents, processing_status
    
    # Clear the temporary directory and reset variables
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR, exist_ok=True)
    vectors = None
    final_documents = []
    processing_status = {
        "current_file": "",
        "total_files": 0,
        "processed_files": 0,
        "status": "idle"
    }
    
    start_time = time.time()
    processing_status["status"] = "processing"
    processing_status["total_files"] = len(files)
    processing_status["processed_files"] = 0
    
    try:
        # Save files
        saved_files = []
        for file in files:
            file_path = os.path.join(TEMP_DIR, file.filename)
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            saved_files.append(file_path)
            
            processing_status["current_file"] = file.filename
            processing_status["processed_files"] += 1

        # Process PDFs using asyncio
        loop = asyncio.get_event_loop()
        processed_documents = []
        
        # Process files sequentially but in the background
        for file_path in saved_files:
            result = await loop.run_in_executor(None, process_pdf, file_path)
            processed_documents.extend(result)
            
        final_documents = processed_documents
        
        # Create vector store with optimized settings
        if final_documents:
            vectors = FAISS.from_documents(
                final_documents,
                embeddings,
                distance_strategy="METRIC_INNER_PRODUCT"
            )
        
        processing_time = time.time() - start_time
        processing_status["status"] = "completed"
        
        return {
            "message": "PDF uploaded and processed successfully!",
            "processing_time": f"{processing_time:.2f} seconds",
            "documents_processed": len(final_documents)
        }
        
    except Exception as e:
        processing_status["status"] = "error"
        return JSONResponse(
            content={"error": f"Error processing PDFs: {str(e)}"},
            status_code=500
        )

@app.post("/ask-question/")
async def ask_question(question: str = Form(...)):
    global vectors, history
    
    if not vectors:
        return {"error": "Please upload PDFs first."}
    
    start = time.time()
    
    try:
        # Create retrieval chain with optimized settings
        document_chain = create_stuff_documents_chain(
            llm,
            prompt,
            document_separator="\n\n",
            document_prompt=ChatPromptTemplate.from_template("{page_content}")
        )
        
        retriever = vectors.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )
        
        retrieval_chain = create_retrieval_chain(retriever, document_chain)
        
        # Get the event loop for this request
        loop = asyncio.get_event_loop()
        
        # Run the chain in the background
        response = await loop.run_in_executor(
            None, 
            lambda: retrieval_chain.invoke({'input': question})
        )
        
        end = time.time()
        
        # Add to history
        history.append({
            "question": question,
            "answer": response['answer'],
            "response_time": f"{(end - start):.2f} seconds"
        })
        
        return {
            "response": response['answer'],
            "response_time": f"{(end - start):.2f} seconds",
            "history": history
        }
        
    except Exception as e:
        return JSONResponse(
            content={"error": f"Error processing question: {str(e)}"},
            status_code=500
        )

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("index.html", "r") as f:
        return HTMLResponse(content=f.read(), status_code=200)

# Cleanup on shutdown
@app.on_event("shutdown")
async def cleanup():
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

