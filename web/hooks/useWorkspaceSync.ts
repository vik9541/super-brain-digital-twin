/**
 * useWorkspaceSync Hook - Phase 7.2
 * 
 * Real-time WebSocket synchronization for workspace collaboration.
 * Handles:
 * - Contact creation/updates/deletion sync
 * - User presence tracking (who's online)
 * - Typing indicators
 * - Automatic reconnection
 * - Offline message queuing
 */

import { useEffect, useCallback, useRef, useState } from 'react';

export interface UserPresence {
  user_id: string;
  email?: string;
  name?: string;
  joined_at: string;
  status: 'online' | 'away' | 'offline';
  last_activity: string;
  editing_contact_id?: string;
  editing_field?: string;
}

export interface Contact {
  id: string;
  name: string;
  email?: string;
  phone?: string;
  company?: string;
  notes?: string;
  [key: string]: any;
}

export interface WebSocketMessage {
  type: string;
  timestamp?: string;
  workspace_id?: string;
  [key: string]: any;
}

export interface UseWorkspaceSyncOptions {
  workspaceId: string;
  userId: string;
  token: string;
  wsUrl?: string;
  autoReconnect?: boolean;
  reconnectInterval?: number;
  onConnected?: () => void;
  onDisconnected?: () => void;
  onError?: (error: Error) => void;
}

export interface UseWorkspaceSyncReturn {
  isConnected: boolean;
  presence: UserPresence[];
  send: (message: WebSocketMessage) => void;
  sendContactCreated: (contact: Contact) => void;
  sendContactUpdated: (contactId: string, changes: Partial<Contact>) => void;
  sendContactDeleted: (contactId: string) => void;
  sendTyping: (contactId: string, field: string, isTyping: boolean) => void;
  sendNoteAdded: (contactId: string, note: string) => void;
}

