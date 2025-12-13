"""
Graph construction module for contact recommendation GNN.

Builds PyTorch Geometric graph from Supabase contact data:
- Nodes: Contacts with features (influence, tags, organization)
- Edges: Interactions with weights (frequency, recency)
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import torch
from torch_geometric.data import Data

logger = logging.getLogger(__name__)


class ContactGraphBuilder:
    """Builds PyTorch Geometric graphs from contact and interaction data."""

    def __init__(self, supabase_client):
        """
        Initialize graph builder.

        Args:
            supabase_client: Supabase client for database queries
        """
        self.supabase = supabase_client
        self.contact_id_to_idx: Dict[str, int] = {}
        self.idx_to_contact_id: Dict[int, str] = {}

    async def build_graph(
        self, user_id: str, min_interaction_count: int = 1, include_shared_tags: bool = True
    ) -> Data:
        """
        Build complete graph for a user's contacts.

        Args:
            user_id: User ID to build graph for
            min_interaction_count: Minimum interactions to create edge
            include_shared_tags: Whether to add edges for shared tags

        Returns:
            PyTorch Geometric Data object with:
                - x: Node features [num_nodes, 3]
                - edge_index: Edge connections [2, num_edges]
                - edge_attr: Edge weights [num_edges, 1]
        """
        logger.info(f"Building graph for user {user_id}")

        # 1. Fetch contacts
        contacts = await self._fetch_contacts(user_id)
        if not contacts:
            logger.warning(f"No contacts found for user {user_id}")
            return self._create_empty_graph()

        logger.info(f"Found {len(contacts)} contacts")

        # 2. Build contact mapping
        self._build_contact_mapping(contacts)

        # 3. Extract node features
        node_features = self._extract_node_features(contacts)

        # 4. Build edges from interactions
        edge_index, edge_weights = await self._build_edges_from_interactions(
            user_id, min_interaction_count
        )

        # 5. Add edges from shared tags (optional)
        if include_shared_tags:
            tag_edges, tag_weights = self._build_edges_from_tags(contacts)
            edge_index = torch.cat([edge_index, tag_edges], dim=1)
            edge_weights = torch.cat([edge_weights, tag_weights], dim=0)

        # 6. Make graph bidirectional (undirected)
        edge_index, edge_weights = self._make_bidirectional(edge_index, edge_weights)

        logger.info(f"Graph built: {node_features.shape[0]} nodes, " f"{edge_index.shape[1]} edges")

        return Data(
            x=node_features,
            edge_index=edge_index,
            edge_attr=edge_weights.unsqueeze(1),  # [num_edges, 1]
        )

    async def _fetch_contacts(self, user_id: str) -> List[Dict]:
        """Fetch all contacts for a user from database."""
        try:
            response = (
                self.supabase.table("apple_contacts")
                .select("id, name, organization, influence_score, tags")
                .eq("user_id", user_id)
                .execute()
            )

            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching contacts: {e}")
            return []

    def _build_contact_mapping(self, contacts: List[Dict]) -> None:
        """Build bidirectional mapping between contact IDs and indices."""
        self.contact_id_to_idx = {contact["id"]: idx for idx, contact in enumerate(contacts)}
        self.idx_to_contact_id = {idx: contact["id"] for idx, contact in enumerate(contacts)}

    def _extract_node_features(self, contacts: List[Dict]) -> torch.Tensor:
        """
        Extract normalized node features.

        Features (3-dimensional):
        1. Influence score (normalized to 0-1)
        2. Tag count (normalized by /10)
        3. Has organization (binary 0/1)

        Returns:
            Tensor of shape [num_contacts, 3]
        """
        features = []

        for contact in contacts:
            # Feature 1: Normalized influence score
            influence = contact.get("influence_score", 0.0)
            norm_influence = min(influence / 100.0, 1.0)

            # Feature 2: Tag count (normalized)
            tags = contact.get("tags", [])
            tag_count = len(tags) if tags else 0
            norm_tag_count = min(tag_count / 10.0, 1.0)

            # Feature 3: Has organization (binary)
            has_org = 1.0 if contact.get("organization") else 0.0

            features.append([norm_influence, norm_tag_count, has_org])

        return torch.tensor(features, dtype=torch.float)

    async def _build_edges_from_interactions(
        self, user_id: str, min_count: int
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Build edges from contact_activity_log table.

        Edge weight = interaction_frequency * recency_factor

        Returns:
            edge_index: [2, num_edges]
            edge_weights: [num_edges]
        """
        try:
            # Fetch activity logs from last 90 days
            since_date = (datetime.now() - timedelta(days=90)).isoformat()

            response = (
                self.supabase.table("contact_activity_log")
                .select("contact_id, activity_type, created_at")
                .eq("user_id", user_id)
                .gte("created_at", since_date)
                .execute()
            )

            if not response.data:
                return torch.empty((2, 0), dtype=torch.long), torch.empty(0)

            # Count interactions between contacts
            interaction_counts = {}

            for log in response.data:
                contact_id = log["contact_id"]
                if contact_id not in self.contact_id_to_idx:
                    continue

                idx = self.contact_id_to_idx[contact_id]

                # For now, create self-loops (contact interacted)
                # In future: extract actual contact-to-contact interactions
                key = (idx, idx)
                interaction_counts[key] = interaction_counts.get(key, 0) + 1

            # Build edge tensors
            edges = []
            weights = []

            for (src, dst), count in interaction_counts.items():
                if count >= min_count:
                    edges.append([src, dst])
                    weights.append(float(count))

            if not edges:
                return torch.empty((2, 0), dtype=torch.long), torch.empty(0)

            edge_index = torch.tensor(edges, dtype=torch.long).t()
            edge_weights = torch.tensor(weights, dtype=torch.float)

            return edge_index, edge_weights

        except Exception as e:
            logger.error(f"Error building edges from interactions: {e}")
            return torch.empty((2, 0), dtype=torch.long), torch.empty(0)

    def _build_edges_from_tags(self, contacts: List[Dict]) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Build edges between contacts with shared tags.

        Weight = number of shared tags / max(tags_a, tags_b)
        """
        edges = []
        weights = []

        # Build tag -> contact_indices mapping
        tag_to_contacts = {}
        for idx, contact in enumerate(contacts):
            tags = contact.get("tags", [])
            if not tags:
                continue

            for tag in tags:
                if tag not in tag_to_contacts:
                    tag_to_contacts[tag] = []
                tag_to_contacts[tag].append(idx)

        # Create edges for contacts sharing tags
        for tag, contact_indices in tag_to_contacts.items():
            if len(contact_indices) < 2:
                continue

            # Connect all pairs with this tag
            for i in range(len(contact_indices)):
                for j in range(i + 1, len(contact_indices)):
                    idx_a, idx_b = contact_indices[i], contact_indices[j]

                    # Calculate shared tags
                    tags_a = set(contacts[idx_a].get("tags", []))
                    tags_b = set(contacts[idx_b].get("tags", []))
                    shared = len(tags_a & tags_b)

                    if shared > 0:
                        weight = shared / max(len(tags_a), len(tags_b))
                        edges.append([idx_a, idx_b])
                        weights.append(weight)

        if not edges:
            return torch.empty((2, 0), dtype=torch.long), torch.empty(0)

        edge_index = torch.tensor(edges, dtype=torch.long).t()
        edge_weights = torch.tensor(weights, dtype=torch.float)

        return edge_index, edge_weights

    def _make_bidirectional(
        self, edge_index: torch.Tensor, edge_weights: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Make graph undirected by adding reverse edges."""
        if edge_index.shape[1] == 0:
            return edge_index, edge_weights

        # Reverse edges
        reverse_edges = edge_index.flip(0)

        # Concatenate
        edge_index = torch.cat([edge_index, reverse_edges], dim=1)
        edge_weights = torch.cat([edge_weights, edge_weights], dim=0)

        return edge_index, edge_weights

    def _create_empty_graph(self) -> Data:
        """Create empty graph for edge cases."""
        return Data(
            x=torch.zeros((1, 3), dtype=torch.float),
            edge_index=torch.empty((2, 0), dtype=torch.long),
            edge_attr=torch.empty((0, 1), dtype=torch.float),
        )

    def get_contact_id(self, node_idx: int) -> Optional[str]:
        """Get contact ID from node index."""
        return self.idx_to_contact_id.get(node_idx)

    def get_node_idx(self, contact_id: str) -> Optional[int]:
        """Get node index from contact ID."""
        return self.contact_id_to_idx.get(contact_id)
