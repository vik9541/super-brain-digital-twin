"""Gmail Routes API - Phase 9 Day 6-7"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from api.core.supabase_client import get_current_user
from api.integrations.gmail_sync import GmailSyncManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/gmail", tags=["Gmail Integration"])


class SyncRequest(BaseModel):
    workspace_id: str
    max_emails: int = 500


async def get_gmail_manager() -> GmailSyncManager:
    """Get GmailSyncManager from app state"""
    from api.main import supabase

    if not supabase:
        raise HTTPException(status_code=500, detail="Database not initialized")
    return GmailSyncManager(supabase)


@router.get("/connect")
async def get_gmail_connect_url(
    gmail: GmailSyncManager = Depends(get_gmail_manager),
    current_user: dict = Depends(get_current_user),
):
    """Get OAuth URL to connect Gmail"""
    try:
        auth_url = await gmail.get_auth_url(current_user["id"])
        return {"auth_url": auth_url}
    except Exception as e:
        logger.error(f"Failed to get auth URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/oauth-callback")
async def gmail_oauth_callback(
    code: str,
    gmail: GmailSyncManager = Depends(get_gmail_manager),
    current_user: dict = Depends(get_current_user),
):
    """Handle OAuth callback from Google"""
    try:
        success = await gmail.handle_oauth_callback(code, current_user["id"])
        if success:
            return {"status": "connected", "message": "Gmail connected successfully"}
        else:
            raise HTTPException(status_code=400, detail="OAuth failed")
    except Exception as e:
        logger.error(f"OAuth callback failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync")
async def sync_gmail_contacts(
    request: SyncRequest,
    gmail: GmailSyncManager = Depends(get_gmail_manager),
    current_user: dict = Depends(get_current_user),
):
    """Manually trigger Gmail sync"""
    try:
        result = await gmail.sync_contacts_and_interactions(
            current_user["id"], request.workspace_id, request.max_emails
        )
        return result
    except Exception as e:
        logger.error(f"Gmail sync failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_gmail_status(
    gmail: GmailSyncManager = Depends(get_gmail_manager),
    current_user: dict = Depends(get_current_user),
):
    """Get Gmail connection status"""
    try:
        status = await gmail.get_sync_status(current_user["id"])
        return status
    except Exception as e:
        logger.error(f"Failed to get status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/disconnect")
async def disconnect_gmail(
    gmail: GmailSyncManager = Depends(get_gmail_manager),
    current_user: dict = Depends(get_current_user),
):
    """Disconnect Gmail integration"""
    try:
        success = await gmail.disconnect(current_user["id"])
        if success:
            return {"status": "disconnected"}
        else:
            raise HTTPException(status_code=400, detail="Disconnect failed")
    except Exception as e:
        logger.error(f"Disconnect failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
