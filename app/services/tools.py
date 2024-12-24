import asyncio
from functools import lru_cache, wraps
from typing import Any, Callable, Dict, Optional

def async_lru_cache(maxsize: Optional[int] = 128, typed: bool = False):
    """
    LRU cache decorator for async functions with minimal overhead.
    
    Args:
        maxsize: Maximum size of the cache
        typed: If True, arguments of different types will be cached separately
    
    Returns:
        Cached async function
    """
    def decorator(func):
        @lru_cache(maxsize=maxsize, typed=typed)
        def cached_func(*args, **kwargs):
            return asyncio.run(func(*args, **kwargs))
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: cached_func(*args, **kwargs)
            )
        
        wrapper.cache_info = cached_func.cache_info
        wrapper.cache_clear = cached_func.cache_clear
        return wrapper
    
    return decorator




