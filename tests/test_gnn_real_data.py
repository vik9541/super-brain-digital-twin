"""
Phase 8: GNN Real Data Tests
Tests with actual workspace data from Supabase
"""

import pytest
import os
from api.ml.gnn_recommender import GNNRecommender


@pytest.fixture
def supabase_client():
    """Get real Supabase client (requires env vars)"""
    from supabase import create_client
    
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    if not url or not key:
        pytest.skip("SUPABASE_URL and SUPABASE_KEY environment variables required")
    
    return create_client(url, key)


@pytest.fixture
def test_workspace_id(supabase_client):
    """Get a workspace with contacts for testing"""
    # Query for a workspace that has contacts
    result = supabase_client.table('workspaces').select('id').limit(1).execute()
    
    if not result.data:
        pytest.skip("No workspaces found in database")
    
    return result.data[0]['id']


@pytest.fixture
def test_contact_id(supabase_client, test_workspace_id):
    """Get a contact from the test workspace"""
    result = supabase_client.table('apple_contacts') \
        .select('id') \
        .eq('workspace_id', test_workspace_id) \
        .limit(1) \
        .execute()
    
    if not result.data:
        pytest.skip("No contacts found in test workspace")
    
    return result.data[0]['id']


@pytest.mark.integration
@pytest.mark.asyncio
async def test_recommendations_with_real_workspace(supabase_client, test_workspace_id, test_contact_id):
    """Test recommendations with real workspace data"""
    
    recommender = GNNRecommender(supabase_client)
    
    # Get recommendations
    result = await recommender.get_recommendations(
        workspace_id=test_workspace_id,
        contact_id=test_contact_id,
        k=20,
        explain=True
    )
    
    print(f"\n📊 Real Data Test Results:")
    print(f"   Workspace: {test_workspace_id}")
    print(f"   Target Contact: {test_contact_id}")
    print(f"   Recommendations: {len(result['recommendations'])}")
    
    # Validate response
    assert 'recommendations' in result
    assert 'method' in result
    assert result['method'] == 'graph_neural_network'
    
    recommendations = result['recommendations']
    
    # Should get some recommendations (unless graph is too small)
    if len(recommendations) > 0:
        print(f"\n   Top 5 Recommendations:")
        for i, rec in enumerate(recommendations[:5], 1):
            print(f"   {i}. {rec['name']} (score: {rec['similarity_score']:.3f})")
        
        # Validate structure
        for rec in recommendations:
            assert 'id' in rec
            assert 'name' in rec
            assert 'similarity_score' in rec
            assert 'confidence' in rec
            assert 'reason' in rec
            
            # Validate ranges
            assert 0 <= rec['similarity_score'] <= 1
            assert 0.7 <= rec['confidence'] <= 0.99


@pytest.mark.integration
@pytest.mark.asyncio
async def test_training_with_real_data(supabase_client, test_workspace_id):
    """Test model training with real workspace data"""
    
    recommender = GNNRecommender(supabase_client)
    
    # Train model
    result = await recommender.train_model(
        workspace_id=test_workspace_id,
        epochs=10,
        learning_rate=0.01
    )
    
    print(f"\n📊 Training Results:")
    print(f"   Status: {result['status']}")
    print(f"   Nodes: {result['nodes']}")
    print(f"   Edges: {result['edges']}")
    print(f"   Epochs: {result['epochs']}")
    
    # Validate training result
    assert result['status'] == 'training_complete'
    assert result['nodes'] > 0
    assert result['epochs'] == 10
    
    # Model should be cached
    assert test_workspace_id in recommender.model_cache


