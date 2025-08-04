# test_api.py - Minimal working version for testing
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="HackRX Document Q&A API - Test Version",
    description="AI-powered document analysis with batch processing (Test Mode)",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class QueryRequest(BaseModel):
    documents: str
    questions: List[str]

class QueryResponse(BaseModel):
    answers: List[str]
    status: str = "success"

# Authentication
ALLOWED_API_KEYS = os.getenv("ALLOWED_API_KEYS", "api_key_1,api_key_2,api_key_3").split(",")

def verify_api_key(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    api_key = authorization.replace("Bearer ", "").strip()
    if api_key not in [key.strip() for key in ALLOWED_API_KEYS]:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return api_key

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "api": "healthy",
            "authentication": "healthy",
            "gemini": "available" if os.getenv("GEMINI_API_KEY") else "not_configured"
        }
    }

# Main API endpoint
@app.post("/hackrx/run", response_model=QueryResponse)
async def process_documents(
    request: QueryRequest,
    api_key: str = Depends(verify_api_key)
):
    try:
        # Mock responses for testing (replace with actual AI processing)
        mock_answers = []
        
        for i, question in enumerate(request.questions):
            if "grace period" in question.lower():
                mock_answers.append("The grace period for premium payment is 30 days.")
            elif "waiting period" in question.lower():
                mock_answers.append("The waiting period for pre-existing diseases is 36 months.")
            elif "maternity" in question.lower():
                mock_answers.append("Maternity expenses are covered after 9 months of continuous coverage.")
            elif "cataract" in question.lower():
                mock_answers.append("Cataract surgery has a waiting period of 24 months.")
            elif "organ donor" in question.lower():
                mock_answers.append("Medical expenses for organ donors are covered up to policy limits.")
            elif "no claim discount" in question.lower():
                mock_answers.append("No Claim Discount ranges from 5% to 50% based on claim-free years.")
            elif "health check" in question.lower():
                mock_answers.append("Annual preventive health check-ups are covered up to Rs. 2,000.")
            elif "hospital" in question.lower():
                mock_answers.append("Hospital is defined as a registered medical institution with 24/7 medical care.")
            elif "ayush" in question.lower():
                mock_answers.append("AYUSH treatments are covered up to 10% of sum insured.")
            elif "room rent" in question.lower():
                mock_answers.append("Room rent is covered without sub-limits under Plan A.")
            else:
                mock_answers.append(f"Answer for question {i+1}: Based on the document analysis, this information is available in the policy terms.")
        
        return QueryResponse(
            answers=mock_answers,
            status="success"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "HackRX Document Q&A API - Test Version",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "main_api": "/hackrx/run",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    PORT = int(os.getenv("PORT", 8003))
    uvicorn.run(app, host="0.0.0.0", port=PORT)
