# advanced_document_api_v2.py - Working AI-Powered Document Analysis
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import asyncio
import logging
from dotenv import load_dotenv
import fitz  # PyMuPDF
import requests
from urllib.parse import urlparse
import tempfile
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="HackRX Advanced Document Q&A API v2 - BATCH OPTIMIZED",
    description="AI-powered document analysis with TRUE batch processing - ONE API call for multiple questions",
    version="2.1.0"
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

# Global AI model
gemini_model = None

# Initialize AI model
async def initialize_ai_model():
    global gemini_model
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise Exception("GEMINI_API_KEY not found")
        
        genai.configure(api_key=api_key)
        gemini_model = genai.GenerativeModel("gemini-1.5-flash")
        logger.info("✅ Gemini model initialized")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize Gemini: {e}")
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
        
        suffix = ".pdf"
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
        
        # Get document metadata
        metadata = doc.metadata if doc.metadata else {}
        document_info = {
            "total_pages": doc.page_count,
            "title": metadata.get("title", "Unknown"),
            "author": metadata.get("author", "Unknown"),
            "file_type": "PDF"
        }
        
        # Extract text from all pages
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text_content += f"\\n=== Page {page_num + 1} ===\\n"
            page_text = page.get_text()
            text_content += page_text
        
        doc.close()
        
        if len(text_content.strip()) < 50:
            raise Exception("No readable text found in PDF")
        
        return text_content, document_info
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract text from PDF: {str(e)}")

async def generate_ai_answer(question: str, document_content: str) -> str:
    """Generate AI answer using Gemini with document context"""
    if not gemini_model:
        raise Exception("Gemini model not initialized")
    
    # Create comprehensive prompt for document analysis
    prompt = f"""You are an expert document analyst. You have been provided with a document and need to answer questions about it accurately.

DOCUMENT CONTENT:
{document_content}

QUESTION: {question}

INSTRUCTIONS:
1. Analyze the document content carefully
2. Answer the question based ONLY on the information found in the document
3. If the information is not available in the document, clearly state "This information is not available in the provided document"
4. Be specific and detailed in your response
5. Quote relevant parts from the document when appropriate
6. If it's a resume/CV, provide comprehensive details about education, skills, experience, etc.

ANSWER:"""

    try:
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return f"Error generating answer: {str(e)}"

async def generate_batch_answers(questions: List[str], document_content: str) -> List[str]:
    """Generate ALL answers in ONE Gemini API call - BATCH PROCESSING"""
    if not gemini_model:
        raise Exception("Gemini model not initialized")
    
    # Create BATCH prompt for ALL questions at once
    questions_text = ""
    for i, question in enumerate(questions, 1):
        questions_text += f"\nQ{i}: {question}"
    
    prompt = f"""You are an expert document analyst. You have been provided with a document and need to answer multiple questions about it accurately.

DOCUMENT CONTENT:
{document_content}

QUESTIONS TO ANSWER:
{questions_text}

INSTRUCTIONS:
1. Analyze the document content carefully
2. Answer each question based ONLY on the information found in the document
3. If information is not available for any question, clearly state "This information is not available in the provided document"
4. Be specific and detailed in your responses
5. Quote relevant parts from the document when appropriate
6. Format your response as follows:

ANSWER Q1: [Your detailed answer to question 1]

ANSWER Q2: [Your detailed answer to question 2]

ANSWER Q3: [Your detailed answer to question 3]

[Continue for all questions...]

Make sure to provide complete, professional answers for each question."""

    try:
        logger.info(f"🚀 Making ONE API call for {len(questions)} questions")
        response = gemini_model.generate_content(prompt)
        full_response = response.text.strip()
        
        # Parse the batch response into individual answers
        answers = []
        lines = full_response.split('\n')
        current_answer = ""
        
        for line in lines:
            if line.startswith("ANSWER Q"):
                if current_answer:
                    # Clean and add the previous answer
                    clean_answer = current_answer.strip()
                    if clean_answer.startswith("ANSWER Q"):
                        clean_answer = clean_answer.split(":", 1)[1].strip()
                    answers.append(clean_answer)
                current_answer = line
            else:
                current_answer += "\n" + line
        
        # Add the last answer
        if current_answer:
            clean_answer = current_answer.strip()
            if clean_answer.startswith("ANSWER Q"):
                clean_answer = clean_answer.split(":", 1)[1].strip()
            answers.append(clean_answer)
        
        # Ensure we have the right number of answers
        while len(answers) < len(questions):
            answers.append("Unable to generate answer for this question.")
        
        # Trim to exact number if we have too many
        answers = answers[:len(questions)]
        
        logger.info(f"✅ Successfully generated {len(answers)} answers in ONE API call")
        return answers
        
    except Exception as e:
        logger.error(f"Batch AI processing error: {e}")
        # Fallback: return error for all questions
        return [f"Error generating answer: {str(e)}"] * len(questions)

