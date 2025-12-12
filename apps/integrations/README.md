# Enterprise Integrations

Bidirectional sync modules for enriched contact data between Supabase and enterprise systems.

## Modules

### Salesforce Sync (`salesforce_sync.py`)

Push influencer contacts and community data from Supabase to Salesforce CRM.

#### Features
- ✅ Push top influencers by influence score
- ✅ Push entire communities by community ID
- ✅ Automatic create/update detection by email
- ✅ Custom field mapping (requires Salesforce schema extensions)

#### Configuration

Required environment variables:
```bash
SF_USERNAME=your-salesforce-username
SF_PASSWORD=your-salesforce-password
SF_SECURITY_TOKEN=your-security-token
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
```

#### Usage

```python
from apps.integrations.salesforce_sync import SalesforceContactsSync

# Initialize
syncer = SalesforceContactsSync()

# Push top 100 influencers with score >= 0.5
results = syncer.push_influencers(min_influence_score=0.5, limit=100)

# Push entire community
results = syncer.push_community(community_id=42)

# Results structure:
# {
#   'total': 100,
#   'created': 45,
#   'updated': 55,
#   'errors': [],
#   'timestamp': '2024-12-11T03:00:00Z'
# }
```

#### Salesforce Schema

Requires custom fields in Salesforce Contact object:
- `Influence_Score__c` (Number, 2 decimals)
- `Community_ID__c` (Number)
- `Supabase_ID__c` (Text, 36 chars)
- `Community_1__c`, `Community_2__c`, etc. (Checkbox) - for community markers

### MS Graph Sync (`ms_graph_sync.py`)

Bidirectional sync between Supabase and Microsoft 365 Outlook contacts.

#### Features
- ✅ Push enriched contacts to Outlook
- ✅ Pull contacts from Outlook for enrichment
- ✅ Async operations with aiohttp
- ✅ OAuth2 authentication via Azure AD

#### Configuration

Required environment variables:
```bash
MS_CLIENT_ID=your-azure-app-client-id
MS_CLIENT_SECRET=your-azure-app-secret
MS_TENANT_ID=your-azure-tenant-id
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
```

#### Azure AD App Setup

1. Register app in Azure Portal
2. Grant permissions: `Contacts.ReadWrite` (Application)
3. Generate client secret
4. Admin consent for tenant

#### Usage

```python
import asyncio
from apps.integrations.ms_graph_sync import MSGraphContactsSync

# Initialize
syncer = MSGraphContactsSync()

# Push contacts to user's Outlook
results = asyncio.run(
    syncer.push_contacts(
        user_id="admin@company.com",
        min_influence_score=0.5,
        limit=100
    )
)

# Pull contacts from Outlook for enrichment
results = asyncio.run(
    syncer.pull_contacts(user_id="admin@company.com")
)

# Results structure same as Salesforce
```

## Scheduled Jobs

Integrate with APScheduler for automated nightly syncs:

```python
from apscheduler.decorators import scheduled_job
from apps.integrations.salesforce_sync import sync_influencers_job
from apps.integrations.ms_graph_sync import sync_ms_graph_job

# Salesforce sync at 03:00 daily
@scheduled_job('cron', hour=3, minute=0)
def nightly_salesforce_sync():
    return sync_influencers_job(min_score=0.5, limit=100)

# MS Graph sync at 03:20 daily
@scheduled_job('cron', hour=3, minute=20)
def nightly_msgraph_sync():
    return sync_ms_graph_job(user_id="admin@company.com", min_score=0.5, limit=100)
```

## Dependencies

```bash
pip install simple-salesforce msal aiohttp supabase
```

Or from `requirements.txt`:
```
simple-salesforce>=1.12.6
msal>=1.26.0
aiohttp>=3.9.1
supabase>=2.3.0
```

## Error Handling

Both modules return detailed error reports:

```python
results = syncer.push_influencers(min_influence_score=0.5)

if results['errors']:
    print(f"Failed to sync {len(results['errors'])} contacts:")
    for error in results['errors']:
        print(f"  - {error['email']}: {error['error']}")
```

## Field Mapping

### Supabase → Salesforce

| Supabase Field     | Salesforce Field      | Type          |
|--------------------|-----------------------|---------------|
| `first_name`       | `FirstName`           | Standard      |
| `last_name`        | `LastName`            | Standard      |
| `email`            | `Email`               | Standard      |
| `organization`     | `AccountName`         | Standard      |
| `influence_score`  | `Influence_Score__c`  | Custom Number |
| `community_id`     | `Community_ID__c`     | Custom Number |
| `id` (UUID)        | `Supabase_ID__c`      | Custom Text   |

### Supabase → MS Graph

| Supabase Field     | Graph Field              | Type            |
|--------------------|--------------------------|-----------------|
| `first_name`       | `givenName`              | Standard        |
| `last_name`        | `surname`                | Standard        |
| `email`            | `emailAddresses[0]`      | Standard        |
| `organization`     | `companyName`            | Standard        |
| `influence_score`  | `extensions.influenceScore` | Custom       |
| `community_id`     | `extensions.communityId` | Custom          |

## Security Considerations

- ⚠️ Never commit credentials to Git
- ✅ Use `.env` files with `.gitignore`
- ✅ Rotate Salesforce security tokens regularly
- ✅ Use Azure Key Vault for MS Graph secrets in production
- ✅ Enable API rate limiting in both platforms

## License

MIT

## Support

For issues: https://github.com/vik9541/super-brain-digital-twin/issues
