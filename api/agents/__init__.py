"""
Scheduler module for automated ML tasks.

Provides background job scheduling for:
- Contact embeddings generation
- Churn prediction
- Sentiment analysis
- Recommendation generation
- Contact clustering
"""

from .scheduler import start_scheduler, stop_scheduler

__all__ = ["start_scheduler", "stop_scheduler"]
