"""
Phase 9 Day 1: Redis Cache Tests

Test Coverage:
1. test_cache_hit - Cache retrieval works
2. test_cache_miss - Miss returns None
3. test_cache_invalidation - Workspace invalidation
4. test_ttl_expiration - TTL works correctly
5. test_cache_stats - Statistics tracking
6. test_concurrent_access - Thread safety
7. test_cache_warmup - Pre-computation
8. test_redis_connection_failure - Error handling

Target: 4x performance (200ms → 50ms)
"""

import pytest
import asyncio
import time
from typing import List
import redis.asyncio as redis

from api.cache import CacheManager, ContactRecommendation, CacheStats


@pytest.fixture
async def redis_client():
    """Create Redis test client"""
    client = redis.Redis(
        host='localhost',
        port=6379,
        password='superbrain_redis_2025',
        decode_responses=False
    )
    
    # Clear test data
    await client.flushdb()
    
    yield client
    
    # Cleanup
    await client.flushdb()
    await client.close()


@pytest.fixture
async def cache_manager(redis_client):
    """Create CacheManager instance"""
    manager = CacheManager(
        redis_client=redis_client,
        default_ttl=86400,
        key_prefix="test_superbrain"
    )
    yield manager
    await manager.close()


# ========== Test 1: Cache Hit ==========

@pytest.mark.asyncio
async def test_cache_hit(cache_manager):
    """Test successful cache retrieval"""
    workspace_id = "ws_123"
    contact_id = "contact_456"
    k = 20
    
    # Create test recommendations
    recommendations = [
        ContactRecommendation(contact_id=f"rec_{i}", score=0.9 - i*0.05)
        for i in range(k)
    ]
    
    # Set cache
    success = await cache_manager.set_recommendations(
        workspace_id, contact_id, recommendations, k
    )
    assert success is True
    
    # Get from cache
    cached = await cache_manager.get_recommendations(workspace_id, contact_id, k)
    
    assert cached is not None
    assert len(cached) == k
    assert cached[0].contact_id == "rec_0"
    assert cached[0].score == 0.9
    assert cache_manager.stats.hit_count == 1


# ========== Test 2: Cache Miss ==========

@pytest.mark.asyncio
async def test_cache_miss(cache_manager):
    """Test cache miss returns None"""
    result = await cache_manager.get_recommendations("ws_999", "contact_999", 20)
    
    assert result is None
    assert cache_manager.stats.miss_count == 1


# ========== Test 3: Cache Invalidation ==========

@pytest.mark.asyncio
async def test_cache_invalidation(cache_manager):
    """Test workspace cache invalidation"""
    workspace_id = "ws_789"
    
    # Cache 3 different contacts
    for i in range(3):
        recs = [ContactRecommendation(contact_id=f"c_{i}_{j}", score=0.8) for j in range(5)]
        await cache_manager.set_recommendations(workspace_id, f"contact_{i}", recs, k=5)
    
    # Verify cached
    cached = await cache_manager.get_recommendations(workspace_id, "contact_0", 5)
    assert cached is not None
    
    # Invalidate workspace
    deleted = await cache_manager.invalidate_workspace(workspace_id)
    assert deleted >= 3  # At least 3 keys deleted
    
    # Verify cache cleared
    cached_after = await cache_manager.get_recommendations(workspace_id, "contact_0", 5)
    assert cached_after is None


# ========== Test 4: TTL Expiration ==========

@pytest.mark.asyncio
async def test_ttl_expiration(cache_manager):
    """Test TTL expiration works"""
    workspace_id = "ws_ttl"
    contact_id = "contact_ttl"
    
    recs = [ContactRecommendation(contact_id="rec_1", score=0.9)]
    
    # Set with 2 second TTL
    await cache_manager.set_recommendations(
        workspace_id, contact_id, recs, k=1, ttl=2
    )
    
    # Immediately available
    cached = await cache_manager.get_recommendations(workspace_id, contact_id, 1)
    assert cached is not None
    
    # Wait for expiration
    await asyncio.sleep(3)
    
    # Should be expired
    cached_after = await cache_manager.get_recommendations(workspace_id, contact_id, 1)
    assert cached_after is None


# ========== Test 5: Cache Statistics ==========

@pytest.mark.asyncio
async def test_cache_stats(cache_manager):
    """Test cache statistics tracking"""
    workspace_id = "ws_stats"
    
    # Generate some cache activity
    recs = [ContactRecommendation(contact_id="c1", score=0.8)]
    
    # 3 sets
    for i in range(3):
        await cache_manager.set_recommendations(workspace_id, f"c{i}", recs, k=1)
    
    # 2 hits
    await cache_manager.get_recommendations(workspace_id, "c0", 1)
    await cache_manager.get_recommendations(workspace_id, "c1", 1)
    
    # 1 miss
    await cache_manager.get_recommendations(workspace_id, "c999", 1)
    
    # Get stats
    stats = await cache_manager.get_cache_stats()
    
    assert stats['hit_count'] == 2
    assert stats['miss_count'] == 1
    assert stats['hit_rate'] == pytest.approx(0.667, rel=0.01)
    assert stats['total_keys'] >= 3


# ========== Test 6: Concurrent Access ==========

@pytest.mark.asyncio
async def test_concurrent_access(cache_manager):
    """Test concurrent cache operations (thread safety)"""
    workspace_id = "ws_concurrent"
    
    async def cache_operation(contact_id: str):
        recs = [ContactRecommendation(contact_id=f"rec_{contact_id}", score=0.7)]
        await cache_manager.set_recommendations(workspace_id, contact_id, recs, k=1)
        result = await cache_manager.get_recommendations(workspace_id, contact_id, 1)
        return result
    
    # Run 10 concurrent operations
    tasks = [cache_operation(f"c{i}") for i in range(10)]
    results = await asyncio.gather(*tasks)
    
    # All should succeed
    assert all(r is not None for r in results)
    assert len(results) == 10


# ========== Test 7: Cache Warmup ==========

@pytest.mark.asyncio
async def test_cache_warmup(cache_manager):
    """Test cache warmup pre-computation"""
    workspace_id = "ws_warmup"
    
    # Mock functions
    async def mock_get_top_contacts(ws_id: str, limit: int):
        return [{'id': f"contact_{i}"} for i in range(limit)]
    
    async def mock_generate_recommendations(ws_id: str, contact_id: str, k: int):
        return [
            ContactRecommendation(contact_id=f"rec_{i}", score=0.9)
            for i in range(k)
        ]
    
    # Warmup with 5 contacts
    result = await cache_manager.warmup_cache(
        workspace_id=workspace_id,
        limit=5,
        get_top_contacts_func=mock_get_top_contacts,
        generate_recommendations_func=mock_generate_recommendations
    )
    
    assert result['contacts_cached'] == 5
    assert result['recommendations_generated'] == 5 * 20  # 5 contacts × 20 recs
    assert result['time_taken_sec'] > 0
    
    # Verify cache populated
    cached = await cache_manager.get_recommendations(workspace_id, "contact_0", 20)
    assert cached is not None
    assert len(cached) == 20


# ========== Test 8: Redis Connection Failure ==========

@pytest.mark.asyncio
async def test_redis_connection_failure():
    """Test graceful handling of Redis connection failure"""
    # Create client with wrong connection
    bad_client = redis.Redis(host='invalid_host', port=6379)
    cache_manager = CacheManager(redis_client=bad_client)
    
    # Should handle gracefully (not raise exception)
    result = await cache_manager.get_recommendations("ws_1", "c_1", 20)
    assert result is None  # Returns None on error
    
    success = await cache_manager.set_recommendations(
        "ws_1", "c_1", 
        [ContactRecommendation(contact_id="c1", score=0.8)],
        k=1
    )
    assert success is False  # Returns False on error
    
    await cache_manager.close()


# ========== Performance Test (Bonus) ==========

@pytest.mark.asyncio
async def test_performance_4x_improvement(cache_manager):
    """
    Test 4x latency improvement target
    
    Without cache: ~200ms (simulated GNN computation)
    With cache: <50ms (target)
    """
    workspace_id = "ws_perf"
    contact_id = "contact_perf"
    
    # Simulate slow GNN computation
    async def slow_compute():
        await asyncio.sleep(0.2)  # 200ms
        return [ContactRecommendation(contact_id=f"r{i}", score=0.9) for i in range(20)]
    
    # First call: compute + cache (slow)
    start = time.time()
    recs = await slow_compute()
    await cache_manager.set_recommendations(workspace_id, contact_id, recs, k=20)
    first_call_time = time.time() - start
    
    # Second call: from cache (fast!)
    start = time.time()
    cached_recs = await cache_manager.get_recommendations(workspace_id, contact_id, 20)
    cache_call_time = time.time() - start
    
    assert cached_recs is not None
    assert cache_call_time < 0.05  # <50ms (4x improvement!)
    assert first_call_time > 0.15  # >150ms (slow)
    
    speedup = first_call_time / cache_call_time
    print(f"\n✅ Performance: {speedup:.1f}x speedup ({first_call_time*1000:.0f}ms → {cache_call_time*1000:.0f}ms)")
    assert speedup >= 4  # At least 4x faster
