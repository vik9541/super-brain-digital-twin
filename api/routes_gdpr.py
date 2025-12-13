"""
GDPR API Routes - Phase 9 Day 3-4

Endpoints for GDPR compliance.

Author: Super Brain Team
Created: 2025-12-13
"""

import logging
import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel

from api.core.gdpr import GDPRManager
from api.core.supabase_client import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/gdpr", tags=["GDPR Compliance"])


# Dependency: Get GDPRManager
async def get_gdpr_manager() -> GDPRManager:
    """Get GDPRManager from app state"""
    from api.main import supabase

    if not supabase:
        raise HTTPException(status_code=500, detail="Database not initialized")
    return GDPRManager(supabase)


# ========== Request Models ==========


class ExportRequest(BaseModel):
    workspace_id: str
    authorized_by: Optional[str] = None


class DeleteRequest(BaseModel):
    reason: str
    confirm: bool  # User must explicitly confirm
    authorized_by: Optional[str] = None


# ========== Endpoints ==========


@router.post("/export")
async def request_data_export(
    request: ExportRequest,
    gdpr: GDPRManager = Depends(get_gdpr_manager),
    current_user: dict = Depends(get_current_user),
):
    """
    Request data export (GDPR Article 15 - Right to Access)

    Returns export_id to track status.
    """
    try:
        user_id = current_user["id"]

        export_id = await gdpr.export_user_data(
            user_id=user_id,
            workspace_id=request.workspace_id,
            authorized_by=request.authorized_by or user_id,
        )

        return {
            "export_id": export_id,
            "status": "in_progress",
            "message": "Your data export is being prepared",
            "check_status_url": f"/api/gdpr/export-status/{export_id}",
        }

    except Exception as e:
        logger.error(f"Export request failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export-status/{export_id}")
async def get_export_status(
    export_id: str,
    gdpr: GDPRManager = Depends(get_gdpr_manager),
    current_user: dict = Depends(get_current_user),
):
    """Get export status by export_id"""
    try:
        status = await gdpr.get_export_status(export_id)
        return status
    except Exception as e:
        logger.error(f"Failed to get export status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{export_id}")
async def download_export(
    export_id: str,
    gdpr: GDPRManager = Depends(get_gdpr_manager),
    current_user: dict = Depends(get_current_user),
):
    """Download exported data as ZIP"""
    try:
        zip_path = os.path.join(gdpr.exports_dir, f"{export_id}.zip")

        if not os.path.exists(zip_path):
            raise HTTPException(status_code=404, detail="Export not found")

        with open(zip_path, "rb") as f:
            content = f.read()

        return Response(
            content=content,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename=gdpr_export_{export_id}.zip"},
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/delete")
async def request_data_deletion(
    request: DeleteRequest,
    gdpr: GDPRManager = Depends(get_gdpr_manager),
    current_user: dict = Depends(get_current_user),
):
    """
    Request data deletion (GDPR Article 17 - Right to Erasure)

    IMPORTANT: This anonymizes data, not hard delete.
    """
    try:
        if not request.confirm:
            raise HTTPException(
                status_code=400, detail="You must confirm deletion by setting 'confirm': true"
            )

        user_id = current_user["id"]

        operation_id = await gdpr.delete_user_data(
            user_id=user_id, reason=request.reason, authorized_by=request.authorized_by or user_id
        )

        return {
            "operation_id": operation_id,
            "status": "completed",
            "message": "Your data has been anonymized",
            "legal_notice": "Data anonymized per GDPR Article 17. Audit logs retained for 7 years.",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Deletion request failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/restrict")
async def restrict_processing(
    gdpr: GDPRManager = Depends(get_gdpr_manager), current_user: dict = Depends(get_current_user)
):
    """
    Restrict data processing (GDPR Article 18)

    When restricted:
    - Data stored but not processed
    - No recommendations, analytics, emails
    """
    try:
        user_id = current_user["id"]

        success = await gdpr.restrict_processing(user_id, authorized_by=user_id)

        if success:
            return {
                "status": "restricted",
                "message": "Data processing has been restricted",
                "effects": [
                    "Recommendations disabled",
                    "Analytics disabled",
                    "Email notifications disabled",
                    "Data stored but not processed",
                ],
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to restrict processing")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Restrict processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/unrestrict")
async def unrestrict_processing(
    gdpr: GDPRManager = Depends(get_gdpr_manager), current_user: dict = Depends(get_current_user)
):
    """Unrestrict data processing"""
    try:
        user_id = current_user["id"]
        success = await gdpr.unrestrict_processing(user_id, authorized_by=user_id)

        if success:
            return {"status": "unrestricted", "message": "Data processing has been enabled"}
        else:
            raise HTTPException(status_code=500, detail="Failed to unrestrict processing")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unrestrict processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data-locations")
async def get_data_locations(
    gdpr: GDPRManager = Depends(get_gdpr_manager), current_user: dict = Depends(get_current_user)
):
    """
    Show where your data is stored (transparency)

    Returns databases, file storage, third-party services, retention periods.
    """
    try:
        user_id = current_user["id"]
        locations = await gdpr.get_data_locations(user_id)
        return locations

    except Exception as e:
        logger.error(f"Failed to get data locations: {e}")
        raise HTTPException(status_code=500, detail=str(e))
