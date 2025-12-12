"""
GraphQL API module for Super Brain Digital Twin.

Provides GraphQL queries and mutations for:
- Contact management
- ML-powered features (embeddings, recommendations, churn, sentiment, clustering)
- Network analysis
- Community detection
"""

from .schema import schema

__all__ = ["schema"]
