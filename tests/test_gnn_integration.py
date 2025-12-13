"""
Phase 8: GNN Integration Tests
End-to-end tests for GNN recommendation system
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from api.ml.gnn_recommender import GNNRecommender


@pytest.fixture
def mock_supabase():
    """Mock Supabase client for testing"""
    client = Mock()
    
    # Mock contacts data
    mock_contacts = [
        {
            'id': f'contact_{i}',
            'name': f'Contact {i}',
            'email': f'contact{i}@test.com',
            'influence_score': 50 + i,
            'organization': 'Test Org' if i % 2 == 0 else None,
            'tags': ['tech', 'business'][:i % 3]
        }
        for i in range(20)
    ]
    
    # Mock interactions data
    mock_interactions = [
        {
            'contact1_id': f'contact_{i}',
            'contact2_id': f'contact_{(i+1)%20}',
            'interaction_frequency': 5 - (i % 5)
        }
        for i in range(40)
    ]
    
    # Setup table mocks
    client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = mock_contacts
    client.table.return_value.select.return_value.execute.return_value.data = mock_interactions
    
    return client


@pytest.fixture
def mock_graph_builder():
    """Mock graph builder"""
    with patch('api.ml.gnn_recommender.ContactGraphBuilder') as mock:
        builder = Mock()
        
        # Mock graph data
        import torch
        from torch_geometric.data import Data
        
        x = torch.randn(20, 3)
        edge_index = torch.randint(0, 20, (2, 40))
        graph_data = Data(x=x, edge_index=edge_index, num_nodes=20)
        
        contact_ids = [f'contact_{i}' for i in range(20)]
        id_to_idx = {cid: i for i, cid in enumerate(contact_ids)}
        
        async def mock_build_graph(workspace_id):
            return graph_data, contact_ids, id_to_idx
        
        builder.build_graph_for_workspace = AsyncMock(side_effect=mock_build_graph)
        mock.return_value = builder
        
        yield builder


@pytest.mark.asyncio
async def test_get_recommendations_basic(mock_supabase, mock_graph_builder):
    """Test basic recommendation retrieval"""
    recommender = GNNRecommender(mock_supabase)
    
    result = await recommender.get_recommendations(
        workspace_id='test_workspace',
        contact_id='contact_0',
        k=10,
        explain=True
    )
    
    # Validate response structure
    assert 'recommendations' in result
    assert 'method' in result
    assert 'accuracy' in result
    
    # Check method
    assert result['method'] == 'graph_neural_network'
    assert result['accuracy'] == 0.95
    
    # Check recommendations
    recommendations = result['recommendations']
    assert len(recommendations) <= 10
    
    # Validate each recommendation
    for rec in recommendations:
        assert 'id' in rec
        assert 'name' in rec
        assert 'similarity_score' in rec
        assert 'confidence' in rec
        assert 'rank' in rec
        
        # Validate ranges
        assert 0 <= rec['similarity_score'] <= 1
        assert 0.7 <= rec['confidence'] <= 0.99
        assert rec['rank'] >= 1


@pytest.mark.asyncio
async def test_get_recommendations_with_explanation(mock_supabase, mock_graph_builder):
    """Test recommendations include explanations"""
    recommender = GNNRecommender(mock_supabase)
    
    result = await recommender.get_recommendations(
        workspace_id='test_workspace',
        contact_id='contact_0',
        k=5,
        explain=True
    )
    
    recommendations = result['recommendations']
    
    for rec in recommendations:
        assert 'reason' in rec
        assert isinstance(rec['reason'], str)
        assert len(rec['reason']) > 0


@pytest.mark.asyncio
async def test_recommendations_exclude_self(mock_supabase, mock_graph_builder):
    """Test recommendations don't include the target contact"""
    recommender = GNNRecommender(mock_supabase)
    
    target_id = 'contact_5'
    
    result = await recommender.get_recommendations(
        workspace_id='test_workspace',
        contact_id=target_id,
        k=10
    )
    
    recommendations = result['recommendations']
    recommended_ids = [rec['id'] for rec in recommendations]
    
    # Target should not be in recommendations
    assert target_id not in recommended_ids


