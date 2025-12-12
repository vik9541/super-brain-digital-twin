"""
Salesforce Contacts Sync Module

Syncs influencer contacts and community data from Supabase to Salesforce.
"""

import os
from datetime import datetime
from typing import Dict, Optional

from simple_salesforce import Salesforce
from supabase import Client, create_client


class SalesforceContactsSync:
    """Sync enriched contacts from Supabase to Salesforce"""

    def __init__(
        self,
        sf_username: Optional[str] = None,
        sf_password: Optional[str] = None,
        sf_security_token: Optional[str] = None,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
    ):
        """
        Initialize Salesforce and Supabase clients

        Args:
            sf_username: Salesforce username (or from SF_USERNAME env)
            sf_password: Salesforce password (or from SF_PASSWORD env)
            sf_security_token: Salesforce security token (or from SF_SECURITY_TOKEN env)
            supabase_url: Supabase URL (or from SUPABASE_URL env)
            supabase_key: Supabase anon key (or from SUPABASE_KEY env)
        """
        self.sf = Salesforce(
            username=sf_username or os.getenv("SF_USERNAME"),
            password=sf_password or os.getenv("SF_PASSWORD"),
            security_token=sf_security_token or os.getenv("SF_SECURITY_TOKEN"),
        )

        self.supabase: Client = create_client(
            supabase_url or os.getenv("SUPABASE_URL"), supabase_key or os.getenv("SUPABASE_KEY")
        )

    def push_influencers(self, min_influence_score: float = 0.5, limit: int = 100) -> Dict:
        """
        Push top influencers from Supabase to Salesforce

        Args:
            min_influence_score: Minimum influence score threshold (default: 0.5)
            limit: Maximum number of influencers to sync (default: 100)

        Returns:
            Dict with success/failure counts and details
        """
        # Fetch influencers from Supabase
        response = (
            self.supabase.table("contacts")
            .select("*")
            .gte("influence_score", min_influence_score)
            .order("influence_score", desc=True)
            .limit(limit)
            .execute()
        )

        influencers = response.data

        results = {
            "total": len(influencers),
            "created": 0,
            "updated": 0,
            "errors": [],
            "timestamp": datetime.utcnow().isoformat(),
        }

        for contact in influencers:
            try:
                sf_contact_data = self._map_contact_to_salesforce(contact)

                # Check if contact exists by email
                email = contact.get("email")
                if email:
                    existing = self.sf.query(f"SELECT Id FROM Contact WHERE Email = '{email}'")

                    if existing["totalSize"] > 0:
                        # Update existing contact
                        sf_id = existing["records"][0]["Id"]
                        self.sf.Contact.update(sf_id, sf_contact_data)
                        results["updated"] += 1
                    else:
                        # Create new contact
                        self.sf.Contact.create(sf_contact_data)
                        results["created"] += 1
                else:
                    # No email, create new
                    self.sf.Contact.create(sf_contact_data)
                    results["created"] += 1

            except Exception as e:
                results["errors"].append(
                    {
                        "contact_id": contact.get("id"),
                        "email": contact.get("email"),
                        "error": str(e),
                    }
                )

        return results

    def push_community(self, community_id: int) -> Dict:
        """
        Push all contacts from a specific community to Salesforce

        Args:
            community_id: Community ID to sync

        Returns:
            Dict with success/failure counts and details
        """
        # Fetch community contacts
        response = (
            self.supabase.table("contacts").select("*").eq("community_id", community_id).execute()
        )

        contacts = response.data

        results = {
            "community_id": community_id,
            "total": len(contacts),
            "created": 0,
            "updated": 0,
            "errors": [],
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Create custom field for community ID if needed
        community_field = f"Community_{community_id}__c"

        for contact in contacts:
            try:
                sf_contact_data = self._map_contact_to_salesforce(contact)
                # Add community marker
                sf_contact_data[community_field] = True

                email = contact.get("email")
                if email:
                    existing = self.sf.query(f"SELECT Id FROM Contact WHERE Email = '{email}'")

                    if existing["totalSize"] > 0:
                        sf_id = existing["records"][0]["Id"]
                        self.sf.Contact.update(sf_id, sf_contact_data)
                        results["updated"] += 1
                    else:
                        self.sf.Contact.create(sf_contact_data)
                        results["created"] += 1
                else:
                    self.sf.Contact.create(sf_contact_data)
                    results["created"] += 1

            except Exception as e:
                results["errors"].append(
                    {
                        "contact_id": contact.get("id"),
                        "email": contact.get("email"),
                        "error": str(e),
                    }
                )

        return results

    def _map_contact_to_salesforce(self, contact: Dict) -> Dict:
        """
        Map Supabase contact to Salesforce Contact object

        Args:
            contact: Contact dict from Supabase

        Returns:
            Dict with Salesforce Contact fields
        """
        sf_contact = {}

        # Standard fields
        if contact.get("first_name"):
            sf_contact["FirstName"] = contact["first_name"]
        if contact.get("last_name"):
            sf_contact["LastName"] = contact["last_name"] or "Unknown"  # Required field
        if contact.get("email"):
            sf_contact["Email"] = contact["email"]
        if contact.get("organization"):
            sf_contact["AccountName"] = contact["organization"]

        # Custom fields (assumes these exist in your Salesforce org)
        if contact.get("influence_score") is not None:
            sf_contact["Influence_Score__c"] = contact["influence_score"]
        if contact.get("community_id") is not None:
            sf_contact["Community_ID__c"] = contact["community_id"]
        if contact.get("id"):
            sf_contact["Supabase_ID__c"] = str(contact["id"])

        # Ensure LastName exists (required by Salesforce)
        if "LastName" not in sf_contact:
            sf_contact["LastName"] = contact.get("email", "Unknown").split("@")[0]

        return sf_contact


def sync_influencers_job(min_score: float = 0.5, limit: int = 100):
    """
    Scheduled job to sync influencers

    Usage with APScheduler:
        from apscheduler.decorators import scheduled_job

        @scheduled_job('cron', hour=3, minute=0)
        def nightly_influencers_sync():
            return sync_influencers_job()
    """
    syncer = SalesforceContactsSync()
    results = syncer.push_influencers(min_influence_score=min_score, limit=limit)

    print(f"[{results['timestamp']}] Salesforce Influencers Sync:")
    print(f"  Total: {results['total']}")
    print(f"  Created: {results['created']}")
    print(f"  Updated: {results['updated']}")
    print(f"  Errors: {len(results['errors'])}")

    if results["errors"]:
        for error in results["errors"][:5]:  # Show first 5 errors
            print(f"    - {error}")

    return results
