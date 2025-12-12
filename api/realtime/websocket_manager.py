"""WebSocket Connection Manager - Phase 7.2

Manages WebSocket connections, presence tracking, and message broadcasting
for real-time workspace collaboration.
"""

import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Dict, List, Optional, Set

from fastapi import WebSocket

logger = logging.getLogger(__name__)


@dataclass
class UserPresence:
    """User presence information"""

    user_id: str
    email: Optional[str] = None
    name: Optional[str] = None
    joined_at: str = None
    status: str = "online"
    last_activity: str = None
    editing_contact_id: Optional[str] = None
    editing_field: Optional[str] = None

    def __post_init__(self):
        if self.joined_at is None:
            self.joined_at = datetime.utcnow().isoformat()
        if self.last_activity is None:
            self.last_activity = datetime.utcnow().isoformat()

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow().isoformat()


class ConnectionManager:
    """Manages WebSocket connections per workspace

    Features:
    - Room-based broadcasting (by workspace_id)
    - User presence tracking
    - Personal message delivery
    - Automatic cleanup on disconnect
    - Heartbeat/ping-pong for connection health
    """

    def __init__(self):
        # workspace_id -> Set[WebSocket]
        self.active_connections: Dict[str, Set[WebSocket]] = {}

        # workspace_id -> user_id -> UserPresence
        self.user_presence: Dict[str, Dict[str, UserPresence]] = {}

        # WebSocket -> (workspace_id, user_id) mapping for cleanup
        self.connection_map: Dict[WebSocket, tuple] = {}

        # Message queue for offline users (workspace_id -> List[messages])
        self.offline_queue: Dict[str, List[dict]] = {}

        logger.info("ConnectionManager initialized")

    async def connect(
        self,
        workspace_id: str,
        user_id: str,
        websocket: WebSocket,
        user_email: Optional[str] = None,
        user_name: Optional[str] = None,
    ):
        """Connect a user to a workspace

        Args:
            workspace_id: Workspace identifier
            user_id: User identifier
            websocket: WebSocket connection
            user_email: Optional user email
            user_name: Optional user name
        """
        await websocket.accept()
        logger.info(f"User {user_id} connecting to workspace {workspace_id}")

        # Add to active connections
        if workspace_id not in self.active_connections:
            self.active_connections[workspace_id] = set()

        self.active_connections[workspace_id].add(websocket)
        self.connection_map[websocket] = (workspace_id, user_id)

        # Add to presence
        if workspace_id not in self.user_presence:
            self.user_presence[workspace_id] = {}

        presence = UserPresence(user_id=user_id, email=user_email, name=user_name, status="online")
        self.user_presence[workspace_id][user_id] = presence

        # Send queued messages if any
        await self._send_queued_messages(workspace_id, websocket)

        # Notify others about new user
        await self.broadcast_presence(workspace_id)

        # Send welcome message to the connected user
        await self.send_personal(
            websocket,
            {
                "type": "connected",
                "workspace_id": workspace_id,
                "user_id": user_id,
                "message": "Successfully connected to workspace",
            },
        )

        logger.info(f"User {user_id} connected to workspace {workspace_id}")

    async def disconnect(self, websocket: WebSocket):
        """Disconnect a user from workspace

        Args:
            websocket: WebSocket connection to close
        """
        if websocket not in self.connection_map:
            logger.warning("Disconnect called for unknown websocket")
            return

        workspace_id, user_id = self.connection_map[websocket]
        logger.info(f"User {user_id} disconnecting from workspace {workspace_id}")

        # Remove from active connections
        if workspace_id in self.active_connections:
            self.active_connections[workspace_id].discard(websocket)

            # Clean up empty workspace
            if not self.active_connections[workspace_id]:
                del self.active_connections[workspace_id]

        # Remove from presence
        if workspace_id in self.user_presence:
            self.user_presence[workspace_id].pop(user_id, None)

            # Clean up empty presence
            if not self.user_presence[workspace_id]:
                del self.user_presence[workspace_id]

        # Remove from connection map
        del self.connection_map[websocket]

        # Notify others about user leaving
        await self.broadcast_presence(workspace_id)

        logger.info(f"User {user_id} disconnected from workspace {workspace_id}")

    async def broadcast(
        self, workspace_id: str, message: dict, exclude_websocket: Optional[WebSocket] = None
    ):
        """Broadcast message to all users in workspace

        Args:
            workspace_id: Workspace identifier
            message: Message dict to broadcast
            exclude_websocket: Optional websocket to exclude (sender)
        """
        if workspace_id not in self.active_connections:
            logger.debug(f"No active connections for workspace {workspace_id}")
            # Queue message for offline users
            if workspace_id not in self.offline_queue:
                self.offline_queue[workspace_id] = []
            self.offline_queue[workspace_id].append(message)
            return

        # Add timestamp if not present
        if "timestamp" not in message:
            message["timestamp"] = datetime.utcnow().isoformat()

        # Add workspace_id to message
        message["workspace_id"] = workspace_id

        disconnected = []

        for connection in self.active_connections[workspace_id]:
            if exclude_websocket and connection == exclude_websocket:
                continue

            try:
                await connection.send_json(message)
                logger.debug(f"Broadcasted {message.get('type')} to workspace {workspace_id}")
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)

        # Clean up disconnected websockets
        for ws in disconnected:
            await self.disconnect(ws)

    async def broadcast_presence(self, workspace_id: str):
        """Broadcast updated presence list to all users in workspace

        Args:
            workspace_id: Workspace identifier
        """
        if workspace_id not in self.user_presence:
            return

        presence_list = [
            presence.to_dict() for presence in self.user_presence[workspace_id].values()
        ]

        await self.broadcast(
            workspace_id,
            {"type": "presence_update", "users": presence_list, "count": len(presence_list)},
        )

        logger.debug(
            f"Broadcasted presence update for workspace {workspace_id}: {len(presence_list)} users"
        )

    async def send_personal(self, websocket: WebSocket, message: dict):
        """Send message to specific websocket connection

        Args:
            websocket: Target websocket
            message: Message dict to send
        """
        try:
            if "timestamp" not in message:
                message["timestamp"] = datetime.utcnow().isoformat()

            await websocket.send_json(message)
            logger.debug(f"Sent personal message: {message.get('type')}")
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            await self.disconnect(websocket)

    async def update_user_activity(
        self,
        workspace_id: str,
        user_id: str,
        editing_contact_id: Optional[str] = None,
        editing_field: Optional[str] = None,
    ):
        """Update user activity and broadcast

        Args:
            workspace_id: Workspace identifier
            user_id: User identifier
            editing_contact_id: Optional contact being edited
            editing_field: Optional field being edited
        """
        if workspace_id not in self.user_presence:
            return

        if user_id not in self.user_presence[workspace_id]:
            return

        presence = self.user_presence[workspace_id][user_id]
        presence.update_activity()
        presence.editing_contact_id = editing_contact_id
        presence.editing_field = editing_field

        await self.broadcast_presence(workspace_id)

    async def _send_queued_messages(self, workspace_id: str, websocket: WebSocket):
        """Send queued messages to newly connected user

        Args:
            workspace_id: Workspace identifier
            websocket: Newly connected websocket
        """
        if workspace_id not in self.offline_queue:
            return

        messages = self.offline_queue[workspace_id]

        for message in messages:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending queued message: {e}")
                break

        # Clear queue after sending
        self.offline_queue[workspace_id] = []
        logger.info(f"Sent {len(messages)} queued messages to user in workspace {workspace_id}")

    def get_workspace_users(self, workspace_id: str) -> List[dict]:
        """Get list of users currently in workspace

        Args:
            workspace_id: Workspace identifier

        Returns:
            List of user presence dictionaries
        """
        if workspace_id not in self.user_presence:
            return []

        return [presence.to_dict() for presence in self.user_presence[workspace_id].values()]

    def get_connection_count(self, workspace_id: str) -> int:
        """Get number of active connections in workspace

        Args:
            workspace_id: Workspace identifier

        Returns:
            Number of active connections
        """
        if workspace_id not in self.active_connections:
            return 0

        return len(self.active_connections[workspace_id])


# Global manager instance
manager = ConnectionManager()
