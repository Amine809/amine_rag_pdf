from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse
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

load_dotenv()

app = FastAPI()

# Initialize the API keys and model
groq_api_key = os.getenv('GROQ_API_KEY')
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

llm = ChatGroq(groq_api_key=groq_api_key, model_name="Llama3-8b-8192")

# Create temporary directory for PDFs
os.makedirs("temp", exist_ok=True)

# Session storage for chat history
history = []

# Initialize embeddings and vector store
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
vectors = None
final_documents = []

# Define the prompt template
prompt = ChatPromptTemplate.from_template("""
Answer the questions based on the provided context only.
Provide the most accurate response based on the question.
<context>
{context}
</context>
Questions: {input}
""")

@app.post("/upload-pdf/")
async def upload_pdf(files: list[UploadFile] = File(...)):
    global vectors, final_documents
    
    # Save and process the uploaded PDFs
    for uploaded_file in files:
        with open(f"temp/{uploaded_file.filename}", "wb") as f:
            f.write(await uploaded_file.read())

    # Load PDFs using the PyPDFDirectoryLoader
    loader = PyPDFDirectoryLoader("temp")
    documents = loader.load()

    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    final_documents = text_splitter.split_documents(documents)
    
    # Create the vector store
    vectors = FAISS.from_documents(final_documents, embeddings)

    return {"message": "PDF uploaded and processed successfully!"}

@app.post("/ask-question/")
async def ask_question(question: str = Form(...)):
    global vectors, history

    if not vectors:
        return {"error": "Please upload PDFs first."}

    # Create the retrieval chain and fetch the answer
    document_chain = create_stuff_documents_chain(llm, prompt)
    retriever = vectors.as_retriever()
    retrieval_chain = create_retrieval_chain(retriever, document_chain)

    start = time.process_time()
    response = retrieval_chain.invoke({'input': question})
    end = time.process_time()

    # Add question and answer to history
    history.append({"question": question, "answer": response['answer']})

    return {
        "response": response['answer'],
        "response_time": round(end - start, 4),
        "history": history
    }

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("index.html", "r") as f:
        return HTMLResponse(content=f.read(), status_code=200)

# Serve static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")
