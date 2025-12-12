"""
Enterprise Integrations Module

This package contains sync modules for external enterprise systems:
- Salesforce CRM
- Microsoft Graph (Outlook/Teams contacts)

Usage:
    from apps.integrations.salesforce_sync import SalesforceContactsSync
    from apps.integrations.ms_graph_sync import MSGraphContactsSync
"""

__version__ = "1.0.0"
__all__ = ["SalesforceContactsSync", "MSGraphContactsSync"]
