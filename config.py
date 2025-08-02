import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the application"""
    
    # API Configuration
    API_TITLE = "LLM-Powered Intelligent Query-Retrieval System"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = "Process large documents and make contextual decisions for insurance, legal, HR, and compliance domains"
    
    # Security
    SECRET_KEY = os.getenv("API_SECRET_KEY", "your-secret-key-change-this-in-production")
    ALLOWED_API_KEYS = os.getenv("ALLOWED_API_KEYS", "").split(",")
    
    # LLM Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = "gemini-1.5-flash"
    
    # Vector Store Configuration
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "document-embeddings")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "gcp-starter")
    
    # Database Configuration
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "llm_query_system")
    
    # Document Processing
    MAX_DOCUMENT_SIZE = 50 * 1024 * 1024  # 50MB
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # Search Configuration
    SEMANTIC_SEARCH_TOP_K = 5
    SIMILARITY_THRESHOLD = 0.7
    
    # Embedding Configuration
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION = 384
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validate configuration and return status"""
        issues = []
        
        if not cls.GEMINI_API_KEY:
            issues.append("GEMINI_API_KEY not set")
        
        if not cls.ALLOWED_API_KEYS or cls.ALLOWED_API_KEYS == [""]:
            issues.append("ALLOWED_API_KEYS not set")
        
        if not cls.MONGODB_URL:
            issues.append("MONGODB_URL not set")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }

# Development Configuration
class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = "DEBUG"

# Production Configuration
class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = "INFO"

# Test Configuration
class TestConfig(Config):
    TESTING = True
    MONGODB_DATABASE = "llm_query_system_test"

# Configuration mapping
config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "test": TestConfig
}

def get_config(environment: str = "development") -> Config:
    """Get configuration based on environment"""
    return config_map.get(environment, DevelopmentConfig)
