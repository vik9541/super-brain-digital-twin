"""
Analytics API Routes - Phase 9 Day 8-9

Endpoints for advanced analytics dashboard.

Author: Super Brain Team
Created: 2025-12-13
"""

import logging

from fastapi import APIRouter, Depends, HTTPException

from api.analytics.metrics import AnalyticsMetrics
from api.core.supabase_client import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


async def get_analytics_manager() -> AnalyticsMetrics:
    """Get AnalyticsMetrics from app state"""
    from api.main import supabase

    if not supabase:
        raise HTTPException(status_code=500, detail="Database not initialized")
    return AnalyticsMetrics(supabase)


@router.get("/metrics/{workspace_id}")
async def get_analytics_metrics(
    workspace_id: str,
    analytics: AnalyticsMetrics = Depends(get_analytics_manager),
    current_user: dict = Depends(get_current_user),
):
    """
    Get all analytics metrics

    Returns CLV, health score, engagement trends, top contacts
    """
    try:
        metrics = await analytics.get_metrics(workspace_id)
        return metrics
    except Exception as e:
        logger.error(f"Failed to get analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clv/{workspace_id}")
async def get_clv_metrics(
    workspace_id: str,
    analytics: AnalyticsMetrics = Depends(get_analytics_manager),
    current_user: dict = Depends(get_current_user),
):
    """Get Contact Lifetime Value metrics"""
    try:
        clv = await analytics.calculate_clv(workspace_id)
        return clv
    except Exception as e:
        logger.error(f"Failed to get CLV: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health/{workspace_id}")
async def get_health_score(
    workspace_id: str,
    analytics: AnalyticsMetrics = Depends(get_analytics_manager),
    current_user: dict = Depends(get_current_user),
):
    """Get Relationship Health Score"""
    try:
        health = await analytics.calculate_health_score(workspace_id)
        return health
    except Exception as e:
        logger.error(f"Failed to get health score: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/engagement/{workspace_id}")
async def get_engagement_trends(
    workspace_id: str,
    days: int = 30,
    analytics: AnalyticsMetrics = Depends(get_analytics_manager),
    current_user: dict = Depends(get_current_user),
):
    """Get engagement trends over time"""
    try:
        trends = await analytics.get_engagement_trends(workspace_id, days)
        return trends
    except Exception as e:
        logger.error(f"Failed to get engagement trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-contacts/{workspace_id}")
async def get_top_contacts(
    workspace_id: str,
    limit: int = 10,
    analytics: AnalyticsMetrics = Depends(get_analytics_manager),
    current_user: dict = Depends(get_current_user),
):
    """Get top performing contacts"""
    try:
        contacts = await analytics.get_top_contacts(workspace_id, limit)
        return {"contacts": contacts, "total": len(contacts)}
    except Exception as e:
        logger.error(f"Failed to get top contacts: {e}")
        raise HTTPException(status_code=500, detail=str(e))
