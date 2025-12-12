"""
Sentiment Analyzer

Analyzes the "tone" or sentiment of contacts based on:
- Tags (positive/negative keywords)
- Notes content (TextBlob polarity)
- Interaction patterns (frequency)

Returns sentiment score (-1 to 1) and label.
"""

import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from textblob import TextBlob
from supabase import Client

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Analyzes sentiment/tone of contacts."""
    
    # Positive and negative tags
    POSITIVE_TAGS = {
        'mentor', 'friend', 'collaborator', 'advisor', 'supporter',
        'partner', 'ally', 'champion', 'guide', 'coach',
        'helpful', 'positive', 'enthusiastic', 'engaged'
    }
    
    NEGATIVE_TAGS = {
        'difficult', 'skeptical', 'competitor', 'rival',
        'challenging', 'negative', 'unresponsive', 'critical',
        'demanding', 'problematic'
    }
    
    # Sentiment weights
    WEIGHT_TAGS = 0.4
    WEIGHT_NOTES = 0.3
    WEIGHT_INTERACTIONS = 0.3
    
    def __init__(self, supabase_client: Client):
        """
        Initialize SentimentAnalyzer.
        
        Args:
            supabase_client: Supabase client instance
        """
        self.supabase = supabase_client
    
    async def analyze_contact_sentiment(self, contact_id: str) -> Dict:
        """
        Analyze sentiment for a contact.
        
        Returns overall sentiment score (-1 to 1) and label.
        
        Args:
            contact_id: Contact UUID
            
        Returns:
            Dictionary with:
            - contact_id
            - overall_sentiment (-1 to 1)
            - sentiment_label (Very Positive/Positive/Neutral/Negative/Very Negative)
            - components (breakdown by tags, notes, interactions)
        """
        try:
            logger.info(f"Analyzing sentiment for contact {contact_id}")
            
            # Get contact data
            contact_response = self.supabase.table('contacts').select('*').eq('id', contact_id).execute()
            
            if not contact_response.data or len(contact_response.data) == 0:
                logger.warning(f"Contact {contact_id} not found")
                return {
                    'contact_id': contact_id,
                    'overall_sentiment': 0.0,
                    'sentiment_label': 'UNKNOWN',
                    'components': None
                }
            
            contact = contact_response.data[0]
            
            # Component 1: Tag-based sentiment
            tag_sentiment = self._analyze_tag_sentiment(contact.get('tags', []))
            
            # Component 2: Notes-based sentiment
            notes_sentiment = self._analyze_notes_sentiment(contact.get('notes'))
            
            # Component 3: Interaction pattern sentiment
            interaction_sentiment = await self._analyze_interaction_sentiment(contact_id)
            
            # Weighted average
            overall_sentiment = (
                tag_sentiment * self.WEIGHT_TAGS +
                notes_sentiment * self.WEIGHT_NOTES +
                interaction_sentiment * self.WEIGHT_INTERACTIONS
            )
            
            # Convert to label
            sentiment_label = self._sentiment_label(overall_sentiment)
            
            result = {
                'contact_id': contact_id,
                'overall_sentiment': round(overall_sentiment, 3),
                'sentiment_label': sentiment_label,
                'components': {
                    'tags': round(tag_sentiment, 3),
                    'notes': round(notes_sentiment, 3),
                    'interactions': round(interaction_sentiment, 3)
                }
            }
            
            logger.info(f"Sentiment for {contact_id}: {sentiment_label} ({overall_sentiment:.3f})")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze sentiment for {contact_id}: {str(e)}")
            return {
                'contact_id': contact_id,
                'overall_sentiment': 0.0,
                'sentiment_label': 'ERROR',
                'components': None,
                'error': str(e)
            }
    
    def _analyze_tag_sentiment(self, tags: List[str]) -> float:
        """
        Compute tag-based sentiment.
        
        Positive tags get +1, negative tags get -1.
        Score = (positive_count - negative_count) / total_count
        
        Args:
            tags: List of tag strings
            
        Returns:
            Sentiment score (-1 to 1)
        """
        try:
            if not tags or len(tags) == 0:
                return 0.0
            
            # Normalize tags to lowercase
            tags_lower = [tag.lower().strip() for tag in tags]
            
            positive_count = 0
            negative_count = 0
            
            for tag in tags_lower:
                if tag in self.POSITIVE_TAGS:
                    positive_count += 1
                elif tag in self.NEGATIVE_TAGS:
                    negative_count += 1
            
            total = len(tags_lower)
            
            if total == 0:
                return 0.0
            
            # Normalize to -1..1
            tag_sentiment = (positive_count - negative_count) / total
            
            # Clamp to [-1, 1]
            tag_sentiment = max(-1.0, min(1.0, tag_sentiment))
            
            logger.debug(f"Tag sentiment: {tag_sentiment} (pos={positive_count}, neg={negative_count}, total={total})")
            
            return tag_sentiment
            
        except Exception as e:
            logger.error(f"Error analyzing tag sentiment: {str(e)}")
            return 0.0
    
    def _analyze_notes_sentiment(self, notes: Optional[str]) -> float:
        """
        Compute notes-based sentiment using TextBlob.
        
        Args:
            notes: Notes text content
            
        Returns:
            Sentiment polarity (-1 to 1)
        """
        try:
            if not notes or not notes.strip():
                return 0.0
            
            # Use TextBlob for sentiment analysis
            blob = TextBlob(notes)
            polarity = blob.sentiment.polarity  # Returns -1 to 1
            
            logger.debug(f"Notes sentiment: {polarity}")
            
            return polarity
            
        except Exception as e:
            logger.error(f"Error analyzing notes sentiment: {str(e)}")
            return 0.0
    
    async def _analyze_interaction_sentiment(self, contact_id: str) -> float:
        """
        Compute interaction pattern sentiment.
        
        High interaction frequency = positive
        Low interaction frequency = negative
        
        Args:
            contact_id: Contact UUID
            
        Returns:
            Sentiment score (-1 to 1)
        """
        try:
            # Get interactions in last 3 months
            three_months_ago = (datetime.utcnow() - timedelta(days=90)).isoformat()
            
            interaction_response = self.supabase.table('sync_history').select('id').eq('contact_id', contact_id).gte('synced_at', three_months_ago).execute()
            
            interaction_count = len(interaction_response.data) if interaction_response.data else 0
            
            # Calculate interactions per month
            interactions_per_month = interaction_count / 3.0
            
            # Scoring:
            # >1 per month = +0.3
            # <0.1 per month = -0.3
            # In between = proportional
            
            if interactions_per_month > 1.0:
                interaction_sentiment = 0.3
            elif interactions_per_month < 0.1:
                interaction_sentiment = -0.3
            else:
                # Linear interpolation between -0.3 and 0.3
                interaction_sentiment = -0.3 + (interactions_per_month - 0.1) / 0.9 * 0.6
            
            logger.debug(f"Interaction sentiment: {interaction_sentiment} ({interaction_count} interactions in 90 days)")
            
            return interaction_sentiment
            
        except Exception as e:
            logger.error(f"Error analyzing interaction sentiment: {str(e)}")
            return 0.0
    
    def _sentiment_label(self, sentiment: float) -> str:
        """
        Convert sentiment score to label.
        
        Args:
            sentiment: Sentiment score (-1 to 1)
            
        Returns:
            Sentiment label string
        """
        if sentiment > 0.5:
            return 'Very Positive'
        elif sentiment > 0.2:
            return 'Positive'
        elif sentiment > -0.2:
            return 'Neutral'
        elif sentiment > -0.5:
            return 'Negative'
        else:
            return 'Very Negative'
