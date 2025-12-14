"""WebSocket Routes - Phase 7.2

Real-time WebSocket endpoints for workspace collaboration.
Handles contact updates, presence, typing indicators, and cursor positions.
"""

import json
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect

from .websocket_manager import manager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ws", tags=["websockets"])


async def get_user_from_token(token: Optional[str]) -> tuple:
    """Extract user info from JWT token

    Args:
        token: JWT token string

    Returns:
        Tuple of (user_id, email, name)

    Raises:
        HTTPException: If token is invalid
    """
    if not token:
        raise HTTPException(status_code=401, detail="Token required")

    # TODO: Implement JWT token verification
    # For now, return mock data
    # In production, decode JWT and extract user info

    try:
        # from api.auth import verify_jwt_token
        # payload = verify_jwt_token(token)
        # return (payload['user_id'], payload.get('email'), payload.get('name'))

        # Mock implementation
        return ("user_" + token[:8], f"user@example.com", "Demo User")
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")


@router.websocket("/workspace/{workspace_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    workspace_id: str,
    token: Optional[str] = Query(None, description="JWT authentication token"),
):
    """WebSocket endpoint for real-time workspace synchronization

    Usage:
        const ws = new WebSocket('ws://localhost:8001/ws/workspace/{id}?token=YOUR_JWT')

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data)

            switch(data.type) {
                case 'contact_created': // New contact added
                case 'contact_updated': // Contact modified
                case 'contact_deleted': // Contact removed
                case 'note_added': // Note added to contact
                case 'presence_update': // Users online changed
                case 'typing': // Someone is typing
                case 'cursor_position': // Remote cursor position
            }
        }

    Message Types (Client -> Server):
        - contact_created: { type, contact }
        - contact_updated: { type, contact_id, changes }
        - contact_deleted: { type, contact_id }
        - note_added: { type, contact_id, note }
        - typing: { type, contact_id, field }
        - cursor_position: { type, x, y }

    Message Types (Server -> Client):
        - connected: Welcome message
        - presence_update: { type, users[], count }
        - contact_created: { type, contact, created_by }
        - contact_updated: { type, contact_id, changes, updated_by }
        - contact_deleted: { type, contact_id, deleted_by }
        - note_added: { type, contact_id, note, added_by }
        - typing: { type, contact_id, field, user_id }
        - cursor_position: { type, x, y, user_id }
        - error: { type, message }
    """

    # Authenticate user
    try:
        user_id, email, name = await get_user_from_token(token)
    except HTTPException as e:
        await websocket.close(code=4001, reason="Unauthorized")
        logger.warning(f"Unauthorized WebSocket connection attempt to workspace {workspace_id}")
        return

    # TODO: Verify user has access to this workspace
    # Check database if user is member of workspace
    # For now, allow all authenticated users

    # Connect user to workspace
    await manager.connect(
        workspace_id=workspace_id,
        user_id=user_id,
        websocket=websocket,
        user_email=email,
        user_name=name,
    )

    try:
        while True:
            # Receive message from client
            try:
                data = await websocket.receive_json()
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON received: {e}")
                await manager.send_personal(
                    websocket, {"type": "error", "message": "Invalid JSON format"}
                )
                continue

            # Extract message type
            message_type = data.get("type")

            if not message_type:
                await manager.send_personal(
                    websocket, {"type": "error", "message": "Message type is required"}
                )
                continue

            # Update user activity
            await manager.update_user_activity(
                workspace_id=workspace_id,
                user_id=user_id,
                editing_contact_id=data.get("contact_id"),
                editing_field=data.get("field"),
            )

            # Handle different message types
            if message_type == "contact_created":
                # New contact added
                contact = data.get("contact")

                if not contact:
                    await manager.send_personal(
                        websocket, {"type": "error", "message": "Contact data is required"}
                    )
                    continue

                await manager.broadcast(
                    workspace_id=workspace_id,
                    message={
                        "type": "contact_created",
                        "contact": contact,
                        "created_by": user_id,
                        "created_by_email": email,
                        "created_by_name": name,
                    },
                    exclude_websocket=websocket,  # Don't send back to sender
                )

                logger.info(f"Contact created by {user_id} in workspace {workspace_id}")

            elif message_type == "contact_updated":
                # Contact modified
                contact_id = data.get("contact_id")
                changes = data.get("changes")

                if not contact_id or not changes:
                    await manager.send_personal(
                        websocket,
                        {"type": "error", "message": "contact_id and changes are required"},
                    )
                    continue

                await manager.broadcast(
                    workspace_id=workspace_id,
                    message={
                        "type": "contact_updated",
                        "contact_id": contact_id,
                        "changes": changes,
                        "updated_by": user_id,
                        "updated_by_email": email,
                        "updated_by_name": name,
                    },
                    exclude_websocket=websocket,
                )

                logger.info(
                    f"Contact {contact_id} updated by {user_id} in workspace {workspace_id}"
                )

            elif message_type == "contact_deleted":
                # Contact removed
                contact_id = data.get("contact_id")

                if not contact_id:
                    await manager.send_personal(
                        websocket, {"type": "error", "message": "contact_id is required"}
                    )
                    continue

                await manager.broadcast(
                    workspace_id=workspace_id,
                    message={
                        "type": "contact_deleted",
                        "contact_id": contact_id,
                        "deleted_by": user_id,
                        "deleted_by_email": email,
                        "deleted_by_name": name,
                    },
                    exclude_websocket=websocket,
                )

                logger.info(
                    f"Contact {contact_id} deleted by {user_id} in workspace {workspace_id}"
                )

            elif message_type == "note_added":
                # Note added to contact
                contact_id = data.get("contact_id")
                note = data.get("note")

                if not contact_id or not note:
                    await manager.send_personal(
                        websocket, {"type": "error", "message": "contact_id and note are required"}
                    )
                    continue

                await manager.broadcast(
                    workspace_id=workspace_id,
                    message={
                        "type": "note_added",
                        "contact_id": contact_id,
                        "note": note,
                        "added_by": user_id,
                        "added_by_email": email,
                        "added_by_name": name,
                    },
                    exclude_websocket=websocket,
                )

                logger.info(
                    f"Note added to contact {contact_id} by {user_id} in workspace {workspace_id}"
                )

            elif message_type == "typing":
                # Typing indicator
                contact_id = data.get("contact_id")
                field = data.get("field")
                is_typing = data.get("is_typing", True)

                await manager.broadcast(
                    workspace_id=workspace_id,
                    message={
                        "type": "typing",
                        "contact_id": contact_id,
                        "field": field,
                        "is_typing": is_typing,
                        "user_id": user_id,
                        "user_email": email,
                        "user_name": name,
                    },
                    exclude_websocket=websocket,
                )

            elif message_type == "cursor_position":
                # Remote cursor position
                x = data.get("x")
                y = data.get("y")

                if x is None or y is None:
                    continue

                await manager.broadcast(
                    workspace_id=workspace_id,
                    message={
                        "type": "cursor_position",
                        "x": x,
                        "y": y,
                        "user_id": user_id,
                        "user_email": email,
                        "user_name": name,
                    },
                    exclude_websocket=websocket,
                )

            elif message_type == "ping":
                # Heartbeat/keepalive
                await manager.send_personal(
                    websocket, {"type": "pong", "timestamp": datetime.utcnow().isoformat()}
                )

            else:
                # Unknown message type
                await manager.send_personal(
                    websocket, {"type": "error", "message": f"Unknown message type: {message_type}"}
                )
                logger.warning(
                    f"Unknown message type '{message_type}' from {user_id} in workspace {workspace_id}"
                )

    except WebSocketDisconnect:
        await manager.disconnect(websocket)
        logger.info(f"User {user_id} disconnected from workspace {workspace_id}")

    except Exception as e:
        logger.error(f"WebSocket error for user {user_id} in workspace {workspace_id}: {e}")
        await manager.disconnect(websocket)


@router.get("/workspace/{workspace_id}/users")
async def get_workspace_users(workspace_id: str):
    """Get list of currently connected users in workspace

    Args:
        workspace_id: Workspace identifier

    Returns:
        Dict with users list and count
    """
    users = manager.get_workspace_users(workspace_id)
    count = manager.get_connection_count(workspace_id)

    return {
        "workspace_id": workspace_id,
        "users": users,
        "count": count,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/health")
async def websocket_health():
    """Health check for WebSocket service

    Returns:
        Service status and statistics
    """
    total_workspaces = len(manager.active_connections)
    total_connections = sum(len(connections) for connections in manager.active_connections.values())

    return {
        "status": "healthy",
        "service": "websocket",
        "total_workspaces": total_workspaces,
        "total_connections": total_connections,
        "timestamp": datetime.utcnow().isoformat(),
    }
