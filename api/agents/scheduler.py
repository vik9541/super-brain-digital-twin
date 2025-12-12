"""
Automated ML Job Scheduler for Super Brain Digital Twin.

Runs nightly ML tasks at 04:00-05:00 UTC:
1. 04:00 - Batch generate embeddings for new/updated contacts
2. 04:15 - Run churn prediction for all contacts
3. 04:30 - Analyze sentiment for all contacts
4. 04:45 - Generate recommendations for top 1000 users
5. 05:00 - Cluster contacts (K-means with n_clusters=5)

Uses APScheduler with AsyncIOScheduler for async/await compatibility.
"""

import asyncio
import logging

# Import ML services
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from ml.churn_predictor import ChurnPredictor
from ml.clustering_service import ContactClusteringService
from ml.embeddings_service import ContactEmbeddingsService
from ml.recommendation_engine import RecommendationEngine
from ml.sentiment_analyzer import SentimentAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Global scheduler instance
_scheduler: Optional[AsyncIOScheduler] = None

# ML service instances (initialized on first use)
_embeddings_service: Optional[ContactEmbeddingsService] = None
_recommendation_engine: Optional[RecommendationEngine] = None
_churn_predictor: Optional[ChurnPredictor] = None
_sentiment_analyzer: Optional[SentimentAnalyzer] = None
_clustering_service: Optional[ContactClusteringService] = None


def _get_embeddings_service() -> ContactEmbeddingsService:
    """Lazy initialization of ContactEmbeddingsService."""
    global _embeddings_service
    if _embeddings_service is None:
        _embeddings_service = ContactEmbeddingsService()
        logger.info("Initialized ContactEmbeddingsService")
    return _embeddings_service


def _get_recommendation_engine() -> RecommendationEngine:
    """Lazy initialization of RecommendationEngine."""
    global _recommendation_engine
    if _recommendation_engine is None:
        _recommendation_engine = RecommendationEngine()
        logger.info("Initialized RecommendationEngine")
    return _recommendation_engine


def _get_churn_predictor() -> ChurnPredictor:
    """Lazy initialization of ChurnPredictor."""
    global _churn_predictor
    if _churn_predictor is None:
        _churn_predictor = ChurnPredictor()
        logger.info("Initialized ChurnPredictor")
    return _churn_predictor


def _get_sentiment_analyzer() -> SentimentAnalyzer:
    """Lazy initialization of SentimentAnalyzer."""
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        _sentiment_analyzer = SentimentAnalyzer()
        logger.info("Initialized SentimentAnalyzer")
    return _sentiment_analyzer


def _get_clustering_service() -> ContactClusteringService:
    """Lazy initialization of ContactClusteringService."""
    global _clustering_service
    if _clustering_service is None:
        _clustering_service = ContactClusteringService()
        logger.info("Initialized ContactClusteringService")
    return _clustering_service


# ============================================================================
# SCHEDULED JOB FUNCTIONS
# ============================================================================


async def job_generate_embeddings():
    """
    Job 1: Generate embeddings for new/updated contacts (04:00 UTC).

    Strategy:
    - Query contacts updated in last 24 hours OR missing embeddings
    - Batch process with OpenAI API (10 contacts/batch, 1s delay)
    - Skip contacts that already have fresh embeddings
    """
    try:
        logger.info("=== Starting Embeddings Generation Job (04:00 UTC) ===")
        start_time = datetime.utcnow()

        service = _get_embeddings_service()

        # Query contacts needing embeddings
        # Filter: updated in last 24h OR no embedding exists
        yesterday = datetime.utcnow() - timedelta(days=1)

        query = """
            SELECT c.id, c.first_name, c.last_name, c.organization, 
                   c.tags, c.notes, c.updated_at
            FROM contacts c
            LEFT JOIN contact_embeddings ce ON c.id = ce.contact_id
            WHERE c.updated_at > %s 
               OR ce.id IS NULL
               OR ce.updated_at < c.updated_at
            ORDER BY c.updated_at DESC
            LIMIT 500
        """

        result = (
            service.supabase.table("contacts")
            .select("id, first_name, last_name, organization, tags, notes, updated_at")
            .gte("updated_at", yesterday.isoformat())
            .execute()
        )

        contacts = result.data if result.data else []

        if not contacts:
            logger.info("No contacts need embeddings. Job completed.")
            return

        logger.info(f"Found {len(contacts)} contacts needing embeddings")

        # Batch generate embeddings
        processed = await service.batch_generate_embeddings(contacts, batch_size=10)

        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.info(
            f"✅ Embeddings job completed: {processed}/{len(contacts)} contacts "
            f"in {duration:.2f}s"
        )

    except Exception as e:
        logger.error(f"❌ Embeddings job failed: {str(e)}", exc_info=True)


