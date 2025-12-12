# api/workspaces/service.py
# Phase 7: Team Collaboration - Service Layer

import logging
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from .models import (
    SharedContactListCreate,
    WorkspaceCreate,
    WorkspaceMemberInvite,
    WorkspaceResponse,
    WorkspaceRole,
)

logger = logging.getLogger(__name__)


class WorkspaceService:
    """Service for managing workspaces and team collaboration"""

    def __init__(self, supabase_client, auth_client, email_service):
        self.db = supabase_client
        self.auth = auth_client
        self.email = email_service

    # ============ WORKSPACE MANAGEMENT ============

    async def create_workspace(
        self, user_id: UUID, workspace_data: WorkspaceCreate
    ) -> WorkspaceResponse:
        """Create a new workspace for user"""
        try:
            # 1. Create workspace
            workspace = (
                await self.db.table("workspaces")
                .insert(
                    {
                        "name": workspace_data.name,
                        "owner_id": str(user_id),
                        "plan": workspace_data.plan.value,
                        "created_at": datetime.utcnow().isoformat(),
                        "updated_at": datetime.utcnow().isoformat(),
                    }
                )
                .execute()
            )

            workspace_id = workspace.data[0]["id"]

            # 2. Add owner as admin member
            await self.db.table("workspace_members").insert(
                {
                    "workspace_id": workspace_id,
                    "user_id": str(user_id),
                    "role": WorkspaceRole.OWNER.value,
                    "joined_at": datetime.utcnow().isoformat(),
                }
            ).execute()

            # 3. Log activity
            await self._log_activity(
                workspace_id=workspace_id,
                user_id=user_id,
                action="workspace_created",
                description=f'Created workspace "{workspace_data.name}"',
            )

            logger.info(f"Workspace {workspace_id} created by user {user_id}")
            return await self.get_workspace(workspace_id, user_id)

        except Exception as e:
            logger.error(f"Error creating workspace: {e}")
            raise

    async def get_workspace(self, workspace_id: UUID, user_id: UUID) -> WorkspaceResponse:
        """Get workspace details"""
        try:
            # 1. Check user has access
            member = (
                await self.db.table("workspace_members")
                .select("*")
                .eq("workspace_id", str(workspace_id))
                .eq("user_id", str(user_id))
                .execute()
            )

            if not member.data:
                raise PermissionError(f"User {user_id} not member of workspace {workspace_id}")

            # 2. Get workspace
            workspace = (
                await self.db.table("workspaces").select("*").eq("id", str(workspace_id)).execute()
            )

            if not workspace.data:
                raise ValueError(f"Workspace {workspace_id} not found")

            # 3. Get members
            members = (
                await self.db.table("workspace_members")
                .select("*")
                .eq("workspace_id", str(workspace_id))
                .execute()
            )

            ws_data = workspace.data[0]
            members_list = [
                {
                    "user_id": m["user_id"],
                    "email": m.get("email", ""),
                    "role": m["role"],
                    "joined_at": m["joined_at"],
                }
                for m in members.data
            ]

            return WorkspaceResponse(
                id=UUID(ws_data["id"]),
                name=ws_data["name"],
                owner_id=UUID(ws_data["owner_id"]),
                plan=ws_data["plan"],
                member_count=len(members_list),
                members=members_list,
                created_at=datetime.fromisoformat(ws_data["created_at"]),
                updated_at=datetime.fromisoformat(ws_data["updated_at"]),
            )

        except Exception as e:
            logger.error(f"Error getting workspace: {e}")
            raise

    async def list_user_workspaces(self, user_id: UUID, page: int = 1, per_page: int = 10):
        """List all workspaces for user"""
        try:
            offset = (page - 1) * per_page

            # Get workspace IDs user is member of
            members = (
                await self.db.table("workspace_members")
                .select("workspace_id")
                .eq("user_id", str(user_id))
                .range(offset, offset + per_page - 1)
                .execute()
            )

            workspace_ids = [m["workspace_id"] for m in members.data]

            # Get workspace details
            workspaces = []
            for ws_id in workspace_ids:
                try:
                    ws = await self.get_workspace(UUID(ws_id), user_id)
                    workspaces.append(ws)
                except:
                    pass  # Skip if access denied

            # Get total count
            total = (
                await self.db.table("workspace_members")
                .select("*", count="exact")
                .eq("user_id", str(user_id))
                .execute()
            )

            return {
                "workspaces": workspaces,
                "total": total.count or 0,
                "page": page,
                "per_page": per_page,
            }

        except Exception as e:
            logger.error(f"Error listing workspaces: {e}")
            raise

    # ============ MEMBER MANAGEMENT ============

    async def invite_member(
        self, workspace_id: UUID, user_id: UUID, invite_data: WorkspaceMemberInvite
    ) -> Dict[str, Any]:
        """Invite user to workspace"""
        try:
            # 1. Check inviter has permission (admin or owner)
            inviter = (
                await self.db.table("workspace_members")
                .select("role")
                .eq("workspace_id", str(workspace_id))
                .eq("user_id", str(user_id))
                .execute()
            )

            if not inviter.data or inviter.data[0]["role"] not in ["owner", "admin"]:
                raise PermissionError(f"User {user_id} cannot invite members")

            # 2. Find or create user by email
            invited_user = await self.auth.get_user_by_email(invite_data.email)

            # 3. Check not already member
            existing = (
                await self.db.table("workspace_members")
                .select("*")
                .eq("workspace_id", str(workspace_id))
                .eq("user_id", str(invited_user.id))
                .execute()
            )

            if existing.data:
                raise ValueError(f"User already member of workspace")

            # 4. Add member
            member = (
                await self.db.table("workspace_members")
                .insert(
                    {
                        "workspace_id": str(workspace_id),
                        "user_id": str(invited_user.id),
                        "email": invite_data.email,
                        "role": invite_data.role.value,
                        "joined_at": datetime.utcnow().isoformat(),
                    }
                )
                .execute()
            )

            # 5. Send invite email
            await self.email.send_workspace_invite(
                to_email=invite_data.email,
                workspace_id=str(workspace_id),
                invited_by=str(user_id),
                message=invite_data.message,
            )

            # 6. Create notification
            await self._create_notification(
                user_id=invited_user.id,
                workspace_id=workspace_id,
                type="member_added",
                title="Added to Workspace",
                message=f"You were added to a workspace",
                data={"workspace_id": str(workspace_id), "invited_by": str(user_id)},
            )

            # 7. Log activity
            await self._log_activity(
                workspace_id=workspace_id,
                user_id=user_id,
                action="member_invited",
                description=f"Invited {invite_data.email} as {invite_data.role.value}",
            )

            logger.info(f"User {invited_user.id} invited to workspace {workspace_id}")

            return {
                "success": True,
                "message": f"Invitation sent to {invite_data.email}",
                "user_id": str(invited_user.id),
                "role": invite_data.role.value,
            }

        except Exception as e:
            logger.error(f"Error inviting member: {e}")
            raise

    async def remove_member(
        self, workspace_id: UUID, user_id: UUID, member_id: UUID
    ) -> Dict[str, Any]:
        """Remove member from workspace"""
        try:
            # 1. Check remover has permission
            remover = (
                await self.db.table("workspace_members")
                .select("role")
                .eq("workspace_id", str(workspace_id))
                .eq("user_id", str(user_id))
                .execute()
            )

            if not remover.data or remover.data[0]["role"] not in ["owner", "admin"]:
                raise PermissionError(f"User {user_id} cannot remove members")

            # 2. Check target not owner
            target = (
                await self.db.table("workspace_members")
                .select("role")
                .eq("workspace_id", str(workspace_id))
                .eq("user_id", str(member_id))
                .execute()
            )

            if target.data and target.data[0]["role"] == "owner":
                raise ValueError("Cannot remove workspace owner")

            # 3. Remove member
            await self.db.table("workspace_members").delete().eq(
                "workspace_id", str(workspace_id)
            ).eq("user_id", str(member_id)).execute()

            # 4. Log activity
            await self._log_activity(
                workspace_id=workspace_id,
                user_id=user_id,
                action="member_removed",
                description=f"Removed member {member_id}",
            )

            logger.info(f"Member {member_id} removed from workspace {workspace_id}")

            return {"success": True, "message": "Member removed"}

        except Exception as e:
            logger.error(f"Error removing member: {e}")
            raise

    # ============ SHARED CONTACTS ============

    async def create_shared_list(
        self, workspace_id: UUID, user_id: UUID, list_data: SharedContactListCreate
    ):
        """Create shared contact list"""
        try:
            shared_list = (
                await self.db.table("shared_contact_lists")
                .insert(
                    {
                        "workspace_id": str(workspace_id),
                        "name": list_data.name,
                        "description": list_data.description,
                        "contact_ids": list_data.contact_ids,
                        "created_by": str(user_id),
                        "created_at": datetime.utcnow().isoformat(),
                        "updated_at": datetime.utcnow().isoformat(),
                    }
                )
                .execute()
            )

            # Log activity
            await self._log_activity(
                workspace_id=workspace_id,
                user_id=user_id,
                action="list_created",
                description=f'Created shared list "{list_data.name}" with {len(list_data.contact_ids)} contacts',
            )

            return shared_list.data[0]

        except Exception as e:
            logger.error(f"Error creating shared list: {e}")
            raise

    # ============ ACTIVITY & NOTIFICATIONS ============

    async def _log_activity(
        self,
        workspace_id: UUID,
        user_id: UUID,
        action: str,
        description: str = "",
        contact_id: Optional[UUID] = None,
    ):
        """Log activity to audit trail"""
        try:
            await self.db.table("contact_activity_log").insert(
                {
                    "workspace_id": str(workspace_id),
                    "user_id": str(user_id),
                    "contact_id": str(contact_id) if contact_id else None,
                    "action": action,
                    "description": description,
                    "created_at": datetime.utcnow().isoformat(),
                }
            ).execute()
        except Exception as e:
            logger.error(f"Error logging activity: {e}")

    async def _create_notification(
        self, user_id: UUID, workspace_id: UUID, type: str, title: str, message: str, data: Dict
    ):
        """Create notification"""
        try:
            await self.db.table("notifications").insert(
                {
                    "user_id": str(user_id),
                    "workspace_id": str(workspace_id),
                    "type": type,
                    "title": title,
                    "message": message,
                    "data": data,
                    "read": False,
                    "created_at": datetime.utcnow().isoformat(),
                }
            ).execute()
        except Exception as e:
            logger.error(f"Error creating notification: {e}")

    async def get_notifications(self, user_id: UUID, workspace_id: UUID, limit: int = 20):
        """Get notifications for user"""
        try:
            notifications = (
                await self.db.table("notifications")
                .select("*")
                .eq("user_id", str(user_id))
                .eq("workspace_id", str(workspace_id))
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

            unread = (
                await self.db.table("notifications")
                .select("*", count="exact")
                .eq("user_id", str(user_id))
                .eq("workspace_id", str(workspace_id))
                .eq("read", False)
                .execute()
            )

            return {
                "notifications": notifications.data,
                "unread_count": unread.count or 0,
                "total": len(notifications.data),
            }

        except Exception as e:
            logger.error(f"Error getting notifications: {e}")
            raise

    async def mark_notification_read(self, notification_id: UUID):
        """Mark notification as read"""
        try:
            await self.db.table("notifications").update({"read": True}).eq(
                "id", str(notification_id)
            ).execute()
        except Exception as e:
            logger.error(f"Error marking notification: {e}")
            raise
