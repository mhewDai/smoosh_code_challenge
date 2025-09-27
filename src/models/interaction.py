from .database import db
from datetime import datetime

class Interaction(db.Model):
    __tablename__ = 'interactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    concert_id = db.Column(db.Integer, db.ForeignKey('concerts.id'), nullable=True)
    
    # Interaction types: view, click, ticket_purchase, merch_purchase, social_share, stream
    interaction_type = db.Column(db.String(50), nullable=False)
    
    # Channel where interaction occurred: website, mobile_app, social_media, streaming_platform
    channel = db.Column(db.String(50))
    
    # Additional metadata
    value = db.Column(db.Float)  # Monetary value for purchases, play time for streams, etc.
    metadata = db.Column(db.JSON)  # Additional data like product details, stream duration, etc.
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    session_id = db.Column(db.String(255))  # To group related interactions
    
    # Foreign key relationships
    artist = db.relationship('Artist', backref='interactions')
    
    def __repr__(self):
        return f'<Interaction {self.interaction_type} by User {self.user_id} for Artist {self.artist_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'artist_id': self.artist_id,
            'concert_id': self.concert_id,
            'interaction_type': self.interaction_type,
            'channel': self.channel,
            'value': self.value,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'session_id': self.session_id
        }