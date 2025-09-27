from .database import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    user_id = db.Column(db.String(255), unique=True)  # External user ID
    name = db.Column(db.String(255))
    age_group = db.Column(db.String(50))  # e.g., '18-24', '25-34', etc.
    location = db.Column(db.String(255))
    spotify_user_id = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    interactions = db.relationship('Interaction', backref='user', lazy=True)
    attributions = db.relationship('Attribution', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'user_id': self.user_id,
            'name': self.name,
            'age_group': self.age_group,
            'location': self.location,
            'spotify_user_id': self.spotify_user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }