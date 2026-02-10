from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os
import uuid
from processor import PDFProcessor
from rag_engine import RAGEngine
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "storage/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# In-memory storage for processed documents (for demo purposes)
# In a real app, you'd use a database and persistent vector store
doc_sessions = {}

processor = PDFProcessor()
rag_engine = RAGEngine()

class ChatRequest(BaseModel):
    session_id: str
    message: str
    language: str = "en"

class SummaryRequest(BaseModel):
    session_id: str
    style: str = "Detailed Summary"
    language: str = "en"

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    session_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{session_id}.pdf")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Process PDF
    text, chunks, detected_lang = processor.process_pdf(file_path)
    if not text:
        raise HTTPException(status_code=400, detail="Could not extract text from PDF.")
    
    # Create vector store
    vector_store = rag_engine.create_vector_store(chunks)
    
    # Store session data
    doc_sessions[session_id] = {
        "text": text,
        "vector_store": vector_store,
        "detected_lang": detected_lang
    }
    
    return {
        "session_id": session_id,
        "detected_lang": detected_lang,
        "message": "File uploaded and processed successfully."
    }

@app.post("/summarize")
async def summarize(request: SummaryRequest):
    if request.session_id not in doc_sessions:
        raise HTTPException(status_code=404, detail="Session not found.")
    
    session_data = doc_sessions[request.session_id]
    summary = rag_engine.get_summary(
        session_data["text"], 
        style=request.style, 
        language=request.language
    )
    
    return {"summary": summary}

@app.post("/chat")
async def chat(request: ChatRequest):
    if request.session_id not in doc_sessions:
        raise HTTPException(status_code=404, detail="Session not found.")
    
    session_data = doc_sessions[request.session_id]
    qa_chain = rag_engine.get_qa_chain(
        session_data["vector_store"], 
        language=request.language
    )
    
    # LangChain RetrievalQA expects 'query' or 'question' depending on version/config
    # Our template uses {question}
    response = qa_chain.invoke(request.message)
    
    return {"response": response["result"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
