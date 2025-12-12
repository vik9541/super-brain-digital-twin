# api/workspaces/routes.py
# Phase 7: Team Collaboration - API Routes

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.dependencies import get_current_user, get_workspace_service

from .models import (
    ActivityLogResponse,
    NotificationListResponse,
    SharedContactListCreate,
    WorkspaceCreate,
    WorkspaceMemberInvite,
    WorkspaceResponse,
)
from .service import WorkspaceService

router = APIRouter(prefix="/api/workspaces", tags=["workspaces"])


# ============ WORKSPACE MANAGEMENT ============


@router.post("/", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    workspace_data: WorkspaceCreate,
    current_user: dict = Depends(get_current_user),
    workspace_service: WorkspaceService = Depends(get_workspace_service),
):
    """
    Create a new workspace.

    - **name**: Workspace name (required)
    - **plan**: Subscription plan (free, pro, enterprise) - default: pro
    """
    try:
        workspace = await workspace_service.create_workspace(
            user_id=UUID(current_user["id"]), workspace_data=workspace_data
        )
        return workspace
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=dict)
async def list_workspaces(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    workspace_service: WorkspaceService = Depends(get_workspace_service),
):
    """
    List all workspaces for current user.

    - **page**: Page number (default: 1)
    - **per_page**: Results per page (default: 10, max: 100)
    """
    try:
        result = await workspace_service.list_user_workspaces(
            user_id=UUID(current_user["id"]), page=page, per_page=per_page
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: UUID,
    current_user: dict = Depends(get_current_user),
    workspace_service: WorkspaceService = Depends(get_workspace_service),
):
    """
    Get workspace details by ID.
    """
    try:
        workspace = await workspace_service.get_workspace(
            workspace_id=workspace_id, user_id=UUID(current_user["id"])
        )
        return workspace
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You don't have access to this workspace"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============ MEMBER MANAGEMENT ============


@router.post("/{workspace_id}/members", status_code=status.HTTP_201_CREATED)
async def invite_member(
    workspace_id: UUID,
    invite_data: WorkspaceMemberInvite,
    current_user: dict = Depends(get_current_user),
    workspace_service: WorkspaceService = Depends(get_workspace_service),
):
    """
    Invite a member to the workspace.

    - **email**: Email address of user to invite (required)
    - **role**: Role (member, admin, viewer) - default: member
    - **message**: Optional invitation message
    """
    try:
        result = await workspace_service.invite_member(
            workspace_id=workspace_id, user_id=UUID(current_user["id"]), invite_data=invite_data
        )
        return result
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to invite members",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{workspace_id}/members/{member_id}")
async def remove_member(
    workspace_id: UUID,
    member_id: UUID,
    current_user: dict = Depends(get_current_user),
    workspace_service: WorkspaceService = Depends(get_workspace_service),
):
    """
    Remove a member from the workspace.
    """
    try:
        result = await workspace_service.remove_member(
            workspace_id=workspace_id, user_id=UUID(current_user["id"]), member_id=member_id
        )
        return result
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to remove members",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============ SHARED CONTACTS ============


@router.post("/{workspace_id}/shared-lists", status_code=status.HTTP_201_CREATED)
async def create_shared_list(
    workspace_id: UUID,
    list_data: SharedContactListCreate,
    current_user: dict = Depends(get_current_user),
    workspace_service: WorkspaceService = Depends(get_workspace_service),
):
    """
    Create a shared contact list.

    - **name**: List name (required)
    - **description**: Optional description
    - **contact_ids**: List of contact UUIDs to include
    """
    try:
        shared_list = await workspace_service.create_shared_list(
            workspace_id=workspace_id, user_id=UUID(current_user["id"]), list_data=list_data
        )
        return shared_list
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============ NOTIFICATIONS ============


@router.get("/{workspace_id}/notifications", response_model=NotificationListResponse)
async def get_notifications(
    workspace_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    workspace_service: WorkspaceService = Depends(get_workspace_service),
):
    """
    Get notifications for current user in workspace.

    - **limit**: Number of notifications to return (default: 20, max: 100)
    """
    try:
        result = await workspace_service.get_notifications(
            user_id=UUID(current_user["id"]), workspace_id=workspace_id, limit=limit
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: UUID,
    current_user: dict = Depends(get_current_user),
    workspace_service: WorkspaceService = Depends(get_workspace_service),
):
    """
    Mark notification as read.
    """
    try:
        await workspace_service.mark_notification_read(notification_id)
        return {"success": True, "message": "Notification marked as read"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============ ACTIVITY LOG ============


@router.get("/{workspace_id}/activity", response_model=ActivityLogResponse)
async def get_activity_log(
    workspace_id: UUID,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    workspace_service: WorkspaceService = Depends(get_workspace_service),
):
    """
    Get activity log for workspace.

    - **page**: Page number (default: 1)
    - **per_page**: Results per page (default: 20, max: 100)
    """
    try:
        # Verify user has access to workspace
        await workspace_service.get_workspace(
            workspace_id=workspace_id, user_id=UUID(current_user["id"])
        )

        # Get activity log
        offset = (page - 1) * per_page
        activity = (
            await workspace_service.db.table("contact_activity_log")
            .select("*")
            .eq("workspace_id", str(workspace_id))
            .order("created_at", desc=True)
            .range(offset, offset + per_page - 1)
            .execute()
        )

        total = (
            await workspace_service.db.table("contact_activity_log")
            .select("*", count="exact")
            .eq("workspace_id", str(workspace_id))
            .execute()
        )

        return {
            "entries": activity.data or [],
            "total": total.count or 0,
            "page": page,
            "per_page": per_page,
        }
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You don't have access to this workspace"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
