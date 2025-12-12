# api/workspaces/models.py
# Phase 7: Team Collaboration - Models & Schemas

from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
from uuid import UUID


class WorkspaceRole(str, Enum):
    """Workspace member roles"""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class WorkspacePlan(str, Enum):
    """Workspace subscription plans"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


# ============ CREATE REQUESTS ============

class WorkspaceCreate(BaseModel):
    """Create new workspace"""
    name: str
    plan: WorkspacePlan = WorkspacePlan.PRO
    
    @validator('name')
    def name_not_empty(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Workspace name cannot be empty')
        if len(v) > 100:
            raise ValueError('Workspace name must be <= 100 characters')
        return v.strip()


class WorkspaceMemberInvite(BaseModel):
    """Invite member to workspace"""
    email: EmailStr
    role: WorkspaceRole = WorkspaceRole.MEMBER
    message: Optional[str] = None


class WorkspaceUpdate(BaseModel):
    """Update workspace settings"""
    name: Optional[str] = None
    plan: Optional[WorkspacePlan] = None


# ============ RESPONSE MODELS ============

class WorkspaceMemberInfo(BaseModel):
    """Member in workspace"""
    user_id: UUID
    email: str
    name: Optional[str] = None
    role: WorkspaceRole
    joined_at: datetime
    
    class Config:
        from_attributes = True


class WorkspaceResponse(BaseModel):
    """Workspace details"""
    id: UUID
    name: str
    owner_id: UUID
    plan: WorkspacePlan
    member_count: int
    members: List[WorkspaceMemberInfo] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WorkspaceListResponse(BaseModel):
    """List of workspaces"""
    workspaces: List[WorkspaceResponse]
    total: int
    page: int
    per_page: int


class SharedContactListCreate(BaseModel):
    """Create shared contact list"""
    name: str
    description: Optional[str] = None
    contact_ids: List[UUID] = []
    
    @validator('name')
    def name_not_empty(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('List name cannot be empty')
        return v.strip()


class SharedContactList(BaseModel):
    """Shared contact list"""
    id: UUID
    workspace_id: UUID
    name: str
    description: Optional[str] = None
    contact_count: int
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ActivityLogEntry(BaseModel):
    """Activity log entry"""
    id: UUID
    workspace_id: UUID
    contact_id: Optional[UUID] = None
    user_id: UUID
    user_name: Optional[str] = None
    action: str  # viewed, contacted, added_note, shared, etc
    description: Optional[str] = None
    details: Dict[str, Any] = {}
    created_at: datetime
    
    class Config:
        from_attributes = True


class ActivityLogResponse(BaseModel):
    """Activity log response"""
    entries: List[ActivityLogEntry]
    total: int
    page: int
    per_page: int


class NotificationResponse(BaseModel):
    """Notification"""
    id: UUID
    type: str  # contact_shared, member_added, etc
    title: str
    message: str
    data: Dict[str, Any]
    read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """List of notifications"""
    notifications: List[NotificationResponse]
    unread_count: int
    total: int


# ============ DATABASE MODELS (for reference) ============

class WorkspaceDB(BaseModel):
    """Workspace database model"""
    id: UUID
    name: str
    owner_id: UUID
    plan: WorkspacePlan
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WorkspaceMemberDB(BaseModel):
    """Workspace member database model"""
    id: UUID
    workspace_id: UUID
    user_id: UUID
    email: str
    role: WorkspaceRole
    joined_at: datetime
    
    class Config:
        from_attributes = True