@pytest.mark.asyncio
async def test_model_caching(mock_supabase, mock_graph_builder):
    """Test model is cached after first use"""
    recommender = GNNRecommender(mock_supabase)
    workspace_id = 'test_workspace'
    
    # First call - should create model
    result1 = await recommender.get_recommendations(
        workspace_id=workspace_id,
        contact_id='contact_0',
        k=5
    )
    
    # Check cache
    assert workspace_id in recommender.model_cache
    cache_entry = recommender.model_cache[workspace_id]
    assert 'model' in cache_entry
    assert 'embeddings' in cache_entry
    assert 'contact_ids' in cache_entry
    assert 'timestamp' in cache_entry
    
    # Second call - should use cached model
    result2 = await recommender.get_recommendations(
        workspace_id=workspace_id,
        contact_id='contact_1',
        k=5
    )
    
    # Both results should be valid
    assert len(result1['recommendations']) > 0
    assert len(result2['recommendations']) > 0


@pytest.mark.asyncio
async def test_train_model_endpoint(mock_supabase, mock_graph_builder):
    """Test model training functionality"""
    recommender = GNNRecommender(mock_supabase)
    workspace_id = 'test_workspace'
    
    # Train model
    result = await recommender.train_model(
        workspace_id=workspace_id,
        epochs=5,
        learning_rate=0.01
    )
    
    # Validate training result
    assert 'status' in result
    assert result['status'] == 'training_complete'
    assert 'epochs' in result
    assert result['epochs'] == 5
    assert 'nodes' in result
    assert 'edges' in result
    
    # Model should be cached
    assert workspace_id in recommender.model_cache


@pytest.mark.asyncio
async def test_different_k_values(mock_supabase, mock_graph_builder):
    """Test recommendations with different k values"""
    recommender = GNNRecommender(mock_supabase)
    
    k_values = [5, 10, 20]
    
    for k in k_values:
        result = await recommender.get_recommendations(
            workspace_id='test_workspace',
            contact_id='contact_0',
            k=k
        )
        
        recommendations = result['recommendations']
        # Should get at most k recommendations
        assert len(recommendations) <= k


@pytest.mark.asyncio
async def test_recommendations_sorted_by_similarity(mock_supabase, mock_graph_builder):
    """Test recommendations are sorted by similarity (descending)"""
    recommender = GNNRecommender(mock_supabase)
    
    result = await recommender.get_recommendations(
        workspace_id='test_workspace',
        contact_id='contact_0',
        k=10
    )
    
    recommendations = result['recommendations']
    similarities = [rec['similarity_score'] for rec in recommendations]
    
    # Check descending order
    assert similarities == sorted(similarities, reverse=True)


@pytest.mark.asyncio
async def test_rank_assignment(mock_supabase, mock_graph_builder):
    """Test recommendations have correct rank assignments"""
    recommender = GNNRecommender(mock_supabase)
    
    result = await recommender.get_recommendations(
        workspace_id='test_workspace',
        contact_id='contact_0',
        k=10
    )
    
    recommendations = result['recommendations']
    ranks = [rec['rank'] for rec in recommendations]
    
    # Ranks should be 1, 2, 3, ..., len(recommendations)
    assert ranks == list(range(1, len(recommendations) + 1))


@pytest.mark.asyncio
async def test_error_handling_invalid_contact(mock_supabase, mock_graph_builder):
    """Test error handling for invalid contact ID"""
    recommender = GNNRecommender(mock_supabase)
    
    # This should handle gracefully
    try:
        result = await recommender.get_recommendations(
            workspace_id='test_workspace',
            contact_id='nonexistent_contact',
            k=10
        )
        # If it returns empty, that's acceptable
        assert isinstance(result, dict)
    except Exception as e:
        # Or it raises a clear error
        assert 'contact' in str(e).lower() or 'not found' in str(e).lower()


@pytest.mark.asyncio
async def test_concurrent_requests(mock_supabase, mock_graph_builder):
    """Test handling concurrent recommendation requests"""
    recommender = GNNRecommender(mock_supabase)
    
    # Create multiple concurrent requests
    tasks = [
        recommender.get_recommendations('test_workspace', f'contact_{i}', k=5)
        for i in range(5)
    ]
    
    results = await asyncio.gather(*tasks)
    
    # All requests should succeed
    assert len(results) == 5
    for result in results:
        assert 'recommendations' in result
        assert len(result['recommendations']) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
