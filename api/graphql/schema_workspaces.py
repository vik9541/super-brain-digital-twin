# api/graphql/schema_workspaces.py
# Phase 7: Team Collaboration - GraphQL Schema

from ariadne import ObjectType, QueryType, MutationType, make_executable_schema
from ariadne.asgi import make_graphql_handler
from typing import Optional, List
from uuid import UUID

# Type definitions
type_defs = """
    enum WorkspaceRole {
        OWNER
        ADMIN
        MEMBER
        VIEWER
    }
    
    enum WorkspacePlan {
        FREE
        PRO
        ENTERPRISE
    }
    
    type WorkspaceMember {
        userId: UUID!
        email: String!
        name: String
        role: WorkspaceRole!
        joinedAt: DateTime!
    }
    
    type Workspace {
        id: UUID!
        name: String!
        ownerId: UUID!
        plan: WorkspacePlan!
        memberCount: Int!
        members: [WorkspaceMember!]!
        createdAt: DateTime!
        updatedAt: DateTime!
    }
    
    type WorkspaceList {
        workspaces: [Workspace!]!
        total: Int!
        page: Int!
        perPage: Int!
    }
    
    type SharedContactList {
        id: UUID!
        workspaceId: UUID!
        name: String!
        description: String
        contactCount: Int!
        createdBy: UUID!
        createdAt: DateTime!
        updatedAt: DateTime!
    }
    
    type ActivityLogEntry {
        id: UUID!
        workspaceId: UUID!
        contactId: UUID
        userId: UUID!
        userName: String
        action: String!
        description: String
        details: JSON
        createdAt: DateTime!
    }
    
    type ActivityLog {
        entries: [ActivityLogEntry!]!
        total: Int!
        page: Int!
        perPage: Int!
    }
    
    type Notification {
        id: UUID!
        type: String!
        title: String!
        message: String!
        data: JSON!
        read: Boolean!
        createdAt: DateTime!
    }
    
    type NotificationList {
        notifications: [Notification!]!
        unreadCount: Int!
        total: Int!
    }
    
    type Query {
        # Workspace queries
        myWorkspaces(page: Int = 1, perPage: Int = 10): WorkspaceList!
        workspace(id: UUID!): Workspace
        
        # Shared contacts
        workspaceSharedLists(workspaceId: UUID!): [SharedContactList!]!
        
        # Activity
        workspaceActivity(workspaceId: UUID!, page: Int = 1, perPage: Int = 20): ActivityLog!
        
        # Notifications
        myNotifications(workspaceId: UUID!, limit: Int = 20): NotificationList!
    }
    
    type Mutation {
        # Workspace management
        createWorkspace(name: String!, plan: WorkspacePlan): Workspace!
        updateWorkspace(id: UUID!, name: String, plan: WorkspacePlan): Workspace!
        deleteWorkspace(id: UUID!): Boolean!
        
        # Member management
        inviteMember(workspaceId: UUID!, email: String!, role: WorkspaceRole, message: String): InviteResult!
        removeMember(workspaceId: UUID!, memberId: UUID!): Boolean!
        updateMemberRole(workspaceId: UUID!, memberId: UUID!, role: WorkspaceRole!): WorkspaceMember!
        
        # Shared contacts
        createSharedList(workspaceId: UUID!, name: String!, description: String, contactIds: [UUID!]): SharedContactList!
        updateSharedList(id: UUID!, name: String, description: String, contactIds: [UUID!]): SharedContactList!
        deleteSharedList(id: UUID!): Boolean!
        
        # Notifications
        markNotificationRead(notificationId: UUID!): Boolean!
        markAllNotificationsRead(workspaceId: UUID!): Boolean!
    }
    
    type InviteResult {
        success: Boolean!
        message: String!
        userId: UUID
        role: WorkspaceRole
    }
"""

# Create resolvers
query = QueryType()
mutation = MutationType()
workspace_type = ObjectType("Workspace")


# ============ QUERIES ============

@query.field("myWorkspaces")
async def resolve_my_workspaces(obj, info, page=1, per_page=10):
    """Get user's workspaces"""
    user = info.context["user"]
    workspace_service = info.context["workspace_service"]
    
    result = await workspace_service.list_user_workspaces(
        user_id=user['id'],
        page=page,
        per_page=per_page
    )
    return result


