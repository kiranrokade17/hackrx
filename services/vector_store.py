import os
import logging
import uuid
from typing import List, Dict, Any, Optional
from pinecone import Pinecone, ServerlessSpec
import faiss
import numpy as np
from datetime import datetime

from services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

class VectorStore:
    """Vector store service supporting both Pinecone and FAISS"""
    
    def __init__(self):
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.pinecone_index_name = os.getenv("PINECONE_INDEX_NAME", "document-embeddings")
        self.pinecone_environment = os.getenv("PINECONE_ENVIRONMENT", "gcp-starter")
        
        # Temporarily disable Pinecone to test with FAISS
        self.use_pinecone = False  # bool(self.pinecone_api_key)
        self.pinecone_index = None
        self.faiss_index = None
        self.faiss_metadata = {}  # Store metadata for FAISS
        self.embedding_service = EmbeddingService()
        
        logger.info(f"Vector store initialized with {'Pinecone' if self.use_pinecone else 'FAISS'}")
    
    async def initialize(self):
        """Initialize the vector store"""
        try:
            if self.use_pinecone:
                await self._initialize_pinecone()
            else:
                await self._initialize_faiss()
            
            logger.info("Vector store initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {str(e)}")
            raise Exception(f"Failed to initialize vector store: {str(e)}")
    
    async def _initialize_pinecone(self):
        """Initialize Pinecone vector store"""
        try:
            # Initialize Pinecone with new API
            pc = Pinecone(api_key=self.pinecone_api_key)
            
            # Check if index exists
            existing_indexes = pc.list_indexes().names()
            
            if self.pinecone_index_name not in existing_indexes:
                # Create index with ServerlessSpec
                logger.info(f"Creating Pinecone index: {self.pinecone_index_name}")
                pc.create_index(
                    name=self.pinecone_index_name,
                    dimension=384,  # all-MiniLM-L6-v2 dimension
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud='aws',
                        region=self.pinecone_environment
                    )
                )
            
            self.pinecone_index = pc.Index(self.pinecone_index_name)
            logger.info("Pinecone initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {str(e)}")
            raise
    
    async def _initialize_faiss(self):
        """Initialize FAISS vector store"""
        try:
            # Create FAISS index with cosine similarity
            dimension = 384  # all-MiniLM-L6-v2 dimension
            self.faiss_index = faiss.IndexFlatIP(dimension)  # Inner Product for cosine similarity
            logger.info("FAISS initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize FAISS: {str(e)}")
            raise
    
    async def store_embeddings(
        self, 
        chunks_with_embeddings: List[Dict[str, Any]], 
        metadata: Dict[str, Any]
    ) -> str:
        """
        Store embeddings in the vector store
        """
        try:
            document_id = str(uuid.uuid4())
            
            if self.use_pinecone:
                await self._store_in_pinecone(chunks_with_embeddings, document_id, metadata)
            else:
                await self._store_in_faiss(chunks_with_embeddings, document_id, metadata)
            
            logger.info(f"Stored {len(chunks_with_embeddings)} embeddings for document {document_id}")
            return document_id
            
        except Exception as e:
            logger.error(f"Error storing embeddings: {str(e)}")
            raise Exception(f"Failed to store embeddings: {str(e)}")
    
    async def _store_in_pinecone(
        self, 
        chunks_with_embeddings: List[Dict[str, Any]], 
        document_id: str, 
        metadata: Dict[str, Any]
    ):
        """Store embeddings in Pinecone"""
        vectors = []
        
        for chunk in chunks_with_embeddings:
            vector_id = f"{document_id}_{chunk['chunk_id']}"
            vector_metadata = {
                **chunk.get("metadata", {}),
                **metadata,
                "document_id": document_id,
                "content": chunk["content"][:1000],  # Limit content size
                "chunk_id": chunk["chunk_id"]
            }
            
            vectors.append({
                "id": vector_id,
                "values": chunk["embedding"],
                "metadata": vector_metadata
            })
        
        # Upsert vectors in batches
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self.pinecone_index.upsert(vectors=batch)
    
    async def _store_in_faiss(
        self, 
        chunks_with_embeddings: List[Dict[str, Any]], 
        document_id: str, 
        metadata: Dict[str, Any]
    ):
        """Store embeddings in FAISS"""
        embeddings = []
        
        for chunk in chunks_with_embeddings:
            embedding = np.array(chunk["embedding"], dtype=np.float32)
            # Normalize for cosine similarity
            embedding = embedding / np.linalg.norm(embedding)
            embeddings.append(embedding)
            
            # Store metadata
            vector_id = self.faiss_index.ntotal  # Current count becomes the ID
            self.faiss_metadata[vector_id] = {
                **chunk.get("metadata", {}),
                **metadata,
                "document_id": document_id,
                "content": chunk["content"],
                "chunk_id": chunk["chunk_id"]
            }
        
        # Add to FAISS index
        embeddings_array = np.vstack(embeddings)
        self.faiss_index.add(embeddings_array)
    
    async def get_all_chunks(self) -> List[Dict[str, Any]]:
        """Get all stored chunks - useful for small documents"""
        try:
            all_chunks = []
            for idx, metadata in self.faiss_metadata.items():
                all_chunks.append({
                    "content": metadata.get("content", ""),
                    "similarity_score": 1.0,  # Max similarity since we want all chunks
                    "metadata": metadata,
                    "chunk_id": metadata.get("chunk_id", "")
                })
            
            # Sort by chunk_id to maintain order
            all_chunks.sort(key=lambda x: x.get("chunk_id", ""))
            logger.info(f"Retrieved {len(all_chunks)} chunks")
            return all_chunks
            
        except Exception as e:
            logger.error(f"Error getting all chunks: {str(e)}")
            return []

    async def semantic_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform semantic search to find relevant chunks
        """
        try:
            # Generate query embedding
            query_embedding = await self.embedding_service.generate_query_embedding(query)
            
            if self.use_pinecone:
                results = await self._search_pinecone(query_embedding, top_k)
            else:
                results = await self._search_faiss(query_embedding, top_k)
            
            logger.info(f"Found {len(results)} relevant chunks for query")
            return results
            
        except Exception as e:
            logger.error(f"Error in semantic search: {str(e)}")
            raise Exception(f"Failed to perform semantic search: {str(e)}")
    
    async def _search_pinecone(self, query_embedding: List[float], top_k: int) -> List[Dict[str, Any]]:
        """Search using Pinecone"""
        response = self.pinecone_index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        results = []
        for match in response.matches:
            results.append({
                "content": match.metadata.get("content", ""),
                "similarity_score": float(match.score),
                "metadata": match.metadata,
                "chunk_id": match.metadata.get("chunk_id", "")
            })
        
        return results
    
    async def _search_faiss(self, query_embedding: List[float], top_k: int) -> List[Dict[str, Any]]:
        """Search using FAISS"""
        if self.faiss_index.ntotal == 0:
            return []
        
        # Normalize query embedding for cosine similarity
        query_array = np.array([query_embedding], dtype=np.float32)
        query_array = query_array / np.linalg.norm(query_array)
        
        # Search
        scores, indices = self.faiss_index.search(query_array, min(top_k, self.faiss_index.ntotal))
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1:  # Valid result
                metadata = self.faiss_metadata.get(idx, {})
                results.append({
                    "content": metadata.get("content", ""),
                    "similarity_score": float(score),
                    "metadata": metadata,
                    "chunk_id": metadata.get("chunk_id", "")
                })
        
        return results
    
    async def health_check(self) -> str:
        """Health check for vector store"""
        try:
            if self.use_pinecone:
                if self.pinecone_index is None:
                    return "unhealthy - Pinecone not initialized"
                # Test Pinecone connection
                stats = self.pinecone_index.describe_index_stats()
                return "healthy"
            else:
                if self.faiss_index is None:
                    return "unhealthy - FAISS not initialized"
                return "healthy"
                
        except Exception as e:
            logger.error(f"Vector store health check failed: {str(e)}")
            return "unhealthy"
