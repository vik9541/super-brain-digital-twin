"""
Cache API Routes для Phase 9

Endpoints:
    POST /api/cache/invalidate/{workspace_id} - Clear workspace cache
    GET /api/cache/stats - Cache statistics
    DELETE /api/cache/{key} - Delete specific cache key
    POST /api/cache/warmup/{workspace_id} - Pre-compute recommendations

Author: Super Brain Team
Created: 2025-12-13
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging

from api.cache import CacheManager
from api.core.supabase_client import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/cache", tags=["Cache"])


# Dependency: Get CacheManager instance
# Will be injected from main.py via app.state
async def get_cache_manager() -> CacheManager:
    """Get CacheManager from app state"""
    from api.main import app
    if not hasattr(app.state, 'cache_manager'):
        raise HTTPException(status_code=500, detail="Cache manager not initialized")
    return app.state.cache_manager


@router.post("/invalidate/{workspace_id}")
async def invalidate_workspace_cache(
    workspace_id: str,
    cache_manager: CacheManager = Depends(get_cache_manager),
    current_user: Dict = Depends(get_current_user)
):
    """
    Invalidate all cache for workspace
    
    Use cases:
        - Contact added/updated/deleted
        - Manual cache clear
        - After model retraining
    
    Returns:
        {
            "workspace_id": str,
            "keys_deleted": int,
            "message": str
        }
    """
    try:
        deleted_count = await cache_manager.invalidate_workspace(workspace_id)
        
        return {
            "workspace_id": workspace_id,
            "keys_deleted": deleted_count,
            "message": f"Successfully invalidated {deleted_count} cache keys"
        }
    
    except Exception as e:
        logger.error(f"Cache invalidation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_cache_statistics(
    cache_manager: CacheManager = Depends(get_cache_manager),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get cache statistics
    
    Returns:
        {
            "memory_usage_mb": float,
            "total_keys": int,
            "hit_count": int,
            "miss_count": int,
            "hit_rate": float (0.0 - 1.0),
            "miss_rate": float (0.0 - 1.0)
        }
    """
    try:
        stats = await cache_manager.get_cache_stats()
        return stats
    
    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{key}")
async def delete_cache_key(
    key: str,
    cache_manager: CacheManager = Depends(get_cache_manager),
    current_user: Dict = Depends(get_current_user)
):
    """
    Delete specific cache key
    
    Args:
        key: Full cache key (e.g., "superbrain:rec:ws123:contact456:20")
    
    Returns:
        {
            "key": str,
            "deleted": bool,
            "message": str
        }
    """
    try:
        deleted = await cache_manager.delete_cache_key(key)
        
        if deleted:
            return {
                "key": key,
                "deleted": True,
                "message": "Cache key deleted successfully"
            }
        else:
            return {
                "key": key,
                "deleted": False,
                "message": "Cache key not found or already deleted"
            }
    
    except Exception as e:
        logger.error(f"Failed to delete cache key: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/warmup/{workspace_id}")
async def warmup_workspace_cache(
    workspace_id: str,
    limit: int = 100,
    cache_manager: CacheManager = Depends(get_cache_manager),
    current_user: Dict = Depends(get_current_user)
):
    """
    Pre-compute recommendations for top contacts
    
    Strategy:
        1. Get top N contacts by interaction frequency
        2. Generate recommendations for each
        3. Cache results
    
    Use cases:
        - Server startup
        - After model retraining
        - Scheduled job (daily)
    
    Args:
        workspace_id: Workspace ID
        limit: Number of top contacts to warm up (default: 100)
    
    Returns:
        {
            "workspace_id": str,
            "contacts_cached": int,
            "recommendations_generated": int,
            "time_taken_sec": float
        }
    """
    try:
        # Import GNN recommender functions
        from api.ml.gnn_recommender import get_top_contacts, generate_recommendations
        
        result = await cache_manager.warmup_cache(
            workspace_id=workspace_id,
            limit=limit,
            get_top_contacts_func=get_top_contacts,
            generate_recommendations_func=generate_recommendations
        )
        
        return {
            "workspace_id": workspace_id,
            **result
        }
    
    except Exception as e:
        logger.error(f"Cache warmup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/keys")
async def list_cache_keys(
    pattern: str = "*",
    cache_manager: CacheManager = Depends(get_cache_manager),
    current_user: Dict = Depends(get_current_user)
):
    """
    List all cache keys matching pattern
    
    Args:
        pattern: Redis pattern (e.g., "rec:*", "rec:ws123:*")
    
    Returns:
        {
            "pattern": str,
            "keys": List[str],
            "count": int
        }
    """
    try:
        keys = await cache_manager.get_all_cache_keys(pattern)
        
        return {
            "pattern": pattern,
            "keys": keys,
            "count": len(keys)
        }
    
    except Exception as e:
        logger.error(f"Failed to list cache keys: {e}")
        raise HTTPException(status_code=500, detail=str(e))
