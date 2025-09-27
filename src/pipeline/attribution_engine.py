from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from sqlalchemy import func
from ..models import db, User, Artist, Interaction, Attribution

class AttributionEngine:
    """Engine for calculating user-artist attribution scores"""
    
    def __init__(self):
        self.interaction_weights = {
            'view': 1.0,
            'click': 2.0,
            'social_share': 3.0,
            'merch_purchase': 5.0,
            'ticket_purchase': 8.0,
            'stream': 4.0
        }
        
        self.channel_multipliers = {
            'website': 1.0,
            'mobile_app': 1.2,
            'social_media': 0.8,
            'streaming_platform': 1.1,
            'email': 0.9
        }
    
    def calculate_all_attributions(self) -> List[Attribution]:
        """Calculate attribution scores for all user-artist pairs"""
        attributions = []
        
        # Get all unique user-artist combinations from interactions
        user_artist_pairs = db.session.query(
            Interaction.user_id, 
            Interaction.artist_id
        ).distinct().all()
        
        for user_id, artist_id in user_artist_pairs:
            attribution = self.calculate_user_artist_attribution(user_id, artist_id)
            if attribution:
                attributions.append(attribution)
        
        return attributions
    
    def calculate_user_artist_attribution(self, user_id: int, artist_id: int) -> Attribution:
        """Calculate attribution score for a specific user-artist pair"""
        
        # Get all interactions for this user-artist pair
        interactions = Interaction.query.filter_by(
            user_id=user_id,
            artist_id=artist_id
        ).order_by(Interaction.timestamp).all()
        
        if not interactions:
            return None
        
        # Find or create attribution record
        attribution = Attribution.query.filter_by(
            user_id=user_id,
            artist_id=artist_id
        ).first()
        
        if not attribution:
            attribution = Attribution(user_id=user_id, artist_id=artist_id)
            db.session.add(attribution)
        
        # Calculate scores
        attribution.engagement_score = self._calculate_engagement_score(interactions)
        attribution.purchase_score = self._calculate_purchase_score(interactions)
        attribution.loyalty_score = self._calculate_loyalty_score(interactions)
        attribution.recency_score = self._calculate_recency_score(interactions)
        
        # Calculate composite score
        attribution.total_score = (
            attribution.engagement_score * 0.3 +
            attribution.purchase_score * 0.4 +
            attribution.loyalty_score * 0.2 +
            attribution.recency_score * 0.1
        )
        
        # Update funnel stages
        interaction_types = {i.interaction_type for i in interactions}
        attribution.has_viewed = 'view' in interaction_types
        attribution.has_clicked = 'click' in interaction_types
        attribution.has_purchased = any(t in interaction_types for t in ['ticket_purchase', 'merch_purchase'])
        attribution.has_streamed = 'stream' in interaction_types
        
        # Update metrics
        attribution.total_interactions = len(interactions)
        attribution.total_spent = sum(i.value or 0 for i in interactions if i.interaction_type in ['ticket_purchase', 'merch_purchase'])
        attribution.first_interaction = interactions[0].timestamp
        attribution.last_interaction = interactions[-1].timestamp
        
        db.session.commit()
        return attribution
    
    def _calculate_engagement_score(self, interactions: List[Interaction]) -> float:
        """Calculate engagement score based on interaction frequency and types"""
        if not interactions:
            return 0.0
        
        total_score = 0.0
        for interaction in interactions:
            # Base score from interaction type
            base_score = self.interaction_weights.get(interaction.interaction_type, 1.0)
            
            # Channel multiplier
            channel_mult = self.channel_multipliers.get(interaction.channel, 1.0)
            
            # Value multiplier (for streams, purchases, etc.)
            value_mult = 1.0
            if interaction.value:
                if interaction.interaction_type == 'stream':
                    value_mult = min(interaction.value / 3.0, 3.0)  # Stream time in minutes
                elif interaction.interaction_type in ['ticket_purchase', 'merch_purchase']:
                    value_mult = min(interaction.value / 100.0, 5.0)  # Purchase value
            
            total_score += base_score * channel_mult * value_mult
        
        # Normalize by interaction count to prevent simple volume bias
        return min(total_score / len(interactions), 100.0)
    
    def _calculate_purchase_score(self, interactions: List[Interaction]) -> float:
        """Calculate purchase behavior score"""
        purchase_interactions = [
            i for i in interactions 
            if i.interaction_type in ['ticket_purchase', 'merch_purchase']
        ]
        
        if not purchase_interactions:
            return 0.0
        
        # Base score for making purchases
        base_score = len(purchase_interactions) * 20.0
        
        # Value bonus
        total_value = sum(i.value or 0 for i in purchase_interactions)
        value_score = min(total_value / 10.0, 50.0)  # Cap at 50 points
        
        return min(base_score + value_score, 100.0)
    
    def _calculate_loyalty_score(self, interactions: List[Interaction]) -> float:
        """Calculate loyalty score based on repeat engagement over time"""
        if len(interactions) < 2:
            return 0.0
        
        # Time span of interactions
        first_interaction = min(i.timestamp for i in interactions)
        last_interaction = max(i.timestamp for i in interactions)
        time_span = (last_interaction - first_interaction).days
        
        if time_span == 0:
            return 10.0  # Single day multiple interactions
        
        # Frequency score
        frequency_score = min((len(interactions) / max(time_span, 1)) * 30.0, 70.0)
        
        # Consistency score (regular interaction patterns)
        weekly_interactions = {}
        for interaction in interactions:
            week = interaction.timestamp.strftime('%Y-W%U')
            weekly_interactions[week] = weekly_interactions.get(week, 0) + 1
        
        consistency_score = min(len(weekly_interactions) * 5.0, 30.0)
        
        return min(frequency_score + consistency_score, 100.0)
    
    def _calculate_recency_score(self, interactions: List[Interaction]) -> float:
        """Calculate recency score based on how recent the last interaction was"""
        if not interactions:
            return 0.0
        
        last_interaction = max(i.timestamp for i in interactions)
        days_since = (datetime.utcnow() - last_interaction).days
        
        # Decay function - starts at 100 and decays over time
        if days_since <= 1:
            return 100.0
        elif days_since <= 7:
            return 80.0
        elif days_since <= 30:
            return 60.0
        elif days_since <= 90:
            return 40.0
        elif days_since <= 180:
            return 20.0
        else:
            return 10.0
    
    def get_top_attributions(self, limit: int = 100) -> List[Attribution]:
        """Get top user-artist attributions by score"""
        return Attribution.query.order_by(Attribution.total_score.desc()).limit(limit).all()
    
    def get_artist_attributions(self, artist_id: int, limit: int = 50) -> List[Attribution]:
        """Get top attributions for a specific artist"""
        return Attribution.query.filter_by(artist_id=artist_id)\
            .order_by(Attribution.total_score.desc()).limit(limit).all()
    
    def get_user_attributions(self, user_id: int) -> List[Attribution]:
        """Get all attributions for a specific user"""
        return Attribution.query.filter_by(user_id=user_id)\
            .order_by(Attribution.total_score.desc()).all()