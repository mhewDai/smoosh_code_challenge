import unittest
import tempfile
import os
from datetime import datetime, timedelta

from src.api import create_app
from src.models import db, Artist, User, Concert, Interaction, Attribution
from src.pipeline import DataIngestionPipeline, AttributionEngine, ConversionCalculator

class TestPipeline(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.db_fd, self.db_path = tempfile.mkstemp()
        
        config = {
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': f'sqlite:///{self.db_path}',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False
        }
        
        self.app = create_app(config)
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
        
        self.pipeline = DataIngestionPipeline()
        self.attribution_engine = AttributionEngine()
        self.conversion_calculator = ConversionCalculator()
    
    def tearDown(self):
        """Clean up test fixtures"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_artist_creation(self):
        """Test artist model creation"""
        artist_data = {
            'name': 'Test Artist',
            'genre': 'Rock',
            'external_id': 'test_artist_1'
        }
        
        artist = self.pipeline._find_or_create_artist(artist_data)
        self.assertIsNotNone(artist)
        self.assertEqual(artist.name, 'Test Artist')
        self.assertEqual(artist.genre, 'Rock')
    
    def test_user_creation(self):
        """Test user model creation"""
        user_data = {
            'email': 'test@example.com',
            'name': 'Test User',
            'age_group': '25-34'
        }
        
        user = self.pipeline._find_or_create_user(user_data)
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.name, 'Test User')
    
    def test_data_ingestion(self):
        """Test complete data ingestion pipeline"""
        sample_data = self.pipeline.generate_sample_data()
        
        # Ingest concerts
        concerts = self.pipeline.ingest_concert_data(sample_data['concerts'])
        self.assertGreater(len(concerts), 0)
        
        # Ingest interactions
        interactions = self.pipeline.ingest_user_interactions(sample_data['interactions'])
        self.assertGreater(len(interactions), 0)
        
        # Verify data was created
        self.assertGreater(Artist.query.count(), 0)
        self.assertGreater(User.query.count(), 0)
        self.assertGreater(Concert.query.count(), 0)
        self.assertGreater(Interaction.query.count(), 0)
    
    def test_attribution_calculation(self):
        """Test attribution score calculation"""
        # Create test data
        sample_data = self.pipeline.generate_sample_data()
        self.pipeline.ingest_concert_data(sample_data['concerts'])
        interactions = self.pipeline.ingest_user_interactions(sample_data['interactions'])
        
        # Calculate attributions
        attributions = self.attribution_engine.calculate_all_attributions()
        self.assertGreater(len(attributions), 0)
        
        # Check attribution properties
        attribution = attributions[0]
        self.assertIsInstance(attribution.total_score, float)
        self.assertGreaterEqual(attribution.total_score, 0)
        self.assertGreater(attribution.total_interactions, 0)
    
    def test_conversion_calculation(self):
        """Test conversion metrics calculation"""
        # Create test data
        sample_data = self.pipeline.generate_sample_data()
        self.pipeline.ingest_concert_data(sample_data['concerts'])
        interactions = self.pipeline.ingest_user_interactions(sample_data['interactions'])
        
        # Get an artist ID
        artist = Artist.query.first()
        self.assertIsNotNone(artist)
        
        # Calculate conversions
        conversions = self.conversion_calculator.calculate_artist_conversions(artist.id)
        
        # Check conversion structure
        self.assertIn('funnel_counts', conversions)
        self.assertIn('conversion_rates', conversions)
        self.assertIn('revenue_metrics', conversions)
        self.assertIn('engagement_metrics', conversions)
        
        # Check funnel counts
        funnel = conversions['funnel_counts']
        self.assertIn('view', funnel)
        self.assertIn('click', funnel)
        self.assertIn('purchase', funnel)
        self.assertIn('stream', funnel)

if __name__ == '__main__':
    unittest.main()