"""
GNN Model for Contact Recommendations

Graph Neural Network using GraphSAGE architecture to learn
contact embeddings for high-quality recommendations.
"""

import torch
import torch.nn.functional as F
from torch_geometric.nn import SAGEConv
from torch.nn import BatchNorm1d, Dropout, ReLU
import logging

logger = logging.getLogger(__name__)


class ContactRecommenderGNN(torch.nn.Module):
    """
    Graph Neural Network для рекомендаций контактов
    
    Архитектура:
    - 3 GraphSAGE layers (aggregates features from neighbors)
    - BatchNormalization (для стабилизации обучения)
    - Dropout (для регуляризации)
    - Output: 128-dimensional embeddings
    
    Как это работает:
    1. Каждый node агрегирует features от соседей
    2. После 3 итераций каждый node "знает" информацию на расстоянии 3 хопов
    3. Similar nodes в embedding space = good recommendations
    """
    
    def __init__(
        self,
        in_features: int = 3,
        hidden_dim: int = 64,
        out_dim: int = 128,
        num_layers: int = 3,
        dropout: float = 0.2
    ):
        super().__init__()
        
        self.in_features = in_features
        self.hidden_dim = hidden_dim
        self.out_dim = out_dim
        self.num_layers = num_layers
        
        # GraphSAGE layers
        self.layers = torch.nn.ModuleList()
        self.batch_norms = torch.nn.ModuleList()
        self.dropouts = torch.nn.ModuleList()
        
        # Layer 1: input -> hidden
        self.layers.append(SAGEConv(in_features, hidden_dim))
        self.batch_norms.append(BatchNorm1d(hidden_dim))
        self.dropouts.append(Dropout(dropout))
        
        # Layers 2-(N-1): hidden -> hidden
        for _ in range(num_layers - 2):
            self.layers.append(SAGEConv(hidden_dim, hidden_dim))
            self.batch_norms.append(BatchNorm1d(hidden_dim))
            self.dropouts.append(Dropout(dropout))
        
        # Output layer: hidden -> out_dim
        self.layers.append(SAGEConv(hidden_dim, out_dim))
        
        self.relu = ReLU()
        
        logger.info(
            f"✅ GNN Model created: {num_layers} layers, "
            f"{in_features}→{hidden_dim}→{out_dim}"
        )
    
    def forward(self, x, edge_index):
        """
        Forward pass через GNN
        
        Args:
            x: Node features [num_nodes, in_features]
            edge_index: Edge indices [2, num_edges]
        
        Returns:
            embeddings: [num_nodes, out_dim]
        """
        
        # Layers 1 to N-1: with activation and normalization
        for i in range(len(self.layers) - 1):
            x = self.layers[i](x, edge_index)
            x = self.batch_norms[i](x)
            x = self.relu(x)
            x = self.dropouts[i](x)
        
        # Last layer: no activation (embedding space)
        x = self.layers[-1](x, edge_index)
        
        return x
    
    def get_recommendations(
        self,
        embeddings: torch.Tensor,
        target_idx: int,
        k: int = 20,
        exclude_indices: list = None
    ) -> torch.Tensor:
        """
        Получи top-k рекомендаций для контакта
        
        Используй cosine similarity в embedding space
        
        Args:
            embeddings: [num_nodes, embedding_dim]
            target_idx: Index целевого контакта
            k: Кол-во рекомендаций
            exclude_indices: Indices для исключения
        
        Returns:
            torch.Tensor: Top-k indices
        """
        
        if exclude_indices is None:
            exclude_indices = []
        
        # Normalize embeddings
        embeddings_norm = F.normalize(embeddings, p=2, dim=1)
        
        # Get target embedding
        target_embedding = embeddings_norm[target_idx].unsqueeze(0)  # [1, dim]
        
        # Compute cosine similarity
        similarities = F.cosine_similarity(
            target_embedding,
            embeddings_norm,
            dim=1
        )  # [num_nodes]
        
        # Set excluded to -inf
        similarities[target_idx] = -float('inf')
        for idx in exclude_indices:
            if idx < len(similarities):
                similarities[idx] = -float('inf')
        
        # Get top-k
        k = min(k, len(similarities) - 1 - len(exclude_indices))
        if k <= 0:
            return torch.tensor([], dtype=torch.long)
        
        top_k_values, top_k_indices = torch.topk(similarities, k)
        
        return top_k_indices
    
    def save(self, path: str):
        """Сохрани модель"""
        torch.save(self.state_dict(), path)
        logger.info(f"✅ Model saved to {path}")
    
    def load(self, path: str):
        """Загрузи модель"""
        self.load_state_dict(torch.load(path))
        self.eval()
        logger.info(f"✅ Model loaded from {path}")
