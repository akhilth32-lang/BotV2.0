# utils/cache_helpers.py

import time

class SimpleCache:
    def __init__(self):
        self.cache = {}

    def set(self, key, value, ttl=None):
        """Set a cache key with optional TTL (in seconds)."""
        expire_at = time.time() + ttl if ttl else None
        self.cache[key] = (value, expire_at)

    def get(self, key):
        """Get a cache value if valid; else None."""
        data = self.cache.get(key)
        if not data:
            return None

        value, expire_at = data
        if expire_at is None or expire_at > time.time():
            return value
        else:
            # Expired; remove from cache
            self.cache.pop(key, None)
            return None

    def delete(self, key):
        """Delete a key from cache."""
        self.cache.pop(key, None)

    def clear(self):
        """Clear entire cache."""
        self.cache.clear()

# Create a global simple cache instance for shared use
simple_cache = SimpleCache()