@pytest.mark.integration
@pytest.mark.asyncio
async def test_model_persistence(supabase_client, test_workspace_id, test_contact_id, tmp_path):
    """Test model save and load with real data"""
    
    recommender = GNNRecommender(supabase_client)
    
    # Get recommendations (trains model)
    result1 = await recommender.get_recommendations(
        workspace_id=test_workspace_id,
        contact_id=test_contact_id,
        k=10
    )
    
    # Save model
    model_path = tmp_path / f"{test_workspace_id}.pt"
    cache_entry = recommender.model_cache[test_workspace_id]
    cache_entry['model'].save(str(model_path))
    
    # Clear cache
    recommender.model_cache.clear()
    
    # Load model
    from api.ml.gnn_model import ContactRecommenderGNN
    loaded_model = ContactRecommenderGNN()
    loaded_model.load(str(model_path))
    
    # Add back to cache
    recommender.model_cache[test_workspace_id] = {
        'model': loaded_model,
        'embeddings': cache_entry['embeddings'],
        'contact_ids': cache_entry['contact_ids'],
        'id_to_idx': cache_entry['id_to_idx'],
        'timestamp': cache_entry['timestamp']
    }
    
    # Get recommendations again
    result2 = await recommender.get_recommendations(
        workspace_id=test_workspace_id,
        contact_id=test_contact_id,
        k=10
    )
    
    # Results should be similar (same model)
    assert len(result1['recommendations']) == len(result2['recommendations'])


@pytest.mark.integration
@pytest.mark.asyncio
async def test_multiple_workspaces(supabase_client):
    """Test handling multiple workspaces"""
    
    # Get multiple workspace IDs
    result = supabase_client.table('workspaces').select('id').limit(3).execute()
    
    if len(result.data) < 2:
        pytest.skip("Need at least 2 workspaces for this test")
    
    workspace_ids = [w['id'] for w in result.data[:2]]
    
    recommender = GNNRecommender(supabase_client)
    
    # Train models for both workspaces
    for workspace_id in workspace_ids:
        await recommender.train_model(workspace_id=workspace_id, epochs=5)
    
    # Both should be cached
    for workspace_id in workspace_ids:
        assert workspace_id in recommender.model_cache
    
    print(f"\n📊 Multi-Workspace Test:")
    print(f"   Cached models: {len(recommender.model_cache)}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_recommendation_quality(supabase_client, test_workspace_id, test_contact_id):
    """Test recommendation quality metrics"""
    
    recommender = GNNRecommender(supabase_client)
    
    # Get recommendations
    result = await recommender.get_recommendations(
        workspace_id=test_workspace_id,
        contact_id=test_contact_id,
        k=20
    )
    
    recommendations = result['recommendations']
    
    if len(recommendations) == 0:
        pytest.skip("No recommendations available")
    
    # Check similarity scores are decreasing
    scores = [rec['similarity_score'] for rec in recommendations]
    assert scores == sorted(scores, reverse=True), "Scores should be in descending order"
    
    # Check confidence scores are reasonable
    confidences = [rec['confidence'] for rec in recommendations]
    assert all(0.7 <= c <= 0.99 for c in confidences), "Confidence should be in [0.7, 0.99]"
    
    # Top recommendation should have high confidence
    if recommendations:
        assert recommendations[0]['confidence'] >= 0.8, "Top recommendation should have high confidence"
        
        print(f"\n📊 Quality Metrics:")
        print(f"   Top similarity: {scores[0]:.3f}")
        print(f"   Top confidence: {confidences[0]:.3f}")
        print(f"   Avg similarity: {sum(scores)/len(scores):.3f}")
        print(f"   Avg confidence: {sum(confidences)/len(confidences):.3f}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_edge_cases_real_data(supabase_client):
    """Test edge cases with real data"""
    
    recommender = GNNRecommender(supabase_client)
    
    # Test 1: Invalid workspace
    try:
        await recommender.get_recommendations(
            workspace_id='invalid_workspace_id',
            contact_id='some_contact',
            k=10
        )
    except Exception as e:
        # Should raise or return empty gracefully
        assert 'workspace' in str(e).lower() or 'not found' in str(e).lower()
    
    # Test 2: Invalid contact (but valid workspace)
    result = supabase_client.table('workspaces').select('id').limit(1).execute()
    if result.data:
        workspace_id = result.data[0]['id']
        try:
            result = await recommender.get_recommendations(
                workspace_id=workspace_id,
                contact_id='invalid_contact_id',
                k=10
            )
            # If it returns, should be empty or handle gracefully
            assert isinstance(result, dict)
        except Exception as e:
            assert 'contact' in str(e).lower()


if __name__ == '__main__':
    # Run with: pytest tests/test_gnn_real_data.py -v -s -m integration
    pytest.main([__file__, '-v', '-s', '-m', 'integration'])
