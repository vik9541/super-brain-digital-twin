"""
Contact Clustering Service

Groups contacts into clusters based on semantic similarity of embeddings.
Uses K-means clustering to discover interest-based groups.
"""

import logging
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional

import numpy as np
from sklearn.cluster import KMeans
from supabase import Client

logger = logging.getLogger(__name__)


class ContactClusteringService:
    """Service for clustering contacts by interests/topics."""

    def __init__(self, supabase_client: Client, embeddings_service):
        """
        Initialize ContactClusteringService.

        Args:
            supabase_client: Supabase client instance
            embeddings_service: ContactEmbeddingsService instance
        """
        self.supabase = supabase_client
        self.embeddings_service = embeddings_service

    async def cluster_contacts(self, n_clusters: int = 5) -> Dict:
        """
        Cluster all contacts using K-means on embeddings.

        Algorithm:
        1. Load all embeddings from database
        2. Run K-means clustering
        3. Group contacts by cluster ID
        4. Save clusters to database
        5. Return cluster summary

        Args:
            n_clusters: Number of clusters to create (default: 5)

        Returns:
            Dictionary with:
            - total_clusters
            - clusters (dict of cluster_id -> list of contact_ids)
            - cluster_sizes (dict of cluster_id -> size)
        """
        try:
            logger.info(f"Starting contact clustering with n_clusters={n_clusters}")

            # Step 1: Query all embeddings
            embeddings_response = self.supabase.table("contact_embeddings").select("*").execute()

            if not embeddings_response.data or len(embeddings_response.data) < n_clusters:
                logger.warning(
                    f"Insufficient embeddings for clustering: {len(embeddings_response.data) if embeddings_response.data else 0}"
                )
                return {
                    "total_clusters": 0,
                    "clusters": {},
                    "cluster_sizes": {},
                    "error": "Insufficient data for clustering",
                }

            # Step 2: Prepare data
            contact_ids = []
            embeddings = []

            for row in embeddings_response.data:
                contact_ids.append(row["contact_id"])
                embeddings.append(np.array(row["embedding"], dtype=np.float32))

            embeddings_array = np.array(embeddings)

            logger.info(f"Loaded {len(embeddings)} embeddings with shape {embeddings_array.shape}")

            # Step 3: K-means clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10, max_iter=300)

            labels = kmeans.fit_predict(embeddings_array)

            logger.info(f"K-means clustering complete, inertia: {kmeans.inertia_:.2f}")

            # Step 4: Group contacts by cluster
            clusters = defaultdict(list)

            for contact_id, label in zip(contact_ids, labels):
                cluster_id = int(label)
                clusters[cluster_id].append(contact_id)

            # Compute cluster sizes
            cluster_sizes = {cluster_id: len(contacts) for cluster_id, contacts in clusters.items()}

            logger.info(f"Created {len(clusters)} clusters: {cluster_sizes}")

            # Step 5: Save to database
            await self._save_clusters_to_db(clusters)

            # Step 6: Infer cluster topics (optional enhancement)
            cluster_topics = {}
            for cluster_id in clusters.keys():
                topics = await self.infer_cluster_topics(cluster_id, clusters[cluster_id])
                cluster_topics[cluster_id] = topics

            result = {
                "total_clusters": len(clusters),
                "clusters": {k: v for k, v in clusters.items()},
                "cluster_sizes": cluster_sizes,
                "cluster_topics": cluster_topics,
                "timestamp": datetime.utcnow().isoformat(),
            }

            logger.info(f"Clustering complete: {len(clusters)} clusters, sizes: {cluster_sizes}")

            return result

        except Exception as e:
            logger.error(f"Failed to cluster contacts: {str(e)}")
            return {"total_clusters": 0, "clusters": {}, "cluster_sizes": {}, "error": str(e)}

    async def _save_clusters_to_db(self, clusters: Dict[int, List[str]]) -> None:
        """
        Save cluster assignments to contact_clusters table.

        Args:
            clusters: Dictionary mapping cluster_id -> list of contact_ids
        """
        try:
            # Delete old clusters
            self.supabase.table("contact_clusters").delete().neq("cluster_id", -1).execute()

            # Insert new clusters
            cluster_records = []

            for cluster_id, contact_ids in clusters.items():
                record = {
                    "cluster_id": cluster_id,
                    "contact_ids": contact_ids,
                    "cluster_size": len(contact_ids),
                    "created_at": datetime.utcnow().isoformat(),
                }
                cluster_records.append(record)

            if cluster_records:
                self.supabase.table("contact_clusters").insert(cluster_records).execute()
                logger.info(f"Saved {len(cluster_records)} clusters to database")

        except Exception as e:
            logger.error(f"Failed to save clusters to database: {str(e)}")

    async def infer_cluster_topics(self, cluster_id: int, contact_ids: List[str]) -> List[str]:
        """
        Infer topics for a cluster based on common tags.

        Analyzes all contacts in the cluster and returns top 3-5 tags
        that appear most frequently.

        Args:
            cluster_id: Cluster ID
            contact_ids: List of contact UUIDs in cluster

        Returns:
            List of top tags (topics) for the cluster
        """
        try:
            logger.info(f"Inferring topics for cluster {cluster_id} ({len(contact_ids)} contacts)")

            if not contact_ids:
                return []

            # Get all contacts in cluster
            contacts_response = (
                self.supabase.table("contacts")
                .select("tags, organization")
                .in_("id", contact_ids)
                .execute()
            )

            if not contacts_response.data:
                return []

            # Count tag frequencies
            tag_counts = defaultdict(int)
            org_counts = defaultdict(int)

            for contact in contacts_response.data:
                # Count tags
                tags = contact.get("tags", [])
                if isinstance(tags, list):
                    for tag in tags:
                        if tag and tag.strip():
                            tag_counts[tag.lower().strip()] += 1

                # Count organizations
                org = contact.get("organization")
                if org and org.strip():
                    org_counts[org.strip()] += 1

            # Get top 5 tags
            top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            topics = [tag for tag, count in top_tags if count >= 2]  # Must appear at least twice

            # Add top organization if significant
            if org_counts:
                top_org = max(org_counts.items(), key=lambda x: x[1])
                if top_org[1] >= len(contact_ids) * 0.3:  # At least 30% of cluster
                    topics.append(f"Organization: {top_org[0]}")

            logger.info(f"Cluster {cluster_id} topics: {topics}")

            return topics

        except Exception as e:
            logger.error(f"Failed to infer topics for cluster {cluster_id}: {str(e)}")
            return []

    async def get_contact_cluster(self, contact_id: str) -> Optional[int]:
        """
        Get cluster assignment for a specific contact.

        Args:
            contact_id: Contact UUID

        Returns:
            Cluster ID or None if not found
        """
        try:
            # Query all clusters
            clusters_response = self.supabase.table("contact_clusters").select("*").execute()

            if not clusters_response.data:
                return None

            # Find contact in clusters
            for cluster_row in clusters_response.data:
                if contact_id in cluster_row["contact_ids"]:
                    return cluster_row["cluster_id"]

            return None

        except Exception as e:
            logger.error(f"Failed to get cluster for contact {contact_id}: {str(e)}")
            return None

    async def get_cluster_members(self, cluster_id: int) -> List[Dict]:
        """
        Get all contacts in a specific cluster with their details.

        Args:
            cluster_id: Cluster ID

        Returns:
            List of contact dictionaries
        """
        try:
            # Get cluster
            cluster_response = (
                self.supabase.table("contact_clusters")
                .select("*")
                .eq("cluster_id", cluster_id)
                .execute()
            )

            if not cluster_response.data or len(cluster_response.data) == 0:
                logger.warning(f"Cluster {cluster_id} not found")
                return []

            contact_ids = cluster_response.data[0]["contact_ids"]

            # Get contact details
            contacts_response = (
                self.supabase.table("contacts").select("*").in_("id", contact_ids).execute()
            )

            return contacts_response.data if contacts_response.data else []

        except Exception as e:
            logger.error(f"Failed to get members for cluster {cluster_id}: {str(e)}")
            return []
