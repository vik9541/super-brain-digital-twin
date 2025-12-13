-- GDPR Compliance Database Migrations
-- Phase 9 Day 3-4
-- 
-- Tables:
-- 1. gdpr_operations - Audit trail (7-year retention)
-- 2. users table updates - Add GDPR columns

-- ========================================
-- Table: gdpr_operations (Audit Trail)
-- ========================================

CREATE TABLE IF NOT EXISTS gdpr_operations (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    operation_type VARCHAR(50) NOT NULL, -- 'export_data', 'delete_data', 'restrict_processing'
    status VARCHAR(20) NOT NULL, -- 'in_progress', 'completed', 'failed'
    details JSONB, -- Additional details
    authorized_by UUID, -- Who authorized (for admin operations)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Indexes for fast queries
    INDEX idx_gdpr_ops_user_id (user_id),
    INDEX idx_gdpr_ops_created_at (created_at),
    INDEX idx_gdpr_ops_type (operation_type)
);

-- Retention policy: 7 years (legal requirement)
COMMENT ON TABLE gdpr_operations IS 'GDPR operations audit trail. Retention: 7 years per legal requirements.';


-- ========================================
-- users table updates
-- ========================================

-- Add GDPR-related columns to users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS processing_restricted BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS processing_restricted_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS gdpr_deletion_requested_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS gdpr_deleted BOOLEAN DEFAULT FALSE;

-- Index for checking restricted users
CREATE INDEX IF NOT EXISTS idx_users_processing_restricted ON users(processing_restricted) WHERE processing_restricted = TRUE;

-- Comments
COMMENT ON COLUMN users.processing_restricted IS 'GDPR Article 18: Right to restrict processing';
COMMENT ON COLUMN users.gdpr_deleted IS 'GDPR Article 17: User data anonymized (not hard deleted)';


-- ========================================
-- Sample Queries (for reference)
-- ========================================

-- Get all GDPR operations for a user
-- SELECT * FROM gdpr_operations WHERE user_id = 'xxx' ORDER BY created_at DESC;

-- Get users with restricted processing
-- SELECT id, email, processing_restricted_at FROM users WHERE processing_restricted = TRUE;

-- Get deleted/anonymized users
-- SELECT id, email, gdpr_deletion_requested_at FROM users WHERE gdpr_deleted = TRUE;

-- Audit trail for last 30 days
-- SELECT user_id, operation_type, status, created_at 
-- FROM gdpr_operations 
-- WHERE created_at > NOW() - INTERVAL '30 days'
-- ORDER BY created_at DESC;
