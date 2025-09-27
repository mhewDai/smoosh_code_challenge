from .database import db
from datetime import datetime

class Attribution(db.Model):
    __tablename__ = 'attributions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    
    # Attribution scores
    engagement_score = db.Column(db.Float, default=0.0)  # Overall engagement score
    purchase_score = db.Column(db.Float, default=0.0)    # Purchase behavior score
    loyalty_score = db.Column(db.Float, default=0.0)     # Repeat engagement score
    recency_score = db.Column(db.Float, default=0.0)     # Recent activity score
    total_score = db.Column(db.Float, default=0.0)       # Composite score
    
    # Conversion funnel stages
    has_viewed = db.Column(db.Boolean, default=False)
    has_clicked = db.Column(db.Boolean, default=False) 
    has_purchased = db.Column(db.Boolean, default=False)
    has_streamed = db.Column(db.Boolean, default=False)
    
    # Metrics
    total_interactions = db.Column(db.Integer, default=0)
    total_spent = db.Column(db.Float, default=0.0)
    first_interaction = db.Column(db.DateTime)
    last_interaction = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint to ensure one attribution per user-artist pair
    __table_args__ = (db.UniqueConstraint('user_id', 'artist_id', name='unique_user_artist_attribution'),)
    
    def __repr__(self):
        return f'<Attribution User {self.user_id} -> Artist {self.artist_id} (Score: {self.total_score})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'artist_id': self.artist_id,
            'engagement_score': self.engagement_score,
            'purchase_score': self.purchase_score,
            'loyalty_score': self.loyalty_score,
            'recency_score': self.recency_score,
            'total_score': self.total_score,
            'has_viewed': self.has_viewed,
            'has_clicked': self.has_clicked,
            'has_purchased': self.has_purchased,
            'has_streamed': self.has_streamed,
            'total_interactions': self.total_interactions,
            'total_spent': self.total_spent,
            'first_interaction': self.first_interaction.isoformat() if self.first_interaction else None,
            'last_interaction': self.last_interaction.isoformat() if self.last_interaction else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }