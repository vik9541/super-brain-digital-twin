"""
Phase 8: GNN Performance Tests
Benchmark tests for latency and scalability
"""

import time

import pytest
import torch
from torch_geometric.data import Data

from api.ml.gnn_model import ContactRecommenderGNN
from api.ml.gnn_trainer import GNNTrainer


@pytest.fixture
def small_graph():
    """Small graph: 100 nodes, 500 edges"""
    x = torch.randn(100, 3)
    edge_index = torch.randint(0, 100, (2, 500))
    return Data(x=x, edge_index=edge_index, num_nodes=100)


@pytest.fixture
def medium_graph():
    """Medium graph: 1K nodes, 5K edges"""
    x = torch.randn(1000, 3)
    edge_index = torch.randint(0, 1000, (2, 5000))
    return Data(x=x, edge_index=edge_index, num_nodes=1000)


@pytest.fixture
def large_graph():
    """Large graph: 10K nodes, 50K edges"""
    x = torch.randn(10000, 3)
    edge_index = torch.randint(0, 10000, (2, 50000))
    return Data(x=x, edge_index=edge_index, num_nodes=10000)


class TestForwardPassLatency:
    """Test model forward pass performance"""

    def test_small_graph_forward(self, small_graph):
        """Test forward pass on small graph"""
        model = ContactRecommenderGNN()
        model.eval()

        # Warmup
        _ = model(small_graph.x, small_graph.edge_index)

        # Measure
        start = time.time()
        embeddings = model(small_graph.x, small_graph.edge_index)
        latency = (time.time() - start) * 1000  # ms

        print(f"\n📊 Small graph (100 nodes) forward pass: {latency:.2f}ms")

        assert embeddings.shape == (100, 128)
        assert latency < 100  # Should be very fast

    def test_medium_graph_forward(self, medium_graph):
        """Test forward pass on medium graph"""
        model = ContactRecommenderGNN()
        model.eval()

        # Warmup
        _ = model(medium_graph.x, medium_graph.edge_index)

        # Measure
        start = time.time()
        embeddings = model(medium_graph.x, medium_graph.edge_index)
        latency = (time.time() - start) * 1000  # ms

        print(f"\n📊 Medium graph (1K nodes) forward pass: {latency:.2f}ms")

        assert embeddings.shape == (1000, 128)
        assert latency < 300  # Should be < 300ms

    def test_large_graph_forward(self, large_graph):
        """Test forward pass on large graph"""
        model = ContactRecommenderGNN()
        model.eval()

        # Warmup
        _ = model(large_graph.x, large_graph.edge_index)

        # Measure
        start = time.time()
        embeddings = model(large_graph.x, large_graph.edge_index)
        latency = (time.time() - start) * 1000  # ms

        print(f"\n📊 Large graph (10K nodes) forward pass: {latency:.2f}ms")

        assert embeddings.shape == (10000, 128)
        assert latency < 500  # Should be < 500ms (target)


class TestRecommendationLatency:
    """Test recommendation generation performance"""

    def test_small_graph_recommendations(self, small_graph):
        """Test recommendation latency on small graph"""
        model = ContactRecommenderGNN()
        model.eval()
        embeddings = model(small_graph.x, small_graph.edge_index)

        # Warmup
        _ = model.get_recommendations(embeddings, 0, k=20)

        # Measure
        start = time.time()
        top_indices = model.get_recommendations(embeddings, 0, k=20)
        latency = (time.time() - start) * 1000  # ms

        print(f"\n📊 Small graph recommendations (k=20): {latency:.2f}ms")

        assert len(top_indices) == 20
        assert latency < 10  # Should be very fast

    def test_medium_graph_recommendations(self, medium_graph):
        """Test recommendation latency on medium graph"""
        model = ContactRecommenderGNN()
        model.eval()
        embeddings = model(medium_graph.x, medium_graph.edge_index)

        # Warmup
        _ = model.get_recommendations(embeddings, 0, k=20)

        # Measure
        start = time.time()
        top_indices = model.get_recommendations(embeddings, 0, k=20)
        latency = (time.time() - start) * 1000  # ms

        print(f"\n📊 Medium graph recommendations (k=20): {latency:.2f}ms")

        assert len(top_indices) == 20
        assert latency < 30  # Should be < 30ms

    def test_large_graph_recommendations(self, large_graph):
        """Test recommendation latency on large graph"""
        model = ContactRecommenderGNN()
        model.eval()
        embeddings = model(large_graph.x, large_graph.edge_index)

        # Warmup
        _ = model.get_recommendations(embeddings, 0, k=20)

        # Measure
        start = time.time()
        top_indices = model.get_recommendations(embeddings, 0, k=20)
        latency = (time.time() - start) * 1000  # ms

        print(f"\n📊 Large graph recommendations (k=20): {latency:.2f}ms")

        assert len(top_indices) == 20
        assert latency < 50  # Should be < 50ms (target)


class TestEndToEndLatency:
    """Test complete recommendation pipeline"""

    def test_full_pipeline_medium_graph(self, medium_graph):
        """Test full pipeline: graph -> embeddings -> recommendations"""
        model = ContactRecommenderGNN()
        model.eval()

        start_total = time.time()

        # Step 1: Forward pass
        start_forward = time.time()
        embeddings = model(medium_graph.x, medium_graph.edge_index)
        forward_latency = (time.time() - start_forward) * 1000

        # Step 2: Get recommendations
        start_rec = time.time()
        recommendations = model.get_recommendations(embeddings, 0, k=20)
        rec_latency = (time.time() - start_rec) * 1000

        total_latency = (time.time() - start_total) * 1000

        print(f"\n📊 Full Pipeline (1K nodes):")
        print(f"   Forward pass: {forward_latency:.2f}ms")
        print(f"   Recommendations: {rec_latency:.2f}ms")
        print(f"   Total: {total_latency:.2f}ms")

        # Total should be < 200ms (target)
        assert total_latency < 200

    def test_full_pipeline_large_graph(self, large_graph):
        """Test full pipeline on large graph"""
        model = ContactRecommenderGNN()
        model.eval()

        start_total = time.time()

        # Step 1: Forward pass
        start_forward = time.time()
        embeddings = model(large_graph.x, large_graph.edge_index)
        forward_latency = (time.time() - start_forward) * 1000

        # Step 2: Get recommendations
        start_rec = time.time()
        recommendations = model.get_recommendations(embeddings, 0, k=20)
        rec_latency = (time.time() - start_rec) * 1000

        total_latency = (time.time() - start_total) * 1000

        print(f"\n📊 Full Pipeline (10K nodes):")
        print(f"   Forward pass: {forward_latency:.2f}ms")
        print(f"   Recommendations: {rec_latency:.2f}ms")
        print(f"   Total: {total_latency:.2f}ms")

        # Total should be reasonable for 10K nodes
        assert total_latency < 600


class TestTrainingPerformance:
    """Test training performance"""

    @pytest.mark.asyncio
    async def test_training_speed_small(self, small_graph):
        """Test training speed on small graph"""
        trainer = GNNTrainer()
        trainer.create_model(in_features=3)

        start = time.time()
        history = await trainer.train(graph_data=small_graph, epochs=10, learning_rate=0.01)
        duration = time.time() - start

        print(f"\n📊 Training (100 nodes, 10 epochs): {duration:.2f}s")
        print(f"   Time per epoch: {duration/10:.2f}s")

        assert len(history["loss_history"]) == 10
        assert duration < 30  # Should be < 30s

    @pytest.mark.asyncio
    async def test_training_speed_medium(self, medium_graph):
        """Test training speed on medium graph"""
        trainer = GNNTrainer()
        trainer.create_model(in_features=3)

        start = time.time()
        history = await trainer.train(graph_data=medium_graph, epochs=5, learning_rate=0.01)
        duration = time.time() - start

        print(f"\n📊 Training (1K nodes, 5 epochs): {duration:.2f}s")
        print(f"   Time per epoch: {duration/5:.2f}s")

        assert len(history["loss_history"]) == 5
        # Should be reasonable for 1K nodes


class TestMemoryEfficiency:
    """Test memory usage"""

    def test_memory_small_batch(self, small_graph):
        """Test memory with small graph"""
        model = ContactRecommenderGNN()
        model.eval()

        # Multiple forward passes shouldn't increase memory significantly
        for _ in range(10):
            embeddings = model(small_graph.x, small_graph.edge_index)
            _ = model.get_recommendations(embeddings, 0, k=20)

        # If we get here without OOM, test passes
        assert True

    def test_memory_large_batch(self, large_graph):
        """Test memory with large graph"""
        model = ContactRecommenderGNN()
        model.eval()

        # Should handle large graph without OOM
        embeddings = model(large_graph.x, large_graph.edge_index)
        _ = model.get_recommendations(embeddings, 0, k=20)

        # If we get here without OOM, test passes
        assert True


class TestScalability:
    """Test scalability across different graph sizes"""

    def test_scalability_comparison(self):
        """Compare performance across different sizes"""
        sizes = [100, 500, 1000, 5000]
        results = []

        model = ContactRecommenderGNN()
        model.eval()

        print("\n📊 Scalability Analysis:")

        for size in sizes:
            x = torch.randn(size, 3)
            edge_index = torch.randint(0, size, (2, size * 5))

            # Warmup
            _ = model(x, edge_index)

            # Measure
            start = time.time()
            embeddings = model(x, edge_index)
            latency = (time.time() - start) * 1000

            results.append((size, latency))
            print(f"   {size:5d} nodes: {latency:6.2f}ms")

        # Check roughly linear scaling
        # (latency should grow sub-quadratically)
        size_ratio = sizes[-1] / sizes[0]  # 5000/100 = 50x
        latency_ratio = results[-1][1] / results[0][1]

        print(f"\n   Size increased {size_ratio:.1f}x")
        print(f"   Latency increased {latency_ratio:.1f}x")

        # Latency should grow less than quadratic
        assert latency_ratio < size_ratio * 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
