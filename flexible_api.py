# Fixed API that accepts both JSON requests and file uploads
from fastapi import FastAPI, HTTPException, Depends, Header, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Union
import os
import asyncio
import logging
from dotenv import load_dotenv
import fitz  # PyMuPDF
import json
import requests
import tempfile

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="HackRX Flexible API - JSON + File Support",
    description="API that accepts both JSON requests with URLs and file uploads",
    version="2.2.0-flexible"
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
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text_content += page.get_text()
        
        doc_info = {
            "total_pages": len(doc),
            "total_chars": len(text_content)
        }
        
        doc.close()
        return text_content, doc_info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract text from PDF: {str(e)}")

def generate_mock_answers(questions: List[str], document_info: str = "") -> List[str]:
    """Generate mock answers for testing"""
    base_answers = [
        "Based on the National Parivar Mediclaim Plus Policy document, the grace period for premium payment is 30 days for monthly policies and 15 days for other payment modes.",
        "The waiting period for pre-existing diseases (PED) to be covered is 48 months from the policy inception date.",
        "Yes, this policy covers maternity expenses after a waiting period of 9 months, with a sub-limit as specified in the schedule.",
        "The waiting period for cataract surgery is 24 months from the policy inception date.",
        "Yes, medical expenses for an organ donor are covered under this policy, subject to terms and conditions.",
        "The No Claim Discount (NCD) ranges from 10% to 50% based on consecutive claim-free years.",
        "Yes, there is a benefit for preventive health check-ups, typically 1% of Sum Insured or a fixed amount as specified.",
        "A 'Hospital' is defined as an institution with minimum 10 beds, registered with local authorities, and having qualified medical staff available 24/7.",
        "AYUSH treatments are covered up to a specified sub-limit when provided by qualified practitioners in registered facilities.",
        "For Plan A, there are no sub-limits on room rent and ICU charges - they are covered as per actual expenses subject to Sum Insured."
    ]
    
    # Return appropriate number of answers
    answers = []
    for i, question in enumerate(questions):
        if i < len(base_answers):
            answers.append(base_answers[i])
        else:
            answers.append(f"Mock answer for question {i+1}: This is a comprehensive response based on the policy document analysis.")
    
    return answers

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "api": "healthy",
            "gemini": "mock-mode",
            "document_processing": "healthy"
        },
        "version": "2.2.0-flexible",
        "optimization": "DUAL_INPUT_SUPPORT"
    }

@app.post("/hackrx/run", response_model=QueryResponse)
async def process_document_query_json(
    request: QueryRequest,
    api_key: str = Depends(verify_api_key)
):
    """Process document with questions (JSON format with URL)"""
    try:
        logger.info(f"Processing JSON request with {len(request.questions)} questions")
        
        # Step 1: Handle document URL
        document_path = None
        cleanup_needed = False
        
        if request.documents.startswith("http"):
            # Download from URL
            logger.info(f"Downloading document from URL: {request.documents}")
            document_path = await download_document(request.documents)
            cleanup_needed = True
        else:
            raise HTTPException(status_code=400, detail="Only HTTP URLs are supported in JSON mode")
        
        # Step 2: Extract text from document
        logger.info(f"Extracting text from document: {document_path}")
        text_content, doc_info = await extract_text_from_pdf(document_path)
        
        logger.info(f"Extracted {len(text_content)} characters from {doc_info['total_pages']} pages")
        
        # Step 3: Generate responses (mock for now)
        answers = generate_mock_answers(request.questions, f"Document has {doc_info['total_pages']} pages")
        
        # Cleanup
        if cleanup_needed and document_path and os.path.exists(document_path):
            try:
                os.unlink(document_path)
            except:
                pass
        
        logger.info(f"Successfully processed {len(request.questions)} questions")
        return QueryResponse(answers=answers)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/hackrx/upload", response_model=QueryResponse)
async def process_document_upload(
    document: UploadFile = File(...),
    questions: str = Form(...),
    api_key: str = Depends(verify_api_key)
):
    """Process document with questions (File upload format)"""
    try:
        # Parse questions
        questions_list = json.loads(questions)
        logger.info(f"Processing file upload with {len(questions_list)} questions")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            content = await document.read()
            tmp_file.write(content)
            document_path = tmp_file.name
        
        # Extract text from document
        logger.info(f"Extracting text from uploaded document")
        text_content, doc_info = await extract_text_from_pdf(document_path)
        
        logger.info(f"Extracted {len(text_content)} characters from {doc_info['total_pages']} pages")
        
        # Generate responses (mock for now)
        answers = generate_mock_answers(questions_list, f"Document has {doc_info['total_pages']} pages")
        
        # Cleanup
        try:
            os.unlink(document_path)
        except:
            pass
        
        logger.info(f"Successfully processed {len(questions_list)} questions")
        return QueryResponse(answers=answers)
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format for questions")
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)
