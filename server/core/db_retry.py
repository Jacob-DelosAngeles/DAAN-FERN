"""
Database retry utility for handling transient connection failures.
Useful for cross-region connections (e.g., Render US <-> Supabase Singapore).
"""

import time
import logging
from functools import wraps
from sqlalchemy.exc import OperationalError, InterfaceError

logger = logging.getLogger(__name__)


def with_db_retry(max_retries: int = 3, delay: float = 0.5):
    """
    Decorator that retries database operations on connection failures.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries (increases exponentially)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (OperationalError, InterfaceError) as e:
                    last_exception = e
                    error_msg = str(e)
                    
                    # Check if it's a connection-related error
                    if any(x in error_msg.lower() for x in [
                        'connection', 'timeout', 'could not connect',
                        'server closed', 'connection refused',
                        'connection reset', 'eof detected'
                    ]):
                        if attempt < max_retries:
                            wait_time = delay * (2 ** attempt)  # Exponential backoff
                            logger.warning(
                                f"Database connection failed (attempt {attempt + 1}/{max_retries + 1}). "
                                f"Retrying in {wait_time:.1f}s..."
                            )
                            time.sleep(wait_time)
                            continue
                    
                    # Not a connection error or max retries reached
                    raise
            
            # Max retries exhausted
            logger.error(f"Database connection failed after {max_retries + 1} attempts")
            raise last_exception
        
        return wrapper
    return decorator


async def with_db_retry_async(max_retries: int = 3, delay: float = 0.5):
    """
    Async version of the retry decorator.
    """
    import asyncio
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except (OperationalError, InterfaceError) as e:
                    last_exception = e
                    error_msg = str(e)
                    
                    if any(x in error_msg.lower() for x in [
                        'connection', 'timeout', 'could not connect',
                        'server closed', 'connection refused',
                        'connection reset', 'eof detected'
                    ]):
                        if attempt < max_retries:
                            wait_time = delay * (2 ** attempt)
                            logger.warning(
                                f"Database connection failed (attempt {attempt + 1}/{max_retries + 1}). "
                                f"Retrying in {wait_time:.1f}s..."
                            )
                            await asyncio.sleep(wait_time)
                            continue
                    
                    raise
            
            raise last_exception
        
        return wrapper
    return decorator
