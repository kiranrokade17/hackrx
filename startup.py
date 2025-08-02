#!/usr/bin/env python3
"""
Startup script for the LLM-Powered Intelligent Query-Retrieval System
This script validates the environment and starts the application
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import Config
from utils.helpers import setup_logging

# Setup logging
setup_logging("INFO")
logger = logging.getLogger(__name__)

async def validate_environment():
    """Validate the environment configuration"""
    logger.info("Validating environment configuration...")
    
    # Check configuration
    config_status = Config.validate_config()
    if not config_status["valid"]:
        logger.error("Configuration validation failed:")
        for issue in config_status["issues"]:
            logger.error(f"  - {issue}")
        return False
    
    logger.info("✓ Configuration validation passed")
    
    # Test services
    try:
        # Test database connection
        from services.database import DatabaseService
        db_service = DatabaseService()
        await db_service.connect()
        db_health = await db_service.health_check()
        await db_service.disconnect()
        
        if db_health != "healthy":
            logger.warning("⚠ Database connection issues detected")
        else:
            logger.info("✓ Database connection test passed")
        
        # Test embedding service
        from services.embedding_service import EmbeddingService
        embedding_service = EmbeddingService()
        embedding_health = embedding_service.health_check()
        
        if embedding_health != "healthy":
            logger.warning("⚠ Embedding service issues detected")
        else:
            logger.info("✓ Embedding service test passed")
        
        # Test LLM service
        from services.llm_service import LLMService
        llm_service = LLMService()
        llm_health = llm_service.health_check()
        
        if llm_health != "healthy":
            logger.warning("⚠ LLM service issues detected")
        else:
            logger.info("✓ LLM service test passed")
        
        return True
        
    except Exception as e:
        logger.error(f"Service validation failed: {str(e)}")
        return False

def main():
    """Main startup function"""
    logger.info("Starting LLM-Powered Intelligent Query-Retrieval System...")
    logger.info("=" * 60)
    
    # Validate environment
    try:
        validation_result = asyncio.run(validate_environment())
        if not validation_result:
            logger.error("Environment validation failed. Please check the configuration.")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        sys.exit(1)
    
    logger.info("=" * 60)
    logger.info("Environment validation completed successfully!")
    logger.info("Starting FastAPI application...")
    
    # Start the FastAPI application
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
