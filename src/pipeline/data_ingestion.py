import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from ..models import db, Artist, User, Concert, Interaction

class DataIngestionPipeline:
    """Pipeline for ingesting concert and user interaction data"""
    
    def __init__(self):
        self.session = requests.Session()
    
    def ingest_concert_data(self, concerts_data: List[Dict]) -> List[Concert]:
        """Ingest concert data from external sources"""
        ingested_concerts = []
        
        for concert_data in concerts_data:
            # Find or create artist
            artist = self._find_or_create_artist(concert_data.get('artist'))
            
            # Create concert
            concert = Concert(
                artist_id=artist.id,
                title=concert_data.get('title', ''),
                venue=concert_data.get('venue', ''),
                city=concert_data.get('city', ''),
                state=concert_data.get('state', ''),
                country=concert_data.get('country', ''),
                date=self._parse_date(concert_data.get('date')),
                ticket_price_min=concert_data.get('ticket_price_min'),
                ticket_price_max=concert_data.get('ticket_price_max'),
                tickets_available=concert_data.get('tickets_available'),
                external_id=concert_data.get('external_id'),
                status=concert_data.get('status', 'active')
            )
            
            db.session.add(concert)
            ingested_concerts.append(concert)
        
        db.session.commit()
        return ingested_concerts
    
    def ingest_user_interactions(self, interactions_data: List[Dict]) -> List[Interaction]:
        """Ingest user interaction data"""
        ingested_interactions = []
        
        for interaction_data in interactions_data:
            # Find or create user
            user = self._find_or_create_user(interaction_data.get('user'))
            
            # Find or create artist
            artist = self._find_or_create_artist(interaction_data.get('artist'))
            
            # Find concert if specified
            concert_id = None
            if interaction_data.get('concert_id'):
                concert = Concert.query.filter_by(
                    external_id=interaction_data.get('concert_id')
                ).first()
                if concert:
                    concert_id = concert.id
            
            # Create interaction
            interaction = Interaction(
                user_id=user.id,
                artist_id=artist.id,
                concert_id=concert_id,
                interaction_type=interaction_data.get('type', 'view'),
                channel=interaction_data.get('channel', 'website'),
                value=interaction_data.get('value'),
                metadata=interaction_data.get('metadata', {}),
                timestamp=self._parse_date(interaction_data.get('timestamp')) or datetime.utcnow(),
                session_id=interaction_data.get('session_id')
            )
            
            db.session.add(interaction)
            ingested_interactions.append(interaction)
        
        db.session.commit()
        return ingested_interactions
    
    def _find_or_create_artist(self, artist_data: Dict) -> Artist:
        """Find existing artist or create new one"""
        if not artist_data:
            return None
            
        # Try to find by external_id or spotify_id first
        artist = None
        if artist_data.get('external_id'):
            artist = Artist.query.filter_by(external_id=artist_data['external_id']).first()
        elif artist_data.get('spotify_id'):
            artist = Artist.query.filter_by(spotify_id=artist_data['spotify_id']).first()
        
        # If not found, try by name
        if not artist and artist_data.get('name'):
            artist = Artist.query.filter_by(name=artist_data['name']).first()
        
        # Create new artist if not found
        if not artist:
            artist = Artist(
                name=artist_data.get('name', ''),
                genre=artist_data.get('genre'),
                spotify_id=artist_data.get('spotify_id'),
                external_id=artist_data.get('external_id')
            )
            db.session.add(artist)
            db.session.flush()  # Get the ID without committing
        
        return artist
    
    def _find_or_create_user(self, user_data: Dict) -> User:
        """Find existing user or create new one"""
        if not user_data:
            return None
            
        # Try to find by email or user_id
        user = None
        if user_data.get('email'):
            user = User.query.filter_by(email=user_data['email']).first()
        elif user_data.get('user_id'):
            user = User.query.filter_by(user_id=user_data['user_id']).first()
        
        # Create new user if not found
        if not user:
            user = User(
                email=user_data.get('email', ''),
                user_id=user_data.get('user_id'),
                name=user_data.get('name'),
                age_group=user_data.get('age_group'),
                location=user_data.get('location'),
                spotify_user_id=user_data.get('spotify_user_id')
            )
            db.session.add(user)
            db.session.flush()  # Get the ID without committing
        
        return user
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object"""
        if not date_str:
            return None
            
        try:
            # Try different date formats
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ']:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
        except Exception:
            pass
        
        return None
    
    def generate_sample_data(self) -> Dict:
        """Generate sample data for testing"""
        # Sample artists
        artists_data = [
            {'name': 'The Rolling Stones', 'genre': 'Rock', 'external_id': 'artist_1'},
            {'name': 'Taylor Swift', 'genre': 'Pop', 'external_id': 'artist_2'},
            {'name': 'Drake', 'genre': 'Hip-Hop', 'external_id': 'artist_3'},
        ]
        
        # Sample concerts
        concerts_data = [
            {
                'artist': artists_data[0],
                'title': 'Rolling Stones World Tour 2024',
                'venue': 'Madison Square Garden',
                'city': 'New York',
                'state': 'NY',
                'country': 'USA',
                'date': '2024-06-15 20:00:00',
                'ticket_price_min': 75.0,
                'ticket_price_max': 250.0,
                'tickets_available': 20000,
                'external_id': 'concert_1'
            },
            {
                'artist': artists_data[1],
                'title': 'Eras Tour',
                'venue': 'Wembley Stadium',
                'city': 'London',
                'country': 'UK',
                'date': '2024-07-20 19:30:00',
                'ticket_price_min': 50.0,
                'ticket_price_max': 400.0,
                'tickets_available': 90000,
                'external_id': 'concert_2'
            }
        ]
        
        # Sample user interactions
        interactions_data = [
            {
                'user': {'email': 'user1@example.com', 'name': 'John Doe', 'age_group': '25-34'},
                'artist': artists_data[0],
                'type': 'view',
                'channel': 'website',
                'timestamp': '2024-01-15 10:30:00',
                'session_id': 'session_1'
            },
            {
                'user': {'email': 'user1@example.com'},
                'artist': artists_data[0],
                'type': 'click',
                'channel': 'website',
                'timestamp': '2024-01-15 10:32:00',
                'session_id': 'session_1'
            },
            {
                'user': {'email': 'user1@example.com'},
                'artist': artists_data[0],
                'type': 'ticket_purchase',
                'channel': 'website',
                'value': 150.0,
                'timestamp': '2024-01-15 10:35:00',
                'session_id': 'session_1',
                'concert_id': 'concert_1'
            },
            {
                'user': {'email': 'user2@example.com', 'name': 'Jane Smith', 'age_group': '18-24'},
                'artist': artists_data[1],
                'type': 'stream',
                'channel': 'spotify',
                'value': 3.5,  # minutes streamed
                'timestamp': '2024-01-16 14:20:00'
            }
        ]
        
        return {
            'artists': artists_data,
            'concerts': concerts_data,
            'interactions': interactions_data
        }