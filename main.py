from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
import logging
from dotenv import load_dotenv
import hashlib
import json
import asyncio
import time

from services.document_processor import DocumentProcessor
from services.embedding_service import EmbeddingService
from services.llm_service import LLMService
from services.vector_store import VectorStore
from services.database import DatabaseService
from services.rag_service import RAGService
from services.semantic_chunker import SemanticChunker
from services.rag_vector_store import RAGVectorStore
from models.api_models import QueryRequest, QueryResponse, DocumentMetadata

# Load environment variables
load_dotenv()

# Global cache for processed documents
document_cache = {}
CACHE_EXPIRY = 3600  # 1 hour

def clean_expired_cache():
    """Remove expired cache entries"""
    current_time = time.time()
    expired_keys = [
        key for key, value in document_cache.items() 
        if current_time - value['processed_at'] > CACHE_EXPIRY
    ]
    for key in expired_keys:
        del document_cache[key]
    if expired_keys:
        logger.info(f"Cleaned {len(expired_keys)} expired cache entries")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="LLM-Powered Intelligent Query-Retrieval System",
    description="Process large documents and make contextual decisions for insurance, legal, HR, and compliance domains",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
ALLOWED_API_KEYS = os.getenv("ALLOWED_API_KEYS", "").split(",")

def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """Verify API key authentication"""
    if credentials.credentials not in ALLOWED_API_KEYS:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    return credentials.credentials

# Initialize services
document_processor = DocumentProcessor()
embedding_service = EmbeddingService()
llm_service = LLMService()
vector_store = VectorStore()
db_service = DatabaseService()

# Initialize RAG services
rag_service = RAGService()
semantic_chunker = SemanticChunker()
rag_vector_store = RAGVectorStore()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        await db_service.connect()
        await vector_store.initialize()
        rag_vector_store.initialize()
        logger.info("All services including RAG initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    try:
        await db_service.disconnect()
        logger.info("Services cleaned up successfully")
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "LLM-Powered Intelligent Query-Retrieval System",
        "status": "active",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "database": await db_service.health_check(),
            "vector_store": await vector_store.health_check(),
            "llm_service": llm_service.health_check(),
            "embedding_service": embedding_service.health_check()
        }
    }

