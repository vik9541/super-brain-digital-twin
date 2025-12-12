"""Database Persistence Helper - Phase 7.2

Helper functions for storing WebSocket messages and sessions in database.
"""

from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class WebSocketPersistence:
    """Handle WebSocket message and session persistence"""
    
    def __init__(self, supabase_client=None):
        """Initialize with Supabase client
        
        Args:
            supabase_client: Supabase client instance (from api.main)
        """
        self.supabase = supabase_client
    
    async def save_message(
        self,
        workspace_id: str,
        message_type: str,
        user_id: str,
        payload: Dict
    ) -> Optional[int]:
        """Save WebSocket message to database
        
        Args:
            workspace_id: Workspace identifier
            message_type: Type of message (contact_created, etc.)
            user_id: User who sent the message
            payload: Complete message payload
            
        Returns:
            Message ID if successful, None otherwise
        """
        if not self.supabase:
            logger.warning("Supabase client not available, skipping message persistence")
            return None
        
        try:
            result = self.supabase.table('websocket_messages').insert({
                'workspace_id': int(workspace_id) if workspace_id.isdigit() else 0,
                'message_type': message_type,
                'user_id': user_id,
                'payload': payload,
                'created_at': datetime.utcnow().isoformat(),
                'delivered': False
            }).execute()
            
            if result.data:
                message_id = result.data[0]['id']
                logger.debug(f"Saved message {message_id}: {message_type}")
                return message_id
            
        except Exception as e:
            logger.error(f"Failed to save message: {e}")
        
        return None
    
    async def get_undelivered_messages(
        self,
        workspace_id: str,
        user_id: str,
        since_hours: int = 24
    ) -> List[Dict]:
        """Get undelivered messages for user
        
        Args:
            workspace_id: Workspace identifier
            user_id: User identifier
            since_hours: How many hours back to fetch (default 24)
            
        Returns:
            List of undelivered messages
        """
        if not self.supabase:
            return []
        
        try:
            # Calculate cutoff time
            from datetime import timedelta
            cutoff = datetime.utcnow() - timedelta(hours=since_hours)
            
            result = self.supabase.rpc(
                'get_undelivered_messages',
                {
                    'p_workspace_id': int(workspace_id) if workspace_id.isdigit() else 0,
                    'p_user_id': user_id,
                    'p_since': cutoff.isoformat()
                }
            ).execute()
            
            if result.data:
                logger.info(f"Retrieved {len(result.data)} undelivered messages for {user_id}")
                return result.data
            
        except Exception as e:
            logger.error(f"Failed to get undelivered messages: {e}")
        
        return []
    
    async def mark_delivered(self, message_id: int) -> bool:
        """Mark message as delivered
        
        Args:
            message_id: Message identifier
            
        Returns:
            True if successful
        """
        if not self.supabase:
            return False
        
        try:
            self.supabase.rpc('mark_message_delivered', {'message_id': message_id}).execute()
            logger.debug(f"Marked message {message_id} as delivered")
            return True
        except Exception as e:
            logger.error(f"Failed to mark message delivered: {e}")
            return False
    
    async def create_session(
        self,
        workspace_id: str,
        user_id: str
    ) -> Optional[int]:
        """Create new WebSocket session record
        
        Args:
            workspace_id: Workspace identifier
            user_id: User identifier
            
        Returns:
            Session ID if successful
        """
        if not self.supabase:
            return None
        
        try:
            result = self.supabase.table('websocket_sessions').insert({
                'workspace_id': int(workspace_id) if workspace_id.isdigit() else 0,
                'user_id': user_id,
                'connected_at': datetime.utcnow().isoformat(),
                'messages_sent': 0,
                'messages_received': 0
            }).execute()
            
            if result.data:
                session_id = result.data[0]['id']
                logger.info(f"Created session {session_id} for user {user_id}")
                return session_id
            
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
        
        return None
    
    async def end_session(self, session_id: int) -> bool:
        """End WebSocket session
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if successful
        """
        if not self.supabase:
            return False
        
        try:
            self.supabase.rpc('end_websocket_session', {'p_session_id': session_id}).execute()
            logger.info(f"Ended session {session_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to end session: {e}")
            return False
    
    async def update_session_stats(
        self,
        session_id: int,
        messages_sent: int = 0,
        messages_received: int = 0
    ) -> bool:
        """Update session statistics
        
        Args:
            session_id: Session identifier
            messages_sent: Number of messages sent
            messages_received: Number of messages received
            
        Returns:
            True if successful
        """
        if not self.supabase:
            return False
        
        try:
            self.supabase.rpc('update_session_stats', {
                'p_session_id': session_id,
                'p_messages_sent': messages_sent,
                'p_messages_received': messages_received
            }).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to update session stats: {e}")
            return False
    
    async def get_active_sessions(self, workspace_id: str) -> List[Dict]:
        """Get active sessions in workspace
        
        Args:
            workspace_id: Workspace identifier
            
        Returns:
            List of active session records
        """
        if not self.supabase:
            return []
        
        try:
            result = self.supabase.from_('active_websocket_sessions')\
                .select('*')\
                .eq('workspace_id', int(workspace_id) if workspace_id.isdigit() else 0)\
                .execute()
            
            if result.data:
                return result.data
            
        except Exception as e:
            logger.error(f"Failed to get active sessions: {e}")
        
        return []
    
    async def get_message_stats(self, workspace_id: str) -> Dict:
        """Get message statistics for workspace
        
        Args:
            workspace_id: Workspace identifier
            
        Returns:
            Dictionary with message statistics
        """
        if not self.supabase:
            return {}
        
        try:
            result = self.supabase.from_('websocket_message_stats')\
                .select('*')\
                .eq('workspace_id', int(workspace_id) if workspace_id.isdigit() else 0)\
                .execute()
            
            if result.data:
                # Aggregate stats by message type
                stats = {
                    'total_messages': sum(row['total_messages'] for row in result.data),
                    'by_type': {row['message_type']: row for row in result.data}
                }
                return stats
            
        except Exception as e:
            logger.error(f"Failed to get message stats: {e}")
        
        return {}


# Global instance (will be initialized with supabase client)
_persistence = None


def get_persistence(supabase_client=None):
    """Get or create WebSocketPersistence instance
    
    Args:
        supabase_client: Optional Supabase client to initialize with
        
    Returns:
        WebSocketPersistence instance
    """
    global _persistence
    
    if _persistence is None:
        _persistence = WebSocketPersistence(supabase_client)
    elif supabase_client is not None:
        _persistence.supabase = supabase_client
    
    return _persistence
