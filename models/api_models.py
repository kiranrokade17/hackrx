from pydantic import BaseModel, Field, HttpUrl, validator
from typing import List, Optional, Dict, Any
from datetime import datetime

class QueryRequest(BaseModel):
    """Request model for document query processing"""
    documents: str = Field(..., description="URL to the document (PDF, DOCX, etc.)")
    questions: List[str] = Field(..., description="List of questions to ask about the document")
    
    @validator('questions')
    def validate_questions(cls, v):
        if len(v) < 1:
            raise ValueError('At least one question is required')
        return v

class QueryResponse(BaseModel):
    """Response model for document query processing"""
    answers: List[str] = Field(..., description="List of answers corresponding to the questions")

class DocumentChunk(BaseModel):
    """Model for document chunks"""
    chunk_id: str
    content: str
    metadata: Dict[str, Any] = {}
    embedding: Optional[List[float]] = None

class DocumentMetadata(BaseModel):
    """Model for document metadata"""
    document_id: str
    url: str
    title: Optional[str] = None
    file_type: str
    size_bytes: Optional[int] = None
    processed_at: datetime
    chunk_count: int
    status: str = "processed"

class SemanticSearchResult(BaseModel):
    """Model for semantic search results"""
    chunk_id: str
    content: str
    similarity_score: float
    metadata: Dict[str, Any] = {}

class QueryRecord(BaseModel):
    """Model for storing query records in database"""
    query_id: str
    document_url: str
    questions: List[str]
    answers: List[str]
    document_id: str
    api_key_used: str
    processed_at: datetime
    processing_time_ms: Optional[int] = None

class HealthStatus(BaseModel):
    """Model for health check responses"""
    status: str
    timestamp: datetime
    services: Dict[str, str]

class ErrorResponse(BaseModel):
    """Model for error responses"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime
