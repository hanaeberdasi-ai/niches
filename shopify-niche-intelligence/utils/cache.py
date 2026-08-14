"""
Caching utilities for Shopify Niche Intelligence
"""
import time
import hashlib
import json
from typing import Any, Optional, Callable
from functools import wraps
from cachetools import TTLCache
import streamlit as st

from config.settings import config


class CacheManager:
    """Manages caching for the application"""
    
    def __init__(self, maxsize: int = 1000, ttl: int = 3600):
        self._cache = TTLCache(maxsize=maxsize, ttl=ttl)
    
    def _make_key(self, *args, **kwargs) -> str:
        """Generate a cache key from arguments"""
        key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        return self._cache.get(key)
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache"""
        self._cache[key] = value
    
    def delete(self, key: str) -> None:
        """Delete value from cache"""
        if key in self._cache:
            del self._cache[key]
    
    def clear(self) -> None:
        """Clear all cache"""
        self._cache.clear()
    
    def cached(self, ttl: Optional[int] = None):
        """Decorator to cache function results"""
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                key = f"{func.__name__}:{self._make_key(*args, **kwargs)}"
                result = self.get(key)
                if result is not None:
                    return result
                result = func(*args, **kwargs)
                self.set(key, result)
                return result
            return wrapper
        return decorator


# Global cache instance
cache_manager = CacheManager(
    maxsize=config.cache.max_size,
    ttl=config.cache.ttl
)


def get_session_cache(key: str, default: Any = None) -> Any:
    """Get value from Streamlit session state"""
    if key not in st.session_state:
        st.session_state[key] = default
    return st.session_state[key]


def set_session_cache(key: str, value: Any) -> None:
    """Set value in Streamlit session state"""
    st.session_state[key] = value


def clear_session_cache() -> None:
    """Clear all session cache"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
