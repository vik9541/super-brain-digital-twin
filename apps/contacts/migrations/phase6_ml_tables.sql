-- PHASE 6: Advanced ML Tables Migration
-- Created: 2025-12-12
-- Description: Tables for embeddings, recommendations, churn prediction, sentiment, and clustering

-- Enable pgvector extension for embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- =====================================================
-- TABLE 1: contact_embeddings
-- Stores 1536-dimensional OpenAI embeddings for semantic search
-- =====================================================
CREATE TABLE IF NOT EXISTS contact_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    embedding vector(1536) NOT NULL,  -- OpenAI text-embedding-3-small dimension
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(contact_id)
);

-- Index for fast vector similarity search
CREATE INDEX IF NOT EXISTS idx_contact_embeddings_vector 
ON contact_embeddings USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Index for contact lookups
CREATE INDEX IF NOT EXISTS idx_contact_embeddings_contact_id 
ON contact_embeddings(contact_id);

-- Index for recent updates
CREATE INDEX IF NOT EXISTS idx_contact_embeddings_updated_at 
ON contact_embeddings(updated_at DESC);

COMMENT ON TABLE contact_embeddings IS 'Stores OpenAI embeddings for semantic contact search';
COMMENT ON COLUMN contact_embeddings.embedding IS '1536-dimensional vector from text-embedding-3-small';


-- =====================================================
-- TABLE 2: contact_recommendations
-- Caches "People You Should Know" recommendations
-- =====================================================
CREATE TABLE IF NOT EXISTS contact_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    recommended_contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    recommendation_score DECIMAL(5,3) NOT NULL CHECK (recommendation_score >= 0.0 AND recommendation_score <= 1.0),
    score_components JSONB NOT NULL,  -- {mutual_friends, semantic_similarity, influence_score, same_organization}
    reason TEXT,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '7 days'),
    
    -- Constraints
    UNIQUE(user_contact_id, recommended_contact_id),
    CHECK (user_contact_id != recommended_contact_id)
);

-- Index for user lookups
CREATE INDEX IF NOT EXISTS idx_contact_recommendations_user 
ON contact_recommendations(user_contact_id, recommendation_score DESC);

-- Index for expiration cleanup
CREATE INDEX IF NOT EXISTS idx_contact_recommendations_expires_at 
ON contact_recommendations(expires_at);

-- Index for score-based queries
CREATE INDEX IF NOT EXISTS idx_contact_recommendations_score 
ON contact_recommendations(recommendation_score DESC);

COMMENT ON TABLE contact_recommendations IS 'Cached contact recommendations with expiration';
COMMENT ON COLUMN contact_recommendations.score_components IS 'JSON with weighted components: mutual_friends, semantic_similarity, influence_score, same_organization';


-- =====================================================
-- TABLE 3: churn_predictions
-- Stores ML-based churn risk predictions
-- =====================================================
CREATE TABLE IF NOT EXISTS churn_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    churn_probability DECIMAL(5,3) NOT NULL CHECK (churn_probability >= 0.0 AND churn_probability <= 1.0),
    risk_level VARCHAR(20) NOT NULL CHECK (risk_level IN ('HIGH', 'MEDIUM', 'LOW')),
    features JSONB NOT NULL,  -- {days_since_update, interaction_frequency, inverse_influence, tag_count, community_size}
    interventions JSONB,  -- Array of suggested actions
    predicted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '30 days'),
    
    -- Constraints
    UNIQUE(contact_id)
);

-- Index for contact lookups
CREATE INDEX IF NOT EXISTS idx_churn_predictions_contact_id 
ON churn_predictions(contact_id);

-- Index for risk level queries
CREATE INDEX IF NOT EXISTS idx_churn_predictions_risk_level 
ON churn_predictions(risk_level, churn_probability DESC);

-- Index for high-risk contacts
CREATE INDEX IF NOT EXISTS idx_churn_predictions_high_risk 
ON churn_predictions(churn_probability DESC) 
WHERE risk_level = 'HIGH';

-- Index for expiration cleanup
CREATE INDEX IF NOT EXISTS idx_churn_predictions_expires_at 
ON churn_predictions(expires_at);

COMMENT ON TABLE churn_predictions IS 'ML-based predictions of contact churn risk';
COMMENT ON COLUMN churn_predictions.features IS 'JSON with 5 normalized features used for prediction';
COMMENT ON COLUMN churn_predictions.interventions IS 'Array of suggested actions to prevent churn';


-- =====================================================
-- TABLE 4: contact_sentiment
-- Stores multi-component sentiment analysis results
-- =====================================================
CREATE TABLE IF NOT EXISTS contact_sentiment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    overall_sentiment DECIMAL(4,3) NOT NULL CHECK (overall_sentiment >= -1.0 AND overall_sentiment <= 1.0),
    sentiment_label VARCHAR(30) NOT NULL CHECK (sentiment_label IN ('Very Positive', 'Positive', 'Neutral', 'Negative', 'Very Negative')),
    components JSONB NOT NULL,  -- {tags, notes, interactions}
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '14 days'),
    
    -- Constraints
    UNIQUE(contact_id)
);

-- Index for contact lookups
CREATE INDEX IF NOT EXISTS idx_contact_sentiment_contact_id 
ON contact_sentiment(contact_id);

-- Index for sentiment-based queries
CREATE INDEX IF NOT EXISTS idx_contact_sentiment_label 
ON contact_sentiment(sentiment_label, overall_sentiment DESC);

-- Index for positive contacts
CREATE INDEX IF NOT EXISTS idx_contact_sentiment_positive 
ON contact_sentiment(overall_sentiment DESC) 
WHERE sentiment_label IN ('Very Positive', 'Positive');

-- Index for negative contacts (needs attention)
CREATE INDEX IF NOT EXISTS idx_contact_sentiment_negative 
ON contact_sentiment(overall_sentiment ASC) 
WHERE sentiment_label IN ('Negative', 'Very Negative');

-- Index for expiration cleanup
CREATE INDEX IF NOT EXISTS idx_contact_sentiment_expires_at 
ON contact_sentiment(expires_at);

COMMENT ON TABLE contact_sentiment IS 'Multi-component sentiment analysis for contacts';
COMMENT ON COLUMN contact_sentiment.components IS 'JSON with tag-based, notes-based, and interaction-based sentiment scores';


-- =====================================================
-- TABLE 5: contact_clusters
-- Stores K-means clustering results for interest groups
-- =====================================================
CREATE TABLE IF NOT EXISTS contact_clusters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cluster_id INTEGER NOT NULL,
    contact_ids UUID[] NOT NULL,  -- Array of contact UUIDs in this cluster
    cluster_size INTEGER NOT NULL,
    cluster_topics TEXT[],  -- Array of common tags/topics
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(cluster_id),
    CHECK (cluster_size > 0),
    CHECK (array_length(contact_ids, 1) = cluster_size)
);

-- Index for cluster lookups
CREATE INDEX IF NOT EXISTS idx_contact_clusters_cluster_id 
ON contact_clusters(cluster_id);

-- Index for size-based queries
CREATE INDEX IF NOT EXISTS idx_contact_clusters_size 
ON contact_clusters(cluster_size DESC);

-- Index for contact membership (GIN for array contains)
CREATE INDEX IF NOT EXISTS idx_contact_clusters_contact_ids 
ON contact_clusters USING gin(contact_ids);

-- Index for topic searches
CREATE INDEX IF NOT EXISTS idx_contact_clusters_topics 
ON contact_clusters USING gin(cluster_topics);

COMMENT ON TABLE contact_clusters IS 'K-means clustering results grouping contacts by interests';
COMMENT ON COLUMN contact_clusters.contact_ids IS 'Array of all contact UUIDs belonging to this cluster';
COMMENT ON COLUMN contact_clusters.cluster_topics IS 'Inferred topics from common tags and organizations';


-- =====================================================
-- TABLE 6: ml_models
-- Stores serialized ML models (Random Forest, etc.)
-- =====================================================
CREATE TABLE IF NOT EXISTS ml_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name VARCHAR(100) NOT NULL,
    model_pickle BYTEA NOT NULL,  -- Pickled scikit-learn model
    accuracy DECIMAL(5,3),
    precision DECIMAL(5,3),
    recall DECIMAL(5,3),
    f1_score DECIMAL(5,3),
    training_samples INTEGER,
    test_samples INTEGER,
    hyperparameters JSONB,
    trained_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Constraints
    UNIQUE(model_name, version)
);

-- Index for model lookups
CREATE INDEX IF NOT EXISTS idx_ml_models_name 
ON ml_models(model_name, version DESC);

-- Index for active models
CREATE INDEX IF NOT EXISTS idx_ml_models_active 
ON ml_models(model_name) 
WHERE is_active = TRUE;

-- Index for performance queries
CREATE INDEX IF NOT EXISTS idx_ml_models_accuracy 
ON ml_models(accuracy DESC);

COMMENT ON TABLE ml_models IS 'Stores trained ML models with versioning';
COMMENT ON COLUMN ml_models.model_pickle IS 'Serialized scikit-learn model using pickle';
COMMENT ON COLUMN ml_models.hyperparameters IS 'JSON with model configuration (n_estimators, max_depth, etc.)';


-- =====================================================
-- HELPER FUNCTIONS
-- =====================================================

-- Function: Find similar contacts using cosine similarity
CREATE OR REPLACE FUNCTION find_similar_contacts(
    target_contact_id UUID,
    top_n INTEGER DEFAULT 10
)
RETURNS TABLE (
    contact_id UUID,
    similarity DECIMAL(5,3)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ce.contact_id,
        (1 - (ce.embedding <=> te.embedding))::DECIMAL(5,3) AS similarity
    FROM contact_embeddings ce
    CROSS JOIN (
        SELECT embedding FROM contact_embeddings WHERE contact_id = target_contact_id
    ) te
    WHERE ce.contact_id != target_contact_id
    ORDER BY ce.embedding <=> te.embedding
    LIMIT top_n;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION find_similar_contacts IS 'Returns top-N most similar contacts using cosine similarity';


-- Function: Get cluster for a contact
CREATE OR REPLACE FUNCTION get_contact_cluster(
    target_contact_id UUID
)
RETURNS INTEGER AS $$
DECLARE
    cluster_num INTEGER;
BEGIN
    SELECT cluster_id INTO cluster_num
    FROM contact_clusters
    WHERE target_contact_id = ANY(contact_ids);
    
    RETURN cluster_num;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_contact_cluster IS 'Returns cluster_id for a given contact, or NULL if not clustered';


-- Function: Cleanup expired recommendations
CREATE OR REPLACE FUNCTION cleanup_expired_ml_data()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER := 0;
BEGIN
    -- Delete expired recommendations
    DELETE FROM contact_recommendations WHERE expires_at < NOW();
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Delete expired churn predictions
    DELETE FROM churn_predictions WHERE expires_at < NOW();
    
    -- Delete expired sentiment analysis
    DELETE FROM contact_sentiment WHERE expires_at < NOW();
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION cleanup_expired_ml_data IS 'Removes expired ML predictions and cached results';


-- =====================================================
-- TRIGGERS
-- =====================================================

-- Auto-update updated_at timestamp for contact_embeddings
CREATE OR REPLACE FUNCTION update_contact_embeddings_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_contact_embeddings_timestamp
    BEFORE UPDATE ON contact_embeddings
    FOR EACH ROW
    EXECUTE FUNCTION update_contact_embeddings_timestamp();


-- Auto-update updated_at timestamp for contact_clusters
CREATE OR REPLACE FUNCTION update_contact_clusters_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_contact_clusters_timestamp
    BEFORE UPDATE ON contact_clusters
    FOR EACH ROW
    EXECUTE FUNCTION update_contact_clusters_timestamp();


-- =====================================================
-- GRANTS (adjust as needed for your setup)
-- =====================================================

-- Grant permissions to service role (adjust role name as needed)
-- GRANT ALL ON contact_embeddings TO service_role;
-- GRANT ALL ON contact_recommendations TO service_role;
-- GRANT ALL ON churn_predictions TO service_role;
-- GRANT ALL ON contact_sentiment TO service_role;
-- GRANT ALL ON contact_clusters TO service_role;
-- GRANT ALL ON ml_models TO service_role;


-- =====================================================
-- SAMPLE DATA (for testing)
-- =====================================================

-- Uncomment to insert sample data
/*
INSERT INTO ml_models (model_name, model_pickle, accuracy, precision, recall, training_samples, hyperparameters)
VALUES (
    'churn_predictor',
    '\x80\x03'::bytea,  -- Placeholder pickle bytes
    0.85,
    0.82,
    0.88,
    1000,
    '{"n_estimators": 100, "max_depth": 10, "random_state": 42}'::jsonb
);
*/


-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================

-- Verify tables created
DO $$
DECLARE
    table_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_name IN (
        'contact_embeddings',
        'contact_recommendations',
        'churn_predictions',
        'contact_sentiment',
        'contact_clusters',
        'ml_models'
    );
    
    RAISE NOTICE 'Phase 6 Migration Complete: % tables created', table_count;
END $$;
