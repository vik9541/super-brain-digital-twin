# 📋 MEGA TECHNICAL SPECIFICATION
## Contacts v2.0: From MVP to $10M ARR

**Document:** MEGA_TZ_CONTACTS_v2.0_SCALE  
**Version:** 1.0 COMPLETE  
**Date:** 12 Dec 2025  
**Status:** 🚀 READY TO BUILD  
**Total Epic:** 12 phases, 50+ features, 15,000+ LOC expected  

---

## 💣 EXECUTIVE SUMMARY

This is the **COMPLETE TZ** for taking Contacts v2.0 from current state (Phase 1-6 complete) to $10M ARR enterprise product.

**What you'll build:**
- 4 more Phases (7-10) of features
- Full enterprise platform (RBAC, SSO, GDPR)
- Mobile apps (iOS + Android production)
- Global scaling (multi-region, CDN)
- AI/ML optimization
- Sales infrastructure

**Investment needed:** $250K-500K (pre-seed)  
**Timeline:** 12 months  
**Expected outcome:** $3.3M ARR + Series A ready  

---

# PHASE 7: TEAM COLLABORATION & ENTERPRISE BASICS
## Timeline: Weeks 1-4

### 7.1: Multi-User Workspaces

**Description:** Support multiple users collaborating on shared contacts

**Requirements:**

```sql
-- New tables
CREATE TABLE workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    owner_id UUID NOT NULL REFERENCES auth.users,
    plan TEXT DEFAULT 'pro',  -- free, pro, enterprise
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(owner_id, name)
);

CREATE TABLE workspace_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces,
    user_id UUID NOT NULL REFERENCES auth.users,
    role TEXT NOT NULL,  -- owner, admin, member, viewer
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(workspace_id, user_id)
);

CREATE TABLE shared_contact_lists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    contact_ids UUID[] DEFAULT '{}',
    created_by UUID NOT NULL REFERENCES auth.users,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE contact_activity_log (
    id BIGSERIAL PRIMARY KEY,
    workspace_id UUID NOT NULL REFERENCES workspaces,
    contact_id UUID NOT NULL REFERENCES apple_contacts,
    user_id UUID NOT NULL REFERENCES auth.users,
    action TEXT NOT NULL,  -- viewed, contacted, added_note, etc
    details JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_workspaces_owner ON workspaces(owner_id);
CREATE INDEX idx_workspace_members_user ON workspace_members(user_id);
CREATE INDEX idx_contact_activity_workspace ON contact_activity_log(workspace_id, created_at DESC);
```

**Backend Changes:**

```python
# api/workspaces/models.py
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class WorkspaceRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"

class WorkspaceCreate(BaseModel):
    name: str
    plan: str = "pro"

class WorkspaceMember(BaseModel):
    user_id: str
    role: WorkspaceRole
    email: str

class Workspace(BaseModel):
    id: str
    name: str
    owner_id: str
    plan: str
    members: List[WorkspaceMember]
    created_at: str

# api/workspaces/service.py
class WorkspaceService:
    def __init__(self, supabase, auth):
        self.db = supabase
        self.auth = auth
    
    async def create_workspace(self, user_id: str, name: str, plan: str) -> Workspace:
        """Create new workspace for user"""
        workspace = await self.db.table('workspaces').insert({
            'name': name,
            'owner_id': user_id,
            'plan': plan
        }).execute()
        return workspace.data[0]
    
    async def add_member(self, workspace_id: str, email: str, role: WorkspaceRole) -> WorkspaceMember:
        """Invite user to workspace"""
        # 1. Find user by email
        user = await self.auth.get_user_by_email(email)
        
        # 2. Add to workspace_members table
        member = await self.db.table('workspace_members').insert({
            'workspace_id': workspace_id,
            'user_id': user.id,
            'role': role
        }).execute()
        
        # 3. Send invite email
        await self._send_invite_email(email, workspace_id)
        
        return member.data[0]
    
    async def get_workspace_contacts(self, workspace_id: str, user_id: str) -> List[Dict]:
        """Get contacts visible to user in workspace"""
        # Check user has access
        member = await self.db.table('workspace_members')\
            .select('role').eq('workspace_id', workspace_id)\
            .eq('user_id', user_id).execute()
        
        if not member.data:
            raise PermissionError("User not in workspace")
        
        # Get all contacts in workspace
        contacts = await self.db.table('apple_contacts')\
            .select('*').eq('workspace_id', workspace_id).execute()
        
        return contacts.data
```

**GraphQL Changes:**

```graphql
# Add to schema
type Workspace {
    id: UUID!
    name: String!
    plan: String!
    members: [WorkspaceMember!]!
    createdAt: DateTime!
}

type WorkspaceMember {
    userId: UUID!
    email: String!
    role: WorkspaceRole!
    joinedAt: DateTime!
}

enum WorkspaceRole {
    OWNER
    ADMIN
    MEMBER
    VIEWER
}

type Query {
    myWorkspaces: [Workspace!]!
    workspace(id: UUID!): Workspace
    workspaceContacts(workspaceId: UUID!): [Contact!]!
}

type Mutation {
    createWorkspace(name: String!, plan: String!): Workspace!
    addWorkspaceMember(workspaceId: UUID!, email: String!, role: WorkspaceRole!): WorkspaceMember!
    removeWorkspaceMember(workspaceId: UUID!, userId: UUID!): Boolean!
}
```

**Frontend Changes:**

```typescript
// web/app/dashboard/workspaces/page.tsx
import { useQuery } from '@apollo/client';
import { GET_MY_WORKSPACES } from '@/lib/queries';

export default function WorkspacesPage() {
    const { data, loading } = useQuery(GET_MY_WORKSPACES);
    
    if (loading) return <div>Loading...</div>;
    
    return (
        <div className="p-8">
            <h1 className="text-3xl font-bold mb-6">My Workspaces</h1>
            
            {data?.myWorkspaces.map(ws => (
                <div key={ws.id} className="card mb-4 p-6">
                    <h2 className="text-xl font-bold">{ws.name}</h2>
                    <p className="text-gray-600">Plan: {ws.plan}</p>
                    <p className="text-gray-600">{ws.members.length} members</p>
                    <button className="btn btn-primary mt-4">
                        Open Workspace
                    </button>
                </div>
            ))}
        </div>
    );
}

// web/app/dashboard/workspaces/[id]/page.tsx
export default function WorkspaceDetail({ params }) {
    const [inviteEmail, setInviteEmail] = useState('');
    const { data: workspace } = useQuery(GET_WORKSPACE, {
        variables: { id: params.id }
    });
    
    return (
        <div className="p-8">
            <h1>{workspace?.name}</h1>
            
            <div className="mt-8">
                <h2 className="text-xl font-bold mb-4">Members</h2>
                {workspace?.members.map(m => (
                    <div key={m.userId} className="flex justify-between items-center py-2">
                        <span>{m.email} ({m.role})</span>
                        <button className="text-red-500">Remove</button>
                    </div>
                ))}
            </div>
            
            <div className="mt-8">
                <h2 className="text-xl font-bold mb-4">Invite Member</h2>
                <input
                    type="email"
                    value={inviteEmail}
                    onChange={(e) => setInviteEmail(e.target.value)}
                    placeholder="email@example.com"
                    className="input"
                />
                <select className="input ml-2">
                    <option>Member</option>
                    <option>Admin</option>
                    <option>Viewer</option>
                </select>
                <button className="btn btn-primary ml-2">Invite</button>
            </div>
        </div>
    );
}
```

**Testing:**

```python
# tests/test_workspaces.py
import pytest
from api.workspaces.service import WorkspaceService

@pytest.mark.asyncio
async def test_create_workspace(supabase, auth):
    service = WorkspaceService(supabase, auth)
    
    workspace = await service.create_workspace(
        user_id="user123",
        name="Sales Team",
        plan="pro"
    )
    
    assert workspace['name'] == "Sales Team"
    assert workspace['plan'] == "pro"

@pytest.mark.asyncio
async def test_add_member(supabase, auth):
    service = WorkspaceService(supabase, auth)
    
    member = await service.add_member(
        workspace_id="ws123",
        email="john@example.com",
        role="member"
    )
    
    assert member['role'] == "member"
```

**Deliverables:**
- Workspace creation & management
- User invitation system
- RBAC (role-based access)
- Activity logging
- Email notifications

---

### 7.2: Real-Time Sync (WebSockets)

**Description:** Live collaboration - changes sync instantly across team

**Tech Stack:**
- FastAPI WebSocket
- Redis pub/sub
- Socket.IO client (web)

**Implementation:**

```python
# api/realtime/websocket.py
from fastapi import WebSocket, WebSocketDisconnect
from redis import Redis
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}
    
    async def connect(self, workspace_id: str, websocket: WebSocket):
        await websocket.accept()
        if workspace_id not in self.active_connections:
            self.active_connections[workspace_id] = []
        self.active_connections[workspace_id].append(websocket)
    
    async def disconnect(self, workspace_id: str, websocket: WebSocket):
        self.active_connections[workspace_id].remove(websocket)
    
    async def broadcast(self, workspace_id: str, message: dict):
        """Send message to all users in workspace"""
        for connection in self.active_connections.get(workspace_id, []):
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()
redis_client = Redis()

@app.websocket("/ws/workspace/{workspace_id}")
async def websocket_endpoint(websocket: WebSocket, workspace_id: str):
    await manager.connect(workspace_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            
            # Broadcast to all users
            await manager.broadcast(workspace_id, {
                "type": data["type"],
                "payload": data["payload"],
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Persist to DB if needed
            if data["type"] == "contact_update":
                await supabase.table('apple_contacts').update(
                    data["payload"]
                ).eq('id', data["payload"]["id"]).execute()
    except WebSocketDisconnect:
        await manager.disconnect(workspace_id, websocket)
```

**Frontend:**

```typescript
// web/hooks/useWebSocket.ts
import { useEffect, useCallback } from 'react';
import { io } from 'socket.io-client';

export function useWebSocket(workspaceId: string) {
    const socket = io(`ws://localhost:8000/ws/workspace/${workspaceId}`);
    
    useEffect(() => {
        socket.on('connect', () => {
            console.log('Connected to workspace');
        });
        
        socket.on('contact_update', (data) => {
            // Update UI in real-time
            updateContactInUI(data);
        });
        
        return () => socket.disconnect();
    }, [workspaceId]);
    
    return socket;
}

// Usage in component
export default function ContactsPage() {
    const socket = useWebSocket(workspaceId);
    
    const handleContactUpdate = useCallback((contact) => {
        socket.emit('contact_update', contact);
    }, [socket]);
    
    return (
        <div>
            {/* Contact list that updates in real-time */}
        </div>
    );
}
```

---

### 7.3: Activity Feed & Notifications

**Database:**

```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users,
    workspace_id UUID NOT NULL REFERENCES workspaces,
    type VARCHAR(50),  -- contact_shared, member_added, etc
    data JSONB,
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_notifications_user_unread ON notifications(user_id, read, created_at DESC);
```

**Backend:**

```python
class NotificationService:
    async def notify_contact_shared(self, from_user_id: str, to_user_id: str, contact_id: str):
        await self.db.table('notifications').insert({
            'user_id': to_user_id,
            'type': 'contact_shared',
            'data': {
                'from_user': from_user_id,
                'contact_id': contact_id,
                'message': f"{from_user_id} shared a contact with you"
            }
        }).execute()
        
        # Send email
        await self._send_email(to_user_id, 'A contact was shared')
```

---

## PHASE 8: ADVANCED ML & ANALYTICS
## Timeline: Weeks 5-8

### 8.1: Graph Neural Network Recommendations

**Tech:** PyTorch Geometric + Neo4j

```python
# api/ml/gnn_recommender.py
import torch
from torch_geometric.nn import GCNConv
from torch_geometric.data import Data
import numpy as np

class ContactGNNRecommender:
    def __init__(self, embedding_dim=256, num_layers=3):
        self.embedding_dim = embedding_dim
        self.layers = [
            GCNConv(embedding_dim, embedding_dim)
            for _ in range(num_layers)
        ]
    
    async def build_graph(self, workspace_id: str):
        """Build contact graph from connections"""
        # 1. Get all contacts & connections
        contacts = await self.supabase.table('apple_contacts')\
            .select('id').eq('workspace_id', workspace_id).execute()
        
        connections = await self.supabase.table('contact_connections')\
            .select('*').eq('workspace_id', workspace_id).execute()
        
        # 2. Build edge list
        edge_index = []
        for conn in connections.data:
            edge_index.append([conn['contact_id_1'], conn['contact_id_2']])
        
        # 3. Create node features (embeddings)
        embeddings = await self.get_contact_embeddings(workspace_id)
        x = torch.tensor(embeddings, dtype=torch.float)
        
        # 4. Create PyTorch Geometric Data object
        self.graph = Data(
            x=x,
            edge_index=torch.tensor(edge_index).t().contiguous()
        )
    
    async def recommend(self, contact_id: str, k: int = 20) -> List[str]:
        """Recommend contacts using GNN"""
        # 1. Forward pass through GNN
        embeddings = self.layers[0](self.graph.x, self.graph.edge_index)
        for layer in self.layers[1:]:
            embeddings = layer(embeddings, self.graph.edge_index)
        
        # 2. Get target contact embedding
        target_idx = self.contact_id_to_idx[contact_id]
        target_emb = embeddings[target_idx]
        
        # 3. Compute similarity with all contacts
        similarities = torch.cosine_similarity(
            target_emb.unsqueeze(0),
            embeddings
        )
        
        # 4. Get top-k
        top_k_idx = torch.topk(similarities, k + 1)[1]  # +1 to exclude self
        top_k_ids = [self.idx_to_contact_id[i] for i in top_k_idx if i != target_idx]
        
        return top_k_ids[:k]
```

**Expected improvement:** +25% accuracy over basic recommendations

---

### 8.2: Predictive Analytics Dashboard

**Frontend (React):**

```typescript
// web/app/dashboard/analytics/page.tsx
import { LineChart, BarChart, PieChart } from 'recharts';

export default function AnalyticsPage() {
    const { data: stats } = useQuery(GET_WORKSPACE_STATS);
    
    return (
        <div className="p-8">
            <h1 className="text-3xl font-bold mb-8">Analytics</h1>
            
            {/* Key Metrics */}
            <div className="grid grid-cols-4 gap-4 mb-8">
                <Card>
                    <h3>Total Contacts</h3>
                    <p className="text-3xl font-bold">{stats?.total_contacts}</p>
                </Card>
                <Card>
                    <h3>Avg Influence Score</h3>
                    <p className="text-3xl font-bold">{stats?.avg_influence.toFixed(2)}</p>
                </Card>
                <Card>
                    <h3>Communities</h3>
                    <p className="text-3xl font-bold">{stats?.num_communities}</p>
                </Card>
                <Card>
                    <h3>Churn Risk</h3>
                    <p className="text-3xl font-bold text-red-600">{stats?.churn_count}</p>
                </Card>
            </div>
            
            {/* Network Growth Over Time */}
            <div className="bg-white p-6 rounded-lg mb-8">
                <h2 className="text-xl font-bold mb-4">Network Growth</h2>
                <LineChart width={800} height={300} data={stats?.growth_timeline}>
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Line type="monotone" dataKey="contacts" stroke="#8884d8" />
                </LineChart>
            </div>
            
            {/* Influence Distribution */}
            <div className="bg-white p-6 rounded-lg">
                <h2 className="text-xl font-bold mb-4">Influence Distribution</h2>
                <PieChart width={400} height={300}>
                    <Pie data={stats?.influence_distribution} />
                </PieChart>
            </div>
        </div>
    );
}
```

---

## PHASE 9: ENTERPRISE COMPLIANCE & SECURITY
## Timeline: Weeks 9-12

### 9.1: GDPR/CCPA Compliance

**Features:**
- Data export (downloadable ZIP)
- Account deletion (7-day delay)
- Audit logs (all actions)
- GDPR request handling

```python
# api/compliance/gdpr.py
class GDPRService:
    async def export_user_data(self, user_id: str, workspace_id: str) -> str:
        """Export all user data in GDPR format"""
        # 1. Get all data
        user = await self.supabase.table('auth.users').select('*').eq('id', user_id).execute()
        contacts = await self.supabase.table('apple_contacts')\
            .select('*').eq('workspace_id', workspace_id).execute()
        activity = await self.supabase.table('contact_activity_log')\
            .select('*').eq('user_id', user_id).execute()
        
        # 2. Create JSON export
        export_data = {
            'user': user.data[0],
            'contacts': contacts.data,
            'activity_log': activity.data,
            'export_date': datetime.utcnow().isoformat()
        }
        
        # 3. Create ZIP file
        import zipfile
        zip_path = f"/tmp/gdpr_export_{user_id}.zip"
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr('user_data.json', json.dumps(export_data, indent=2))
        
        # 4. Upload to S3, return download link
        return await self._upload_to_s3(zip_path)
    
    async def schedule_account_deletion(self, user_id: str, workspace_id: str):
        """Schedule account deletion (7-day delay)"""
        deletion_date = datetime.utcnow() + timedelta(days=7)
        
        await self.supabase.table('deletion_requests').insert({
            'user_id': user_id,
            'workspace_id': workspace_id,
            'deletion_date': deletion_date,
            'status': 'pending'
        }).execute()
        
        # Send email confirmation
        await self._send_cancellation_email(user_id)
```

### 9.2: SSO & SAML Support

```python
# api/auth/sso.py
from python3_saml.binding import saml_binding_http_redirect

class SSOService:
    async def init_saml_auth_request(self, workspace_id: str):
        """Generate SAML AuthnRequest"""
        auth_request = self.saml.create_auth_request()
        return auth_request
    
    async def process_saml_response(self, saml_response: str, workspace_id: str):
        """Process SAML assertion"""
        # 1. Validate SAML response
        auth = self.saml.process_assertion(saml_response)
        
        # 2. Extract user info
        user_email = auth.get_user_email()
        user_name = auth.get_user_name()
        
        # 3. Create/update user
        user = await self._get_or_create_user(user_email, user_name)
        
        # 4. Generate JWT token
        token = self._generate_jwt(user)
        
        return token
```

### 9.3: SOC 2 Type II Readiness

**Audit logging:**
```python
class AuditLogger:
    async def log_action(self, action: str, user_id: str, details: dict):
        await self.supabase.table('audit_logs').insert({
            'action': action,
            'user_id': user_id,
            'details': details,
            'ip_address': get_client_ip(),
            'user_agent': request.headers['user-agent'],
            'timestamp': datetime.utcnow()
        }).execute()
```

---

## PHASE 10: MOBILE APPS (PRODUCTION)
## Timeline: Weeks 13-16

### 10.1: iOS App (SwiftUI)

```swift
// mobile/ios/SuperBrainContacts/Views/ContentView.swift
import SwiftUI

struct ContentView: View {
    @StateObject var viewModel = ContactsViewModel()
    @State var selectedContact: Contact?
    
