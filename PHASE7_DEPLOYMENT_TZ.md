# 📋 PHASE 7.1 DEPLOYMENT TZ
## Complete Production Implementation Guide

**Document:** PHASE7_DEPLOYMENT_TZ  
**Status:** 🚀 READY TO DEPLOY  
**Date:** 12 Dec 2025  
**Estimated Time:** 2-3 hours  
**Complexity:** MEDIUM  

---

# SECTION 1: PRE-DEPLOYMENT CHECKLIST

## 1.1 Verify All Files Are Created

```bash
# Check backend files
ls -la api/workspaces/
  models.py ✓
  service.py ✓
  routes.py ✓
  __init__.py ✓

# Check GraphQL
ls -la api/graphql/
  schema_workspaces.py ✓

# Check frontend
ls -la web/app/workspaces/
  page.tsx ✓
  [id]/
    page.tsx ✓

# Check database
ls -la apps/contacts/migrations/
  phase7_workspaces.sql ✓

# Check tests
ls -la tests/
  test_workspaces.py ✓
```

## 1.2 Git Status

```bash
cd /path/to/super-brain-digital-twin
git status

# You should see 8 new files:
# - api/workspaces/models.py
# - api/workspaces/service.py
# - api/workspaces/routes.py
# - api/graphql/schema_workspaces.py
# - web/app/workspaces/page.tsx
# - web/app/workspaces/[id]/page.tsx
# - apps/contacts/migrations/phase7_workspaces.sql
# - tests/test_workspaces.py

git add -A
git commit -m "Phase 7.1: Team collaboration - workspaces, RBAC, activity logging"
git push origin main
```

---

# SECTION 2: DATABASE SETUP (Supabase)

## 2.1 Create Tables (5 minutes)

**In Supabase dashboard:**

1. Go to SQL Editor
2. Click "New Query"
3. Copy entire contents of:
   ```
   apps/contacts/migrations/phase7_workspaces.sql
   ```
4. Click "Run"
5. Verify success message

**Verify tables created:**

```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
  'workspaces',
  'workspace_members', 
  'shared_contact_lists',
  'contact_activity_log',
  'notifications',
  'audit_log'
)
ORDER BY table_name;
```

**Expected output:**
```
✓ audit_log
✓ contact_activity_log
✓ notifications
✓ shared_contact_lists
✓ workspace_members
✓ workspaces
```

## 2.2 Verify Indexes

```sql
-- Check all indexes created
SELECT indexname FROM pg_indexes 
WHERE schemaname = 'public' 
AND tablename LIKE 'workspace%'
OR tablename LIKE '%activity%'
OR tablename = 'notifications';
```

**Should have 15+ indexes**

## 2.3 Test RLS Policies

```sql
-- List all policies
SELECT schemaname, tablename, policyname 
FROM pg_policies 
WHERE tablename LIKE 'workspace%' 
OR tablename = 'notifications';
```

**Expected: 8 policies** (one per permission check)

---

# SECTION 3: BACKEND SETUP

## 3.1 Install Dependencies

```bash
cd /path/to/super-brain-digital-twin

# Install required packages
pip install --upgrade pip
pip install fastapi uvicorn python-multipart pydantic sqlalchemy supabase

# Verify
python -c "import fastapi; print(f'FastAPI {fastapi.__version__} installed')"
python -c "import supabase; print(f'Supabase installed')"
```

## 3.2 Create Workspace Module Init

**Create `api/workspaces/__init__.py`:**

```python
# api/workspaces/__init__.py
from .models import (
    WorkspaceCreate,
    WorkspaceResponse,
    WorkspaceMemberInvite,
    WorkspaceRole,
    WorkspacePlan
)
from .service import WorkspaceService
from .routes import router

__all__ = [
    'WorkspaceCreate',
    'WorkspaceResponse',
    'WorkspaceMemberInvite',
    'WorkspaceRole',
    'WorkspacePlan',
    'WorkspaceService',
    'router'
]
```

## 3.3 Update Main API File

**In `api/main.py`, add imports:**

```python
# At top of file
from api.workspaces.routes import router as workspaces_router

# After other routers are included
app.include_router(workspaces_router, tags=["workspaces"])
```

## 3.4 Create Dependencies File

**Update `api/auth/dependencies.py`:**

```python
# Add to api/auth/dependencies.py

from api.workspaces.service import WorkspaceService
from api.email.service import EmailService

async def get_workspace_service() -> WorkspaceService:
    """Get workspace service instance"""
    from api.db import get_supabase, get_auth
    
    supabase = get_supabase()
    auth = get_auth()
    email = EmailService()
    
    return WorkspaceService(supabase, auth, email)
```

## 3.5 Test Backend

```bash
# Start backend
cd api
uvicorn main:app --reload --port 8000

# In another terminal, test endpoints
curl -X GET http://localhost:8000/api/workspaces \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Expected: Empty list (no workspaces yet)
# {"workspaces": [], "total": 0}
```

---

# SECTION 4: FRONTEND SETUP

## 4.1 Install Dependencies

```bash
cd web
npm install
npm install @apollo/client graphql
```

## 4.2 Create GraphQL Queries File

**Create `web/lib/graphql/workspaces.ts`:**

```typescript
import gql from 'graphql-tag';

export const GET_MY_WORKSPACES = gql`
  query MyWorkspaces($page: Int = 1, $perPage: Int = 10) {
    myWorkspaces(page: $page, perPage: $perPage) {
      workspaces {
        id
        name
        plan
        memberCount
        members {
          userId
          email
          role
        }
        createdAt
        updatedAt
      }
      total
      page
      perPage
    }
  }
`;

export const GET_WORKSPACE = gql`
  query Workspace($id: UUID!) {
    workspace(id: $id) {
      id
      name
      plan
      memberCount
      members {
        userId
        email
        name
        role
        joinedAt
      }
      createdAt
      updatedAt
    }
  }
`;

export const CREATE_WORKSPACE = gql`
  mutation CreateWorkspace($name: String!, $plan: WorkspacePlan) {
    createWorkspace(name: $name, plan: $plan) {
      id
      name
      plan
      memberCount
      createdAt
    }
  }
`;

export const INVITE_MEMBER = gql`
  mutation InviteMember(
    $workspaceId: UUID!
    $email: String!
    $role: WorkspaceRole
    $message: String
  ) {
    inviteMember(
      workspaceId: $workspaceId
      email: $email
      role: $role
      message: $message
    ) {
      success
      message
      userId
      role
    }
  }
`;

export const REMOVE_MEMBER = gql`
  mutation RemoveMember($workspaceId: UUID!, $memberId: UUID!) {
    removeMember(workspaceId: $workspaceId, memberId: $memberId)
  }
`;

export const DELETE_WORKSPACE = gql`
  mutation DeleteWorkspace($id: UUID!) {
    deleteWorkspace(id: $id)
  }
`;

export const GET_WORKSPACE_ACTIVITY = gql`
  query WorkspaceActivity(
    $workspaceId: UUID!
    $page: Int = 1
    $perPage: Int = 20
  ) {
    workspaceActivity(
      workspaceId: $workspaceId
      page: $page
      perPage: $perPage
    ) {
      entries {
        id
        workspaceId
        contactId
        userId
        userName
        action
        description
        details
        createdAt
      }
      total
      page
      perPage
    }
  }
`;

export const GET_MY_NOTIFICATIONS = gql`
  query MyNotifications($workspaceId: UUID!, $limit: Int = 20) {
    myNotifications(workspaceId: $workspaceId, limit: $limit) {
      notifications {
        id
        type
        title
        message
        data
        read
        createdAt
      }
      unreadCount
      total
    }
  }
`;
```

## 4.3 Update Layout

**In `web/app/layout.tsx`, add navigation:**

```typescript
// Add to navigation menu
<Link href="/workspaces">Workspaces</Link>
```

## 4.4 Test Frontend

```bash
npm run dev

# Open http://localhost:3000/workspaces
# Should see "No workspaces yet" message
```

---

# SECTION 5: TESTING

## 5.1 Run Unit Tests

```bash
# From root directory
pytest tests/test_workspaces.py -v

# Expected output:
# test_create_workspace PASSED
# test_list_user_workspaces PASSED
# test_invite_member PASSED
# test_remove_member PASSED
# test_permission_denied_on_invite PASSED
# test_create_shared_list PASSED
# test_get_notifications PASSED
# test_validation_empty_workspace_name PASSED
# test_validation_invalid_email PASSED
# test_mark_notification_read PASSED
# 
# ===================== 10 passed in 1.45s =====================
```

## 5.2 Test API Endpoints

```bash
# Get JWT token first from login
TOKEN="your_jwt_token_here"

# 1. Create workspace
curl -X POST http://localhost:8000/api/workspaces \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sales Team",
    "plan": "pro"
  }'

# Response:
# {
#   "id": "550e8400-e29b-41d4-a716-446655440000",
#   "name": "Sales Team",
#   "owner_id": "user_id_here",
#   "plan": "pro",
#   "member_count": 1,
#   "members": [...],
#   "created_at": "2025-12-12T20:00:00Z",
#   "updated_at": "2025-12-12T20:00:00Z"
# }

WORKSPACE_ID="550e8400-e29b-41d4-a716-446655440000"

# 2. List workspaces
curl -X GET "http://localhost:8000/api/workspaces?page=1&per_page=10" \
  -H "Authorization: Bearer $TOKEN"

# 3. Get specific workspace
curl -X GET "http://localhost:8000/api/workspaces/$WORKSPACE_ID" \
  -H "Authorization: Bearer $TOKEN"

# 4. Invite member
curl -X POST "http://localhost:8000/api/workspaces/$WORKSPACE_ID/members" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "role": "member"
  }'

# 5. Get activity log
curl -X GET "http://localhost:8000/api/workspaces/$WORKSPACE_ID/activity" \
  -H "Authorization: Bearer $TOKEN"

# 6. Get notifications
curl -X GET "http://localhost:8000/api/workspaces/$WORKSPACE_ID/notifications" \
  -H "Authorization: Bearer $TOKEN"
```

## 5.3 Test GraphQL

```bash
# Test GraphQL query
curl -X POST http://localhost:8000/graphql \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { myWorkspaces(page: 1, perPage: 10) { workspaces { id name } total } }"
  }'
```

## 5.4 Manual UI Testing

1. **Create Workspace**
   - Go to http://localhost:3000/workspaces
   - Click "+ New Workspace"
   - Fill: Name="Marketing", Plan="Pro"
   - Click "Create Workspace"
   - ✓ Should appear in list

2. **Open Workspace**
   - Click on workspace
   - ✓ Should show members (just you)
   - ✓ Should show empty activity log

3. **Invite Member**
   - Click "+ Invite Member"
   - Fill: Email="test@example.com", Role="Member"
   - Click "Send Invite"
   - ✓ Should show success message

4. **View Activity**
   - Scroll down on workspace page
   - ✓ Should show: "workspace_created", "member_invited"

---

# SECTION 6: PRODUCTION DEPLOYMENT

## 6.1 Heroku/Railway Backend

```bash
# Create Procfile
echo "web: uvicorn api.main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Create runtime.txt
echo "python-3.11.7" > runtime.txt

# Create requirements.txt
pip freeze > requirements.txt

# Deploy
git add .
git commit -m "Phase 7.1: Deploy team collaboration"
git push heroku main

# Or with Railway:
railway deploy
```

## 6.2 Vercel Frontend

```bash
# Update .env.production
NEXT_PUBLIC_API_URL=https://your-api.herokuapp.com
NEXT_PUBLIC_GRAPHQL_URL=https://your-api.herokuapp.com/graphql

# Deploy
vercel deploy --prod
```

## 6.3 Environment Variables

**Backend (.env):**
```bash
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=xxxx
JWT_SECRET=your_secret
EMAIL_FROM=noreply@yourdomain.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_password
```

