from .database import db
from datetime import datetime

class Concert(db.Model):
    __tablename__ = 'concerts'
    
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    venue = db.Column(db.String(255))
    city = db.Column(db.String(255))
    state = db.Column(db.String(100))
    country = db.Column(db.String(100))
    date = db.Column(db.DateTime)
    ticket_price_min = db.Column(db.Float)
    ticket_price_max = db.Column(db.Float)
    tickets_available = db.Column(db.Integer)
    tickets_sold = db.Column(db.Integer, default=0)
    external_id = db.Column(db.String(255))  # For external ticketing platforms
    status = db.Column(db.String(50), default='active')  # active, sold_out, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    interactions = db.relationship('Interaction', backref='concert', lazy=True)
    
    def __repr__(self):
        return f'<Concert {self.title} by {self.artist.name if self.artist else "Unknown"}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'artist_id': self.artist_id,
            'title': self.title,
            'venue': self.venue,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'date': self.date.isoformat() if self.date else None,
            'ticket_price_min': self.ticket_price_min,
            'ticket_price_max': self.ticket_price_max,
            'tickets_available': self.tickets_available,
            'tickets_sold': self.tickets_sold,
            'external_id': self.external_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }