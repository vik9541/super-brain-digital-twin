-- ============================================
-- CONTACT INTELLIGENCE MODULE - INCREMENTAL SCHEMA
-- Version: 1.1 (Compatible with existing contacts table)
-- Created: 2025-12-10
-- Purpose: Add Contact Intelligence without destroying existing data
-- ============================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

BEGIN;

-- ============================================
-- STEP 1: EXTEND EXISTING CONTACTS TABLE
-- ============================================

-- Add telegram_id if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'contacts' AND column_name = 'telegram_id'
    ) THEN
        ALTER TABLE contacts ADD COLUMN telegram_id BIGINT UNIQUE;
        CREATE INDEX idx_contacts_telegram_id ON contacts(telegram_id);
    END IF;
END $$;

-- Ensure other useful indexes exist
CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email);
CREATE INDEX IF NOT EXISTS idx_contacts_phone ON contacts(phone);
CREATE INDEX IF NOT EXISTS idx_contacts_created_at ON contacts(created_at);

-- ============================================
-- STEP 2: CREATE INTERACTIONS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS interactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contact_id BIGINT NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    channel TEXT NOT NULL, -- 'telegram', 'whatsapp', 'email', etc.
    direction TEXT NOT NULL, -- 'incoming', 'outgoing'
    message_encrypted TEXT, -- encrypted message content
    message_metadata JSONB DEFAULT '{}', -- sentiment, topics, etc.
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed BOOLEAN DEFAULT FALSE,
    embedding vector(1536), -- OpenAI ada-002 embeddings
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for interactions
CREATE INDEX IF NOT EXISTS idx_interactions_contact_id ON interactions(contact_id);
CREATE INDEX IF NOT EXISTS idx_interactions_timestamp ON interactions(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_interactions_channel ON interactions(channel);
CREATE INDEX IF NOT EXISTS idx_interactions_processed ON interactions(processed) WHERE NOT processed;

-- Vector similarity search index (only if vector extension is available)
DO $$
BEGIN
    CREATE INDEX IF NOT EXISTS idx_interactions_embedding ON interactions 
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
EXCEPTION
    WHEN undefined_function THEN
        RAISE NOTICE 'Vector extension not available, skipping embedding index';
END $$;

-- ============================================
-- STEP 3: CREATE COMMUNICATION_PROFILES TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS communication_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contact_id BIGINT NOT NULL UNIQUE REFERENCES contacts(id) ON DELETE CASCADE,
    preferred_channel TEXT, -- 'telegram', 'whatsapp', 'email'
    response_time_avg INTERVAL, -- average response time
    active_hours JSONB, -- {"start": "09:00", "end": "18:00", "timezone": "UTC+3"}
    communication_style JSONB, -- {"formality": "casual", "emoji_usage": "high"}
    topics_of_interest TEXT[], -- array of topics
    language_preference TEXT DEFAULT 'ru',
    last_analyzed TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_comm_profiles_contact_id ON communication_profiles(contact_id);
CREATE INDEX IF NOT EXISTS idx_comm_profiles_last_analyzed ON communication_profiles(last_analyzed);

-- ============================================
-- STEP 4: CREATE COLLABORATIONS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS collaborations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contact_id BIGINT NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    project_name TEXT NOT NULL,
    status TEXT NOT NULL, -- 'active', 'completed', 'paused', 'cancelled'
    start_date DATE,
    end_date DATE,
    description TEXT,
    deliverables JSONB, -- {"items": [...]}
    budget_info JSONB, -- {"amount": 0, "currency": "RUB"}
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_collaborations_contact_id ON collaborations(contact_id);
CREATE INDEX IF NOT EXISTS idx_collaborations_status ON collaborations(status);
CREATE INDEX IF NOT EXISTS idx_collaborations_start_date ON collaborations(start_date DESC);

-- ============================================
-- STEP 5: CREATE CONTACT_TASKS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS contact_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contact_id BIGINT NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    task_type TEXT NOT NULL, -- 'follow_up', 'reminder', 'auto_response'
    title TEXT NOT NULL,
    description TEXT,
    due_date TIMESTAMP WITH TIME ZONE,
    status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'completed', 'cancelled'
    priority TEXT DEFAULT 'medium', -- 'low', 'medium', 'high', 'urgent'
    auto_generated BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}',
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_contact_tasks_contact_id ON contact_tasks(contact_id);
CREATE INDEX IF NOT EXISTS idx_contact_tasks_status ON contact_tasks(status);
CREATE INDEX IF NOT EXISTS idx_contact_tasks_due_date ON contact_tasks(due_date) WHERE status = 'pending';
CREATE INDEX IF NOT EXISTS idx_contact_tasks_priority ON contact_tasks(priority);

-- ============================================
-- STEP 6: MATERIALIZED VIEW (Adapted to existing contacts)
-- ============================================

DROP MATERIALIZED VIEW IF EXISTS contact_analytics CASCADE;

CREATE MATERIALIZED VIEW contact_analytics AS
SELECT 
    c.id AS contact_id,
    COALESCE(c.full_name, c.first_name || ' ' || c.last_name, 'Unknown') AS name,
    c.telegram_id,
    c.email,
    c.phone,
    COUNT(DISTINCT i.id) AS total_interactions,
    COUNT(DISTINCT i.id) FILTER (WHERE i.direction = 'incoming') AS incoming_count,
    COUNT(DISTINCT i.id) FILTER (WHERE i.direction = 'outgoing') AS outgoing_count,
    MAX(i.timestamp) AS last_interaction,
    COUNT(DISTINCT co.id) FILTER (WHERE co.status = 'active') AS active_collaborations,
    COUNT(DISTINCT ct.id) FILTER (WHERE ct.status = 'pending') AS pending_tasks,
    cp.preferred_channel,
    cp.response_time_avg
FROM contacts c
LEFT JOIN interactions i ON i.contact_id = c.id
LEFT JOIN collaborations co ON co.contact_id = c.id
LEFT JOIN contact_tasks ct ON ct.contact_id = c.id
LEFT JOIN communication_profiles cp ON cp.contact_id = c.id
GROUP BY c.id, c.full_name, c.first_name, c.last_name, c.telegram_id, c.email, c.phone, cp.preferred_channel, cp.response_time_avg;

-- Index for materialized view
CREATE UNIQUE INDEX idx_contact_analytics_contact_id ON contact_analytics(contact_id);

-- ============================================
-- STEP 7: ROW LEVEL SECURITY
-- ============================================

-- Enable RLS
ALTER TABLE interactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE communication_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE collaborations ENABLE ROW LEVEL SECURITY;
ALTER TABLE contact_tasks ENABLE ROW LEVEL SECURITY;

-- Policies for service role
DROP POLICY IF EXISTS "Service role full access interactions" ON interactions;
CREATE POLICY "Service role full access interactions" 
    ON interactions FOR ALL 
    USING (auth.role() = 'service_role');

DROP POLICY IF EXISTS "Service role full access communication_profiles" ON communication_profiles;
CREATE POLICY "Service role full access communication_profiles" 
    ON communication_profiles FOR ALL 
    USING (auth.role() = 'service_role');

DROP POLICY IF EXISTS "Service role full access collaborations" ON collaborations;
CREATE POLICY "Service role full access collaborations" 
    ON collaborations FOR ALL 
    USING (auth.role() = 'service_role');

DROP POLICY IF EXISTS "Service role full access contact_tasks" ON contact_tasks;
CREATE POLICY "Service role full access contact_tasks" 
    ON contact_tasks FOR ALL 
    USING (auth.role() = 'service_role');

-- ============================================
-- STEP 8: TRIGGERS
-- ============================================

-- Function to update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
DROP TRIGGER IF EXISTS update_communication_profiles_updated_at ON communication_profiles;
CREATE TRIGGER update_communication_profiles_updated_at
    BEFORE UPDATE ON communication_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_collaborations_updated_at ON collaborations;
CREATE TRIGGER update_collaborations_updated_at
    BEFORE UPDATE ON collaborations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_contact_tasks_updated_at ON contact_tasks;
CREATE TRIGGER update_contact_tasks_updated_at
    BEFORE UPDATE ON contact_tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- STEP 9: UTILITY FUNCTIONS
-- ============================================

-- Function to refresh analytics
CREATE OR REPLACE FUNCTION refresh_contact_analytics()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY contact_analytics;
END;
$$ LANGUAGE plpgsql;

COMMIT;

-- ============================================
-- VERIFICATION QUERY
-- ============================================

SELECT 
    'contacts' AS table_name,
    COUNT(*) AS existing_rows,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'contacts') AS columns
FROM contacts
UNION ALL
SELECT 'interactions', COUNT(*), (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'interactions') FROM interactions
UNION ALL
SELECT 'communication_profiles', COUNT(*), (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'communication_profiles') FROM communication_profiles
UNION ALL
SELECT 'collaborations', COUNT(*), (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'collaborations') FROM collaborations
UNION ALL
SELECT 'contact_tasks', COUNT(*), (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'contact_tasks') FROM contact_tasks;

-- Show success message
DO $$
BEGIN
    RAISE NOTICE '✅ Contact Intelligence schema deployed successfully!';
    RAISE NOTICE '✅ Existing contacts table preserved';
    RAISE NOTICE '✅ 4 new tables created: interactions, communication_profiles, collaborations, contact_tasks';
    RAISE NOTICE '✅ Materialized view contact_analytics ready';
END $$;