**Frontend (.env.production):**
```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_GRAPHQL_URL=https://api.yourdomain.com/graphql
NEXT_PUBLIC_SUPABASE_URL=https://xxxx.supabase.co
NEXT_PUBLIC_SUPABASE_KEY=xxxx
```

---

# SECTION 7: MONITORING

## 7.1 Health Checks

```bash
# Test API health
curl http://localhost:8000/health
# Expected: {"status": "healthy"}

# Test database connection
curl http://localhost:8000/db-health
# Expected: {"connected": true}
```

## 7.2 Logs

```bash
# View backend logs
tail -f logs/api.log

# View database queries
SELECT * FROM pg_stat_statements ORDER BY query_start DESC LIMIT 10;

# Check error rates
SELECT COUNT(*) FROM audit_log WHERE status = 'error' AND created_at > NOW() - INTERVAL '1 hour';
```

## 7.3 Metrics to Track

```sql
-- Workspace creation rate
SELECT DATE(created_at), COUNT(*) FROM workspaces GROUP BY DATE(created_at);

-- Member invitations
SELECT COUNT(*) FROM workspace_members WHERE joined_at > NOW() - INTERVAL '24 hours';

-- Activity volume
SELECT COUNT(*) FROM contact_activity_log WHERE created_at > NOW() - INTERVAL '24 hours';

-- Error rate
SELECT error_message, COUNT(*) FROM audit_log WHERE status = 'error' GROUP BY error_message;
```

---

# SECTION 8: TROUBLESHOOTING

## 8.1 Database Issues

**Problem:** "relation \"workspaces\" does not exist"
**Solution:** Run migration again
```sql
DROP TABLE IF EXISTS workspaces CASCADE;
-- Re-run migration
```

**Problem:** RLS policy blocking queries
**Solution:** Check policies
```sql
SELECT * FROM pg_policies WHERE tablename = 'workspaces';
-- Temporarily disable for testing: ALTER TABLE workspaces DISABLE ROW LEVEL SECURITY;
```

## 8.2 API Issues

**Problem:** 401 Unauthorized
**Solution:** Check JWT token
```python
from api.auth import decode_token
token = "your_token"
print(decode_token(token))  # Should show user_id
```

**Problem:** CORS error
**Solution:** Update CORS in main.py
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 8.3 Frontend Issues

**Problem:** "Cannot find module '@/workspaces'"
**Solution:** Check import path
```typescript
// Correct:
import { WorkspaceService } from '@/api/workspaces';
// Wrong:
import { WorkspaceService } from '@workspaces';
```

**Problem:** GraphQL query returns null
**Solution:** Check authentication
```typescript
const { data, error, loading } = useQuery(GET_MY_WORKSPACES);
if (error) console.error(error);
```

---

# SECTION 9: SUCCESS CRITERIA

Phase 7.1 is complete when:

✅ All 6 tables created in Supabase  
✅ All API endpoints responding (200 status)  
✅ All unit tests passing (10/10)  
✅ Frontend pages loading without errors  
✅ Can create workspace successfully  
✅ Can invite members successfully  
✅ Activity log recording events  
✅ Notifications being created  
✅ No database errors in logs  
✅ No API errors in console  

---

# SECTION 10: ROLLBACK PROCEDURE

If something goes wrong:

```bash
# 1. Revert git changes
git revert <commit_hash>
git push origin main

# 2. Drop tables (if needed)
DROP TABLE IF EXISTS (
    workspaces,
    workspace_members,
    shared_contact_lists,
    contact_activity_log,
    notifications,
    audit_log
) CASCADE;

# 3. Redeploy backend/frontend
# git push heroku main
# vercel deploy --prod
```

---

# NEXT STEPS

✅ Phase 7.1 Complete: Team Collaboration  
⏳ Phase 7.2: WebSockets (Real-time sync)  
⏳ Phase 8: Advanced ML (GNN recommendations)  
⏳ Phase 9: Enterprise Security (GDPR/SSO)  
⏳ Phase 10: Mobile Apps (iOS/Android)  

**Timeline:** Each phase 1-2 weeks

---

**🎉 YOU'RE READY TO DEPLOY!**

**Total implementation time: 2-3 hours**