export function useWorkspaceSync(
  options: UseWorkspaceSyncOptions
): UseWorkspaceSyncReturn {
  const {
    workspaceId,
    userId,
    token,
    wsUrl = 'ws://localhost:8001',
    autoReconnect = true,
    reconnectInterval = 3000,
    onConnected,
    onDisconnected,
    onError,
  } = options;

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const messageQueueRef = useRef<WebSocketMessage[]>([]);

  const [isConnected, setIsConnected] = useState(false);
  const [presence, setPresence] = useState<UserPresence[]>([]);

  /**
   * Connect to WebSocket server
   */
  const connect = useCallback(() => {
    if (!workspaceId || !token) {
      console.error('useWorkspaceSync: workspaceId and token required');
      return;
    }

    // Clean up existing connection
    if (wsRef.current) {
      wsRef.current.close();
    }

    const url = `${wsUrl}/ws/workspace/${workspaceId}?token=${token}`;
    console.log(`🔌 Connecting to WebSocket: ${url}`);

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('✅ WebSocket connected');
      setIsConnected(true);

      // Send queued messages
      if (messageQueueRef.current.length > 0) {
        console.log(`📤 Sending ${messageQueueRef.current.length} queued messages`);
        messageQueueRef.current.forEach((msg) => {
          ws.send(JSON.stringify(msg));
        });
        messageQueueRef.current = [];
      }

      onConnected?.();
    };

    ws.onmessage = (event) => {
      try {
        const data: WebSocketMessage = JSON.parse(event.data);
        handleMessage(data);
      } catch (error) {
        console.error('❌ Failed to parse WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
      setIsConnected(false);
      onError?.(new Error('WebSocket connection error'));
    };

    ws.onclose = (event) => {
      console.log(`📴 WebSocket disconnected (code: ${event.code})`);
      setIsConnected(false);
      wsRef.current = null;
      onDisconnected?.();

      // Auto-reconnect if enabled
      if (autoReconnect) {
        console.log(`🔄 Reconnecting in ${reconnectInterval}ms...`);
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, reconnectInterval);
      }
    };
  }, [workspaceId, token, wsUrl, autoReconnect, reconnectInterval, onConnected, onDisconnected, onError]);

  /**
   * Handle incoming WebSocket messages
   */
  const handleMessage = useCallback((data: WebSocketMessage) => {
    console.log('📨 Received:', data.type, data);

    switch (data.type) {
      case 'connected':
        console.log('✅ Welcome message:', data.message);
        break;

      case 'presence_update':
        setPresence(data.users || []);
        console.log(`👥 ${data.count} users online`);
        break;

      case 'contact_created':
        // Dispatch custom event for components to listen
        window.dispatchEvent(
          new CustomEvent('workspace:contact_created', {
            detail: {
              contact: data.contact,
              created_by: data.created_by,
              created_by_name: data.created_by_name,
            },
          })
        );
        console.log(`📌 Contact created by ${data.created_by_name}:`, data.contact);
        break;

      case 'contact_updated':
        window.dispatchEvent(
          new CustomEvent('workspace:contact_updated', {
            detail: {
              contact_id: data.contact_id,
              changes: data.changes,
              updated_by: data.updated_by,
              updated_by_name: data.updated_by_name,
            },
          })
        );
        console.log(`✏️ Contact ${data.contact_id} updated by ${data.updated_by_name}`);
        break;

      case 'contact_deleted':
        window.dispatchEvent(
          new CustomEvent('workspace:contact_deleted', {
            detail: {
              contact_id: data.contact_id,
              deleted_by: data.deleted_by,
              deleted_by_name: data.deleted_by_name,
            },
          })
        );
        console.log(`🗑️ Contact ${data.contact_id} deleted by ${data.deleted_by_name}`);
        break;

      case 'note_added':
        window.dispatchEvent(
          new CustomEvent('workspace:note_added', {
            detail: {
              contact_id: data.contact_id,
              note: data.note,
              added_by: data.added_by,
              added_by_name: data.added_by_name,
            },
          })
        );
        console.log(`💬 Note added to ${data.contact_id} by ${data.added_by_name}`);
        break;

      case 'typing':
        window.dispatchEvent(
          new CustomEvent('workspace:typing', {
            detail: {
              contact_id: data.contact_id,
              field: data.field,
              is_typing: data.is_typing,
              user_id: data.user_id,
              user_name: data.user_name,
            },
          })
        );
        break;

      case 'cursor_position':
        window.dispatchEvent(
          new CustomEvent('workspace:cursor_position', {
            detail: {
              x: data.x,
              y: data.y,
              user_id: data.user_id,
              user_name: data.user_name,
            },
          })
        );
        break;

      case 'error':
        console.error('❌ Server error:', data.message);
        break;

      case 'pong':
        // Heartbeat response
        break;

      default:
        console.warn('⚠️ Unknown message type:', data.type);
    }
  }, []);

  /**
   * Send message to server
   */
  const send = useCallback((message: WebSocketMessage) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      // Queue message for when connection is restored
      console.warn('⚠️ WebSocket not connected, queuing message');
      messageQueueRef.current.push(message);
    }
  }, []);

  /**
   * Notify others that a contact was created
   */
  const sendContactCreated = useCallback((contact: Contact) => {
    send({
      type: 'contact_created',
      contact,
    });
  }, [send]);

  /**
   * Notify others that a contact was updated
   */
  const sendContactUpdated = useCallback((contactId: string, changes: Partial<Contact>) => {
    send({
      type: 'contact_updated',
      contact_id: contactId,
      changes,
    });
  }, [send]);

  /**
   * Notify others that a contact was deleted
   */
  const sendContactDeleted = useCallback((contactId: string) => {
    send({
      type: 'contact_deleted',
      contact_id: contactId,
    });
  }, [send]);

  /**
   * Send typing indicator
   */
  const sendTyping = useCallback((contactId: string, field: string, isTyping: boolean) => {
    send({
      type: 'typing',
      contact_id: contactId,
      field,
      is_typing: isTyping,
    });
  }, [send]);

  /**
   * Notify others that a note was added
   */
  const sendNoteAdded = useCallback((contactId: string, note: string) => {
    send({
      type: 'note_added',
      contact_id: contactId,
      note,
    });
  }, [send]);

  /**
   * Connect on mount, cleanup on unmount
   */
  useEffect(() => {
    connect();

    return () => {
      console.log('🔌 Cleaning up WebSocket connection');
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  /**
   * Heartbeat ping every 30 seconds
   */
  useEffect(() => {
    if (!isConnected) return;

    const interval = setInterval(() => {
      send({ type: 'ping' });
    }, 30000);

    return () => clearInterval(interval);
  }, [isConnected, send]);

  return {
    isConnected,
    presence,
    send,
    sendContactCreated,
    sendContactUpdated,
    sendContactDeleted,
    sendTyping,
    sendNoteAdded,
  };
}
