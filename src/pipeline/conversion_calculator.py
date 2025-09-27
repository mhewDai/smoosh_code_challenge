from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from sqlalchemy import func, and_
from ..models import db, Artist, User, Interaction, Attribution

class ConversionCalculator:
    """Calculator for conversion metrics and funnel analysis"""
    
    def __init__(self):
        self.funnel_stages = ['view', 'click', 'purchase', 'stream']
        self.purchase_types = ['ticket_purchase', 'merch_purchase']
    
    def calculate_artist_conversions(self, artist_id: int, days: int = 30) -> Dict:
        """Calculate conversion metrics for a specific artist"""
        
        # Get date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get interactions for this artist in the time period
        interactions = Interaction.query.filter(
            and_(
                Interaction.artist_id == artist_id,
                Interaction.timestamp >= start_date,
                Interaction.timestamp <= end_date
            )
        ).all()
        
        if not interactions:
            return self._empty_conversion_metrics()
        
        # Group interactions by user
        user_interactions = {}
        for interaction in interactions:
            if interaction.user_id not in user_interactions:
                user_interactions[interaction.user_id] = []
            user_interactions[interaction.user_id].append(interaction)
        
        # Calculate funnel metrics
        funnel_counts = self._calculate_funnel_counts(user_interactions)
        conversion_rates = self._calculate_conversion_rates(funnel_counts)
        
        # Calculate additional metrics
        revenue_metrics = self._calculate_revenue_metrics(interactions)
        engagement_metrics = self._calculate_engagement_metrics(interactions)
        
        return {
            'artist_id': artist_id,
            'period_days': days,
            'total_users': len(user_interactions),
            'total_interactions': len(interactions),
            'funnel_counts': funnel_counts,
            'conversion_rates': conversion_rates,
            'revenue_metrics': revenue_metrics,
            'engagement_metrics': engagement_metrics,
            'calculated_at': datetime.utcnow().isoformat()
        }
    
    def calculate_all_artist_conversions(self, days: int = 30) -> List[Dict]:
        """Calculate conversion metrics for all artists"""
        artists = Artist.query.all()
        results = []
        
        for artist in artists:
            conversion_data = self.calculate_artist_conversions(artist.id, days)
            conversion_data['artist_name'] = artist.name
            results.append(conversion_data)
        
        return results
    
    def calculate_conversion_funnel(self, artist_id: int = None, days: int = 30) -> Dict:
        """Calculate overall conversion funnel"""
        
        # Get date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Build query
        query = Interaction.query.filter(
            and_(
                Interaction.timestamp >= start_date,
                Interaction.timestamp <= end_date
            )
        )
        
        if artist_id:
            query = query.filter(Interaction.artist_id == artist_id)
        
        interactions = query.all()
        
        # Group by user
        user_interactions = {}
        for interaction in interactions:
            if interaction.user_id not in user_interactions:
                user_interactions[interaction.user_id] = []
            user_interactions[interaction.user_id].append(interaction)
        
        # Calculate funnel
        funnel_counts = self._calculate_funnel_counts(user_interactions)
        conversion_rates = self._calculate_conversion_rates(funnel_counts)
        
        return {
            'funnel_counts': funnel_counts,
            'conversion_rates': conversion_rates,
            'total_users': len(user_interactions)
        }
    
    def _calculate_funnel_counts(self, user_interactions: Dict[int, List[Interaction]]) -> Dict:
        """Calculate how many users reached each funnel stage"""
        
        counts = {
            'view': 0,
            'click': 0,
            'purchase': 0,
            'stream': 0
        }
        
        for user_id, interactions in user_interactions.items():
            interaction_types = {i.interaction_type for i in interactions}
            
            # Check each funnel stage
            if 'view' in interaction_types:
                counts['view'] += 1
            
            if 'click' in interaction_types:
                counts['click'] += 1
            
            if any(t in interaction_types for t in self.purchase_types):
                counts['purchase'] += 1
            
            if 'stream' in interaction_types:
                counts['stream'] += 1
        
        return counts
    
    def _calculate_conversion_rates(self, funnel_counts: Dict) -> Dict:
        """Calculate conversion rates between funnel stages"""
        
        rates = {}
        
        # Click-through rate (view -> click)
        if funnel_counts['view'] > 0:
            rates['ctr'] = funnel_counts['click'] / funnel_counts['view']
        else:
            rates['ctr'] = 0.0
        
        # Purchase conversion rate (click -> purchase)
        if funnel_counts['click'] > 0:
            rates['purchase_rate'] = funnel_counts['purchase'] / funnel_counts['click']
        else:
            rates['purchase_rate'] = 0.0
        
        # Stream conversion rate (view -> stream)
        if funnel_counts['view'] > 0:
            rates['stream_rate'] = funnel_counts['stream'] / funnel_counts['view']
        else:
            rates['stream_rate'] = 0.0
        
        # Overall conversion rate (view -> purchase)
        if funnel_counts['view'] > 0:
            rates['overall_conversion'] = funnel_counts['purchase'] / funnel_counts['view']
        else:
            rates['overall_conversion'] = 0.0
        
        return rates
    
    def _calculate_revenue_metrics(self, interactions: List[Interaction]) -> Dict:
        """Calculate revenue-related metrics"""
        
        purchase_interactions = [
            i for i in interactions 
            if i.interaction_type in self.purchase_types and i.value
        ]
        
        if not purchase_interactions:
            return {
                'total_revenue': 0.0,
                'average_order_value': 0.0,
                'total_orders': 0,
                'ticket_revenue': 0.0,
                'merch_revenue': 0.0
            }
        
        total_revenue = sum(i.value for i in purchase_interactions)
        ticket_revenue = sum(i.value for i in purchase_interactions if i.interaction_type == 'ticket_purchase')
        merch_revenue = sum(i.value for i in purchase_interactions if i.interaction_type == 'merch_purchase')
        
        return {
            'total_revenue': total_revenue,
            'average_order_value': total_revenue / len(purchase_interactions),
            'total_orders': len(purchase_interactions),
            'ticket_revenue': ticket_revenue,
            'merch_revenue': merch_revenue
        }
    
    def _calculate_engagement_metrics(self, interactions: List[Interaction]) -> Dict:
        """Calculate engagement-related metrics"""
        
        unique_users = len(set(i.user_id for i in interactions))
        unique_sessions = len(set(i.session_id for i in interactions if i.session_id))
        
        stream_interactions = [i for i in interactions if i.interaction_type == 'stream' and i.value]
        total_stream_time = sum(i.value for i in stream_interactions) if stream_interactions else 0.0
        
        social_interactions = [i for i in interactions if i.interaction_type == 'social_share']
        
        return {
            'unique_users': unique_users,
            'unique_sessions': unique_sessions,
            'total_stream_time': total_stream_time,
            'average_stream_time': total_stream_time / len(stream_interactions) if stream_interactions else 0.0,
            'social_shares': len(social_interactions),
            'interactions_per_user': len(interactions) / unique_users if unique_users > 0 else 0.0
        }
    
    def _empty_conversion_metrics(self) -> Dict:
        """Return empty conversion metrics structure"""
        return {
            'total_users': 0,
            'total_interactions': 0,
            'funnel_counts': {'view': 0, 'click': 0, 'purchase': 0, 'stream': 0},
            'conversion_rates': {'ctr': 0.0, 'purchase_rate': 0.0, 'stream_rate': 0.0, 'overall_conversion': 0.0},
            'revenue_metrics': {
                'total_revenue': 0.0,
                'average_order_value': 0.0,
                'total_orders': 0,
                'ticket_revenue': 0.0,
                'merch_revenue': 0.0
            },
            'engagement_metrics': {
                'unique_users': 0,
                'unique_sessions': 0,
                'total_stream_time': 0.0,
                'average_stream_time': 0.0,
                'social_shares': 0,
                'interactions_per_user': 0.0
            }
        }
    
    def get_top_converting_artists(self, limit: int = 10, days: int = 30) -> List[Dict]:
        """Get artists with highest conversion rates"""
        all_conversions = self.calculate_all_artist_conversions(days)
        
        # Sort by overall conversion rate
        sorted_artists = sorted(
            all_conversions, 
            key=lambda x: x['conversion_rates']['overall_conversion'], 
            reverse=True
        )
        
        return sorted_artists[:limit]