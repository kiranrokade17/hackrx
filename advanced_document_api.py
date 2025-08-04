# advanced_document_api.py - Full AI-Powered Document Analysis
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import asyncio
import aiofiles
import logging
from pathlib import Path
from dotenv import load_dotenv

# Document processing imports
import fitz  # PyMuPDF
import requests
from urllib.parse import urlparse
import tempfile

# AI/ML imports
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="HackRX Advanced Document Q&A API",
    description="AI-powered document analysis with real document processing and intelligent answers",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class QueryRequest(BaseModel):
    documents: str
    questions: List[str]

class QueryResponse(BaseModel):
    answers: List[str]
    status: str = "success"
    document_info: Optional[dict] = None

# Global AI models
embedding_model = None
gemini_model = None
vector_index = None
document_chunks = []

# Initialize AI models
async def initialize_ai_models():
    global embedding_model, gemini_model
    
    try:
        # Initialize Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise Exception("GEMINI_API_KEY not found")
        
        genai.configure(api_key=api_key)
        gemini_model = genai.GenerativeModel("gemini-1.5-flash")
        logger.info("✅ Gemini model initialized")
        
        # Initialize embedding model
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("✅ Embedding model initialized")
        
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize AI models: {e}")
        return False

# Authentication
ALLOWED_API_KEYS = os.getenv("ALLOWED_API_KEYS", "api_key_1").split(",")

def verify_api_key(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    api_key = authorization.replace("Bearer ", "").strip()
    if api_key not in [key.strip() for key in ALLOWED_API_KEYS]:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return api_key

# Document processing functions
async def download_document(url: str) -> str:
    """Download document from URL to temporary file"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Create temporary file
        suffix = Path(urlparse(url).path).suffix or '.pdf'
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(response.content)
            return tmp_file.name
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to download document: {str(e)}")

async def extract_text_from_pdf(file_path: str) -> tuple[str, dict]:
    """Extract text from PDF file"""
    try:
        doc = fitz.open(file_path)
        text_content = ""
        metadata = doc.metadata or {}
        document_info = {
            "total_pages": len(doc),
            "title": metadata.get("title", "Unknown"),
            "author": metadata.get("author", "Unknown"),
            "file_type": "PDF"
        }
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text_content += f"\n--- Page {page_num + 1} ---\n"
            try:
                text_content += page.get_text()
            except:
                # Alternative method if get_text() fails
                text_content += str(page.get_text("text"))
        
        doc.close()
        return text_content, document_info
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract text from PDF: {str(e)}")

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks"""
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        # Try to break at sentence boundary
        if end < len(text):
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n')
            break_point = max(last_period, last_newline)
            
            if break_point > start + chunk_size // 2:
                end = start + break_point + 1
                chunk = text[start:end]
        
        chunks.append(chunk.strip())
        start = end - overlap
        
        if start >= len(text):
            break
    
    return [chunk for chunk in chunks if len(chunk.strip()) > 50]

async def create_vector_index(chunks: List[str]) -> faiss.IndexFlatIP:
    """Create FAISS vector index from text chunks"""
    global document_chunks
    document_chunks = chunks
    
    if not embedding_model:
        raise Exception("Embedding model not initialized")
    
    # Generate embeddings
    embeddings = embedding_model.encode(chunks)
    embeddings = np.array(embeddings).astype('float32')
    
    # Normalize embeddings for cosine similarity
    faiss.normalize_L2(embeddings)
    
    # Create FAISS index
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    
    return index

async def search_relevant_chunks(query: str, index: faiss.IndexFlatIP, top_k: int = 3) -> List[str]:
    """Search for relevant chunks using vector similarity"""
    if not embedding_model or not document_chunks:
        return []
    
    # Generate query embedding
    query_embedding = embedding_model.encode([query])
    query_embedding = np.array(query_embedding).astype('float32')
    faiss.normalize_L2(query_embedding)
    
    # Search similar chunks
    scores, indices = index.search(query_embedding, top_k)
    
    relevant_chunks = []
    for i, idx in enumerate(indices[0]):
        if scores[0][i] > 0.3:  # Similarity threshold
            relevant_chunks.append(document_chunks[idx])
    
    return relevant_chunks

async def generate_ai_answer(question: str, context_chunks: List[str]) -> str:
    """Generate AI answer using Gemini with document context"""
    if not gemini_model:
        raise Exception("Gemini model not initialized")
    
    # Prepare context
    context = "\n\n".join(context_chunks) if context_chunks else "No relevant context found."
    
    # Create comprehensive prompt
    prompt = f"""You are an expert document analyst. Analyze the provided document content and answer the question accurately and comprehensively.

DOCUMENT CONTENT:
{context}

QUESTION: {question}

INSTRUCTIONS:
1. Answer based ONLY on the information provided in the document content above
2. If the information is not available in the document, clearly state "This information is not available in the provided document"
3. Provide specific details from the document when available
4. Be concise but comprehensive
5. Use bullet points for lists when appropriate

ANSWER:"""

    try:
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return f"Error generating answer: {str(e)}"

# API Endpoints
@app.on_event("startup")
async def startup_event():
    """Initialize AI models on startup"""
    success = await initialize_ai_models()
    if not success:
        logger.warning("⚠️ Some AI models failed to initialize")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "api": "healthy",
            "gemini": "healthy" if gemini_model else "unhealthy",
            "embeddings": "healthy" if embedding_model else "unhealthy",
            "vector_search": "healthy"
        },
        "version": "2.0.0"
    }