@app.post("/hackrx/run", response_model=QueryResponse)
async def process_query_rag(
    request: QueryRequest,
    api_key: str = Depends(verify_api_key)
) -> QueryResponse:
    """
    RAG-based document Q&A endpoint using proper two-phase approach
    Phase 1: Semantic chunking and embedding indexing
    Phase 2: Semantic retrieval and focused answer generation
    """
    try:
        start_time = time.time()
        logger.info(f"Processing RAG query with {len(request.questions)} questions")
        
        # Clean expired cache entries
        clean_expired_cache()
        
        # Phase 1: Document Indexing (if not cached)
        doc_hash = hashlib.md5(request.documents.encode()).hexdigest()
        
        if doc_hash in document_cache:
            logger.info("Using cached document embeddings")
            document_id = document_cache[doc_hash]['document_id']
            # RAG vector store retains data from previous processing
        else:
            logger.info("Phase 1: Indexing document with RAG approach")
            
            # Step 1a: Download and extract document content
            document_content = await document_processor.process_document(request.documents)
            
            # Step 1b: Smart semantic chunking based on document type
            document_type = "resume" if "resume" in request.documents.lower() else "general"
            chunks = semantic_chunker.chunk_document(document_content, document_type)
            
            logger.info(f"Created {len(chunks)} semantic chunks")
            
            # Step 1c: Create embeddings using Google's embedding model
            chunk_texts = [chunk['content'] for chunk in chunks]
            embeddings = await rag_service.create_embeddings(chunk_texts)
            
            # Step 1d: Store in RAG vector store for semantic search
            document_id = rag_vector_store.store_document(chunks, embeddings)
            
            # Cache the processed document
            document_cache[doc_hash] = {
                'document_id': document_id,
                'processed_at': time.time()
            }
            
            logger.info(f"Phase 1 complete: Indexed {len(chunks)} chunks")
        
        # Phase 2: Question Processing and Answer Generation (BATCH PROCESSING)
        logger.info("Phase 2: Processing all questions with RAG approach")
        
        try:
            # Get comprehensive context for all questions
            all_contexts = []
            for question in request.questions:
                # Step 2a: Create query embedding for each question
                query_embedding = await rag_service.create_query_embedding(question)
                
                # Step 2b: Retrieve relevant chunks for this question
                relevant_chunks = rag_vector_store.retrieve_relevant_chunks(
                    query_embedding, 
                    top_k=3  # Fewer chunks per question since we're batching
                )
                
                if relevant_chunks:
                    context = rag_vector_store.build_context_from_chunks(relevant_chunks)
                    all_contexts.append(context)
            
            # Combine contexts for comprehensive understanding
            combined_context = "\n\n".join(all_contexts) if all_contexts else "No relevant context found."
            
            # Remove duplicates to reduce context size
            unique_chunks = []
            seen_chunks = set()
            for context in all_contexts:
                if context not in seen_chunks:
                    unique_chunks.append(context)
                    seen_chunks.add(context)
            
            # Use the first comprehensive context or combine unique chunks
            final_context = "\n\n".join(unique_chunks[:10])  # Limit to prevent token overflow
            
            # BATCH PROCESSING: Generate answers for ALL questions in ONE API call
            logger.info(f"Processing {len(request.questions)} questions in ONE API call")
            answers = await rag_service.generate_batch_answers(request.questions, final_context)
            
        except Exception as e:
            logger.error(f"Batch processing failed: {str(e)}, falling back to individual processing")
            
            # Fallback to individual processing if batch fails
            async def process_rag_question(question: str) -> str:
                try:
                    logger.info(f"Phase 2: Processing question with RAG: {question[:50]}...")
                    
                    # Step 2a: Create query embedding
                    query_embedding = await rag_service.create_query_embedding(question)
                    
                    # Step 2b: Retrieve most relevant chunks using semantic similarity
                    relevant_chunks = rag_vector_store.retrieve_relevant_chunks(
                        query_embedding, 
                        top_k=5
                    )
                    
                    if not relevant_chunks:
                        logger.warning("No relevant chunks found, using all chunks as fallback")
                        relevant_chunks = rag_vector_store.get_all_chunks()[:5]
                    
                    # Step 2c: Build focused context from retrieved chunks
                    context = rag_vector_store.build_context_from_chunks(relevant_chunks)
                    
                    # Step 2d: Generate answer using RAG approach
                    answer = await rag_service.generate_answer(question, context)
                    
                    logger.info(f"RAG answer generated ({len(answer)} chars)")
                    return answer
                    
                except Exception as e:
                    logger.error(f"Error in RAG question processing: {str(e)}")
                    return f"Error processing question with RAG: {str(e)}"
            
            # Process questions individually with delays
            answers = []
            for i, question in enumerate(request.questions):
                if i > 0:
                    await asyncio.sleep(2)  # 2 second delay between questions
                answer = await process_rag_question(question)
                answers.append(answer)
        
        # Store results
        query_record = {
            "document_url": request.documents,
            "questions": request.questions,
            "answers": answers,
            "document_id": document_id,
            "api_key_used": api_key[:8] + "...",
            "processing_time": time.time() - start_time,
            "method": "RAG"
        }
        await db_service.store_query_result(query_record)
        
        processing_time = time.time() - start_time
        logger.info(f"RAG processing complete: {len(answers)} answers in {processing_time:.2f}s")
        
        return QueryResponse(answers=answers)
        
    except Exception as e:
        logger.error(f"Error in RAG process_query: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"RAG processing error: {str(e)}"
        )

@app.get("/documents/{document_id}/metadata")
async def get_document_metadata(
    document_id: str,
    api_key: str = Depends(verify_api_key)
) -> DocumentMetadata:
    """Get metadata for a processed document"""
    try:
        metadata = await db_service.get_document_metadata(document_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Document not found")
        return DocumentMetadata(**metadata)
    except Exception as e:
        logger.error(f"Error retrieving document metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/queries/history")
async def get_query_history(
    limit: int = 10,
    api_key: str = Depends(verify_api_key)
) -> List[Dict[str, Any]]:
    """Get query history"""
    try:
        history = await db_service.get_query_history(limit=limit)
        return history
    except Exception as e:
        logger.error(f"Error retrieving query history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