# API Endpoints
@app.on_event("startup")
async def startup_event():
    """Initialize AI model on startup"""
    success = await initialize_ai_model()
    if not success:
        logger.warning("⚠️ Gemini model failed to initialize")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "api": "healthy",
            "gemini": "healthy" if gemini_model else "unhealthy",
            "document_processing": "healthy"
        },
        "version": "2.1.0",
        "optimization": "BATCH_PROCESSING"
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
        cleanup_needed = False
        
        if request.documents.startswith("http"):
            # Download from URL
            document_path = await download_document(request.documents)
            cleanup_needed = True
        elif request.documents.startswith("file:///"):
            # Local file path
            local_path = request.documents.replace("file:///", "")
            # Handle Windows paths
            if not local_path.startswith("/") and ":" not in local_path:
                local_path = "/" + local_path
            local_path = local_path.replace("/", "\\")
            
            if not os.path.exists(local_path):
                raise HTTPException(status_code=400, detail=f"File not found: {local_path}")
            document_path = local_path
        else:
            raise HTTPException(status_code=400, detail="Invalid document path. Use HTTP URL or file:/// path")
        
        # Step 2: Extract text from document
        logger.info(f"Extracting text from document: {document_path}")
        text_content, doc_info = await extract_text_from_pdf(document_path)
        
        logger.info(f"Extracted {len(text_content)} characters from {doc_info['total_pages']} pages")
        
        # Step 3: BATCH PROCESS ALL QUESTIONS IN ONE API CALL
        logger.info(f"🚀 BATCH Processing {len(request.questions)} questions in ONE API call")
        
        try:
            # Use batch processing for all questions
            answers = await generate_batch_answers(request.questions, text_content)
            logger.info(f"✅ Batch processing successful: {len(answers)} answers generated")
        except Exception as e:
            logger.error(f"Batch processing failed: {str(e)}, falling back to individual processing")
            
            # Fallback to individual processing if batch fails
            answers = []
            for i, question in enumerate(request.questions):
                logger.info(f"Processing question {i+1}: {question}")
                answer = await generate_ai_answer(question, text_content)
                answers.append(answer)
                
                # Add delay between individual calls to avoid rate limiting
                if i < len(request.questions) - 1:
                    await asyncio.sleep(2)
        
        # Cleanup temporary file if needed
        if cleanup_needed and document_path:
            try:
                os.unlink(document_path)
            except:
                pass
        
        logger.info(f"Successfully processed {len(request.questions)} questions using BATCH processing")
        
        return QueryResponse(
            answers=answers
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
        "message": "HackRX Advanced Document Q&A API v2",
        "version": "2.0.0",
        "features": [
            "Real PDF document processing",
            "AI-powered question answering with Gemini",
            "Support for URLs and local files",
            "Comprehensive document analysis",
            "Batch question processing"
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
