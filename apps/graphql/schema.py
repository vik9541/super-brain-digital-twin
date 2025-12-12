"""
Strawberry GraphQL Schema for Super Brain Digital Twin.

Defines GraphQL types, queries, and mutations.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

import strawberry

# ============================================================================
# CORE TYPES
# ============================================================================


@strawberry.type
class Contact:
    """Contact entity from Supabase database."""

    id: UUID
    first_name: str
    last_name: str
    email: Optional[str] = None
    organization: Optional[str] = None
    influence_score: Optional[float] = None
    community_id: Optional[int] = None
    tags: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime


@strawberry.type
class Connection:
    """Connection between two contacts."""

    id: UUID
    source_id: UUID
    target_id: UUID
    connection_type: Optional[str] = None
    strength: Optional[float] = None
    created_at: datetime


# ============================================================================
# PHASE 6: ML FEATURE TYPES
# ============================================================================


@strawberry.type
class SimilarContact:
    """Similar contact from embedding-based semantic search."""

    contact_id: UUID
    first_name: str
    last_name: str
    organization: Optional[str] = None
    similarity_score: float  # Cosine similarity (0-1)
    common_tags: Optional[List[str]] = None


@strawberry.type
class ScoreComponents:
    """Breakdown of recommendation scoring components."""

    mutual_friends: float  # 0.3 weight
    semantic_similarity: float  # 0.3 weight
    influence_score: float  # 0.25 weight
    same_organization: float  # 0.15 weight


@strawberry.type
class Recommendation:
    """'People You Should Know' recommendation with scoring breakdown."""

    contact_id: UUID
    first_name: str
    last_name: str
    organization: Optional[str] = None
    influence_score: float
    total_score: float  # Weighted total (0-1)
    components: ScoreComponents
    reason: str  # Human-readable explanation


@strawberry.type
class ChurnFeatures:
    """Feature values used for churn prediction."""

    days_since_update_norm: float
    interaction_frequency_norm: float
    inverse_influence: float
    tag_count_norm: float
    community_size_norm: float


@strawberry.type
class ChurnPrediction:
    """Contact churn risk prediction with interventions."""

    contact_id: UUID
    churn_probability: float  # 0-1
    risk_level: str  # HIGH, MEDIUM, LOW
    features: ChurnFeatures
    interventions: List[str]  # Actionable suggestions
    predicted_at: datetime
    expires_at: datetime


@strawberry.type
class SentimentComponents:
    """Breakdown of sentiment analysis components."""

    tags_sentiment: float  # -1 to 1
    notes_sentiment: float  # -1 to 1
    interactions_sentiment: float  # -1 to 1


@strawberry.type
class Sentiment:
    """Multi-component sentiment analysis for contact."""

    contact_id: UUID
    overall_sentiment: float  # -1 (negative) to 1 (positive)
    sentiment_label: str  # Very Positive, Positive, Neutral, Negative, Very Negative
    components: SentimentComponents
    analyzed_at: datetime
    expires_at: datetime


@strawberry.type
class Cluster:
    """Contact cluster with inferred topics."""

    cluster_id: int
    cluster_size: int
    cluster_topics: List[str]  # Top tags/interests
    sample_contacts: Optional[List[Contact]] = None  # First 5 contacts


# ============================================================================
# QUERY ROOT
# ============================================================================


@strawberry.type
class Query:
    """Root GraphQL query type."""

    # Import resolvers (will be defined in resolvers.py)
    from .resolvers import (  # Phase 6: ML-powered queries
        churn_risk,
        contact_clusters,
        contact_sentiment,
        get_contact_by_id,
        get_contacts,
        get_influencers,
        recommended_contacts,
        similar_contacts,
    )

    # Core contact queries
    contacts: List[Contact] = strawberry.field(resolver=get_contacts)
    contact: Optional[Contact] = strawberry.field(resolver=get_contact_by_id)
    influencers: List[Contact] = strawberry.field(resolver=get_influencers)

    # Phase 6: ML-powered queries
    similar_contacts: List[SimilarContact] = strawberry.field(resolver=similar_contacts)
    recommended_contacts: List[Recommendation] = strawberry.field(resolver=recommended_contacts)
    churn_risk: Optional[ChurnPrediction] = strawberry.field(resolver=churn_risk)
    contact_sentiment: Optional[Sentiment] = strawberry.field(resolver=contact_sentiment)
    contact_clusters: List[Cluster] = strawberry.field(resolver=contact_clusters)


# ============================================================================
# SCHEMA DEFINITION
# ============================================================================


schema = strawberry.Schema(query=Query)
