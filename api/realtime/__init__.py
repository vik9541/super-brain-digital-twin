"""Real-Time WebSocket Module - Phase 7.2

Provides WebSocket-based real-time synchronization for workspace collaboration:
- Live contact updates across all connected clients
- User presence tracking (who's online)
- Typing indicators
- Conflict resolution
- Offline support with message queue
"""

from .websocket_manager import ConnectionManager, manager

__all__ = ["ConnectionManager", "manager"]
