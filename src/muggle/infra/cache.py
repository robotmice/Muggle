"""In-memory exact-match query cache with TTL and LRU eviction."""

import threading
import time
from hashlib import md5


class QueryCache:
    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        self._cache: dict[str, tuple[float, str, list[dict]]] = {}
        self._lock = threading.Lock()
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds

    def _normalize(self, query: str) -> str:
        return md5(query.strip().lower().encode()).hexdigest()

    def get(self, query: str) -> tuple[str, list[dict]] | None:
        key = self._normalize(query)
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            ts, response, context = entry
            if time.monotonic() - ts < self.ttl_seconds:
                return response, context
            del self._cache[key]
        return None

    def put(self, query: str, response: str, context: list[dict]):
        key = self._normalize(query)
        with self._lock:
            if key in self._cache:
                return
            if len(self._cache) >= self.max_size:
                oldest = min(self._cache.items(), key=lambda x: x[1][0])
                del self._cache[oldest[0]]
            self._cache[key] = (time.monotonic(), response, context)

    def clear(self):
        with self._lock:
            self._cache.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._cache)
