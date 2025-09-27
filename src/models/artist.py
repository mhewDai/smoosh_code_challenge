from .database import db
from datetime import datetime

class Artist(db.Model):
    __tablename__ = 'artists'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    genre = db.Column(db.String(100))
    spotify_id = db.Column(db.String(255), unique=True)
    external_id = db.Column(db.String(255))  # For external data sources
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    concerts = db.relationship('Concert', backref='artist', lazy=True)
    attributions = db.relationship('Attribution', backref='artist', lazy=True)
    
    def __repr__(self):
        return f'<Artist {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'genre': self.genre,
            'spotify_id': self.spotify_id,
            'external_id': self.external_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }