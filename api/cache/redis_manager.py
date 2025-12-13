"""
Redis Cache Manager для Super Brain Digital Twin

Purpose:
    Кеширование GNN recommendations для:
    - 4x latency improvement: 200ms → 50ms
    - 80% cost reduction
    - Handle 10K req/sec
    - Cache hit rate target: 80%+

Cache Strategy:
    - Recommendations: 24h TTL
    - Model embeddings: 7d TTL
    - Invalidate on contact changes
    - Pre-warm on startup

Author: Super Brain Team
Created: 2025-12-13
"""

import json
import logging
from typing import List, Dict, Optional, Any
from datetime import timedelta
import redis.asyncio as redis
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ContactRecommendation(BaseModel):
    """Cached recommendation structure"""
    contact_id: str
    score: float
    reason: Optional[str] = None


class CacheStats(BaseModel):
    """Cache statistics"""
    total_keys: int = 0
    hit_count: int = 0
    miss_count: int = 0
    
    @property
    def hit_rate(self) -> float:
        total = self.hit_count + self.miss_count
        return self.hit_count / total if total > 0 else 0.0
    
    @property
    def miss_rate(self) -> float:
        return 1 - self.hit_rate


class CacheManager:
    """
    Redis-based caching для GNN recommendations
    
    Example:
        >>> cache = CacheManager(redis_client)
        >>> recommendations = await cache.get_recommendations(workspace_id, contact_id, k=20)
        >>> if recommendations is None:
        ...     recommendations = await compute_recommendations()
        ...     await cache.set_recommendations(workspace_id, contact_id, recommendations)
    """
    
    def __init__(
        self, 
        redis_client: redis.Redis,
        default_ttl: int = 86400,  # 24 hours
        key_prefix: str = "superbrain"
    ):
        """
        Initialize Cache Manager
        
        Args:
            redis_client: Async Redis client
            default_ttl: Default TTL in seconds (24h)
            key_prefix: Prefix for all cache keys
        """
        self.redis = redis_client
        self.default_ttl = default_ttl
        self.key_prefix = key_prefix
        self.stats = CacheStats()
    
    # ========== Core Methods ==========
    
    def _make_key(self, *parts: str) -> str:
        """
        Create cache key
        
        Format: superbrain:rec:{workspace_id}:{contact_id}:{k}
        """
        return f"{self.key_prefix}:{':'.join(parts)}"
    
    async def get_recommendations(
        self, 
        workspace_id: str, 
        contact_id: str, 
        k: int = 20
    ) -> Optional[List[ContactRecommendation]]:
        """
        Get cached recommendations
        
        Args:
            workspace_id: Workspace ID
            contact_id: Contact ID to get recommendations for
            k: Number of recommendations
        
        Returns:
            Cached recommendations if exists, None otherwise
        
        Side effects:
            Increments cache hit/miss stats
        """
        try:
            key = self._make_key("rec", workspace_id, contact_id, str(k))
            cached = await self.redis.get(key)
            
            if cached:
                self.stats.hit_count += 1
                data = json.loads(cached)
                return [ContactRecommendation(**item) for item in data]
            else:
                self.stats.miss_count += 1
                return None
                
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            self.stats.miss_count += 1
            return None
    
    async def set_recommendations(
        self, 
        workspace_id: str, 
        contact_id: str, 
        recommendations: List[ContactRecommendation],
        k: int = 20,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Cache recommendations
        
        Args:
            workspace_id: Workspace ID
            contact_id: Contact ID
            recommendations: List of recommendations to cache
            k: Number of recommendations
            ttl: TTL in seconds (uses default if None)
        
        Returns:
            True if cached successfully, False otherwise
        """
        try:
            key = self._make_key("rec", workspace_id, contact_id, str(k))
            data = [rec.model_dump() for rec in recommendations]
            value = json.dumps(data)
            
            ttl = ttl or self.default_ttl
            await self.redis.setex(key, ttl, value)
            
            logger.debug(f"Cached {len(recommendations)} recommendations for {contact_id} (TTL: {ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def invalidate_workspace(self, workspace_id: str) -> int:
        """
        Invalidate all cache for workspace
        
        Use cases:
            - Contact added/updated/deleted
            - Model retrained
            - Manual cache clear
        
        Args:
            workspace_id: Workspace ID
        
        Returns:
            Number of keys deleted
        """
        try:
            pattern = self._make_key("rec", workspace_id, "*")
            cursor = 0
            deleted_count = 0
            
            # Scan with pattern matching
            while True:
                cursor, keys = await self.redis.scan(
                    cursor=cursor, 
                    match=pattern, 
                    count=100
                )
                
                if keys:
                    deleted_count += await self.redis.delete(*keys)
                
                if cursor == 0:
                    break
            
            logger.info(f"Invalidated {deleted_count} cache keys for workspace {workspace_id}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
            return 0
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """
        Cache statistics
        
        Returns:
            {
                'memory_usage_mb': float,
                'total_keys': int,
                'hit_rate': float,
                'miss_rate': float,
                'avg_latency_ms': float
            }
        """
        try:
            info = await self.redis.info('memory')
            memory_mb = info.get('used_memory', 0) / (1024 * 1024)
            
            # Count total keys with our prefix
            pattern = self._make_key("*")
            cursor = 0
            total_keys = 0
            
            while True:
                cursor, keys = await self.redis.scan(
                    cursor=cursor, 
                    match=pattern, 
                    count=1000
                )
                total_keys += len(keys)
                
                if cursor == 0:
                    break
            
            return {
                'memory_usage_mb': round(memory_mb, 2),
                'total_keys': total_keys,
                'hit_count': self.stats.hit_count,
                'miss_count': self.stats.miss_count,
                'hit_rate': round(self.stats.hit_rate, 3),
                'miss_rate': round(self.stats.miss_rate, 3)
            }
            
        except Exception as e:
            logger.error(f"Stats error: {e}")
            return {
                'error': str(e),
                'hit_rate': self.stats.hit_rate,
                'miss_rate': self.stats.miss_rate
            }
    
    async def delete_cache_key(self, key: str) -> bool:
        """
        Delete specific cache key
        
        Args:
            key: Full cache key to delete
        
        Returns:
            True if deleted, False otherwise
        """
        try:
            deleted = await self.redis.delete(key)
            return deleted > 0
        except Exception as e:
            logger.error(f"Delete error: {e}")
            return False
    
    async def get_all_cache_keys(self, pattern: str = "*") -> List[str]:
        """
        Get all cache keys matching pattern
        
        Args:
            pattern: Redis pattern (e.g., "rec:*")
        
        Returns:
            List of matching keys
        """
        try:
            full_pattern = self._make_key(pattern)
            cursor = 0
            all_keys = []
            
            while True:
                cursor, keys = await self.redis.scan(
                    cursor=cursor, 
                    match=full_pattern, 
                    count=1000
                )
                all_keys.extend([k.decode() if isinstance(k, bytes) else k for k in keys])
                
                if cursor == 0:
                    break
            
            return all_keys
            
        except Exception as e:
            logger.error(f"Get keys error: {e}")
            return []
    
    async def warmup_cache(
        self, 
        workspace_id: str, 
        limit: int = 100,
        get_top_contacts_func = None,
        generate_recommendations_func = None
    ):
        """
        Pre-compute recommendations for top contacts
        
        Strategy:
            1. Get top N contacts by interaction frequency
            2. Pre-compute recommendations for each
            3. Cache results
        
        Use case:
            - On server startup
            - After model retraining
            - Scheduled job (daily)
        
        Args:
            workspace_id: Workspace ID
            limit: Number of top contacts to warm up
            get_top_contacts_func: Function to get top contacts
            generate_recommendations_func: Function to generate recommendations
        
        Returns:
            {
                'contacts_cached': int,
                'recommendations_generated': int,
                'time_taken_sec': float
            }
        """
        import time
        start_time = time.time()
        
        try:
            if not get_top_contacts_func or not generate_recommendations_func:
                logger.warning("Warmup functions not provided, skipping")
                return {
                    'contacts_cached': 0,
                    'recommendations_generated': 0,
                    'time_taken_sec': 0
                }
            
            # Get top contacts
            top_contacts = await get_top_contacts_func(workspace_id, limit)
            
            contacts_cached = 0
            recommendations_generated = 0
            
            for contact in top_contacts:
                # Generate recommendations
                recommendations = await generate_recommendations_func(
                    workspace_id, 
                    contact['id'], 
                    k=20
                )
                
                # Cache
                if recommendations:
                    success = await self.set_recommendations(
                        workspace_id,
                        contact['id'],
                        recommendations,
                        k=20
                    )
                    
                    if success:
                        contacts_cached += 1
                        recommendations_generated += len(recommendations)
            
            time_taken = time.time() - start_time
            
            logger.info(
                f"Cache warmup complete: {contacts_cached} contacts, "
                f"{recommendations_generated} recommendations, "
                f"{time_taken:.2f}s"
            )
            
            return {
                'contacts_cached': contacts_cached,
                'recommendations_generated': recommendations_generated,
                'time_taken_sec': round(time_taken, 2)
            }
            
        except Exception as e:
            logger.error(f"Warmup error: {e}")
            return {
                'error': str(e),
                'contacts_cached': 0,
                'recommendations_generated': 0,
                'time_taken_sec': 0
            }
    
    async def close(self):
        """Close Redis connection"""
        await self.redis.close()
