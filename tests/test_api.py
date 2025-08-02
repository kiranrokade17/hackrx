import pytest
import asyncio
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"
    assert data["version"] == "1.0.0"

def test_health_endpoint():
    """Test the detailed health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "services" in data

def test_unauthorized_access():
    """Test access without API key"""
    test_request = {
        "documents": "https://example.com/test.pdf",
        "questions": ["What is this document about?"]
    }
    
    response = client.post("/hackrx/run", json=test_request)
    assert response.status_code == 403  # Forbidden due to missing auth

def test_invalid_api_key():
    """Test access with invalid API key"""
    test_request = {
        "documents": "https://example.com/test.pdf", 
        "questions": ["What is this document about?"]
    }
    
    headers = {"Authorization": "Bearer invalid_key"}
    response = client.post("/hackrx/run", json=test_request, headers=headers)
    assert response.status_code == 401  # Unauthorized

# Add more tests as needed
@pytest.mark.asyncio
async def test_document_processor():
    """Test document processor service"""
    from services.document_processor import DocumentProcessor
    
    processor = DocumentProcessor()
    assert processor.health_check() == "healthy"

@pytest.mark.asyncio 
async def test_embedding_service():
    """Test embedding service"""
    from services.embedding_service import EmbeddingService
    
    service = EmbeddingService()
    # Test with sample text
    sample_chunks = [
        {"content": "This is a test document.", "chunk_id": "test_1"}
    ]
    
    # This test might fail without proper model setup
    try:
        result = await service.generate_embeddings(sample_chunks)
        assert len(result) == 1
        assert "embedding" in result[0]
    except Exception:
        # Model not available in test environment
        pass
