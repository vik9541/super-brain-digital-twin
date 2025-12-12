# tests/test_workspaces.py
# Phase 7: Team Collaboration - Unit Tests

from uuid import uuid4

import pytest

from api.workspaces.models import (
    WorkspaceCreate,
    WorkspaceMemberInvite,
    WorkspacePlan,
    WorkspaceRole,
)
from api.workspaces.service import WorkspaceService


class MockSupabase:
    """Mock Supabase client for testing"""

    def __init__(self):
        self.data = {
            "workspaces": [],
            "workspace_members": [],
            "notifications": [],
            "contact_activity_log": [],
        }

    def table(self, name):
        return MockTable(self.data, name)


class MockTable:
    """Mock Supabase table"""

    def __init__(self, data, table_name):
        self.data = data
        self.table_name = table_name
        self._filters = {}

    def select(self, *args, **kwargs):
        return self

    def insert(self, data):
        self.data[self.table_name].append(data)
        return MockResult([data])

    def eq(self, key, value):
        self._filters[key] = value
        return self

    def update(self, data):
        for item in self.data[self.table_name]:
            if self._matches_filters(item):
                item.update(data)
        return MockResult([data])

    def delete(self):
        self.data[self.table_name] = [
            item for item in self.data[self.table_name] if not self._matches_filters(item)
        ]
        return MockResult([])

    def order(self, key, desc=False):
        return self

    def limit(self, n):
        return self

    def range(self, start, end):
        return self

    async def execute(self):
        results = [item for item in self.data[self.table_name] if self._matches_filters(item)]
        return MockResult(results)

    def _matches_filters(self, item):
        for key, value in self._filters.items():
            if item.get(key) != value:
                return False
        return True


class MockResult:
    """Mock Supabase result"""

    def __init__(self, data):
        self.data = data
        self.count = len(data)


class MockAuth:
    """Mock Auth client"""

    async def get_user_by_email(self, email):
        return MockUser(str(uuid4()), email)


class MockUser:
    """Mock User object"""

    def __init__(self, user_id, email):
        self.id = user_id
        self.email = email


class MockEmailService:
    """Mock Email service"""

    async def send_workspace_invite(self, to_email, workspace_id, invited_by, message=None):
        pass


# ============ TESTS ============


@pytest.mark.asyncio
async def test_create_workspace():
    """Test creating a new workspace"""
    supabase = MockSupabase()
    auth = MockAuth()
    email = MockEmailService()
    service = WorkspaceService(supabase, auth, email)

    user_id = uuid4()
    workspace_data = WorkspaceCreate(name="Sales Team", plan=WorkspacePlan.PRO)

    workspace = await service.create_workspace(user_id, workspace_data)

    assert workspace.name == "Sales Team"
    assert workspace.plan == WorkspacePlan.PRO.value
    assert workspace.owner_id == user_id
    assert workspace.member_count == 1  # Owner is member


@pytest.mark.asyncio
async def test_list_user_workspaces():
    """Test listing user workspaces"""
    supabase = MockSupabase()
    auth = MockAuth()
    email = MockEmailService()
    service = WorkspaceService(supabase, auth, email)

    user_id = uuid4()

    # Create workspace
    workspace_data = WorkspaceCreate(name="Test Workspace", plan=WorkspacePlan.PRO)
    await service.create_workspace(user_id, workspace_data)

    # List workspaces
    result = await service.list_user_workspaces(user_id)

    assert result["total"] == 1
    assert len(result["workspaces"]) == 1
    assert result["workspaces"][0].name == "Test Workspace"


