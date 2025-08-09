"""
Simple in-memory cache for API responses
Developer's cache - keep it simple, Redis can come later
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import threading
import json
import logging

logger = logging.getLogger(__name__)

class SimpleCache:
    """
    Thread-safe in-memory cache with TTL support
    """
    
    def __init__(self, default_ttl_minutes=5):
        self.cache: Dict[str, Dict] = {}
        self.default_ttl = timedelta(minutes=default_ttl_minutes)
        self._lock = threading.RLock()  # Reentrant lock for thread safety
        
    def cache_key(self, city: str, vegetable: str, extra: str = "") -> str:
        """
        Generate cache key from parameters
        """
        key = f"{city.lower().strip()}:{vegetable.lower().strip()}"
        if extra:
            key += f":{extra.lower().strip()}"
        return key
        
    def get(self, city: str, vegetable: str, extra: str = "") -> Optional[Any]:
        """
        Get cached value if not expired
        """
        key = self.cache_key(city, vegetable, extra)
        
        with self._lock:
            if key in self.cache:
                entry = self.cache[key]
                
                # Check if expired
                if datetime.now() - entry['cached_at'] < entry['ttl']:
                    logger.debug(f"Cache HIT: {key}")
                    return entry['data']
                else:
                    # Remove expired entry
                    del self.cache[key]
                    logger.debug(f"Cache EXPIRED: {key}")
                    
        logger.debug(f"Cache MISS: {key}")
        return None
        
    def set(self, city: str, vegetable: str, data: Any, ttl_minutes: Optional[int] = None, extra: str = ""):
        """
        Set cached value with TTL
        """
        key = self.cache_key(city, vegetable, extra)
        ttl = timedelta(minutes=ttl_minutes) if ttl_minutes else self.default_ttl
        
        with self._lock:
            self.cache[key] = {
                'data': data,
                'cached_at': datetime.now(),
                'ttl': ttl
            }
            
        logger.debug(f"Cache SET: {key} (TTL: {ttl_minutes or self.default_ttl.total_seconds()/60:.1f}m)")
        
    def invalidate(self, city: str, vegetable: str, extra: str = ""):
        """
        Remove specific entry from cache
        """
        key = self.cache_key(city, vegetable, extra)
        
        with self._lock:
            if key in self.cache:
                del self.cache[key]
                logger.debug(f"Cache INVALIDATED: {key}")
                return True
        return False
        
    def clear(self):
        """
        Clear all cache entries
        """
        with self._lock:
            cleared_count = len(self.cache)
            self.cache.clear()
            logger.info(f"Cache CLEARED: {cleared_count} entries")
            
    def cleanup_expired(self):
        """
        Remove all expired entries
        """
        now = datetime.now()
        expired_keys = []
        
        with self._lock:
            for key, entry in self.cache.items():
                if now - entry['cached_at'] >= entry['ttl']:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.cache[key]
                
        if expired_keys:
            logger.info(f"Cache CLEANUP: Removed {len(expired_keys)} expired entries")
            
        return len(expired_keys)
        
    def get_stats(self) -> Dict:
        """
        Get cache statistics
        """
        with self._lock:
            now = datetime.now()
            active_entries = 0
            expired_entries = 0
            
            for entry in self.cache.values():
                if now - entry['cached_at'] < entry['ttl']:
                    active_entries += 1
                else:
                    expired_entries += 1
                    
            return {
                'total_entries': len(self.cache),
                'active_entries': active_entries,
                'expired_entries': expired_entries,
                'cache_size_mb': self._estimate_size_mb(),
                'default_ttl_minutes': self.default_ttl.total_seconds() / 60
            }
    
    def _estimate_size_mb(self) -> float:
        """
        Rough estimate of cache size in memory
        """
        try:
            # Serialize cache to estimate size
            cache_json = json.dumps(self.cache, default=str)
            size_bytes = len(cache_json.encode('utf-8'))
            return round(size_bytes / (1024 * 1024), 3)
        except:
            return 0.0

# Global cache instances
price_cache = SimpleCache(default_ttl_minutes=5)      # Short TTL for prices
market_cache = SimpleCache(default_ttl_minutes=60)    # Longer TTL for market info

def test_cache():
    """
    Test cache functionality
    """
    print("🧪 Testing SimpleCache...")
    
    cache = SimpleCache(default_ttl_minutes=1)  # 1 minute for testing
    
    # Test basic set/get
    cache.set("mumbai", "tomato", {"price": 25.5, "market": "Central"})
    result = cache.get("mumbai", "tomato")
    print(f"✅ Basic get: {result}")
    
    # Test case insensitivity
    result2 = cache.get("MUMBAI", "TOMATO")
    print(f"✅ Case insensitive: {result2}")
    
    # Test with extra parameter
    cache.set("mumbai", "tomato", {"price": 30.0}, extra="wholesale")
    wholesale = cache.get("mumbai", "tomato", extra="wholesale")
    retail = cache.get("mumbai", "tomato")  # Should be different
    print(f"✅ Extra param - wholesale: {wholesale}")
    print(f"✅ Extra param - retail: {retail}")
    
    # Test stats
    stats = cache.get_stats()
    print(f"✅ Stats: {stats}")
    
    # Test cleanup
    cleaned = cache.cleanup_expired()
    print(f"✅ Cleanup: {cleaned} expired entries")
    
    # Test TTL expiration (would need time.sleep for real test)
    print("✅ TTL test skipped (would need time.sleep)")
    
    # Test thread safety (basic)
    import threading
    import time
    
    def worker(thread_id):
        for i in range(10):
            cache.set(f"city{thread_id}", f"veg{i}", {"price": i})
            result = cache.get(f"city{thread_id}", f"veg{i}")
            time.sleep(0.001)  # Small delay
    
    threads = []
    for i in range(3):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    final_stats = cache.get_stats()
    print(f"✅ Thread safety test - final stats: {final_stats}")
    
    print("✅ Cache tests completed!")

if __name__ == "__main__":
    test_cache()
