"""
Churn Predictor

Predicts which contacts are likely to "churn" (become inactive) using:
- Days since last update
- Interaction frequency
- Influence score
- Network activity
- Community engagement

Uses Random Forest classifier from scikit-learn.
"""

import logging
import pickle
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score
from supabase import Client

logger = logging.getLogger(__name__)


class ChurnPredictor:
    """Predicts contact churn risk using machine learning."""
    
    # Feature indices
    FEATURE_DAYS_SINCE_UPDATE = 0
    FEATURE_INTERACTION_FREQ = 1
    FEATURE_INVERSE_INFLUENCE = 2
    FEATURE_TAG_COUNT = 3
    FEATURE_COMMUNITY_SIZE = 4
    
    # Risk thresholds
    RISK_HIGH_THRESHOLD = 0.7
    RISK_MEDIUM_THRESHOLD = 0.4
    
    def __init__(self, supabase_client: Client):
        """
        Initialize ChurnPredictor.
        
        Args:
            supabase_client: Supabase client instance
        """
        self.supabase = supabase_client
        self.model: Optional[RandomForestClassifier] = None
        self._load_model()
        
    def _load_model(self) -> None:
        """Load trained model from database or create new one."""
        try:
            # Try to load existing model from ml_models table
            response = self.supabase.table('ml_models').select('*').eq('model_name', 'churn_predictor').execute()
            
            if response.data and len(response.data) > 0:
                model_data = response.data[0]['model_pickle']
                self.model = pickle.loads(model_data)
                logger.info("Loaded existing churn prediction model from database")
            else:
                # Create new untrained model
                self.model = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42,
                    class_weight='balanced'
                )
                logger.info("Created new churn prediction model (untrained)")
                
        except Exception as e:
            logger.warning(f"Could not load model from database: {str(e)}, creating new model")
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                class_weight='balanced'
            )
    
    async def predict_churn(self, contact_id: str) -> Dict:
        """
        Predict churn probability for a contact.
        
        Returns risk level (HIGH/MEDIUM/LOW) and suggested interventions.
        
        Args:
            contact_id: Contact UUID
            
        Returns:
            Dictionary with:
            - contact_id
            - churn_probability (0.0-1.0)
            - risk_level (HIGH/MEDIUM/LOW)
            - features (extracted feature values)
            - interventions (suggested actions)
        """
        try:
            logger.info(f"Predicting churn for contact {contact_id}")
            
            # Extract features
            features = await self._extract_features(contact_id)
            
            if features is None:
                logger.warning(f"Could not extract features for contact {contact_id}")
                return {
                    'contact_id': contact_id,
                    'churn_probability': 0.5,
                    'risk_level': 'UNKNOWN',
                    'features': None,
                    'interventions': ['Unable to analyze - insufficient data']
                }
            
            # Predict using model
            if self.model is None:
                logger.warning("Model not trained, using heuristic")
                # Fallback heuristic: high days since update = high churn
                churn_prob = features[self.FEATURE_DAYS_SINCE_UPDATE]
            else:
                try:
                    features_array = np.array([features])
                    churn_prob = self.model.predict_proba(features_array)[0][1]  # Probability of class 1 (churn)
                except Exception as e:
                    logger.error(f"Model prediction failed: {str(e)}, using heuristic")
                    churn_prob = features[self.FEATURE_DAYS_SINCE_UPDATE]
            
            # Determine risk level
            risk_level = self._risk_level(churn_prob)
            
            # Generate interventions
            interventions = self._suggest_interventions(features)
            
            result = {
                'contact_id': contact_id,
                'churn_probability': round(float(churn_prob), 3),
                'risk_level': risk_level,
                'features': {
                    'days_since_update': features[self.FEATURE_DAYS_SINCE_UPDATE],
                    'interaction_frequency': features[self.FEATURE_INTERACTION_FREQ],
                    'inverse_influence': features[self.FEATURE_INVERSE_INFLUENCE],
                    'tag_count': features[self.FEATURE_TAG_COUNT],
                    'community_size': features[self.FEATURE_COMMUNITY_SIZE]
                },
                'interventions': interventions
            }
            
            logger.info(f"Churn prediction for {contact_id}: {risk_level} ({churn_prob:.3f})")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to predict churn for {contact_id}: {str(e)}")
            return {
                'contact_id': contact_id,
                'churn_probability': 0.5,
                'risk_level': 'ERROR',
                'features': None,
                'interventions': [f'Error: {str(e)}']
            }
    
    async def train_model(self, training_data: List[Tuple[List[float], int]]) -> Dict:
        """
        Train Random Forest model on labeled data.
        
        Args:
            training_data: List of (features, label) tuples
                          label: 0 = active, 1 = churned
            
        Returns:
            Dictionary with training metrics
        """
        try:
            logger.info(f"Training churn model on {len(training_data)} samples")
            
            if len(training_data) < 10:
                logger.warning("Insufficient training data (need at least 10 samples)")
                return {'error': 'Insufficient training data'}
            
            # Prepare data
            X = np.array([features for features, _ in training_data])
            y = np.array([label for _, label in training_data])
            
            # Split train/test
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y if len(np.unique(y)) > 1 else None
            )
            
            # Train model
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                class_weight='balanced'
            )
            
            self.model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = self.model.predict(X_test)
            
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, zero_division=0)
            recall = recall_score(y_test, y_pred, zero_division=0)
            
            logger.info(f"Model trained: accuracy={accuracy:.3f}, precision={precision:.3f}, recall={recall:.3f}")
            
            # Save model to database
            model_pickle = pickle.dumps(self.model)
            
            model_data = {
                'model_name': 'churn_predictor',
                'model_pickle': model_pickle,
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'trained_at': datetime.utcnow().isoformat(),
                'training_samples': len(training_data)
            }
            
            self.supabase.table('ml_models').upsert(model_data).execute()
            
            logger.info("Model saved to database")
            
            return {
                'accuracy': round(accuracy, 3),
                'precision': round(precision, 3),
                'recall': round(recall, 3),
                'training_samples': len(training_data),
                'test_samples': len(X_test)
            }
            
        except Exception as e:
            logger.error(f"Failed to train model: {str(e)}")
            return {'error': str(e)}
    
    async def _extract_features(self, contact_id: str) -> Optional[List[float]]:
        """
        Extract 5 features for churn prediction.
        
        Features:
        1. Days since last update (normalized by 365)
        2. Interaction frequency (# updates in last 90 days / 3)
        3. Inverse influence score (1 - influence_score)
        4. Number of tags (/ 10)
        5. Community size (/ 100)
        
        Args:
            contact_id: Contact UUID
            
        Returns:
            List of 5 normalized feature values, or None if error
        """
        try:
            # Get contact data
            contact_response = self.supabase.table('contacts').select('*').eq('id', contact_id).execute()
            
            if not contact_response.data or len(contact_response.data) == 0:
                logger.warning(f"Contact {contact_id} not found")
                return None
            
            contact = contact_response.data[0]
            
            # Feature 1: Days since last update
            updated_at = contact.get('updated_at')
            if updated_at:
                try:
                    last_update = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                    days_since = (datetime.utcnow() - last_update.replace(tzinfo=None)).days
                except:
                    days_since = 365  # Default to 1 year if parse fails
            else:
                days_since = 365
            
            days_since_normalized = min(days_since / 365.0, 1.0)
            
            # Feature 2: Interaction frequency (last 90 days)
            ninety_days_ago = (datetime.utcnow() - timedelta(days=90)).isoformat()
            
            interaction_response = self.supabase.table('sync_history').select('id').eq('contact_id', contact_id).gte('synced_at', ninety_days_ago).execute()
            
            interaction_count = len(interaction_response.data) if interaction_response.data else 0
            interaction_freq = min(interaction_count / 3.0, 1.0)  # Normalize: 3+ interactions in 90 days = 1.0
            
            # Feature 3: Inverse influence score
            influence_score = contact.get('influence_score', 0.0)
            inverse_influence = 1.0 - influence_score
            
            # Feature 4: Tag count
            tags = contact.get('tags', [])
            tag_count = len(tags) if isinstance(tags, list) else 0
            tag_count_normalized = min(tag_count / 10.0, 1.0)
            
            # Feature 5: Community size
            community_id = contact.get('community_id')
            
            if community_id is not None:
                community_response = self.supabase.table('communities').select('size').eq('id', community_id).execute()
                
                if community_response.data and len(community_response.data) > 0:
                    community_size = community_response.data[0].get('size', 0)
                else:
                    community_size = 0
            else:
                community_size = 0
            
            community_size_normalized = min(community_size / 100.0, 1.0)
            
            features = [
                days_since_normalized,
                interaction_freq,
                inverse_influence,
                tag_count_normalized,
                community_size_normalized
            ]
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting features for {contact_id}: {str(e)}")
            return None
    
    def _risk_level(self, probability: float) -> str:
        """
        Convert churn probability to risk level.
        
        Args:
            probability: Churn probability (0.0-1.0)
            
        Returns:
            Risk level: HIGH, MEDIUM, or LOW
        """
        if probability >= self.RISK_HIGH_THRESHOLD:
            return 'HIGH'
        elif probability >= self.RISK_MEDIUM_THRESHOLD:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _suggest_interventions(self, features: List[float]) -> List[str]:
        """
        Suggest interventions based on feature values.
        
        Args:
            features: List of 5 feature values
            
        Returns:
            List of intervention suggestions
        """
        interventions = []
        
        # Check days since update
        if features[self.FEATURE_DAYS_SINCE_UPDATE] > 0.5:  # >180 days
            interventions.append("⚠️ Reach out soon - no recent contact")
        
        # Check interaction frequency
        if features[self.FEATURE_INTERACTION_FREQ] < 0.33:  # <1 interaction per month
            interventions.append("📅 Schedule a meeting or call")
        
        # Check influence (inverse)
        if features[self.FEATURE_INVERSE_INFLUENCE] > 0.7:  # Low influence
            interventions.append("🌟 Help them grow their network")
        
        # Check tags
        if features[self.FEATURE_TAG_COUNT] < 0.2:  # <2 tags
            interventions.append("🏷️ Add tags to better categorize")
        
        # Check community size
        if features[self.FEATURE_COMMUNITY_SIZE] < 0.2:  # Small community
            interventions.append("👥 Introduce to others in network")
        
        if not interventions:
            interventions.append("✅ Contact is active - maintain engagement")
        
        return interventions
