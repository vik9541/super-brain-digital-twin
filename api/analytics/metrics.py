"""
Advanced Analytics Module - Phase 9 Day 8-9

Enterprise dashboard metrics:
- Contact Lifetime Value (CLV)
- Relationship Health Score (0-100)
- Engagement Trends (30-day)
- Top Performing Contacts

Author: Super Brain Team
Created: 2025-12-13
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List
from supabase import Client

logger = logging.getLogger(__name__)


class AnalyticsMetrics:
    """
    Advanced analytics for enterprise dashboard
    
    Metrics:
    1. CLV (Contact Lifetime Value) - Estimated business value
    2. Health Score (0-100) - Relationship strength
    3. Engagement Trends - Activity over time
    4. Top Contacts - Most valuable relationships
    """
    
    def __init__(self, supabase: Client):
        self.supabase = supabase
        logger.info("✅ Analytics Metrics initialized")
    
    async def get_metrics(self, workspace_id: str) -> Dict:
        """
        Get all analytics metrics for workspace
        
        Returns:
            {
                'clv': {...},
                'health_score': {...},
                'engagement': {...},
                'top_contacts': [...]
            }
        """
        try:
            clv = await self.calculate_clv(workspace_id)
            health = await self.calculate_health_score(workspace_id)
            engagement = await self.get_engagement_trends(workspace_id)
            top = await self.get_top_contacts(workspace_id)
            
            return {
                "clv": clv,
                "health_score": health,
                "engagement": engagement,
                "top_contacts": top,
                "generated_at": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return {"error": str(e)}
    
    async def calculate_clv(self, workspace_id: str) -> Dict:
        """
        Calculate Contact Lifetime Value
        
        Formula:
        CLV = (Interaction Frequency × Recency Weight × Relationship Strength) × Business Value Multiplier
        
        Returns:
            {
                'total_clv': float,
                'avg_clv_per_contact': float,
                'high_value_contacts': int (CLV > $10k)
            }
        """
        try:
            # Get all contacts with interactions
            contacts = self.supabase.table("contacts").select("id").eq("workspace_id", workspace_id).execute()
            
            if not contacts.data:
                return {"total_clv": 0, "avg_clv_per_contact": 0, "high_value_contacts": 0}
            
            total_clv = 0
            high_value_count = 0
            
            for contact in contacts.data:
                # Get interactions
                interactions = self.supabase.table("interactions").select("*").eq("contact_id", contact["id"]).execute()
                
                interaction_count = len(interactions.data)
                
                # Calculate recency (days since last interaction)
                if interactions.data:
                    last_interaction = max([datetime.fromisoformat(i["occurred_at"].replace("Z", "+00:00")) for i in interactions.data])
                    recency_days = (datetime.utcnow().replace(tzinfo=last_interaction.tzinfo) - last_interaction).days
                    recency_weight = max(0.1, 1 - (recency_days / 365))  # Decay over 1 year
                else:
                    recency_weight = 0.1
                
                # Relationship strength (0-1) based on interaction variety
                relationship_strength = min(1.0, interaction_count / 20)  # Cap at 20 interactions
                
                # Business value multiplier (configurable)
                business_value = 1000  # $1k per strong relationship
                
                # CLV formula
                clv = interaction_count * recency_weight * relationship_strength * business_value
                
                total_clv += clv
                
                if clv > 10000:  # High value threshold: $10k
                    high_value_count += 1
            
            avg_clv = total_clv / len(contacts.data) if contacts.data else 0
            
            return {
                "total_clv": round(total_clv, 2),
                "avg_clv_per_contact": round(avg_clv, 2),
                "high_value_contacts": high_value_count,
                "total_contacts": len(contacts.data)
            }
        
        except Exception as e:
            logger.error(f"CLV calculation failed: {e}")
            return {"error": str(e)}
    
    async def calculate_health_score(self, workspace_id: str) -> Dict:
        """
        Calculate Relationship Health Score (0-100)
        
        Components:
        - Interaction frequency (40%)
        - Recency (30%)
        - Diversity of interaction types (20%)
        - Response rate (10%)
        
        Returns:
            {
                'overall_score': float (0-100),
                'breakdown': {...}
            }
        """
        try:
            contacts = self.supabase.table("contacts").select("id").eq("workspace_id", workspace_id).execute()
            
            if not contacts.data:
                return {"overall_score": 0, "breakdown": {}}
            
            total_score = 0
            scores = []
            
            for contact in contacts.data:
                interactions = self.supabase.table("interactions").select("*").eq("contact_id", contact["id"]).execute()
                
                if not interactions.data:
                    scores.append(0)
                    continue
                
                # Frequency score (40 points) - interactions per month
                interaction_count = len(interactions.data)
                frequency_score = min(40, interaction_count * 2)  # Cap at 40
                
                # Recency score (30 points) - days since last interaction
                last_interaction = max([datetime.fromisoformat(i["occurred_at"].replace("Z", "+00:00")) for i in interactions.data])
                days_ago = (datetime.utcnow().replace(tzinfo=last_interaction.tzinfo) - last_interaction).days
                recency_score = max(0, 30 - (days_ago / 3))  # Decay: -10 points per 90 days
                
                # Diversity score (20 points) - unique interaction types
                interaction_types = set([i["type"] for i in interactions.data])
                diversity_score = min(20, len(interaction_types) * 5)  # 5 points per type
                
                # Response rate score (10 points) - placeholder
                response_score = 10  # TODO: Implement actual response tracking
                
                health_score = frequency_score + recency_score + diversity_score + response_score
                
                total_score += health_score
                scores.append(health_score)
            
            overall_score = total_score / len(contacts.data) if contacts.data else 0
            
            return {
                "overall_score": round(overall_score, 1),
                "breakdown": {
                    "excellent": len([s for s in scores if s >= 80]),
                    "good": len([s for s in scores if 60 <= s < 80]),
                    "fair": len([s for s in scores if 40 <= s < 60]),
                    "poor": len([s for s in scores if s < 40])
                },
                "total_contacts": len(contacts.data)
            }
        
        except Exception as e:
            logger.error(f"Health score calculation failed: {e}")
            return {"error": str(e)}
    
    async def get_engagement_trends(self, workspace_id: str, days: int = 30) -> Dict:
        """
        Get engagement trends over time
        
        Returns daily interaction counts for last N days
        
        Returns:
            {
                'daily_counts': [{date, count}, ...],
                'trend': 'increasing'|'decreasing'|'stable',
                'avg_daily': float
            }
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get interactions in date range
            interactions = self.supabase.table("interactions").select("occurred_at").eq("workspace_id", workspace_id).gte("occurred_at", cutoff_date.isoformat()).execute()
            
            # Group by day
            daily_counts = {}
            for interaction in interactions.data:
                date = interaction["occurred_at"][:10]  # YYYY-MM-DD
                daily_counts[date] = daily_counts.get(date, 0) + 1
            
            # Fill missing days with 0
            all_days = []
            for i in range(days):
                date = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
                all_days.append({"date": date, "count": daily_counts.get(date, 0)})
            
            all_days.reverse()  # Chronological order
            
            # Calculate trend
            if len(all_days) >= 7:
                recent_avg = sum([d["count"] for d in all_days[-7:]]) / 7
                older_avg = sum([d["count"] for d in all_days[:7]]) / 7
                
                if recent_avg > older_avg * 1.2:
                    trend = "increasing"
                elif recent_avg < older_avg * 0.8:
                    trend = "decreasing"
                else:
                    trend = "stable"
            else:
                trend = "insufficient_data"
            
            avg_daily = sum([d["count"] for d in all_days]) / days if all_days else 0
            
            return {
                "daily_counts": all_days,
                "trend": trend,
                "avg_daily": round(avg_daily, 1),
                "period_days": days
            }
        
        except Exception as e:
            logger.error(f"Engagement trends failed: {e}")
            return {"error": str(e)}
    
    async def get_top_contacts(self, workspace_id: str, limit: int = 10) -> List[Dict]:
        """
        Get top performing contacts by combined score
        
        Score = CLV + Health Score + Recent Activity
        
        Returns:
            [
                {
                    'contact_id': str,
                    'name': str,
                    'score': float,
                    'clv': float,
                    'health_score': float,
                    'last_interaction': str
                },
                ...
            ]
        """
        try:
            contacts = self.supabase.table("contacts").select("*").eq("workspace_id", workspace_id).execute()
            
            if not contacts.data:
                return []
            
            scored_contacts = []
            
            for contact in contacts.data:
                interactions = self.supabase.table("interactions").select("*").eq("contact_id", contact["id"]).execute()
                
                if not interactions.data:
                    continue
                
                # Calculate mini-CLV
                interaction_count = len(interactions.data)
                last_interaction = max([datetime.fromisoformat(i["occurred_at"].replace("Z", "+00:00")) for i in interactions.data])
                recency_days = (datetime.utcnow().replace(tzinfo=last_interaction.tzinfo) - last_interaction).days
                recency_weight = max(0.1, 1 - (recency_days / 365))
                clv = interaction_count * recency_weight * 1000
                
                # Calculate mini health score
                frequency_score = min(40, interaction_count * 2)
                recency_score = max(0, 30 - (recency_days / 3))
                health_score = frequency_score + recency_score
                
                # Combined score
                combined_score = (clv / 100) + health_score
                
                scored_contacts.append({
                    "contact_id": contact["id"],
                    "name": f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip() or contact.get('email', 'Unknown'),
                    "email": contact.get("email"),
                    "organization": contact.get("organization"),
                    "score": round(combined_score, 2),
                    "clv": round(clv, 2),
                    "health_score": round(health_score, 1),
                    "interaction_count": interaction_count,
                    "last_interaction": last_interaction.isoformat()
                })
            
            # Sort by score descending
            scored_contacts.sort(key=lambda x: x["score"], reverse=True)
            
            return scored_contacts[:limit]
        
        except Exception as e:
            logger.error(f"Top contacts failed: {e}")
            return []
