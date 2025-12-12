"""Dependencies for FastAPI endpoints"""

from fastapi import Depends, HTTPException, Request
from supabase import Client

from .workspaces.service import WorkspaceService


def get_supabase_client(request: Request) -> Client:
    """Get Supabase client instance from request app state"""
    # Access via request.app.state to avoid circular import
    supabase = getattr(request.app.state, "supabase", None)
    if supabase is None:
        # Try to get from module global (set during startup)
        import api.main as main_module

        supabase = getattr(main_module, "supabase", None)

    if supabase is None:
        raise HTTPException(status_code=503, detail="Database not available")
    return supabase


def get_workspace_service(
    request: Request, db: Client = Depends(get_supabase_client)
) -> WorkspaceService:
    """Get WorkspaceService instance with dependencies"""
    # For now, pass None for auth_client and email_service
    # These can be implemented later
    return WorkspaceService(supabase_client=db, auth_client=None, email_service=None)
