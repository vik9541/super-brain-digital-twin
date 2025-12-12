-- Phase 7.2: WebSocket Message Persistence
-- Store WebSocket messages for offline delivery and audit trail

-- Table: websocket_messages
-- Stores all WebSocket messages for history and offline delivery
CREATE TABLE IF NOT EXISTS websocket_messages (
    id BIGSERIAL PRIMARY KEY,
    workspace_id BIGINT NOT NULL,
    message_type TEXT NOT NULL,
    user_id TEXT NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    delivered BOOLEAN DEFAULT FALSE,
    delivered_at TIMESTAMPTZ
);

-- Indexes for performance
CREATE INDEX idx_ws_messages_workspace ON websocket_messages(workspace_id);
CREATE INDEX idx_ws_messages_user ON websocket_messages(user_id);
CREATE INDEX idx_ws_messages_type ON websocket_messages(message_type);
CREATE INDEX idx_ws_messages_created ON websocket_messages(created_at DESC);
CREATE INDEX idx_ws_messages_undelivered ON websocket_messages(workspace_id, delivered) WHERE delivered = FALSE;

-- Table: websocket_sessions
-- Track user connection sessions for analytics
CREATE TABLE IF NOT EXISTS websocket_sessions (
    id BIGSERIAL PRIMARY KEY,
    workspace_id BIGINT NOT NULL,
    user_id TEXT NOT NULL,
    connected_at TIMESTAMPTZ DEFAULT NOW(),
    disconnected_at TIMESTAMPTZ,
    duration_seconds INTEGER,
    messages_sent INTEGER DEFAULT 0,
    messages_received INTEGER DEFAULT 0
);

-- Indexes
CREATE INDEX idx_ws_sessions_workspace ON websocket_sessions(workspace_id);
CREATE INDEX idx_ws_sessions_user ON websocket_sessions(user_id);
CREATE INDEX idx_ws_sessions_active ON websocket_sessions(workspace_id, user_id) WHERE disconnected_at IS NULL;

-- Function: Mark message as delivered
CREATE OR REPLACE FUNCTION mark_message_delivered(message_id BIGINT)
RETURNS VOID AS $$
BEGIN
    UPDATE websocket_messages
    SET 
        delivered = TRUE,
        delivered_at = NOW()
    WHERE id = message_id;
END;
$$ LANGUAGE plpgsql;

-- Function: Get undelivered messages for user
CREATE OR REPLACE FUNCTION get_undelivered_messages(
    p_workspace_id BIGINT,
    p_user_id TEXT,
    p_since TIMESTAMPTZ DEFAULT NOW() - INTERVAL '24 hours'
)
RETURNS TABLE (
    message_id BIGINT,
    message_type TEXT,
    sender_id TEXT,
    payload JSONB,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        id,
        message_type,
        user_id,
        payload,
        created_at
    FROM websocket_messages
    WHERE 
        workspace_id = p_workspace_id
        AND created_at >= p_since
        AND (delivered = FALSE OR user_id != p_user_id)
    ORDER BY created_at ASC;
END;
$$ LANGUAGE plpgsql;

-- Function: Clean old messages (retention policy)
CREATE OR REPLACE FUNCTION cleanup_old_websocket_messages(
    p_retention_days INTEGER DEFAULT 30
)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM websocket_messages
    WHERE 
        created_at < NOW() - (p_retention_days || ' days')::INTERVAL
        AND delivered = TRUE;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function: Update session statistics
CREATE OR REPLACE FUNCTION update_session_stats(
    p_session_id BIGINT,
    p_messages_sent INTEGER DEFAULT 0,
    p_messages_received INTEGER DEFAULT 0
)
RETURNS VOID AS $$
BEGIN
    UPDATE websocket_sessions
    SET 
        messages_sent = messages_sent + p_messages_sent,
        messages_received = messages_received + p_messages_received
    WHERE id = p_session_id;
END;
$$ LANGUAGE plpgsql;

-- Function: End session
CREATE OR REPLACE FUNCTION end_websocket_session(p_session_id BIGINT)
RETURNS VOID AS $$
BEGIN
    UPDATE websocket_sessions
    SET 
        disconnected_at = NOW(),
        duration_seconds = EXTRACT(EPOCH FROM (NOW() - connected_at))::INTEGER
    WHERE id = p_session_id;
END;
$$ LANGUAGE plpgsql;

-- View: Active WebSocket sessions
CREATE OR REPLACE VIEW active_websocket_sessions AS
SELECT 
    ws.id,
    ws.workspace_id,
    ws.user_id,
    ws.connected_at,
    EXTRACT(EPOCH FROM (NOW() - ws.connected_at))::INTEGER AS duration_seconds,
    ws.messages_sent,
    ws.messages_received
FROM websocket_sessions ws
WHERE ws.disconnected_at IS NULL
ORDER BY ws.connected_at DESC;

-- View: WebSocket message statistics by workspace
CREATE OR REPLACE VIEW websocket_message_stats AS
SELECT 
    workspace_id,
    message_type,
    COUNT(*) AS total_messages,
    COUNT(DISTINCT user_id) AS unique_senders,
    COUNT(*) FILTER (WHERE delivered = TRUE) AS delivered_count,
    COUNT(*) FILTER (WHERE delivered = FALSE) AS pending_count,
    MIN(created_at) AS first_message_at,
    MAX(created_at) AS last_message_at
FROM websocket_messages
GROUP BY workspace_id, message_type;

-- Grant permissions (adjust based on your setup)
-- GRANT ALL ON websocket_messages TO authenticated;
-- GRANT ALL ON websocket_sessions TO authenticated;
-- GRANT EXECUTE ON FUNCTION get_undelivered_messages TO authenticated;
-- GRANT EXECUTE ON FUNCTION mark_message_delivered TO authenticated;

-- Comments
COMMENT ON TABLE websocket_messages IS 'Stores WebSocket messages for offline delivery and audit trail';
COMMENT ON TABLE websocket_sessions IS 'Tracks user WebSocket connection sessions for analytics';
COMMENT ON FUNCTION get_undelivered_messages IS 'Retrieves undelivered messages for a user since a specific time';
COMMENT ON FUNCTION cleanup_old_websocket_messages IS 'Removes delivered messages older than retention period';
COMMENT ON VIEW active_websocket_sessions IS 'Shows currently active WebSocket connections';
COMMENT ON VIEW websocket_message_stats IS 'Aggregated statistics for WebSocket messages by workspace';

-- Example queries:

-- Get undelivered messages for user
-- SELECT * FROM get_undelivered_messages(123, 'user_456');

-- Get active sessions in a workspace
-- SELECT * FROM active_websocket_sessions WHERE workspace_id = 123;

-- Get message statistics
-- SELECT * FROM websocket_message_stats WHERE workspace_id = 123;

-- Clean up old messages (older than 30 days)
-- SELECT cleanup_old_websocket_messages(30);

-- Insert a message
-- INSERT INTO websocket_messages (workspace_id, message_type, user_id, payload)
-- VALUES (123, 'contact_created', 'user_456', '{"contact": {"id": "1", "name": "John"}}');

-- Create a session
-- INSERT INTO websocket_sessions (workspace_id, user_id)
-- VALUES (123, 'user_456')
-- RETURNING id;
