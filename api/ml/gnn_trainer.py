"""
GNN Training Module

Trains Graph Neural Network models using contrastive learning.
"""

import torch
import torch.nn.functional as F
from torch_geometric.data import Data
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class GNNTrainer:
    """Обучение GNN модели"""
    
    def __init__(self, device='cpu'):
        self.device = torch.device(device)
        self.model = None
        self.optimizer = None
        
        logger.info(f"✅ GNNTrainer initialized (device: {device})")
    
    def create_model(self, in_features=3, hidden_dim=64, out_dim=128):
        """Создай новую модель"""
        from api.ml.gnn_model import ContactRecommenderGNN
        
        self.model = ContactRecommenderGNN(
            in_features=in_features,
            hidden_dim=hidden_dim,
            out_dim=out_dim
        ).to(self.device)
        
        logger.info("✅ Model created")
        return self.model
    
    def compute_contrastive_loss(
        self,
        embeddings: torch.Tensor,
        edge_index: torch.Tensor,
        negative_samples: int = 5
    ) -> torch.Tensor:
        """
        Contrastive loss: похожие nodes должны быть близко, непохожие далеко
        
        Для connected edges: similarity -> 1
        Для non-connected: similarity -> -1
        """
        
        if edge_index.shape[1] == 0:
            # No edges - return dummy loss
            return torch.tensor(0.0, device=self.device, requires_grad=True)
        
        # Get positive pairs (connected nodes)
        pos_src, pos_dst = edge_index
        
        # Compute positive scores (should be high)
        pos_scores = F.cosine_similarity(
            embeddings[pos_src],
            embeddings[pos_dst],
            dim=1
        )  # [num_edges]
        
        # Positive loss: push towards +1
        pos_loss = F.relu(1 - pos_scores).mean()
        
        # Negative samples
        num_nodes = embeddings.shape[0]
        neg_loss = 0
        
        for _ in range(negative_samples):
            # Random negative pairs
            neg_idx = torch.randperm(num_nodes, device=self.device)[:len(pos_src)]
            
            neg_scores = F.cosine_similarity(
                embeddings[pos_src],
                embeddings[neg_idx],
                dim=1
            )
            
            # Negative loss: push towards -1
            neg_loss += F.relu(neg_scores + 1).mean()
        
        total_loss = pos_loss + neg_loss / negative_samples
        
        return total_loss
    
    async def train(
        self,
        graph_data: Data,
        epochs: int = 20,
        learning_rate: float = 0.01,
        negative_samples: int = 5
    ):
        """
        Обучи модель
        
        Args:
            graph_data: PyTorch Geometric Data object
            epochs: Кол-во эпох
            learning_rate: Learning rate
            negative_samples: Кол-во негативных сэмплов на позитивный
        """
        
        if self.model is None:
            raise ValueError("Model not created. Call create_model() first")
        
        # Move graph to device
        x = graph_data.x.to(self.device)
        edge_index = graph_data.edge_index.to(self.device)
        
        # Optimizer
        self.optimizer = torch.optim.Adam(
            self.model.parameters(),
            lr=learning_rate
        )
        
        logger.info(f"Starting training for {epochs} epochs")
        
        self.model.train()
        
        for epoch in range(epochs):
            self.optimizer.zero_grad()
            
            # Forward pass
            embeddings = self.model(x, edge_index)
            
            # Compute loss
            loss = self.compute_contrastive_loss(
                embeddings,
                edge_index,
                negative_samples=negative_samples
            )
            
            # Backward pass
            loss.backward()
            self.optimizer.step()
            
            if (epoch + 1) % 5 == 0 or epoch == 0:
                logger.info(f"Epoch {epoch + 1}/{epochs}, Loss: {loss.item():.4f}")
        
        logger.info("✅ Training complete")
        
        return loss.item()
    
    def predict(self, x, edge_index):
        """Получи embeddings"""
        if self.model is None:
            raise ValueError("Model not created")
        
        self.model.eval()
        
        with torch.no_grad():
            x = x.to(self.device)
            edge_index = edge_index.to(self.device)
            embeddings = self.model(x, edge_index)
        
        return embeddings.cpu()
    
    def save_model(self, path: str):
        """Сохрани модель"""
        if self.model is None:
            raise ValueError("No model to save")
        
        self.model.save(path)
    
    def load_model(self, path: str, in_features=3, hidden_dim=64, out_dim=128):
        """Загрузи модель"""
        self.create_model(in_features, hidden_dim, out_dim)
        self.model.load(path)