async def job_predict_churn():
    """
    Job 2: Predict churn risk for all contacts (04:15 UTC).

    Strategy:
    - Process all contacts (or high-value subset)
    - Calculate churn probability with RandomForest
    - Store predictions with 30-day TTL
    - Flag HIGH risk contacts for alerts
    """
    try:
        logger.info("=== Starting Churn Prediction Job (04:15 UTC) ===")
        start_time = datetime.utcnow()

        predictor = _get_churn_predictor()

        # Query all contacts (or filter by importance)
        result = (
            predictor.supabase.table("contacts")
            .select("id, first_name, last_name, influence_score")
            .order("influence_score", desc=True)
            .limit(1000)
            .execute()
        )

        contacts = result.data if result.data else []

        if not contacts:
            logger.info("No contacts found for churn prediction.")
            return

        logger.info(f"Predicting churn for {len(contacts)} contacts")

        processed = 0
        high_risk_count = 0

        for contact in contacts:
            try:
                prediction = await predictor.predict_churn(contact["id"])
                processed += 1

                if prediction.get("risk_level") == "HIGH":
                    high_risk_count += 1
                    logger.warning(
                        f"⚠️ HIGH RISK: {contact['first_name']} {contact['last_name']} "
                        f"({prediction['churn_probability']:.2%})"
                    )

                # Rate limiting
                if processed % 50 == 0:
                    logger.info(f"Progress: {processed}/{len(contacts)} contacts")
                    await asyncio.sleep(0.5)  # Brief pause every 50 contacts

            except Exception as e:
                logger.error(f"Failed to predict churn for contact {contact['id']}: {e}")
                continue

        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.info(
            f"✅ Churn prediction completed: {processed}/{len(contacts)} contacts, "
            f"{high_risk_count} HIGH RISK in {duration:.2f}s"
        )

    except Exception as e:
        logger.error(f"❌ Churn prediction job failed: {str(e)}", exc_info=True)


async def job_analyze_sentiment():
    """
    Job 3: Analyze sentiment for all contacts (04:30 UTC).

    Strategy:
    - Process all contacts with tags/notes/interactions
    - Multi-component analysis (tags 40%, notes 30%, interactions 30%)
    - Store with 14-day TTL
    - Track sentiment distribution for analytics
    """
    try:
        logger.info("=== Starting Sentiment Analysis Job (04:30 UTC) ===")
        start_time = datetime.utcnow()

        analyzer = _get_sentiment_analyzer()

        # Query all contacts
        result = (
            analyzer.supabase.table("contacts")
            .select("id, first_name, last_name")
            .limit(2000)
            .execute()
        )

        contacts = result.data if result.data else []

        if not contacts:
            logger.info("No contacts found for sentiment analysis.")
            return

        logger.info(f"Analyzing sentiment for {len(contacts)} contacts")

        processed = 0
        sentiment_counts = {
            "Very Positive": 0,
            "Positive": 0,
            "Neutral": 0,
            "Negative": 0,
            "Very Negative": 0,
        }

        for contact in contacts:
            try:
                sentiment = await analyzer.analyze_contact_sentiment(contact["id"])
                processed += 1

                label = sentiment.get("sentiment_label", "Neutral")
                sentiment_counts[label] = sentiment_counts.get(label, 0) + 1

                # Log extreme sentiments
                if label in ["Very Positive", "Very Negative"]:
                    logger.info(
                        f"📊 {label}: {contact['first_name']} {contact['last_name']} "
                        f"(score: {sentiment['overall_sentiment']:.2f})"
                    )

                # Rate limiting
                if processed % 100 == 0:
                    logger.info(f"Progress: {processed}/{len(contacts)} contacts")
                    await asyncio.sleep(0.3)

            except Exception as e:
                logger.error(f"Failed sentiment analysis for contact {contact['id']}: {e}")
                continue

        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.info(
            f"✅ Sentiment analysis completed: {processed}/{len(contacts)} contacts "
            f"in {duration:.2f}s"
        )
        logger.info(f"Distribution: {sentiment_counts}")

    except Exception as e:
        logger.error(f"❌ Sentiment analysis job failed: {str(e)}", exc_info=True)


