"""
ML Module for Super Brain Digital Twin

Advanced machine learning services:
- Contact embeddings (semantic search)
- Recommendation engine
- Churn prediction
- Sentiment analysis
- Contact clustering
"""

from .embeddings_service import ContactEmbeddingsService
from .recommendation_engine import RecommendationEngine
from .churn_predictor import ChurnPredictor
from .sentiment_analyzer import SentimentAnalyzer
from .clustering_service import ContactClusteringService

__all__ = [
    'ContactEmbeddingsService',
    'RecommendationEngine',
    'ChurnPredictor',
    'SentimentAnalyzer',
    'ContactClusteringService',
]
