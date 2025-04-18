import time
from typing import Dict, Any

class ScanCache:
  def __init__(self, ttl: int = 3600):
    self.cache: Dict[str, Dict[str, Any]] = {}
    self.ttl = ttl

  def add(self, key: str, data: dict):
    self.cache[key] = {
      "timestamp": time.time(),
      "data": data
    }

  def get(self, key: str) -> dict:
    entry = self.cache.get(key)

    if not entry:
      return None

    if (time.time() - entry["timestamp"]) > self.ttl:
      del self.cache[key]
      return None

    return entry["data"]

  def clear(self):
    self.cache.clear()
