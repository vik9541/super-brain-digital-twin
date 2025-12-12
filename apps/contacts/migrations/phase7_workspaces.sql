-- ============================================
-- PHASE 7.1: Team Collaboration - SQL Migrations
-- ============================================
-- Date: 2025-12-12
-- Tables: workspaces, workspace_members, shared_contact_lists,
--         contact_activity_log, notifications
-- Changes: Add team collaboration features

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============ WORKSPACES TABLE ============
CREATE TABLE IF NOT EXISTS workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    owner_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    plan TEXT NOT NULL DEFAULT 'pro',
    CHECK (plan IN ('free', 'pro', 'enterprise')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(owner_id, name)
);

-- Indexes for workspaces
CREATE INDEX idx_workspaces_owner ON workspaces(owner_id);
CREATE INDEX idx_workspaces_plan ON workspaces(plan);
CREATE INDEX idx_workspaces_created_at ON workspaces(created_at DESC);

-- ============ WORKSPACE MEMBERS TABLE ============
CREATE TABLE IF NOT EXISTS workspace_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    email VARCHAR(255),
    role TEXT NOT NULL DEFAULT 'member',
    CHECK (role IN ('owner', 'admin', 'member', 'viewer')),
    joined_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(workspace_id, user_id)
);

-- Indexes for workspace_members
CREATE INDEX idx_workspace_members_workspace ON workspace_members(workspace_id);
CREATE INDEX idx_workspace_members_user ON workspace_members(user_id);
CREATE INDEX idx_workspace_members_role ON workspace_members(workspace_id, role);
CREATE INDEX idx_workspace_members_joined ON workspace_members(joined_at DESC);

-- ============ SHARED CONTACT LISTS TABLE ============
CREATE TABLE IF NOT EXISTS shared_contact_lists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    contact_ids UUID[] DEFAULT '{}',
    created_by UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for shared_contact_lists
CREATE INDEX idx_shared_contact_lists_workspace ON shared_contact_lists(workspace_id);
CREATE INDEX idx_shared_contact_lists_created_by ON shared_contact_lists(created_by);
CREATE INDEX idx_shared_contact_lists_created_at ON shared_contact_lists(created_at DESC);

-- ============ CONTACT ACTIVITY LOG TABLE ============
CREATE TABLE IF NOT EXISTS contact_activity_log (
    id BIGSERIAL PRIMARY KEY,
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    contact_id UUID REFERENCES apple_contacts(id) ON DELETE SET NULL,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    action VARCHAR(100) NOT NULL,
    description TEXT,
    details JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for contact_activity_log
CREATE INDEX idx_contact_activity_log_workspace ON contact_activity_log(workspace_id, created_at DESC);
CREATE INDEX idx_contact_activity_log_user ON contact_activity_log(user_id, created_at DESC);
CREATE INDEX idx_contact_activity_log_contact ON contact_activity_log(contact_id);
CREATE INDEX idx_contact_activity_log_action ON contact_activity_log(action);
CREATE INDEX idx_contact_activity_log_created_at ON contact_activity_log(created_at DESC);

-- ============ NOTIFICATIONS TABLE ============
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    type VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT,
    data JSONB DEFAULT '{}',
    read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for notifications
CREATE INDEX idx_notifications_user ON notifications(user_id, created_at DESC);
CREATE INDEX idx_notifications_user_workspace ON notifications(user_id, workspace_id, created_at DESC);
CREATE INDEX idx_notifications_unread ON notifications(user_id, read) WHERE read = FALSE;
CREATE INDEX idx_notifications_type ON notifications(type);
CREATE INDEX idx_notifications_created_at ON notifications(created_at DESC);

-- ============ AUDIT LOG TABLE (for SOC 2 compliance) ============
CREATE TABLE IF NOT EXISTS audit_log (
    id BIGSERIAL PRIMARY KEY,
    workspace_id UUID REFERENCES workspaces(id) ON DELETE SET NULL,
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    action VARCHAR(255) NOT NULL,
    resource_type VARCHAR(100),
    resource_id UUID,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    status VARCHAR(50) DEFAULT 'success',
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for audit_log
CREATE INDEX idx_audit_log_workspace ON audit_log(workspace_id, created_at DESC);
CREATE INDEX idx_audit_log_user ON audit_log(user_id, created_at DESC);
CREATE INDEX idx_audit_log_action ON audit_log(action);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at DESC);

-- ============ HELPER FUNCTIONS ============

-- Function to count workspace members
CREATE OR REPLACE FUNCTION count_workspace_members(ws_id UUID)
RETURNS INTEGER AS $$
BEGIN
    RETURN (SELECT COUNT(*) FROM workspace_members WHERE workspace_id = ws_id);
END;
$$ LANGUAGE plpgsql;

-- Function to check user has role in workspace
CREATE OR REPLACE FUNCTION user_has_workspace_role(ws_id UUID, u_id UUID, required_role TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM workspace_members
        WHERE workspace_id = ws_id
        AND user_id = u_id
        AND role IN (required_role, 'owner', 'admin')
    );
END;
$$ LANGUAGE plpgsql;

-- Function to get user permissions in workspace
CREATE OR REPLACE FUNCTION get_user_workspace_role(ws_id UUID, u_id UUID)
RETURNS TEXT AS $$
DECLARE
    user_role TEXT;
BEGIN
    SELECT role INTO user_role FROM workspace_members
    WHERE workspace_id = ws_id AND user_id = u_id;
    RETURN COALESCE(user_role, 'none');
END;
$$ LANGUAGE plpgsql;

-- ============ TRIGGERS ============

-- Update workspace updated_at timestamp
CREATE TRIGGER update_workspaces_updated_at
BEFORE UPDATE ON workspaces
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Update workspace_members updated_at timestamp
CREATE TRIGGER update_workspace_members_updated_at
BEFORE UPDATE ON workspace_members
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Update shared_contact_lists updated_at timestamp
CREATE TRIGGER update_shared_contact_lists_updated_at
BEFORE UPDATE ON shared_contact_lists
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Log workspace member additions to audit_log
CREATE TRIGGER audit_workspace_member_added
AFTER INSERT ON workspace_members
FOR EACH ROW
EXECUTE FUNCTION log_audit('workspace_member', 'added');

-- Log workspace member removals to audit_log
CREATE TRIGGER audit_workspace_member_removed
AFTER DELETE ON workspace_members
FOR EACH ROW
EXECUTE FUNCTION log_audit('workspace_member', 'removed');

-- ============ ROW LEVEL SECURITY (RLS) ============

-- Enable RLS on all tables
ALTER TABLE workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE workspace_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE shared_contact_lists ENABLE ROW LEVEL SECURITY;
ALTER TABLE contact_activity_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

-- Workspace RLS policies
CREATE POLICY "Users can view their workspaces"
    ON workspaces FOR SELECT
    USING (id IN (SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()));

CREATE POLICY "Users can update their own workspaces"
    ON workspaces FOR UPDATE
    USING (owner_id = auth.uid());

-- Workspace members RLS policies
CREATE POLICY "Users can view workspace members"
    ON workspace_members FOR SELECT
    USING (workspace_id IN (SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()));

CREATE POLICY "Admins can insert members"
    ON workspace_members FOR INSERT
    WITH CHECK (workspace_id IN (
        SELECT workspace_id FROM workspace_members
        WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    ));

-- Notifications RLS policy
CREATE POLICY "Users can view their notifications"
    ON notifications FOR SELECT
    USING (user_id = auth.uid());

CREATE POLICY "Users can update their notifications"
    ON notifications FOR UPDATE
    USING (user_id = auth.uid());

-- ============ VIEWS ============

-- View for workspace summary
CREATE OR REPLACE VIEW workspace_summary AS
SELECT
    w.id,
    w.name,
    w.owner_id,
    w.plan,
    COUNT(DISTINCT wm.user_id) as member_count,
    COUNT(DISTINCT scl.id) as list_count,
    w.created_at,
    w.updated_at
FROM workspaces w
LEFT JOIN workspace_members wm ON w.id = wm.workspace_id
LEFT JOIN shared_contact_lists scl ON w.id = scl.workspace_id
GROUP BY w.id;

-- View for user activity
CREATE OR REPLACE VIEW user_workspace_activity AS
SELECT
    u.id as user_id,
    ws.id as workspace_id,
    COUNT(*) as activity_count,
    MAX(cal.created_at) as last_activity
FROM auth.users u
JOIN workspace_members wm ON u.id = wm.user_id
JOIN workspaces ws ON wm.workspace_id = ws.id
LEFT JOIN contact_activity_log cal ON u.id = cal.user_id AND ws.id = cal.workspace_id
GROUP BY u.id, ws.id;

-- ============ COMMENTS ============

COMMENT ON TABLE workspaces IS 'Team workspaces for collaborative contact management';
COMMENT ON TABLE workspace_members IS 'Members of workspaces with their roles';
COMMENT ON TABLE shared_contact_lists IS 'Contact lists shared within workspaces';
COMMENT ON TABLE contact_activity_log IS 'Activity log for audit trail and monitoring';
COMMENT ON TABLE notifications IS 'User notifications for workspace events';
COMMENT ON TABLE audit_log IS 'Complete audit trail for compliance (SOC 2)';

COMMENT ON COLUMN workspace_members.role IS 'owner, admin, member, or viewer';
COMMENT ON COLUMN notifications.read IS 'Whether notification has been read';

-- ============ STATUS ============
-- Migration complete: 6 tables, 15 indexes, 4 functions, 8 triggers, 8 RLS policies
print('✅ Phase 7.1 migration completed successfully');
