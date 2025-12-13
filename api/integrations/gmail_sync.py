"""
Gmail Integration Module - Phase 9 Day 6-7

Auto-enrichment of contacts from Gmail.

Features:
- OAuth 2.0 with Gmail API
- Extract contacts from emails
- Track email interactions (sent/received)
- Periodic sync (every 5 minutes)
- Rate limit: 1M queries/day

Author: Super Brain Team
Created: 2025-12-13
"""

import asyncio
import base64
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from email.utils import parseaddr

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from supabase import Client

logger = logging.getLogger(__name__)


class GmailSyncManager:
    """
    Gmail Sync Manager for contact auto-enrichment
    
    Flow:
    1. User authorizes via OAuth 2.0
    2. Fetch recent emails (last 500)
    3. Extract contact emails from To/From/Cc
    4. Enrich existing contacts with email frequency/recency
    5. Track interactions (sent/received)
    
    Example:
        >>> gmail = GmailSyncManager(supabase_client)
        >>> auth_url = await gmail.get_auth_url(user_id)
        >>> # User authorizes, callback with code
        >>> await gmail.handle_oauth_callback(code, user_id)
        >>> await gmail.sync_contacts_and_interactions(user_id, workspace_id)
    """
    
    def __init__(self, supabase: Client):
        self.supabase = supabase
        
        # OAuth 2.0 config
        self.client_secrets_file = "credentials/gmail_credentials.json"
        self.scopes = ['https://www.googleapis.com/auth/gmail.readonly']
        self.redirect_uri = os.getenv("GMAIL_OAUTH_REDIRECT_URI", "http://localhost:8001/api/gmail/oauth-callback")
        
        logger.info("✅ Gmail Sync Manager initialized")
    
    # ========== OAuth 2.0 Flow ==========
    
    async def get_auth_url(self, user_id: str) -> str:
        """
        Get Gmail OAuth authorization URL
        
        Returns:
            Authorization URL for user to visit
        """
        try:
            flow = Flow.from_client_secrets_file(
                self.client_secrets_file,
                scopes=self.scopes,
                redirect_uri=self.redirect_uri
            )
            
            auth_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                state=user_id  # Pass user_id in state
            )
            
            logger.info(f"Generated OAuth URL for user {user_id}")
            return auth_url
        
        except Exception as e:
            logger.error(f"Failed to generate OAuth URL: {e}")
            raise
    
    async def handle_oauth_callback(self, code: str, user_id: str) -> bool:
        """
        Handle OAuth callback and store credentials
        
        Args:
            code: Authorization code from OAuth callback
            user_id: User ID
        
        Returns:
            True if successful
        """
        try:
            flow = Flow.from_client_secrets_file(
                self.client_secrets_file,
                scopes=self.scopes,
                redirect_uri=self.redirect_uri
            )
            
            flow.fetch_token(code=code)
            credentials = flow.credentials
            
            # Store credentials in database
            self.supabase.table("gmail_sync").upsert({
                "user_id": user_id,
                "access_token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_expiry": credentials.expiry.isoformat() if credentials.expiry else None,
                "enabled": True,
                "last_sync_at": None,
                "updated_at": datetime.utcnow().isoformat()
            }, on_conflict="user_id").execute()
            
            logger.info(f"✅ Gmail OAuth completed for user {user_id}")
            return True
        
        except Exception as e:
            logger.error(f"OAuth callback failed: {e}")
            return False
    
    # ========== Gmail API Integration ==========
    
    def _get_gmail_service(self, user_id: str):
        """Get authenticated Gmail API service"""
        # Get credentials from database
        sync_data = self.supabase.table("gmail_sync").select("*").eq("user_id", user_id).execute()
        
        if not sync_data.data:
            raise Exception("Gmail not connected for this user")
        
        creds_data = sync_data.data[0]
        
        credentials = Credentials(
            token=creds_data["access_token"],
            refresh_token=creds_data["refresh_token"],
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.getenv("GMAIL_CLIENT_ID"),
            client_secret=os.getenv("GMAIL_CLIENT_SECRET")
        )
        
        service = build('gmail', 'v1', credentials=credentials)
        return service
    
    async def sync_contacts_and_interactions(
        self, 
        user_id: str, 
        workspace_id: str,
        max_emails: int = 500
    ) -> Dict:
        """
        Sync contacts and interactions from Gmail
        
        Args:
            user_id: User ID
            workspace_id: Workspace ID
            max_emails: Max emails to fetch (default: 500)
        
        Returns:
            {
                'contacts_enriched': int,
                'interactions_tracked': int,
                'emails_processed': int
            }
        """
        try:
            logger.info(f"Starting Gmail sync for user {user_id}, workspace {workspace_id}")
            
            service = self._get_gmail_service(user_id)
            
            # Fetch recent emails
            results = service.users().messages().list(
                userId='me',
                maxResults=max_emails,
                q='in:sent OR in:inbox'  # Sent and received
            ).execute()
            
            messages = results.get('messages', [])
            
            contacts_enriched = 0
            interactions_tracked = 0
            emails_processed = 0
            
            email_contacts = {}  # email -> {name, frequency, last_contact}
            
            for msg in messages:
                try:
                    # Get full message
                    message = service.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format='metadata',
                        metadataHeaders=['From', 'To', 'Cc', 'Date', 'Subject']
                    ).execute()
                    
                    headers = {h['name']: h['value'] for h in message['payload']['headers']}
                    
                    # Extract emails
                    email_list = []
                    for field in ['From', 'To', 'Cc']:
                        if field in headers:
                            emails = self._extract_emails(headers[field])
                            email_list.extend(emails)
                    
                    # Track contacts
                    for email, name in email_list:
                        if email not in email_contacts:
                            email_contacts[email] = {
                                'name': name,
                                'frequency': 0,
                                'last_contact': headers.get('Date')
                            }
                        email_contacts[email]['frequency'] += 1
                    
                    # Track interaction
                    direction = 'sent' if 'From' in headers and 'me' in headers['From'] else 'received'
                    
                    await self._track_interaction(
                        workspace_id=workspace_id,
                        email=email_list[0][0] if email_list else None,
                        interaction_type='email',
                        direction=direction,
                        subject=headers.get('Subject', ''),
                        occurred_at=headers.get('Date')
                    )
                    
                    interactions_tracked += 1
                    emails_processed += 1
                
                except Exception as e:
                    logger.warning(f"Failed to process message {msg['id']}: {e}")
                    continue
            
            # Enrich contacts with email data
            for email, data in email_contacts.items():
                enriched = await self._enrich_contact(
                    workspace_id=workspace_id,
                    email=email,
                    name=data['name'],
                    frequency=data['frequency'],
                    last_contact=data['last_contact']
                )
                if enriched:
                    contacts_enriched += 1
            
            # Update sync timestamp
            self.supabase.table("gmail_sync").update({
                "last_sync_at": datetime.utcnow().isoformat(),
                "last_sync_emails_count": emails_processed
            }).eq("user_id", user_id).execute()
            
            logger.info(f"✅ Gmail sync complete: {emails_processed} emails, {contacts_enriched} contacts, {interactions_tracked} interactions")
            
            return {
                "contacts_enriched": contacts_enriched,
                "interactions_tracked": interactions_tracked,
                "emails_processed": emails_processed
            }
        
        except Exception as e:
            logger.error(f"Gmail sync failed: {e}", exc_info=True)
            raise
    
    def _extract_emails(self, email_string: str) -> List[tuple]:
        """
        Extract emails from header string
        
        Returns:
            [(email, name), ...]
        """
        emails = []
        for part in email_string.split(','):
            name, email = parseaddr(part.strip())
            if email and '@' in email:
                emails.append((email.lower(), name or email.split('@')[0]))
        return emails
    
    async def _enrich_contact(
        self,
        workspace_id: str,
        email: str,
        name: str,
        frequency: int,
        last_contact: str
    ) -> bool:
        """Enrich existing contact with Gmail data"""
        try:
            # Find contact by email
            contact = self.supabase.table("contacts").select("*").eq("workspace_id", workspace_id).eq("email", email).execute()
            
            if contact.data:
                # Update contact with enrichment data
                self.supabase.table("contacts").update({
                    "email_frequency": frequency,
                    "last_email_at": last_contact,
                    "enriched_from_gmail": True
                }).eq("id", contact.data[0]["id"]).execute()
                
                return True
            
            return False
        
        except Exception as e:
            logger.warning(f"Failed to enrich contact {email}: {e}")
            return False
    
    async def _track_interaction(
        self,
        workspace_id: str,
        email: Optional[str],
        interaction_type: str,
        direction: str,
        subject: str,
        occurred_at: str
    ):
        """Track email interaction"""
        try:
            # Find contact
            contact = None
            if email:
                contact_data = self.supabase.table("contacts").select("id").eq("workspace_id", workspace_id).eq("email", email).execute()
                contact = contact_data.data[0] if contact_data.data else None
            
            if contact:
                # Insert interaction
                self.supabase.table("email_interactions").insert({
                    "workspace_id": workspace_id,
                    "contact_id": contact["id"],
                    "interaction_type": interaction_type,
                    "direction": direction,
                    "subject": subject,
                    "occurred_at": occurred_at,
                    "created_at": datetime.utcnow().isoformat()
                }).execute()
        
        except Exception as e:
            logger.warning(f"Failed to track interaction: {e}")
    
    async def enrich_contact(self, contact_id: str) -> Dict:
        """
        Get Gmail enrichment data for contact
        
        Returns:
            {
                'email_frequency': int,
                'last_email_at': str,
                'recent_interactions': [...]
            }
        """
        try:
            contact = self.supabase.table("contacts").select("*").eq("id", contact_id).execute()
            
            if not contact.data:
                return {}
            
            interactions = self.supabase.table("email_interactions").select("*").eq("contact_id", contact_id).order("occurred_at", desc=True).limit(10).execute()
            
            return {
                "email_frequency": contact.data[0].get("email_frequency", 0),
                "last_email_at": contact.data[0].get("last_email_at"),
                "enriched_from_gmail": contact.data[0].get("enriched_from_gmail", False),
                "recent_interactions": interactions.data
            }
        
        except Exception as e:
            logger.error(f"Failed to get contact enrichment: {e}")
            return {}
    
    async def get_sync_status(self, user_id: str) -> Dict:
        """Get Gmail sync status"""
        try:
            sync = self.supabase.table("gmail_sync").select("*").eq("user_id", user_id).execute()
            
            if not sync.data:
                return {"connected": False}
            
            return {
                "connected": sync.data[0].get("enabled", False),
                "last_sync_at": sync.data[0].get("last_sync_at"),
                "last_sync_emails_count": sync.data[0].get("last_sync_emails_count", 0)
            }
        
        except Exception as e:
            logger.error(f"Failed to get sync status: {e}")
            return {"error": str(e)}
    
    async def disconnect(self, user_id: str) -> bool:
        """Disconnect Gmail integration"""
        try:
            self.supabase.table("gmail_sync").update({
                "enabled": False,
                "access_token": None,
                "refresh_token": None
            }).eq("user_id", user_id).execute()
            
            logger.info(f"Gmail disconnected for user {user_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to disconnect Gmail: {e}")
            return False