    var body: some View {
        NavigationSplitView {
            // Sidebar
            List(viewModel.contacts) { contact in
                NavigationLink(value: contact) {
                    VStack(alignment: .leading) {
                        Text(contact.firstName)
                            .font(.headline)
                        Text(contact.organization ?? "")
                            .font(.caption)
                            .foregroundColor(.gray)
                    }
                }
            }
            .searchable(text: $viewModel.searchText)
            .navigationTitle("Contacts")
        } detail: {
            if let contact = viewModel.selectedContact {
                ContactDetailView(contact: contact)
            } else {
                Text("Select a contact")
            }
        }
    }
}

// ViewModel
@MainActor
class ContactsViewModel: ObservableObject {
    @Published var contacts: [Contact] = []
    @Published var searchText = ""
    @Published var selectedContact: Contact?
    
    private let api = ContactsAPI(baseURL: "https://api.yourdomain.com")
    
    func loadContacts() async {
        do {
            let allContacts = try await api.fetchContacts()
            self.contacts = searchText.isEmpty ? allContacts : 
                allContacts.filter { contact in
                    contact.firstName.localizedCaseInsensitiveContains(searchText) ||
                    contact.lastName.localizedCaseInsensitiveContains(searchText)
                }
        } catch {
            print("Failed to load contacts: \(error)")
        }
    }
}
```

### 10.2: Android App (Jetpack Compose)

```kotlin
// mobile/android/app/src/main/java/com/superbrain/contacts/MainActivity.kt
@Composable
fun ContactsScreen(
    viewModel: ContactsViewModel = hiltViewModel()
) {
    val contacts by viewModel.contacts.collectAsState()
    val searchText by viewModel.searchText.collectAsState()
    
    Column(modifier = Modifier.fillMaxSize()) {
        SearchBar(
            query = searchText,
            onQueryChange = { viewModel.updateSearchText(it) }
        )
        
        LazyColumn {
            items(contacts) { contact ->
                ContactItem(
                    contact = contact,
                    onClick = { viewModel.selectContact(contact) }
                )
            }
        }
    }
}

@HiltViewModel
class ContactsViewModel @Inject constructor(
    private val api: ContactsApi
) : ViewModel() {
    private val _contacts = MutableStateFlow<List<Contact>>(emptyList())
    val contacts = _contacts.asStateFlow()
    
    private val _searchText = MutableStateFlow("")
    val searchText = _searchText.asStateFlow()
    
    init {
        loadContacts()
    }
    
    private fun loadContacts() {
        viewModelScope.launch {
            val allContacts = api.getContacts()
            _contacts.value = allContacts
        }
    }
    
    fun updateSearchText(query: String) {
        _searchText.value = query
    }
}
```

---

## PHASE 11: GROWTH & SCALING
## Timeline: Weeks 17-20

### 11.1: Paid Acquisition Channels

**Google Ads:**
- Target: "CRM for personal network", "AI contact management"
- Budget: $5K/month
- Target CAC: $20
- Expected: 250 customers/month

**LinkedIn Ads:**
- Target: Sales leaders, recruiters
- Budget: $10K/month
- Target CAC: $50
- Expected: 200 enterprise trials

### 11.2: Integrations

**Zapier Integration:**
```javascript
// Auto-sync contacts from Gmail, Salesforce, HubSpot
const triggerNewContact = async (contact) => {
    await contactsAPI.createContact(contact);
};
```

**Slack Bot:**
```python
# /who-to-call: Get AI recommendation
@app.command("/who-to-call")
async def who_to_call(ack, command, client):
    ack()
    
    user_id = command['user_id']
    contacts = await api.get_recommended_contacts(user_id, limit=5)
    
    message = "\ud83e\udd16 Here are people you should reach out to:\n"
    for i, contact in enumerate(contacts, 1):
        message += f"{i}. {contact['first_name']} ({contact['influence_score']:.2f})\n"
    
    await client.chat_postMessage(
        channel=command['channel_id'],
        text=message
    )
