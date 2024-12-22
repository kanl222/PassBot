from typing import Any, Dict, Optional



class LookupCache:
    """Efficient in-memory cache for user lookups."""

    def __init__(self, max_size: int = 1000):
        self._cache: dict = {}
        self._max_size = max_size

    def get(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve cached user data."""
        return self._cache.get(telegram_id)

    def set(self, telegram_id: int, user_data: Dict[str, Any]) -> None:
        """Cache user data with size management."""
        if len(self._cache) >= self._max_size:
            self._cache.pop(next(iter(self._cache)))
        self._cache[telegram_id] = user_data