@pytest.mark.asyncio
async def test_invite_member():
    """Test inviting member to workspace"""
    supabase = MockSupabase()
    auth = MockAuth()
    email = MockEmailService()
    service = WorkspaceService(supabase, auth, email)

    owner_id = uuid4()

    # Create workspace
    workspace_data = WorkspaceCreate(name="Test Workspace", plan=WorkspacePlan.PRO)
    workspace = await service.create_workspace(owner_id, workspace_data)

    # Invite member
    invite_data = WorkspaceMemberInvite(email="member@example.com", role=WorkspaceRole.MEMBER)

    result = await service.invite_member(workspace.id, owner_id, invite_data)

    assert result["success"] is True
    assert "member@example.com" in result["message"]


@pytest.mark.asyncio
async def test_remove_member():
    """Test removing member from workspace"""
    supabase = MockSupabase()
    auth = MockAuth()
    email = MockEmailService()
    service = WorkspaceService(supabase, auth, email)

    owner_id = uuid4()
    member_id = uuid4()

    # Create workspace
    workspace_data = WorkspaceCreate(name="Test Workspace", plan=WorkspacePlan.PRO)
    workspace = await service.create_workspace(owner_id, workspace_data)

    # Add member
    invite_data = WorkspaceMemberInvite(email="member@example.com", role=WorkspaceRole.MEMBER)
    await service.invite_member(workspace.id, owner_id, invite_data)

    # Remove member
    result = await service.remove_member(workspace.id, owner_id, member_id)

    assert result["success"] is True


@pytest.mark.asyncio
async def test_permission_denied_on_invite():
    """Test that non-admin cannot invite members"""
    supabase = MockSupabase()
    auth = MockAuth()
    email = MockEmailService()
    service = WorkspaceService(supabase, auth, email)

    owner_id = uuid4()
    member_id = uuid4()

    # Create workspace
    workspace_data = WorkspaceCreate(name="Test Workspace", plan=WorkspacePlan.PRO)
    workspace = await service.create_workspace(owner_id, workspace_data)

    # Try to invite as non-member
    invite_data = WorkspaceMemberInvite(email="newmember@example.com", role=WorkspaceRole.MEMBER)

    with pytest.raises(PermissionError):
        await service.invite_member(workspace.id, member_id, invite_data)


@pytest.mark.asyncio
async def test_create_shared_list():
    """Test creating shared contact list"""
    supabase = MockSupabase()
    auth = MockAuth()
    email = MockEmailService()
    service = WorkspaceService(supabase, auth, email)

    user_id = uuid4()

    # Create workspace
    workspace_data = WorkspaceCreate(name="Test Workspace", plan=WorkspacePlan.PRO)
    workspace = await service.create_workspace(user_id, workspace_data)

    # Create shared list
    from api.workspaces.models import SharedContactListCreate

    list_data = SharedContactListCreate(
        name="Important Contacts", description="Key stakeholders", contact_ids=[uuid4(), uuid4()]
    )

    shared_list = await service.create_shared_list(workspace.id, user_id, list_data)

    assert shared_list["name"] == "Important Contacts"
    assert len(shared_list["contact_ids"]) == 2


@pytest.mark.asyncio
async def test_get_notifications():
    """Test getting notifications"""
    supabase = MockSupabase()
    auth = MockAuth()
    email = MockEmailService()
    service = WorkspaceService(supabase, auth, email)

    user_id = uuid4()
    workspace_id = uuid4()

    # Create notification
    await service._create_notification(
        user_id=user_id,
        workspace_id=workspace_id,
        type="member_added",
        title="Added to Workspace",
        message="You were added",
        data={"workspace_id": str(workspace_id)},
    )

    # Get notifications
    result = await service.get_notifications(user_id, workspace_id)

    assert result["unread_count"] == 1
    assert len(result["notifications"]) == 1


@pytest.mark.asyncio
async def test_validation_empty_workspace_name():
    """Test that empty workspace name is rejected"""
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        WorkspaceCreate(name="", plan=WorkspacePlan.PRO)


@pytest.mark.asyncio
async def test_validation_invalid_email():
    """Test that invalid email is rejected"""
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        WorkspaceMemberInvite(email="not-an-email", role=WorkspaceRole.MEMBER)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