@query.field("workspace")
async def resolve_workspace(obj, info, id):
    """Get workspace by ID"""
    user = info.context["user"]
    workspace_service = info.context["workspace_service"]
    
    try:
        workspace = await workspace_service.get_workspace(
            workspace_id=id,
            user_id=user['id']
        )
        return workspace
    except:
        return None


@query.field("workspaceSharedLists")
async def resolve_shared_lists(obj, info, workspace_id):
    """Get shared contact lists"""
    user = info.context["user"]
    workspace_service = info.context["workspace_service"]
    
    # Verify access
    try:
        await workspace_service.get_workspace(workspace_id, user['id'])
    except:
        return []
    
    # Get lists
    lists = await workspace_service.db.table('shared_contact_lists')\
        .select('*')\
        .eq('workspace_id', str(workspace_id))\
        .execute()
    
    return lists.data or []


@query.field("workspaceActivity")
async def resolve_activity(obj, info, workspace_id, page=1, per_page=20):
    """Get workspace activity log"""
    user = info.context["user"]
    workspace_service = info.context["workspace_service"]
    
    # Verify access
    await workspace_service.get_workspace(workspace_id, user['id'])
    
    offset = (page - 1) * per_page
    activity = await workspace_service.db.table('contact_activity_log')\
        .select('*')\
        .eq('workspace_id', str(workspace_id))\
        .order('created_at', desc=True)\
        .range(offset, offset + per_page - 1)\
        .execute()
    
    total = await workspace_service.db.table('contact_activity_log')\
        .select('*', count='exact')\
        .eq('workspace_id', str(workspace_id))\
        .execute()
    
    return {
        'entries': activity.data or [],
        'total': total.count or 0,
        'page': page,
        'per_page': per_page
    }


@query.field("myNotifications")
async def resolve_notifications(obj, info, workspace_id, limit=20):
    """Get user notifications"""
    user = info.context["user"]
    workspace_service = info.context["workspace_service"]
    
    result = await workspace_service.get_notifications(
        user_id=user['id'],
        workspace_id=workspace_id,
        limit=limit
    )
    return result


# ============ MUTATIONS ============

@mutation.field("createWorkspace")
async def resolve_create_workspace(obj, info, name, plan="PRO"):
    """Create new workspace"""
    from api.workspaces.models import WorkspaceCreate, WorkspacePlan
    
    user = info.context["user"]
    workspace_service = info.context["workspace_service"]
    
    workspace_data = WorkspaceCreate(
        name=name,
        plan=WorkspacePlan[plan]
    )
    
    return await workspace_service.create_workspace(
        user_id=user['id'],
        workspace_data=workspace_data
    )


@mutation.field("inviteMember")
async def resolve_invite_member(obj, info, workspace_id, email, role="MEMBER", message=None):
    """Invite member to workspace"""
    from api.workspaces.models import WorkspaceMemberInvite, WorkspaceRole
    
    user = info.context["user"]
    workspace_service = info.context["workspace_service"]
    
    invite_data = WorkspaceMemberInvite(
        email=email,
        role=WorkspaceRole[role],
        message=message
    )
    
    return await workspace_service.invite_member(
        workspace_id=workspace_id,
        user_id=user['id'],
        invite_data=invite_data
    )


@mutation.field("removeMember")
async def resolve_remove_member(obj, info, workspace_id, member_id):
    """Remove member from workspace"""
    user = info.context["user"]
    workspace_service = info.context["workspace_service"]
    
    result = await workspace_service.remove_member(
        workspace_id=workspace_id,
        user_id=user['id'],
        member_id=member_id
    )
    return result['success']


@mutation.field("createSharedList")
async def resolve_create_shared_list(obj, info, workspace_id, name, description=None, contact_ids=None):
    """Create shared contact list"""
    from api.workspaces.models import SharedContactListCreate
    
    user = info.context["user"]
    workspace_service = info.context["workspace_service"]
    
    list_data = SharedContactListCreate(
        name=name,
        description=description,
        contact_ids=contact_ids or []
    )
    
    return await workspace_service.create_shared_list(
        workspace_id=workspace_id,
        user_id=user['id'],
        list_data=list_data
    )


@mutation.field("markNotificationRead")
async def resolve_mark_notification_read(obj, info, notification_id):
    """Mark notification as read"""
    workspace_service = info.context["workspace_service"]
    
    try:
        await workspace_service.mark_notification_read(notification_id)
        return True
    except:
        return False


# Build executable schema
schema = make_executable_schema(type_defs, query, mutation, workspace_type)
