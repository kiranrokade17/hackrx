import logging
import time
from functools import wraps
from typing import Any, Callable, Optional, Generator, List
from datetime import datetime

def setup_logging(log_level: str = "INFO"):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def timing_decorator(func: Callable) -> Callable:
    """Decorator to measure function execution time"""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        logger = logging.getLogger(func.__module__)
        logger.info(f"{func.__name__} executed in {execution_time:.2f}ms")
        
        return result
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        logger = logging.getLogger(func.__module__)
        logger.info(f"{func.__name__} executed in {execution_time:.2f}ms")
        
        return result
    
    # Return the appropriate wrapper based on whether the function is async
    return async_wrapper if hasattr(func, '__code__') and func.__code__.co_flags & 0x80 else sync_wrapper

def sanitize_text(text: str) -> str:
    """Sanitize text for safe processing"""
    if not text:
        return ""
    
    # Remove null bytes and other problematic characters
    text = text.replace('\x00', '')
    
    # Limit length to prevent memory issues
    max_length = 1000000  # 1MB of text
    if len(text) > max_length:
        text = text[:max_length] + "... [truncated]"
    
    return text.strip()

def format_error_response(error: Exception, request_id: Optional[str] = None) -> dict:
    """Format error response for API"""
    return {
        "error": str(error),
        "type": type(error).__name__,
        "timestamp": datetime.utcnow().isoformat(),
        "request_id": request_id
    }

def validate_url(url: str) -> bool:
    """Validate if URL is accessible"""
    import re
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return url_pattern.match(url) is not None

def chunk_list(lst: List[Any], chunk_size: int) -> Generator[List[Any], None, None]:
    """Split list into chunks of specified size"""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]
