import os
import logging
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import numpy as np

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating embeddings using sentence transformers"""
    
    def __init__(self):
        self.model_name = "all-MiniLM-L6-v2"  # Lightweight and efficient model
        self.model = None
        self.embedding_dimension = 384  # Dimension for all-MiniLM-L6-v2
    
    def _load_model(self):
        """Lazy load the embedding model"""
        if self.model is None:
            try:
                logger.info(f"Loading embedding model: {self.model_name}")
                self.model = SentenceTransformer(self.model_name)
                logger.info("Embedding model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {str(e)}")
                raise Exception(f"Failed to load embedding model: {str(e)}")
    
    async def generate_embeddings(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for document chunks
        """
        try:
            self._load_model()
            
            texts = [chunk["content"] for chunk in chunks]
            
            logger.info(f"Generating embeddings for {len(texts)} chunks")
            embeddings = self.model.encode(texts, convert_to_tensor=False)
            
            # Add embeddings to chunks
            for i, chunk in enumerate(chunks):
                chunk["embedding"] = embeddings[i].tolist()
            
            logger.info(f"Generated {len(embeddings)} embeddings")
            return chunks
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise Exception(f"Failed to generate embeddings: {str(e)}")
    
    async def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for a single query
        """
        try:
            self._load_model()
            
            embedding = self.model.encode([query], convert_to_tensor=False)
            return embedding[0].tolist()
            
        except Exception as e:
            logger.error(f"Error generating query embedding: {str(e)}")
            raise Exception(f"Failed to generate query embedding: {str(e)}")
    
    def cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings
        """
        try:
            a = np.array(embedding1)
            b = np.array(embedding2)
            
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
            
            similarity = dot_product / (norm_a * norm_b)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {str(e)}")
            return 0.0
    
    def health_check(self) -> str:
        """Health check for embedding service"""
        try:
            if self.model is None:
                self._load_model()
            return "healthy"
        except:
            return "unhealthy"
