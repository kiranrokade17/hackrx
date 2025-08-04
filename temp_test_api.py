# Temporary API with mock responses for testing
from fastapi import FastAPI, HTTPException, Depends, Header, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import asyncio
import logging
from dotenv import load_dotenv
import fitz  # PyMuPDF
import json

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="HackRX Test API - Mock Responses",
    description="Temporary API with mock responses for testing",
    version="2.1.0-test"
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
        "version": "2.1.0-test",
        "optimization": "MOCK_RESPONSES"
    }

@app.post("/hackrx/run", response_model=QueryResponse)
async def process_document_query(
    document: UploadFile = File(...),
    questions: str = Form(...),
    api_key: str = Depends(verify_api_key)
):
    """Process document with questions (MOCK VERSION)"""
    try:
        # Parse questions
        questions_list = json.loads(questions)
        logger.info(f"Processing request with {len(questions_list)} questions")
        
        # Mock responses
        mock_answers = [
            f"Mock answer for question {i+1}: This is a sample response generated for testing purposes. The API is working correctly, but using mock data instead of real AI responses.",
            f"Mock answer for question {i+1}: Your document has been processed successfully. This demonstrates that file upload, authentication, and response formatting are all working properly.",
            f"Mock answer for question {i+1}: The system is ready for production once you update the Gemini API key. All other components are functioning correctly.",
            f"Mock answer for question {i+1}: This mock response shows that your API structure is solid and ready for real AI integration.",
            f"Mock answer for question {i+1}: Everything is working perfectly! Just update the API key and you'll have full AI functionality."
        ]
        
        # Return appropriate number of answers
        answers = mock_answers[:len(questions_list)]
        
        logger.info(f"Successfully processed {len(questions_list)} questions using MOCK responses")
        return QueryResponse(answers=answers)
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format for questions")
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
