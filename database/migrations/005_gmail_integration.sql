-- Gmail Integration Schema - Phase 9 Day 6-7
-- Stores OAuth tokens and email interactions

-- Gmail sync table (OAuth tokens)
CREATE TABLE IF NOT EXISTS gmail_sync (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    access_token TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    token_expiry TIMESTAMP WITH TIME ZONE NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    last_sync_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id)
);

-- Email interactions table
CREATE TABLE IF NOT EXISTS email_interactions (
    id BIGSERIAL PRIMARY KEY,
    workspace_id UUID NOT NULL,
    contact_id BIGINT REFERENCES contacts(id) ON DELETE CASCADE,
    interaction_type VARCHAR(50) DEFAULT 'email', -- email, reply, forward
    direction VARCHAR(20), -- sent, received
    subject TEXT,
    occurred_at TIMESTAMP WITH TIME ZONE NOT NULL,
    gmail_message_id TEXT, -- Gmail internal message ID
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT fk_workspace FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX idx_gmail_sync_user_id ON gmail_sync(user_id);
CREATE INDEX idx_gmail_sync_enabled ON gmail_sync(enabled) WHERE enabled = TRUE;
CREATE INDEX idx_email_interactions_workspace ON email_interactions(workspace_id);
CREATE INDEX idx_email_interactions_contact ON email_interactions(contact_id);
CREATE INDEX idx_email_interactions_occurred_at ON email_interactions(occurred_at DESC);
CREATE INDEX idx_email_interactions_gmail_id ON email_interactions(gmail_message_id);

-- Comments
COMMENT ON TABLE gmail_sync IS 'OAuth tokens for Gmail API integration';
COMMENT ON TABLE email_interactions IS 'Email interactions tracked from Gmail sync';
COMMENT ON COLUMN gmail_sync.token_expiry IS 'When access_token expires (refresh after)';
COMMENT ON COLUMN email_interactions.gmail_message_id IS 'Prevents duplicate processing';
