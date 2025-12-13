"""
ML Module for Super Brain Digital Twin

Advanced machine learning services:
- Contact embeddings (semantic search)
- Recommendation engine (simple + GNN)
- Churn prediction
- Sentiment analysis
- Contact clustering
- Graph Neural Networks (Phase 8)
"""

# Lazy imports - avoid loading heavy dependencies at startup
__all__ = [
    "ContactEmbeddingsService",
    "RecommendationEngine",
    "ChurnPredictor",
    "SentimentAnalyzer",
    "ContactClusteringService",
    "ContactGraphBuilder",
    "ContactRecommenderGNN",
    "GNNTrainer",
    "GNNRecommender",
]
