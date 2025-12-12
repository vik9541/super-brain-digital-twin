"""
Microsoft Graph Contacts Sync Module

Syncs enriched contacts between Supabase and Microsoft 365 (Outlook contacts).
"""

import os
import asyncio
from typing import List, Dict, Optional
from datetime import datetime
import msal
import aiohttp
from supabase import create_client, Client

class MSGraphContactsSync:
    """Sync enriched contacts between Supabase and Microsoft Graph"""
    
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        tenant_id: Optional[str] = None,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None
    ):
        """
        Initialize MS Graph and Supabase clients
        
        Args:
            client_id: Azure AD app client ID (or from MS_CLIENT_ID env)
            client_secret: Azure AD app client secret (or from MS_CLIENT_SECRET env)
            tenant_id: Azure AD tenant ID (or from MS_TENANT_ID env)
            supabase_url: Supabase URL (or from SUPABASE_URL env)
            supabase_key: Supabase anon key (or from SUPABASE_KEY env)
        """
        self.client_id = client_id or os.getenv('MS_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('MS_CLIENT_SECRET')
        self.tenant_id = tenant_id or os.getenv('MS_TENANT_ID')
        
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.scope = ["https://graph.microsoft.com/.default"]
        
        self.msal_app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=self.authority,
            client_credential=self.client_secret
        )
        
        self.supabase: Client = create_client(
            supabase_url or os.getenv('SUPABASE_URL'),
            supabase_key or os.getenv('SUPABASE_KEY')
        )
        
        self.graph_endpoint = "https://graph.microsoft.com/v1.0"
    
    def _get_access_token(self) -> str:
        """Get Microsoft Graph API access token"""
        result = self.msal_app.acquire_token_for_client(scopes=self.scope)
        
        if "access_token" in result:
            return result["access_token"]
        else:
            raise Exception(f"Failed to acquire token: {result.get('error_description')}")
    
    async def push_contacts(
        self,
        user_id: str,
        min_influence_score: float = 0.0,
        limit: int = 100
    ) -> Dict:
        """
        Push enriched contacts from Supabase to MS Graph (user's Outlook contacts)
        
        Args:
            user_id: Microsoft user ID or UPN (email)
            min_influence_score: Minimum influence score threshold
            limit: Maximum number of contacts to sync
            
        Returns:
            Dict with success/failure counts and details
        """
        # Fetch contacts from Supabase
        response = self.supabase.table('contacts') \
            .select('*') \
            .gte('influence_score', min_influence_score) \
            .order('influence_score', desc=True) \
            .limit(limit) \
            .execute()
        
        contacts = response.data
        
        results = {
            'total': len(contacts),
            'created': 0,
            'updated': 0,
            'errors': [],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        access_token = self._get_access_token()
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession(headers=headers) as session:
            for contact in contacts:
                try:
                    graph_contact = self._map_contact_to_graph(contact)
                    
                    # Check if contact exists by email
                    email = contact.get('email')
                    if email:
                        # Search for existing contact
                        search_url = f"{self.graph_endpoint}/users/{user_id}/contacts"
                        search_params = {'$filter': f"emailAddresses/any(e:e/address eq '{email}')"}
                        
                        async with session.get(search_url, params=search_params) as resp:
                            if resp.status == 200:
                                data = await resp.json()
                                
                                if data.get('value'):
                                    # Update existing contact
                                    existing_id = data['value'][0]['id']
                                    update_url = f"{self.graph_endpoint}/users/{user_id}/contacts/{existing_id}"
                                    
                                    async with session.patch(update_url, json=graph_contact) as update_resp:
                                        if update_resp.status in [200, 204]:
                                            results['updated'] += 1
                                        else:
                                            error_text = await update_resp.text()
                                            raise Exception(f"Update failed: {error_text}")
                                else:
                                    # Create new contact
                                    create_url = f"{self.graph_endpoint}/users/{user_id}/contacts"
                                    async with session.post(create_url, json=graph_contact) as create_resp:
                                        if create_resp.status == 201:
                                            results['created'] += 1
                                        else:
                                            error_text = await create_resp.text()
                                            raise Exception(f"Create failed: {error_text}")
                    else:
                        # No email, create new contact
                        create_url = f"{self.graph_endpoint}/users/{user_id}/contacts"
                        async with session.post(create_url, json=graph_contact) as create_resp:
                            if create_resp.status == 201:
                                results['created'] += 1
                            else:
                                error_text = await create_resp.text()
                                raise Exception(f"Create failed: {error_text}")
                                
                except Exception as e:
                    results['errors'].append({
                        'contact_id': contact.get('id'),
                        'email': contact.get('email'),
                        'error': str(e)
                    })
        
        return results
    
    async def pull_contacts(self, user_id: str) -> Dict:
        """
        Pull contacts from MS Graph to Supabase (for enrichment)
        
        Args:
            user_id: Microsoft user ID or UPN (email)
            
        Returns:
            Dict with import counts and details
        """
        access_token = self._get_access_token()
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        results = {
            'total': 0,
            'imported': 0,
            'skipped': 0,
            'errors': [],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        async with aiohttp.ClientSession(headers=headers) as session:
            # Fetch all contacts from Graph
            contacts_url = f"{self.graph_endpoint}/users/{user_id}/contacts"
            
            async with session.get(contacts_url) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise Exception(f"Failed to fetch contacts: {error_text}")
                
                data = await resp.json()
                graph_contacts = data.get('value', [])
                results['total'] = len(graph_contacts)
                
                # Import to Supabase
                for graph_contact in graph_contacts:
                    try:
                        supabase_contact = self._map_graph_to_contact(graph_contact)
                        
                        # Check if already exists by email
                        email = supabase_contact.get('email')
                        if email:
                            existing = self.supabase.table('contacts') \
                                .select('id') \
                                .eq('email', email) \
                                .execute()
                            
                            if existing.data:
                                # Skip if already exists
                                results['skipped'] += 1
                                continue
                        
                        # Insert new contact
                        self.supabase.table('contacts').insert(supabase_contact).execute()
                        results['imported'] += 1
                        
                    except Exception as e:
                        results['errors'].append({
                            'graph_id': graph_contact.get('id'),
                            'email': graph_contact.get('emailAddresses', [{}])[0].get('address'),
                            'error': str(e)
                        })
        
        return results
    
    def _map_contact_to_graph(self, contact: Dict) -> Dict:
        """
        Map Supabase contact to MS Graph Contact format
        
        Args:
            contact: Contact dict from Supabase
            
        Returns:
            Dict with MS Graph Contact fields
        """
        graph_contact = {
            'givenName': contact.get('first_name', ''),
            'surname': contact.get('last_name', ''),
            'emailAddresses': [],
            'businessPhones': []
        }
        
        # Email
        if contact.get('email'):
            graph_contact['emailAddresses'].append({
                'address': contact['email'],
                'name': f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip()
            })
        
        # Organization
        if contact.get('organization'):
            graph_contact['companyName'] = contact['organization']
        
        # Custom extension (for enriched data)
        # Note: Requires schema extension setup in Azure AD
        if contact.get('influence_score') is not None or contact.get('community_id') is not None:
            graph_contact['extensions'] = [{
                'influenceScore': contact.get('influence_score'),
                'communityId': contact.get('community_id'),
                'supabaseId': str(contact.get('id'))
            }]
        
        return graph_contact
    
    def _map_graph_to_contact(self, graph_contact: Dict) -> Dict:
        """
        Map MS Graph Contact to Supabase contact format
        
        Args:
            graph_contact: Contact dict from MS Graph
            
        Returns:
            Dict with Supabase contact fields
        """
        email_addresses = graph_contact.get('emailAddresses', [])
        email = email_addresses[0]['address'] if email_addresses else None
        
        return {
            'first_name': graph_contact.get('givenName'),
            'last_name': graph_contact.get('surname'),
            'email': email,
            'organization': graph_contact.get('companyName'),
            'source': 'ms_graph',
            'ms_graph_id': graph_contact.get('id')
        }


def sync_ms_graph_job(user_id: str, min_score: float = 0.0, limit: int = 100):
    """
    Scheduled job to sync contacts to MS Graph
    
    Usage with APScheduler:
        from apscheduler.decorators import scheduled_job
        
        @scheduled_job('cron', hour=3, minute=20)
        def nightly_msgraph_sync():
            return sync_ms_graph_job(user_id="admin@company.com")
    """
    syncer = MSGraphContactsSync()
    results = asyncio.run(syncer.push_contacts(user_id, min_score, limit))
    
    print(f"[{results['timestamp']}] MS Graph Contacts Sync:")
    print(f"  Total: {results['total']}")
    print(f"  Created: {results['created']}")
    print(f"  Updated: {results['updated']}")
    print(f"  Errors: {len(results['errors'])}")
    
    if results['errors']:
        for error in results['errors'][:5]:  # Show first 5 errors
            print(f"    - {error}")
    
    return results
