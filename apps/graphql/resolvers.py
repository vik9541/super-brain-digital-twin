"""
GraphQL Resolvers for Super Brain Digital Twin.

Implements query resolvers that call:
- Supabase for core data
- ML services for Phase 6 features
"""

import sys
from pathlib import Path
from typing import List, Optional
from uuid import UUID
from datetime import datetime

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Import ML services
from api.ml.embeddings_service import ContactEmbeddingsService
from api.ml.recommendation_engine import RecommendationEngine
from api.ml.churn_predictor import ChurnPredictor
from api.ml.sentiment_analyzer import SentimentAnalyzer
from api.ml.clustering_service import ContactClusteringService

# Import types from schema
from .schema import (
    Contact,
    SimilarContact,
    Recommendation,
    ScoreComponents,
    ChurnPrediction,
    ChurnFeatures,
    Sentiment,
    SentimentComponents,
    Cluster,
)

# Load environment variables
load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")  # Use service key for admin access
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize ML services (lazy loading)
_embeddings_service: Optional[ContactEmbeddingsService] = None
_recommendation_engine: Optional[RecommendationEngine] = None
_churn_predictor: Optional[ChurnPredictor] = None
_sentiment_analyzer: Optional[SentimentAnalyzer] = None
_clustering_service: Optional[ContactClusteringService] = None


def get_embeddings_service() -> ContactEmbeddingsService:
    global _embeddings_service
    if _embeddings_service is None:
        _embeddings_service = ContactEmbeddingsService()
    return _embeddings_service


def get_recommendation_engine() -> RecommendationEngine:
    global _recommendation_engine
    if _recommendation_engine is None:
        _recommendation_engine = RecommendationEngine()
    return _recommendation_engine


def get_churn_predictor() -> ChurnPredictor:
    global _churn_predictor
    if _churn_predictor is None:
        _churn_predictor = ChurnPredictor()
    return _churn_predictor


def get_sentiment_analyzer() -> SentimentAnalyzer:
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        _sentiment_analyzer = SentimentAnalyzer()
    return _sentiment_analyzer


def get_clustering_service() -> ContactClusteringService:
    global _clustering_service
    if _clustering_service is None:
        _clustering_service = ContactClusteringService()
    return _clustering_service


# ============================================================================
# CORE CONTACT RESOLVERS
# ============================================================================


async def get_contacts(
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[Contact]:
    """
    Get list of contacts with optional search.
    
    Args:
        search: Optional search term (matches first_name, last_name, email, org)
        limit: Max results (default 50)
        offset: Pagination offset (default 0)
    """
    query = supabase.table("contacts").select("*")
    
    if search:
        # Simple search across multiple fields
        query = query.or_(
            f"first_name.ilike.%{search}%,"
            f"last_name.ilike.%{search}%,"
            f"email.ilike.%{search}%,"
            f"organization.ilike.%{search}%"
        )
    
    result = query.limit(limit).offset(offset).execute()
    
    return [Contact(**row) for row in result.data] if result.data else []


async def get_contact_by_id(id: UUID) -> Optional[Contact]:
    """Get contact by ID."""
    result = supabase.table("contacts").select("*").eq("id", str(id)).single().execute()
    
    return Contact(**result.data) if result.data else None


async def get_influencers(
    limit: int = 20,
    min_score: float = 0.7,
) -> List[Contact]:
    """
    Get top influencers by influence score.
    
    Args:
        limit: Max results (default 20)
        min_score: Minimum influence score threshold (default 0.7)
    """
    result = (
        supabase.table("contacts")
        .select("*")
        .gte("influence_score", min_score)
        .order("influence_score", desc=True)
        .limit(limit)
        .execute()
    )
    
    return [Contact(**row) for row in result.data] if result.data else []


# ============================================================================
# PHASE 6: ML-POWERED RESOLVERS
# ============================================================================


async def similar_contacts(
    contact_id: UUID,
    limit: int = 10,
) -> List[SimilarContact]:
    """
    Find semantically similar contacts using OpenAI embeddings.
    
    Args:
        contact_id: Target contact ID
        limit: Max similar contacts to return (default 10)
    
    Returns:
        List of similar contacts with cosine similarity scores
    """
    service = get_embeddings_service()
    
    # Call ML service
    results = await service.find_similar_contacts(
        contact_id=str(contact_id),
        top_n=limit
    )
    
    # Transform to GraphQL type
    similar = []
    for result in results:
        similar.append(SimilarContact(
            contact_id=UUID(result["contact_id"]),
            first_name=result["first_name"],
            last_name=result["last_name"],
            organization=result.get("organization"),
            similarity_score=result["similarity_score"],
            common_tags=result.get("common_tags", []),
        ))
    
    return similar


async def recommended_contacts(
    user_id: UUID,
    limit: int = 20,
    min_score: float = 0.6,
) -> List[Recommendation]:
    """
    'People You Should Know' recommendations with 4-component scoring.
    
    Args:
        user_id: User's contact ID
        limit: Max recommendations (default 20)
        min_score: Minimum total score threshold (default 0.6)
    
    Returns:
        List of recommendations with score breakdown and explanations
    """
    engine = get_recommendation_engine()
    
    # Call ML service
    results = await engine.recommend_contacts(
        user_id=str(user_id),
        limit=limit,
        min_score=min_score
    )
    
    # Transform to GraphQL type
    recommendations = []
    for result in results:
        # Extract score components
        components_data = result.get("score_components", {})
        components = ScoreComponents(
            mutual_friends=components_data.get("mutual_friends", 0),
            semantic_similarity=components_data.get("semantic_similarity", 0),
            influence_score=components_data.get("influence_score", 0),
            same_organization=components_data.get("same_organization", 0),
        )
        
        recommendations.append(Recommendation(
            contact_id=UUID(result["contact_id"]),
            first_name=result["first_name"],
            last_name=result["last_name"],
            organization=result.get("organization"),
            influence_score=result["influence_score"],
            total_score=result["total_score"],
            components=components,
            reason=result["reason"],
        ))
    
    return recommendations


async def churn_risk(contact_id: UUID) -> Optional[ChurnPrediction]:
    """
    Predict churn risk for a contact using RandomForest ML model.
    
    Args:
        contact_id: Contact ID to analyze
    
    Returns:
        Churn prediction with risk level, probability, features, and interventions
    """
    predictor = get_churn_predictor()
    
    # Call ML service
    result = await predictor.predict_churn(contact_id=str(contact_id))
    
    if not result:
        return None
    
    # Extract features
    features_data = result.get("features", {})
    features = ChurnFeatures(
        days_since_update_norm=features_data.get("days_since_update_norm", 0),
        interaction_frequency_norm=features_data.get("interaction_frequency_norm", 0),
        inverse_influence=features_data.get("inverse_influence", 0),
        tag_count_norm=features_data.get("tag_count_norm", 0),
        community_size_norm=features_data.get("community_size_norm", 0),
    )
    
    return ChurnPrediction(
        contact_id=contact_id,
        churn_probability=result["churn_probability"],
        risk_level=result["risk_level"],
        features=features,
        interventions=result.get("interventions", []),
        predicted_at=datetime.fromisoformat(result["predicted_at"]),
        expires_at=datetime.fromisoformat(result["expires_at"]),
    )


async def contact_sentiment(contact_id: UUID) -> Optional[Sentiment]:
    """
    Analyze contact sentiment using multi-component analysis.
    
    Components (weighted):
    - Tags: 40% (positive/negative keyword matching)
    - Notes: 30% (TextBlob NLP polarity)
    - Interactions: 30% (frequency-based)
    
    Args:
        contact_id: Contact ID to analyze
    
    Returns:
        Sentiment analysis with overall score, label, and component breakdown
    """
    analyzer = get_sentiment_analyzer()
    
    # Call ML service
    result = await analyzer.analyze_contact_sentiment(contact_id=str(contact_id))
    
    if not result:
        return None
    
    # Extract components
    components_data = result.get("components", {})
    components = SentimentComponents(
        tags_sentiment=components_data.get("tags_sentiment", 0),
        notes_sentiment=components_data.get("notes_sentiment", 0),
        interactions_sentiment=components_data.get("interactions_sentiment", 0),
    )
    
    return Sentiment(
        contact_id=contact_id,
        overall_sentiment=result["overall_sentiment"],
        sentiment_label=result["sentiment_label"],
        components=components,
        analyzed_at=datetime.fromisoformat(result["analyzed_at"]),
        expires_at=datetime.fromisoformat(result["expires_at"]),
    )


async def contact_clusters() -> List[Cluster]:
    """
    Get all contact clusters with inferred topics.
    
    Clusters created by K-means algorithm on contact embeddings.
    Topics inferred from most common tags and organizations.
    
    Returns:
        List of clusters with size, topics, and sample contacts
    """
    service = get_clustering_service()
    
    # Get cluster info from database
    result = supabase.table("contact_clusters").select("*").execute()
    
    if not result.data:
        return []
    
    clusters = []
    for cluster_data in result.data:
        cluster_id = cluster_data["cluster_id"]
        contact_ids = cluster_data["contact_ids"]
        
        # Get sample contacts (first 5)
        sample_contacts = []
        if contact_ids and len(contact_ids) > 0:
            sample_ids = contact_ids[:5]
            contacts_result = (
                supabase.table("contacts")
                .select("*")
                .in_("id", sample_ids)
                .execute()
            )
            
            if contacts_result.data:
                sample_contacts = [Contact(**row) for row in contacts_result.data]
        
        clusters.append(Cluster(
            cluster_id=cluster_id,
            cluster_size=cluster_data["cluster_size"],
            cluster_topics=cluster_data.get("cluster_topics", []),
            sample_contacts=sample_contacts,
        ))
    
    return clusters
