"""
Cache module for Super Brain Digital Twin

Exports:
    - CacheManager: Main Redis caching manager
    - ContactRecommendation: Recommendation data model
    - CacheStats: Cache statistics data model
"""

from api.cache.redis_manager import CacheManager, ContactRecommendation, CacheStats

__all__ = [
    "CacheManager",
    "ContactRecommendation", 
    "CacheStats"
]
