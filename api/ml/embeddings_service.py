"""
Contact Embeddings Service

Generates semantic embeddings for contacts using OpenAI text-embedding-3-small model.
Enables semantic search and similarity-based recommendations.
"""

import logging
import asyncio
from typing import Dict, List, Optional
import numpy as np
from openai import AsyncOpenAI
from supabase import Client
from datetime import datetime

logger = logging.getLogger(__name__)


class ContactEmbeddingsService:
    """Service for generating and managing contact embeddings."""
    
    def __init__(self, supabase_client: Client, openai_client: AsyncOpenAI):
        """
        Initialize ContactEmbeddingsService.
        
        Args:
            supabase_client: Supabase client instance
            openai_client: OpenAI async client instance
        """
        self.supabase = supabase_client
        self.openai = openai_client
        self.model = "text-embedding-3-small"
        self.embedding_dimension = 1536
        
    async def generate_embedding(self, contact: Dict) -> np.ndarray:
        """
        Generate embedding vector for a contact.
        
        Concatenates: first_name + last_name + organization + tags + notes
        and calls OpenAI API to get 1536-dimensional vector.
        
        Args:
            contact: Contact dictionary with fields
            
        Returns:
            numpy array of shape (1536,)
            
        Raises:
            Exception: If OpenAI API call fails
        """
        try:
            # Build text representation
            text_parts = []
            
            if contact.get('first_name'):
                text_parts.append(contact['first_name'])
            if contact.get('last_name'):
                text_parts.append(contact['last_name'])
            if contact.get('organization'):
                text_parts.append(f"Organization: {contact['organization']}")
            if contact.get('tags'):
                tags_str = ', '.join(contact['tags']) if isinstance(contact['tags'], list) else contact['tags']
                text_parts.append(f"Tags: {tags_str}")
            if contact.get('notes'):
                text_parts.append(f"Notes: {contact['notes']}")
                
            text = ' '.join(text_parts)
            
            if not text.strip():
                logger.warning(f"Empty text for contact {contact.get('id')}, using default")
                text = "Unknown contact"
            
            logger.info(f"Generating embedding for contact {contact.get('id')}: '{text[:100]}...'")
            
            # Call OpenAI API
            response = await self.openai.embeddings.create(
                model=self.model,
                input=text,
                encoding_format="float"
            )
            
            embedding = np.array(response.data[0].embedding, dtype=np.float32)
            
            logger.info(f"Generated embedding of shape {embedding.shape} for contact {contact.get('id')}")
            
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding for contact {contact.get('id')}: {str(e)}")
            raise
    
    async def find_similar_contacts(
        self, 
        contact_id: str, 
        top_n: int = 10
    ) -> List[Dict]:
        """
        Find similar contacts using pgvector cosine similarity.
        
        Queries contact_embeddings table and uses PostgreSQL pgvector extension
        to compute cosine similarity: 1 - (embedding <=> target_embedding)
        
        Args:
            contact_id: Target contact UUID
            top_n: Number of similar contacts to return
            
        Returns:
            List of dictionaries with contact_id and similarity score
        """
        try:
            logger.info(f"Finding {top_n} similar contacts for {contact_id}")
            
            # Get target embedding
            target_response = self.supabase.table('contact_embeddings').select('*').eq('contact_id', contact_id).execute()
            
            if not target_response.data or len(target_response.data) == 0:
                logger.warning(f"No embedding found for contact {contact_id}")
                return []
            
            target_embedding = target_response.data[0]['embedding']
            
            # Query similar contacts using pgvector
            # Note: In production, use RPC function with pgvector operator
            # For now, fetch all and compute in Python
            all_embeddings = self.supabase.table('contact_embeddings').select('*').neq('contact_id', contact_id).execute()
            
            similarities = []
            target_vec = np.array(target_embedding, dtype=np.float32)
            
            for row in all_embeddings.data:
                other_vec = np.array(row['embedding'], dtype=np.float32)
                
                # Cosine similarity: 1 - cosine_distance
                dot_product = np.dot(target_vec, other_vec)
                norm_product = np.linalg.norm(target_vec) * np.linalg.norm(other_vec)
                
                if norm_product > 0:
                    similarity = dot_product / norm_product
                else:
                    similarity = 0.0
                
                similarities.append({
                    'contact_id': row['contact_id'],
                    'similarity': float(similarity),
                    'updated_at': row.get('updated_at')
                })
            
            # Sort by similarity DESC and take top N
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            top_similar = similarities[:top_n]
            
            logger.info(f"Found {len(top_similar)} similar contacts for {contact_id}")
            
            return top_similar
            
        except Exception as e:
            logger.error(f"Failed to find similar contacts for {contact_id}: {str(e)}")
            return []
    
    async def batch_generate_embeddings(
        self, 
        contacts: List[Dict],
        batch_size: int = 10,
        delay_seconds: float = 1.0
    ) -> None:
        """
        Generate embeddings for multiple contacts with rate limiting.
        
        Processes contacts in batches to avoid OpenAI rate limits.
        Upserts results to contact_embeddings table.
        
        Args:
            contacts: List of contact dictionaries
            batch_size: Number of contacts to process in parallel
            delay_seconds: Delay between batches to avoid rate limits
            
        Raises:
            Exception: If critical errors occur during processing
        """
        try:
            total = len(contacts)
            logger.info(f"Starting batch embedding generation for {total} contacts")
            
            successful = 0
            failed = 0
            
            for i in range(0, total, batch_size):
                batch = contacts[i:i + batch_size]
                logger.info(f"Processing batch {i//batch_size + 1}/{(total + batch_size - 1)//batch_size}")
                
                # Process batch
                tasks = []
                for contact in batch:
                    task = self._process_single_contact(contact)
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Count successes and failures
                for result in results:
                    if isinstance(result, Exception):
                        failed += 1
                        logger.error(f"Batch processing error: {str(result)}")
                    elif result:
                        successful += 1
                
                # Rate limiting delay
                if i + batch_size < total:
                    logger.info(f"Waiting {delay_seconds}s before next batch...")
                    await asyncio.sleep(delay_seconds)
            
            logger.info(f"Batch processing complete: {successful} successful, {failed} failed out of {total}")
            
        except Exception as e:
            logger.error(f"Critical error in batch_generate_embeddings: {str(e)}")
            raise
    
    async def _process_single_contact(self, contact: Dict) -> bool:
        """
        Process single contact: generate embedding and upsert to database.
        
        Args:
            contact: Contact dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            contact_id = contact.get('id')
            if not contact_id:
                logger.warning("Contact missing ID, skipping")
                return False
            
            # Generate embedding
            embedding = await self.generate_embedding(contact)
            
            # Upsert to database
            embedding_data = {
                'contact_id': contact_id,
                'embedding': embedding.tolist(),  # Convert numpy array to list
                'updated_at': datetime.utcnow().isoformat()
            }
            
            self.supabase.table('contact_embeddings').upsert(embedding_data).execute()
            
            logger.info(f"Successfully saved embedding for contact {contact_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to process contact {contact.get('id')}: {str(e)}")
            return False
