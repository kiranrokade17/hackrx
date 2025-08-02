import numpy as np
import logging
from typing import List, Dict, Any, Tuple
import faiss
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class RAGVectorStore:
    """
    Proper RAG Vector Store with semantic similarity search
    Optimized for accurate retrieval of relevant chunks
    """
    
    def __init__(self):
        self.index = None
        self.chunks = []
        self.embeddings = []
        self.dimension = 768  # Google embedding dimension
        self.is_initialized = False
    
    def initialize(self):
        """Initialize FAISS index for similarity search"""
        try:
            # Use Inner Product index for cosine similarity (after normalization)
            self.index = faiss.IndexFlatIP(self.dimension)
            self.is_initialized = True
            logger.info("RAG Vector Store initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG Vector Store: {str(e)}")
            raise Exception(f"Failed to initialize vector store: {str(e)}")
    
    def store_document(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]) -> str:
        """
        Phase 1: Store document chunks and their embeddings
        """
        try:
            if not self.is_initialized:
                self.initialize()
            
            # Clear previous data for new document
            self.chunks = chunks.copy()
            self.embeddings = embeddings.copy()
            
            # Normalize embeddings for cosine similarity
            embeddings_array = np.array(embeddings, dtype=np.float32)
            norms = np.linalg.norm(embeddings_array, axis=1, keepdims=True)
            normalized_embeddings = embeddings_array / norms
            
            # Reset and populate FAISS index
            self.index.reset()
            self.index.add(normalized_embeddings)
            
            logger.info(f"Stored {len(chunks)} chunks with embeddings in RAG vector store")
            return f"doc_{len(chunks)}_chunks"
            
        except Exception as e:
            logger.error(f"Error storing document in RAG vector store: {str(e)}")
            raise Exception(f"Failed to store document: {str(e)}")
    
    def retrieve_relevant_chunks(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Phase 2: Retrieve most relevant chunks for the query
        """
        try:
            if not self.is_initialized or self.index.ntotal == 0:
                logger.warning("No documents stored in vector store")
                return []
            
            # Normalize query embedding
            query_array = np.array([query_embedding], dtype=np.float32)
            query_norm = np.linalg.norm(query_array)
            if query_norm > 0:
                query_array = query_array / query_norm
            
            # Search for similar chunks
            scores, indices = self.index.search(query_array, min(top_k, self.index.ntotal))
            
            # Prepare results with metadata
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx >= 0 and idx < len(self.chunks):
                    chunk = self.chunks[idx].copy()
                    chunk['similarity_score'] = float(score)
                    chunk['rank'] = len(results) + 1
                    results.append(chunk)
            
            # Sort by similarity score (highest first)
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            logger.info(f"Retrieved {len(results)} relevant chunks (top-{top_k})")
            
            # Log retrieval details for debugging
            for i, chunk in enumerate(results[:3]):  # Log top 3
                content_preview = chunk['content'][:100].replace('\n', ' ')
                logger.info(f"  Rank {i+1}: Score={chunk['similarity_score']:.4f}, Preview='{content_preview}...'")
            
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving relevant chunks: {str(e)}")
            return []
    
    def get_all_chunks(self) -> List[Dict[str, Any]]:
        """
        Get all stored chunks (fallback for small documents)
        """
        try:
            if not self.chunks:
                return []
            
            # Add similarity scores of 1.0 for all chunks
            all_chunks = []
            for i, chunk in enumerate(self.chunks):
                chunk_copy = chunk.copy()
                chunk_copy['similarity_score'] = 1.0
                chunk_copy['rank'] = i + 1
                all_chunks.append(chunk_copy)
            
            logger.info(f"Retrieved all {len(all_chunks)} chunks")
            return all_chunks
            
        except Exception as e:
            logger.error(f"Error getting all chunks: {str(e)}")
            return []
    
    def build_context_from_chunks(self, chunks: List[Dict[str, Any]], max_context_length: int = 4000) -> str:
        """
        Build focused context from retrieved chunks for the LLM
        """
        try:
            if not chunks:
                return "No relevant context found."
            
            context_parts = []
            current_length = 0
            
            for i, chunk in enumerate(chunks):
                content = chunk.get('content', '').strip()
                score = chunk.get('similarity_score', 0)
                chunk_id = chunk.get('chunk_id', f'chunk_{i}')
                
                # Create context section with metadata
                section = f"--- Context Section {i+1} (Relevance: {score:.3f}, ID: {chunk_id}) ---\n{content}\n"
                
                # Check if adding this section would exceed length limit
                if current_length + len(section) > max_context_length and context_parts:
                    break
                
                context_parts.append(section)
                current_length += len(section)
            
            context = "\n".join(context_parts)
            logger.info(f"Built context from {len(context_parts)} chunks ({len(context)} chars)")
            
            return context
            
        except Exception as e:
            logger.error(f"Error building context: {str(e)}")
            return "Error building context from retrieved chunks."
    
    def health_check(self) -> str:
        """Health check for RAG vector store"""
        try:
            if not self.is_initialized:
                return "unhealthy - not initialized"
            
            if self.index is None:
                return "unhealthy - no index"
            
            if self.index.ntotal == 0:
                return "healthy - empty"
            
            return f"healthy - {self.index.ntotal} vectors stored"
            
        except Exception as e:
            logger.error(f"RAG vector store health check failed: {str(e)}")
            return "unhealthy"
