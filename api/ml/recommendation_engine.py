"""
Recommendation Engine

"People You Should Know" - recommends contacts based on:
- Mutual friends (2-hop connections)
- Semantic similarity (embeddings)
- Influence scores
- Organization overlap
"""

import logging
from typing import Dict, List, Optional, Set
from collections import defaultdict
from supabase import Client

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Engine for generating contact recommendations."""
    
    # Recommendation score weights
    WEIGHT_MUTUAL_FRIENDS = 0.3
    WEIGHT_SEMANTIC_SIMILARITY = 0.3
    WEIGHT_INFLUENCE_SCORE = 0.25
    WEIGHT_SAME_ORGANIZATION = 0.15
    
    def __init__(self, supabase_client: Client, embeddings_service):
        """
        Initialize RecommendationEngine.
        
        Args:
            supabase_client: Supabase client instance
            embeddings_service: ContactEmbeddingsService instance
        """
        self.supabase = supabase_client
        self.embeddings_service = embeddings_service
        
    async def recommend_contacts(
        self,
        user_contact_id: str,
        limit: int = 20,
        min_score: float = 0.6
    ) -> List[Dict]:
        """
        Generate contact recommendations for a user.
        
        Algorithm:
        1. Get friends-of-friends (2-hop network)
        2. Compute recommendation score for each candidate
        3. Filter by min_score
        4. Return top-N with explanations
        
        Args:
            user_contact_id: Target user's contact UUID
            limit: Maximum number of recommendations
            min_score: Minimum recommendation score (0.0-1.0)
            
        Returns:
            List of recommended contacts with scores and reasons
        """
        try:
            logger.info(f"Generating {limit} recommendations for contact {user_contact_id}")
            
            # Step 1: Get user's direct connections
            user_response = self.supabase.table('contacts').select('*').eq('id', user_contact_id).execute()
            
            if not user_response.data or len(user_response.data) == 0:
                logger.warning(f"Contact {user_contact_id} not found")
                return []
            
            user_contact = user_response.data[0]
            
            # Step 2: Get friends-of-friends
            candidates = await self._get_friends_of_friends(user_contact_id)
            
            if not candidates:
                logger.info(f"No candidate contacts found for {user_contact_id}")
                return []
            
            logger.info(f"Found {len(candidates)} candidate contacts")
            
            # Step 3: Compute recommendation scores
            recommendations = []
            
            for candidate_id in candidates:
                try:
                    score_data = await self._compute_recommendation_score(
                        user_contact_id,
                        candidate_id,
                        user_contact
                    )
                    
                    if score_data['total_score'] >= min_score:
                        # Get candidate contact data
                        candidate_response = self.supabase.table('contacts').select('*').eq('id', candidate_id).execute()
                        
                        if candidate_response.data:
                            candidate = candidate_response.data[0]
                            
                            recommendations.append({
                                'contact_id': candidate_id,
                                'first_name': candidate.get('first_name'),
                                'last_name': candidate.get('last_name'),
                                'organization': candidate.get('organization'),
                                'influence_score': candidate.get('influence_score', 0.0),
                                'recommendation_score': score_data['total_score'],
                                'score_components': score_data['components'],
                                'reason': self._explain_reason(score_data)
                            })
                            
                except Exception as e:
                    logger.error(f"Error computing score for candidate {candidate_id}: {str(e)}")
                    continue
            
            # Step 4: Sort by score and return top-N
            recommendations.sort(key=lambda x: x['recommendation_score'], reverse=True)
            top_recommendations = recommendations[:limit]
            
            logger.info(f"Generated {len(top_recommendations)} recommendations (filtered from {len(recommendations)} with score >= {min_score})")
            
            return top_recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations for {user_contact_id}: {str(e)}")
            return []
    
    async def _get_friends_of_friends(self, contact_id: str) -> Set[str]:
        """
        Get 2-hop network: friends of friends who are not direct friends.
        
        Args:
            contact_id: Source contact UUID
            
        Returns:
            Set of candidate contact IDs
        """
        try:
            # Get direct connections (1-hop)
            direct_friends_response = self.supabase.table('contact_connections').select('contact_id_2').eq('contact_id_1', contact_id).execute()
            
            direct_friends = set()
            for row in direct_friends_response.data:
                direct_friends.add(row['contact_id_2'])
            
            # Also check reverse connections
            reverse_friends_response = self.supabase.table('contact_connections').select('contact_id_1').eq('contact_id_2', contact_id).execute()
            
            for row in reverse_friends_response.data:
                direct_friends.add(row['contact_id_1'])
            
            logger.info(f"Contact {contact_id} has {len(direct_friends)} direct friends")
            
            # Get friends-of-friends (2-hop)
            friends_of_friends = set()
            
            for friend_id in direct_friends:
                # Get friend's connections
                fof_response = self.supabase.table('contact_connections').select('contact_id_2').eq('contact_id_1', friend_id).execute()
                
                for row in fof_response.data:
                    fof_id = row['contact_id_2']
                    # Exclude self and direct friends
                    if fof_id != contact_id and fof_id not in direct_friends:
                        friends_of_friends.add(fof_id)
                
                # Check reverse connections
                fof_reverse_response = self.supabase.table('contact_connections').select('contact_id_1').eq('contact_id_2', friend_id).execute()
                
                for row in fof_reverse_response.data:
                    fof_id = row['contact_id_1']
                    if fof_id != contact_id and fof_id not in direct_friends:
                        friends_of_friends.add(fof_id)
            
            logger.info(f"Found {len(friends_of_friends)} friends-of-friends candidates")
            
            return friends_of_friends
            
        except Exception as e:
            logger.error(f"Error getting friends-of-friends for {contact_id}: {str(e)}")
            return set()
    
    async def _count_mutual_friends(self, contact_id_1: str, contact_id_2: str) -> int:
        """
        Count mutual friends between two contacts.
        
        Args:
            contact_id_1: First contact UUID
            contact_id_2: Second contact UUID
            
        Returns:
            Number of mutual friends
        """
        try:
            # Get friends of contact 1
            friends_1_response = self.supabase.table('contact_connections').select('contact_id_2').eq('contact_id_1', contact_id_1).execute()
            friends_1 = set(row['contact_id_2'] for row in friends_1_response.data)
            
            # Also check reverse
            reverse_1_response = self.supabase.table('contact_connections').select('contact_id_1').eq('contact_id_2', contact_id_1).execute()
            friends_1.update(row['contact_id_1'] for row in reverse_1_response.data)
            
            # Get friends of contact 2
            friends_2_response = self.supabase.table('contact_connections').select('contact_id_2').eq('contact_id_1', contact_id_2).execute()
            friends_2 = set(row['contact_id_2'] for row in friends_2_response.data)
            
            # Also check reverse
            reverse_2_response = self.supabase.table('contact_connections').select('contact_id_1').eq('contact_id_2', contact_id_2).execute()
            friends_2.update(row['contact_id_1'] for row in reverse_2_response.data)
            
            # Count mutual friends
            mutual = friends_1.intersection(friends_2)
            
            return len(mutual)
            
        except Exception as e:
            logger.error(f"Error counting mutual friends: {str(e)}")
            return 0
    
    async def _compute_recommendation_score(
        self,
        user_id: str,
        candidate_id: str,
        user_contact: Dict
    ) -> Dict:
        """
        Compute weighted recommendation score.
        
        Components:
        - mutual_friends: 0.3
        - semantic_similarity: 0.3
        - influence_score: 0.25
        - same_organization: 0.15
        
        Args:
            user_id: User contact UUID
            candidate_id: Candidate contact UUID
            user_contact: User contact data
            
        Returns:
            Dictionary with total_score and components breakdown
        """
        try:
            components = {}
            
            # Component 1: Mutual friends (normalized 0-1)
            mutual_count = await self._count_mutual_friends(user_id, candidate_id)
            mutual_score = min(mutual_count / 10.0, 1.0)  # Normalize: 10+ mutual friends = 1.0
            components['mutual_friends'] = mutual_score
            
            # Component 2: Semantic similarity (from embeddings)
            try:
                similar_contacts = await self.embeddings_service.find_similar_contacts(user_id, top_n=100)
                
                similarity_score = 0.0
                for similar in similar_contacts:
                    if similar['contact_id'] == candidate_id:
                        similarity_score = similar['similarity']
                        break
                
                # Normalize to 0-1 range (cosine similarity is already -1 to 1, shift to 0-1)
                similarity_score = (similarity_score + 1.0) / 2.0
                components['semantic_similarity'] = similarity_score
                
            except Exception as e:
                logger.warning(f"Could not compute semantic similarity: {str(e)}")
                components['semantic_similarity'] = 0.0
            
            # Component 3: Influence score (higher influence = better recommendation)
            candidate_response = self.supabase.table('contacts').select('influence_score').eq('id', candidate_id).execute()
            
            if candidate_response.data:
                influence_score = candidate_response.data[0].get('influence_score', 0.0)
                components['influence_score'] = influence_score
            else:
                components['influence_score'] = 0.0
            
            # Component 4: Same organization bonus
            candidate_org_response = self.supabase.table('contacts').select('organization').eq('id', candidate_id).execute()
            
            same_org_score = 0.0
            if candidate_org_response.data:
                candidate_org = candidate_org_response.data[0].get('organization')
                user_org = user_contact.get('organization')
                
                if candidate_org and user_org and candidate_org.lower().strip() == user_org.lower().strip():
                    same_org_score = 1.0
            
            components['same_organization'] = same_org_score
            
            # Compute weighted total score
            total_score = (
                components['mutual_friends'] * self.WEIGHT_MUTUAL_FRIENDS +
                components['semantic_similarity'] * self.WEIGHT_SEMANTIC_SIMILARITY +
                components['influence_score'] * self.WEIGHT_INFLUENCE_SCORE +
                components['same_organization'] * self.WEIGHT_SAME_ORGANIZATION
            )
            
            return {
                'total_score': round(total_score, 3),
                'components': components
            }
            
        except Exception as e:
            logger.error(f"Error computing recommendation score: {str(e)}")
            return {'total_score': 0.0, 'components': {}}
    
    def _explain_reason(self, score_data: Dict) -> str:
        """
        Generate human-readable explanation for recommendation.
        
        Args:
            score_data: Score data with components
            
        Returns:
            Explanation string
        """
        components = score_data.get('components', {})
        reasons = []
        
        if components.get('mutual_friends', 0) > 0.3:
            count = int(components['mutual_friends'] * 10)
            reasons.append(f"{count}+ mutual connections")
        
        if components.get('semantic_similarity', 0) > 0.7:
            reasons.append("similar interests")
        
        if components.get('influence_score', 0) > 0.7:
            reasons.append("influential in network")
        
        if components.get('same_organization', 0) == 1.0:
            reasons.append("same organization")
        
        if not reasons:
            reasons.append("potential connection")
        
        return "Recommended: " + ", ".join(reasons)
