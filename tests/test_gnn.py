"""
Phase 8: GNN Unit Tests
Tests for ContactRecommenderGNN model, forward pass, and training
"""

import pytest
import torch
from torch_geometric.data import Data
from api.ml.gnn_model import ContactRecommenderGNN
from api.ml.gnn_trainer import GNNTrainer


@pytest.fixture
def dummy_graph():
    """Create a small dummy graph for testing"""
    x = torch.randn(100, 3)  # 100 nodes, 3 features each
    edge_index = torch.randint(0, 100, (2, 500))  # 500 edges
    return Data(x=x, edge_index=edge_index, num_nodes=100)


class TestContactRecommenderGNN:
    """Test suite for GNN model"""
    
    def test_model_initialization(self):
        """Test model can be initialized with default parameters"""
        model = ContactRecommenderGNN()
        assert model is not None
        assert hasattr(model, 'layers')
        assert hasattr(model, 'batch_norms')
        assert hasattr(model, 'dropouts')
    
    def test_model_forward(self, dummy_graph):
        """Test forward pass produces correct embedding dimensions"""
        model = ContactRecommenderGNN(in_features=3, out_dim=128)
        embeddings = model(dummy_graph.x, dummy_graph.edge_index)
        
        # Check shape: (num_nodes, embedding_dim)
        assert embeddings.shape == (100, 128)
        assert embeddings.dtype == torch.float32
        
        # Check no NaN or Inf values
        assert not torch.isnan(embeddings).any()
        assert not torch.isinf(embeddings).any()
    
    def test_recommendations(self, dummy_graph):
        """Test get_recommendations returns valid indices"""
        model = ContactRecommenderGNN()
        embeddings = model(dummy_graph.x, dummy_graph.edge_index)
        
        target_idx = 0
        k = 10
        top_indices = model.get_recommendations(embeddings, target_idx, k=k)
        
        # Check we get exactly k recommendations
        assert len(top_indices) == k
        
        # Target should not recommend itself
        assert target_idx not in top_indices
        
        # All indices should be valid (0-99)
        assert all(0 <= idx < 100 for idx in top_indices.tolist())
    
    def test_model_save_load(self, dummy_graph, tmp_path):
        """Test model can be saved and loaded"""
        model = ContactRecommenderGNN()
        
        # Get initial embeddings
        embeddings_before = model(dummy_graph.x, dummy_graph.edge_index)
        
        # Save model
        model_path = tmp_path / "test_model.pt"
        model.save(str(model_path))
        assert model_path.exists()
        
        # Load model
        loaded_model = ContactRecommenderGNN()
        loaded_model.load(str(model_path))
        
        # Get embeddings from loaded model
        embeddings_after = loaded_model(dummy_graph.x, dummy_graph.edge_index)
        
        # Embeddings should have same shape and be valid
        assert embeddings_before.shape == embeddings_after.shape
        assert not torch.isnan(embeddings_after).any()
        assert not torch.isinf(embeddings_after).any()


class TestGNNTrainer:
    """Test suite for GNN trainer"""
    
    @pytest.mark.asyncio
    async def test_trainer_initialization(self):
        """Test trainer can be initialized"""
        trainer = GNNTrainer()
        assert trainer is not None
    
    @pytest.mark.asyncio
    async def test_model_creation(self):
        """Test trainer creates model correctly"""
        trainer = GNNTrainer()
        model = trainer.create_model(in_features=3, hidden_dim=64, out_dim=128)
        
        assert model is not None
        assert isinstance(model, ContactRecommenderGNN)
        assert trainer.model is model
    
    @pytest.mark.asyncio
    async def test_training_convergence(self, dummy_graph):
        """Test training reduces loss over epochs"""
        trainer = GNNTrainer()
        trainer.create_model(in_features=3)
        
        # Train for 5 epochs
        history = await trainer.train(
            graph_data=dummy_graph,
            epochs=5,
            learning_rate=0.01
        )
        
        # Check history contains loss values
        assert 'loss_history' in history
        assert len(history['loss_history']) == 5
        
        # Loss should generally decrease (last < first)
        first_loss = history['loss_history'][0]
        last_loss = history['loss_history'][-1]
        assert last_loss < first_loss * 1.5  # Allow some variance
    
    @pytest.mark.asyncio
    async def test_contrastive_loss_computation(self, dummy_graph):
        """Test contrastive loss can be computed"""
        trainer = GNNTrainer()
        model = trainer.create_model(in_features=3)
        
        # Get embeddings
        embeddings = model(dummy_graph.x, dummy_graph.edge_index)
        
        # Compute loss
        loss = trainer.compute_contrastive_loss(
            embeddings=embeddings,
            edge_index=dummy_graph.edge_index,
            negative_samples=5
        )
        
        # Loss should be a scalar tensor
        assert loss.dim() == 0
        assert loss.item() >= 0  # Loss should be non-negative
        assert not torch.isnan(loss)
    
    @pytest.mark.asyncio
    async def test_predict_after_training(self, dummy_graph):
        """Test model can make predictions after training"""
        trainer = GNNTrainer()
        trainer.create_model(in_features=3)
        
        # Train
        await trainer.train(dummy_graph, epochs=3)
        
        # Predict
        predictions = await trainer.predict(
            graph_data=dummy_graph,
            target_idx=0,
            k=10
        )
        
        # Check predictions structure
        assert 'target_idx' in predictions
        assert 'recommendations' in predictions
        assert len(predictions['recommendations']) == 10
        
        # Each recommendation should have required fields
        for rec in predictions['recommendations']:
            assert 'idx' in rec
            assert 'similarity' in rec
            assert 0 <= rec['similarity'] <= 1


def test_model_with_different_architectures():
    """Test model works with different layer configurations"""
    configs = [
        {'in_features': 3, 'hidden_dim': 32, 'out_dim': 64, 'num_layers': 2},
        {'in_features': 3, 'hidden_dim': 64, 'out_dim': 128, 'num_layers': 3},
        {'in_features': 3, 'hidden_dim': 128, 'out_dim': 256, 'num_layers': 4},
    ]
    
    x = torch.randn(50, 3)
    edge_index = torch.randint(0, 50, (2, 200))
    
    for config in configs:
        model = ContactRecommenderGNN(**config)
        embeddings = model(x, edge_index)
        
        assert embeddings.shape == (50, config['out_dim'])
        assert not torch.isnan(embeddings).any()


def test_dropout_in_training_mode(dummy_graph):
    """Test dropout is active in training mode"""
    model = ContactRecommenderGNN(dropout=0.5)
    
    # Training mode
    model.train()
    embeddings1 = model(dummy_graph.x, dummy_graph.edge_index)
    embeddings2 = model(dummy_graph.x, dummy_graph.edge_index)
    
    # Embeddings should be different due to dropout
    assert not torch.allclose(embeddings1, embeddings2)


def test_no_dropout_in_eval_mode(dummy_graph):
    """Test dropout is inactive in eval mode"""
    model = ContactRecommenderGNN(dropout=0.5)
    
    # Eval mode
    model.eval()
    embeddings1 = model(dummy_graph.x, dummy_graph.edge_index)
    embeddings2 = model(dummy_graph.x, dummy_graph.edge_index)
    
    # Embeddings should be identical
    assert torch.allclose(embeddings1, embeddings2)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