async def job_generate_recommendations():
    """
    Job 4: Generate 'People You Should Know' recommendations (04:45 UTC).

    Strategy:
    - Process top 1000 users by influence score
    - 4-component scoring (mutual friends, semantic similarity, influence, org)
    - Store top 20 recommendations per user with 7-day TTL
    - Min score threshold: 0.6
    """
    try:
        logger.info("=== Starting Recommendation Generation Job (04:45 UTC) ===")
        start_time = datetime.utcnow()

        engine = _get_recommendation_engine()

        # Query top users (high influence = more likely to engage)
        result = (
            engine.supabase.table("contacts")
            .select("id, first_name, last_name, influence_score")
            .order("influence_score", desc=True)
            .limit(1000)
            .execute()
        )

        users = result.data if result.data else []

        if not users:
            logger.info("No users found for recommendation generation.")
            return

        logger.info(f"Generating recommendations for {len(users)} users")

        processed = 0
        total_recommendations = 0

        for user in users:
            try:
                recommendations = await engine.recommend_contacts(
                    user_id=user["id"], limit=20, min_score=0.6
                )

                processed += 1
                total_recommendations += len(recommendations)

                # Log high-quality recommendations
                if recommendations and recommendations[0].get("total_score", 0) > 0.85:
                    top = recommendations[0]
                    logger.info(
                        f"🎯 Strong match for {user['first_name']}: "
                        f"{top['first_name']} {top['last_name']} (score: {top['total_score']:.2f})"
                    )

                # Rate limiting
                if processed % 50 == 0:
                    logger.info(
                        f"Progress: {processed}/{len(users)} users, "
                        f"{total_recommendations} recommendations"
                    )
                    await asyncio.sleep(0.5)

            except Exception as e:
                logger.error(f"Failed recommendations for user {user['id']}: {e}")
                continue

        duration = (datetime.utcnow() - start_time).total_seconds()
        avg_recs = total_recommendations / processed if processed > 0 else 0
        logger.info(
            f"✅ Recommendation generation completed: {processed}/{len(users)} users, "
            f"{total_recommendations} total recs (avg {avg_recs:.1f}/user) in {duration:.2f}s"
        )

    except Exception as e:
        logger.error(f"❌ Recommendation generation job failed: {str(e)}", exc_info=True)


async def job_cluster_contacts():
    """
    Job 5: Cluster contacts by interest groups (05:00 UTC).

    Strategy:
    - Load all contact embeddings (1536-dim vectors)
    - Run K-means clustering (n_clusters=5)
    - Infer cluster topics from common tags/orgs
    - Store cluster assignments with topic labels
    """
    try:
        logger.info("=== Starting Contact Clustering Job (05:00 UTC) ===")
        start_time = datetime.utcnow()

        service = _get_clustering_service()

        # Run clustering (handles all embeddings internally)
        n_clusters = 5
        cluster_results = await service.cluster_contacts(n_clusters=n_clusters)

        if not cluster_results:
            logger.warning("Clustering returned no results")
            return

        # Log cluster summaries
        logger.info(f"✅ Created {len(cluster_results)} clusters:")
        for cluster in cluster_results:
            logger.info(
                f"  Cluster {cluster['cluster_id']}: "
                f"{cluster['cluster_size']} contacts, "
                f"topics: {', '.join(cluster['cluster_topics'][:3])}"
            )

        duration = (datetime.utcnow() - start_time).total_seconds()
        total_contacts = sum(c["cluster_size"] for c in cluster_results)
        logger.info(
            f"✅ Clustering completed: {total_contacts} contacts in "
            f"{n_clusters} clusters, {duration:.2f}s"
        )

    except Exception as e:
        logger.error(f"❌ Clustering job failed: {str(e)}", exc_info=True)


# ============================================================================
# SCHEDULER CONTROL FUNCTIONS
# ============================================================================


def start_scheduler():
    """
    Start the APScheduler with all 5 ML jobs.

    Jobs run nightly at:
    - 04:00 UTC: Generate embeddings
    - 04:15 UTC: Predict churn
    - 04:30 UTC: Analyze sentiment
    - 04:45 UTC: Generate recommendations
    - 05:00 UTC: Cluster contacts

    Returns:
        AsyncIOScheduler: The running scheduler instance
    """
    global _scheduler

    if _scheduler is not None and _scheduler.running:
        logger.warning("Scheduler is already running")
        return _scheduler

    # Create AsyncIOScheduler for async/await compatibility
    _scheduler = AsyncIOScheduler(timezone="UTC")

    # Job 1: Generate embeddings (04:00 UTC)
    _scheduler.add_job(
        job_generate_embeddings,
        trigger=CronTrigger(hour=4, minute=0, timezone="UTC"),
        id="job_generate_embeddings",
        name="Generate Contact Embeddings",
        replace_existing=True,
        max_instances=1,  # Prevent overlapping runs
    )
    logger.info("✅ Scheduled: Generate Embeddings (04:00 UTC)")

    # Job 2: Predict churn (04:15 UTC)
    _scheduler.add_job(
        job_predict_churn,
        trigger=CronTrigger(hour=4, minute=15, timezone="UTC"),
        id="job_predict_churn",
        name="Predict Contact Churn",
        replace_existing=True,
        max_instances=1,
    )
    logger.info("✅ Scheduled: Predict Churn (04:15 UTC)")

    # Job 3: Analyze sentiment (04:30 UTC)
    _scheduler.add_job(
        job_analyze_sentiment,
        trigger=CronTrigger(hour=4, minute=30, timezone="UTC"),
        id="job_analyze_sentiment",
        name="Analyze Contact Sentiment",
        replace_existing=True,
        max_instances=1,
    )
    logger.info("✅ Scheduled: Analyze Sentiment (04:30 UTC)")

    # Job 4: Generate recommendations (04:45 UTC)
    _scheduler.add_job(
        job_generate_recommendations,
        trigger=CronTrigger(hour=4, minute=45, timezone="UTC"),
        id="job_generate_recommendations",
        name="Generate Contact Recommendations",
        replace_existing=True,
        max_instances=1,
    )
    logger.info("✅ Scheduled: Generate Recommendations (04:45 UTC)")

    # Job 5: Cluster contacts (05:00 UTC)
    _scheduler.add_job(
        job_cluster_contacts,
        trigger=CronTrigger(hour=5, minute=0, timezone="UTC"),
        id="job_cluster_contacts",
        name="Cluster Contacts by Interests",
        replace_existing=True,
        max_instances=1,
    )
    logger.info("✅ Scheduled: Cluster Contacts (05:00 UTC)")

    # Start the scheduler
    _scheduler.start()
    logger.info("🚀 Scheduler started with 5 ML jobs (04:00-05:00 UTC)")

    return _scheduler


def stop_scheduler():
    """Stop the scheduler gracefully."""
    global _scheduler

    if _scheduler is None:
        logger.warning("Scheduler is not running")
        return

    if _scheduler.running:
        _scheduler.shutdown(wait=True)
        logger.info("🛑 Scheduler stopped")

    _scheduler = None


def get_scheduler_status() -> dict:
    """
    Get current scheduler status and job information.

    Returns:
        dict: Status info including running state, jobs, next run times
    """
    global _scheduler

    if _scheduler is None:
        return {"running": False, "jobs": []}

    jobs_info = []
    for job in _scheduler.get_jobs():
        jobs_info.append(
            {
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
            }
        )

    return {
        "running": _scheduler.running,
        "job_count": len(jobs_info),
        "jobs": jobs_info,
    }


# ============================================================================
# MANUAL JOB TRIGGERS (for testing)
# ============================================================================


async def run_all_jobs_now():
    """Run all 5 ML jobs immediately (for testing/manual trigger)."""
    logger.info("🔧 Manual trigger: Running all ML jobs now")

    await job_generate_embeddings()
    await job_predict_churn()
    await job_analyze_sentiment()
    await job_generate_recommendations()
    await job_cluster_contacts()

    logger.info("✅ All ML jobs completed")


if __name__ == "__main__":
    # For testing: run scheduler in standalone mode
    import signal

    def signal_handler(sig, frame):
        logger.info("Received shutdown signal")
        stop_scheduler()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("Starting scheduler in standalone mode...")
    start_scheduler()

    # Keep running
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        stop_scheduler()