```

---

## PHASE 12: ANALYTICS & OPTIMIZATION
## Timeline: Weeks 21-24

### 12.1: Usage Analytics

```python
# api/analytics/service.py
class AnalyticsService:
    async def track_event(self, event: str, user_id: str, data: dict):
        await self.supabase.table('events').insert({
            'event': event,
            'user_id': user_id,
            'data': data,
            'timestamp': datetime.utcnow()
        }).execute()
    
    async def get_daily_active_users(self, days: int = 30) -> List[dict]:
        """Get DAU trend"""
        query = """
        SELECT DATE(created_at) as date, COUNT(DISTINCT user_id) as dau
        FROM events
        WHERE created_at > NOW() - INTERVAL '{days} days'
        GROUP BY DATE(created_at)
        ORDER BY date
        """
        return await self.supabase.query(query)
    
    async def get_retention_cohort(self):
        """Calculate N-day retention"""
        # Day 1: 100%
        # Day 7: X%
        # Day 30: Y%
        # Day 90: Z%
        pass
```

---

## 📚 FULL FEATURE CHECKLIST

```
🟆 PHASE 7: Team Collaboration
  ✅ Workspaces
  ✅ Multi-user support
  ✅ RBAC (roles)
  ✅ Real-time WebSockets
  ✅ Activity feed
  ✅ Notifications (in-app + email)

🟆 PHASE 8: Advanced ML
  ✅ Graph Neural Networks
  ✅ 25% better recommendations
  ✅ Analytics dashboard
  ✅ Predictive insights

🟆 PHASE 9: Enterprise Security
  ✅ GDPR/CCPA compliance
  ✅ Data export
  ✅ Account deletion
  ✅ SSO/SAML
  ✅ SOC 2 Type II ready
  ✅ Audit logging

🟆 PHASE 10: Mobile Production
  ✅ iOS app (SwiftUI)
  ✅ Android app (Compose)
  ✅ Offline sync
  ✅ Push notifications

🟆 PHASE 11: Growth
  ✅ Paid acquisition
  ✅ Zapier integration
  ✅ Slack bot
  ✅ API marketplace

🟆 PHASE 12: Optimization
  ✅ Analytics dashboard
  ✅ Cohort analysis
  ✅ Performance optimization
  ✅ A/B testing
```

---

## 📊 DEVELOPMENT TIMELINE

```
Week 1-4: Phase 7 (Team Collab)
  1st sprint: Workspaces + RBAC
  2nd sprint: WebSockets + real-time
  3rd sprint: Activity + notifications

Week 5-8: Phase 8 (Advanced ML)
  1st sprint: GNN setup + training
  2nd sprint: Integration + deployment
  3rd sprint: Analytics dashboard

Week 9-12: Phase 9 (Enterprise)
  1st sprint: GDPR/CCPA
  2nd sprint: SSO/SAML
  3rd sprint: SOC 2 audit prep

Week 13-16: Phase 10 (Mobile)
  iOS + Android simultaneous development
  App Store + Play Store submission

Week 17-20: Phase 11 (Growth)
  Ad campaigns
  Integrations
  Marketing automation

Week 21-24: Phase 12 (Analytics)
  Dashboard
  Reports
  Optimization
```

---

## 💰 BUDGET & TEAM

**Team needed:**
- 1 Backend Engineer (GNN, ML)
- 1 iOS Developer (SwiftUI)
- 1 Android Developer (Kotlin)
- 1 Frontend Engineer (React)
- 1 Product Manager
- 1 Growth Lead
- 1 DevOps Engineer

**Monthly burn:** $80-100K  
**Expected revenue (Month 12):** $300K  
**Profitability:** Month 6+

---

## ✅ SUCCESS METRICS

```
Month 3: 50K users, $50K MRR, NPS 50
Month 6: 200K users, $100K MRR, NPS 60, Series A ready
Month 12: 500K users, $300K MRR, NPS 70, $3.3M ARR
```

---

**Status: 🚀 READY TO BUILD**

**Questions? Start with Phase 7!**