@app.post("/hackrx/run", response_model=QueryResponse)
async def process_documents(
    request: QueryRequest,
    api_key: str = Depends(verify_api_key)
):
    """Process documents and answer questions using AI"""
    try:
        logger.info(f"Processing request with {len(request.questions)} questions")
        
        # Step 1: Handle document input
        document_path = None
        if request.documents.startswith("http"):
            # Download from URL
            document_path = await download_document(request.documents)
        elif request.documents.startswith("file:///"):
            # Local file path
            local_path = request.documents.replace("file:///", "").replace("/", "\\")
            if not os.path.exists(local_path):
                raise HTTPException(status_code=400, detail=f"File not found: {local_path}")
            document_path = local_path
        else:
            raise HTTPException(status_code=400, detail="Invalid document path. Use HTTP URL or file:/// path")
        
        # Step 2: Extract text from document
        logger.info("Extracting text from document...")
        text_content, doc_info = await extract_text_from_pdf(document_path)
        
        if len(text_content.strip()) < 100:
            raise HTTPException(status_code=400, detail="Document appears to be empty or unreadable")
        
        # Step 3: Create text chunks and vector index
        logger.info("Creating document chunks and vector index...")
        chunks = chunk_text(text_content)
        vector_index = await create_vector_index(chunks)
        
        # Step 4: Process each question
        answers = []
        for i, question in enumerate(request.questions):
            logger.info(f"Processing question {i+1}: {question}")
            
            # Find relevant context
            relevant_chunks = await search_relevant_chunks(question, vector_index, top_k=3)
            
            # Generate AI answer
            answer = await generate_ai_answer(question, relevant_chunks)
            answers.append(answer)
        
        # Cleanup temporary file if downloaded
        if request.documents.startswith("http") and document_path:
            try:
                os.unlink(document_path)
            except:
                pass
        
        logger.info(f"Successfully processed {len(request.questions)} questions")
        
        return QueryResponse(
            answers=answers,
            status="success",
            document_info=doc_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "HackRX Advanced Document Q&A API",
        "version": "2.0.0",
        "features": [
            "Real document processing (PDF)",
            "AI-powered question answering",
            "Vector similarity search",
            "Batch question processing",
            "Support for URLs and local files"
        ],
        "endpoints": {
            "health": "/health",
            "main_api": "/hackrx/run",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    PORT = int(os.getenv("PORT", 8005))
    uvicorn.run(app, host="0.0.0.0", port=PORT)
