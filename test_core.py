#!/usr/bin/env python3
"""
Test core pipeline functionality without Flask dependencies
"""

import sys
import os
import sqlite3
import json
from datetime import datetime, timedelta

# Simple database wrapper
class SimpleDB:
    def __init__(self, db_path=':memory:'):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
    
    def create_tables(self):
        """Create database tables"""
        cursor = self.conn.cursor()
        
        # Artists table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS artists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                genre TEXT,
                external_id TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT,
                age_group TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Concerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS concerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                artist_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                venue TEXT,
                city TEXT,
                date TIMESTAMP,
                ticket_price_min REAL,
                ticket_price_max REAL,
                external_id TEXT,
                FOREIGN KEY (artist_id) REFERENCES artists (id)
            )
        ''')
        
        # Interactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                artist_id INTEGER NOT NULL,
                concert_id INTEGER,
                interaction_type TEXT NOT NULL,
                channel TEXT,
                value REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                session_id TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (artist_id) REFERENCES artists (id),
                FOREIGN KEY (concert_id) REFERENCES concerts (id)
            )
        ''')
        
        # Attributions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attributions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                artist_id INTEGER NOT NULL,
                total_score REAL DEFAULT 0.0,
                engagement_score REAL DEFAULT 0.0,
                purchase_score REAL DEFAULT 0.0,
                total_interactions INTEGER DEFAULT 0,
                total_spent REAL DEFAULT 0.0,
                has_viewed BOOLEAN DEFAULT 0,
                has_clicked BOOLEAN DEFAULT 0,
                has_purchased BOOLEAN DEFAULT 0,
                has_streamed BOOLEAN DEFAULT 0,
                UNIQUE(user_id, artist_id)
            )
        ''')
        
        self.conn.commit()
    
    def execute(self, query, params=()):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor
    
    def fetch_all(self, query, params=()):
        cursor = self.execute(query, params)
        return cursor.fetchall()
    
    def fetch_one(self, query, params=()):
        cursor = self.execute(query, params)
        return cursor.fetchone()
    
    def commit(self):
        self.conn.commit()
    
    def close(self):
        self.conn.close()

class SimplePipeline:
    """Simplified pipeline for testing"""
    
    def __init__(self, db):
        self.db = db
        self.interaction_weights = {
            'view': 1.0,
            'click': 2.0,
            'ticket_purchase': 8.0,
            'merch_purchase': 5.0,
            'stream': 4.0,
            'social_share': 3.0
        }
    
    def create_artist(self, name, genre=None, external_id=None):
        """Create or find artist"""
        # Check if artist exists
        existing = self.db.fetch_one(
            "SELECT * FROM artists WHERE name = ? OR external_id = ?",
            (name, external_id)
        )
        
        if existing:
            return existing['id']
        
        # Create new artist
        cursor = self.db.execute(
            "INSERT INTO artists (name, genre, external_id) VALUES (?, ?, ?)",
            (name, genre, external_id)
        )
        self.db.commit()
        return cursor.lastrowid
    
    def create_user(self, email, name=None, age_group=None):
        """Create or find user"""
        # Check if user exists
        existing = self.db.fetch_one("SELECT * FROM users WHERE email = ?", (email,))
        
        if existing:
            return existing['id']
        
        # Create new user
        cursor = self.db.execute(
            "INSERT INTO users (email, name, age_group) VALUES (?, ?, ?)",
            (email, name, age_group)
        )
        self.db.commit()
        return cursor.lastrowid
    
    def create_concert(self, artist_id, title, venue=None, city=None, price_min=None, price_max=None):
        """Create concert"""
        cursor = self.db.execute(
            "INSERT INTO concerts (artist_id, title, venue, city, ticket_price_min, ticket_price_max) VALUES (?, ?, ?, ?, ?, ?)",
            (artist_id, title, venue, city, price_min, price_max)
        )
        self.db.commit()
        return cursor.lastrowid
    
    def create_interaction(self, user_id, artist_id, interaction_type, channel=None, value=None, concert_id=None):
        """Create interaction"""
        cursor = self.db.execute(
            "INSERT INTO interactions (user_id, artist_id, concert_id, interaction_type, channel, value) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, artist_id, concert_id, interaction_type, channel, value)
        )
        self.db.commit()
        return cursor.lastrowid
    
    def calculate_attribution(self, user_id, artist_id):
        """Calculate attribution for user-artist pair"""
        # Get interactions
        interactions = self.db.fetch_all(
            "SELECT * FROM interactions WHERE user_id = ? AND artist_id = ?",
            (user_id, artist_id)
        )
        
        if not interactions:
            return None
        
        # Calculate scores
        engagement_score = 0.0
        purchase_score = 0.0
        total_spent = 0.0
        
        interaction_types = set()
        
        for interaction in interactions:
            interaction_type = interaction['interaction_type']
            interaction_types.add(interaction_type)
            
            # Engagement score
            weight = self.interaction_weights.get(interaction_type, 1.0)
            engagement_score += weight
            
            # Purchase score
            if interaction_type in ['ticket_purchase', 'merch_purchase'] and interaction['value']:
                purchase_score += 20.0  # Base purchase score
                total_spent += interaction['value']
        
        # Normalize engagement score
        engagement_score = min(engagement_score / len(interactions), 100.0)
        
        # Total score
        total_score = engagement_score * 0.6 + purchase_score * 0.4
        
        # Funnel stages
        has_viewed = 'view' in interaction_types
        has_clicked = 'click' in interaction_types
        has_purchased = any(t in interaction_types for t in ['ticket_purchase', 'merch_purchase'])
        has_streamed = 'stream' in interaction_types
        
        # Save attribution
        self.db.execute(
            """INSERT OR REPLACE INTO attributions 
               (user_id, artist_id, total_score, engagement_score, purchase_score, 
                total_interactions, total_spent, has_viewed, has_clicked, has_purchased, has_streamed)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, artist_id, total_score, engagement_score, purchase_score,
             len(interactions), total_spent, has_viewed, has_clicked, has_purchased, has_streamed)
        )
        self.db.commit()
        
        return {
            'user_id': user_id,
            'artist_id': artist_id,
            'total_score': total_score,
            'engagement_score': engagement_score,
            'purchase_score': purchase_score,
            'total_interactions': len(interactions),
            'total_spent': total_spent,
            'has_viewed': has_viewed,
            'has_clicked': has_clicked,
            'has_purchased': has_purchased,
            'has_streamed': has_streamed
        }
    
    def get_conversion_metrics(self, artist_id=None):
        """Calculate conversion metrics"""
        if artist_id:
            interactions = self.db.fetch_all(
                "SELECT * FROM interactions WHERE artist_id = ?", (artist_id,)
            )
        else:
            interactions = self.db.fetch_all("SELECT * FROM interactions")
        
        # Group by user
        user_interactions = {}
        for interaction in interactions:
            user_id = interaction['user_id']
            if user_id not in user_interactions:
                user_interactions[user_id] = []
            user_interactions[user_id].append(interaction)
        
        # Calculate funnel counts
        view_count = 0
        click_count = 0
        purchase_count = 0
        stream_count = 0
        total_revenue = 0.0
        
        for user_id, user_ints in user_interactions.items():
            types = {i['interaction_type'] for i in user_ints}
            
            if 'view' in types:
                view_count += 1
            if 'click' in types:
                click_count += 1
            if any(t in types for t in ['ticket_purchase', 'merch_purchase']):
                purchase_count += 1
            if 'stream' in types:
                stream_count += 1
            
            # Calculate revenue
            for interaction in user_ints:
                if interaction['interaction_type'] in ['ticket_purchase', 'merch_purchase'] and interaction['value']:
                    total_revenue += interaction['value']
        
        # Calculate conversion rates
        ctr = click_count / view_count if view_count > 0 else 0.0
        purchase_rate = purchase_count / click_count if click_count > 0 else 0.0
        overall_conversion = purchase_count / view_count if view_count > 0 else 0.0
        
        return {
            'total_users': len(user_interactions),
            'funnel_counts': {
                'view': view_count,
                'click': click_count,
                'purchase': purchase_count,
                'stream': stream_count
            },
            'conversion_rates': {
                'ctr': ctr,
                'purchase_rate': purchase_rate,
                'overall_conversion': overall_conversion
            },
            'total_revenue': total_revenue
        }

def test_pipeline():
    """Test the pipeline functionality"""
    print("🎵 Testing Smoosh Concert Attribution Pipeline")
    print("=" * 50)
    
    # Initialize database and pipeline
    db = SimpleDB()
    pipeline = SimplePipeline(db)
    
    # Create test data
    print("\n1. Creating test artists...")
    taylor_id = pipeline.create_artist("Taylor Swift", "Pop", "taylor_swift_1")
    stones_id = pipeline.create_artist("The Rolling Stones", "Rock", "rolling_stones_1")
    drake_id = pipeline.create_artist("Drake", "Hip-Hop", "drake_1")
    print(f"   ✓ Created artists: Taylor Swift ({taylor_id}), Rolling Stones ({stones_id}), Drake ({drake_id})")
    
    print("\n2. Creating test users...")
    user1_id = pipeline.create_user("fan1@example.com", "John Doe", "25-34")
    user2_id = pipeline.create_user("fan2@example.com", "Jane Smith", "18-24")
    user3_id = pipeline.create_user("fan3@example.com", "Bob Wilson", "35-44")
    print(f"   ✓ Created users: {user1_id}, {user2_id}, {user3_id}")
    
    print("\n3. Creating test concerts...")
    concert1_id = pipeline.create_concert(taylor_id, "Eras Tour", "Madison Square Garden", "New York", 75.0, 400.0)
    concert2_id = pipeline.create_concert(stones_id, "World Tour 2024", "Wembley Stadium", "London", 50.0, 250.0)
    print(f"   ✓ Created concerts: {concert1_id}, {concert2_id}")
    
    print("\n4. Creating test interactions...")
    
    # User 1 - Taylor Swift fan journey (view -> click -> purchase -> stream)
    pipeline.create_interaction(user1_id, taylor_id, "view", "website")
    pipeline.create_interaction(user1_id, taylor_id, "click", "website")
    pipeline.create_interaction(user1_id, taylor_id, "ticket_purchase", "website", 150.0, concert1_id)
    pipeline.create_interaction(user1_id, taylor_id, "stream", "spotify", 45.0)  # 45 minutes
    
    # User 2 - Rolling Stones fan (view -> stream only)
    pipeline.create_interaction(user2_id, stones_id, "view", "website")
    pipeline.create_interaction(user2_id, stones_id, "stream", "spotify", 30.0)
    
    # User 3 - Multi-artist engagement
    pipeline.create_interaction(user3_id, taylor_id, "view", "website")
    pipeline.create_interaction(user3_id, drake_id, "view", "website")
    pipeline.create_interaction(user3_id, drake_id, "click", "website")
    pipeline.create_interaction(user3_id, drake_id, "merch_purchase", "website", 25.0)
    
    print("   ✓ Created various interaction patterns")
    
    print("\n5. Calculating attributions...")
    
    # Calculate attributions for all user-artist pairs
    user_artist_pairs = [
        (user1_id, taylor_id),
        (user2_id, stones_id),
        (user3_id, taylor_id),
        (user3_id, drake_id)
    ]
    
    attributions = []
    for user_id, artist_id in user_artist_pairs:
        attr = pipeline.calculate_attribution(user_id, artist_id)
        if attr:
            attributions.append(attr)
    
    print(f"   ✓ Calculated {len(attributions)} attributions")
    
    print("\n6. Attribution Results:")
    print("   " + "-" * 80)
    print("   User ID | Artist ID | Score | Interactions | Spent | Funnel Stage")
    print("   " + "-" * 80)
    
    for attr in sorted(attributions, key=lambda x: x['total_score'], reverse=True):
        funnel_stage = "View"
        if attr['has_purchased']:
            funnel_stage = "Purchase"
        elif attr['has_clicked']:
            funnel_stage = "Click"
        if attr['has_streamed']:
            funnel_stage += "+Stream"
        
        print(f"   {attr['user_id']:7} | {attr['artist_id']:9} | {attr['total_score']:5.1f} | {attr['total_interactions']:12} | ${attr['total_spent']:5.0f} | {funnel_stage}")
    
    print("\n7. Conversion Metrics:")
    overall_metrics = pipeline.get_conversion_metrics()
    
    print(f"   Total Users: {overall_metrics['total_users']}")
    print(f"   Funnel Progression:")
    print(f"     Views: {overall_metrics['funnel_counts']['view']}")
    print(f"     Clicks: {overall_metrics['funnel_counts']['click']}")
    print(f"     Purchases: {overall_metrics['funnel_counts']['purchase']}")
    print(f"     Streams: {overall_metrics['funnel_counts']['stream']}")
    print(f"   Conversion Rates:")
    print(f"     CTR: {overall_metrics['conversion_rates']['ctr']:.1%}")
    print(f"     Purchase Rate: {overall_metrics['conversion_rates']['purchase_rate']:.1%}")
    print(f"     Overall Conversion: {overall_metrics['conversion_rates']['overall_conversion']:.1%}")
    print(f"   Total Revenue: ${overall_metrics['total_revenue']:.2f}")
    
    # Artist-specific metrics
    print("\n8. Artist-Specific Metrics:")
    for artist_id, artist_name in [(taylor_id, "Taylor Swift"), (stones_id, "Rolling Stones"), (drake_id, "Drake")]:
        metrics = pipeline.get_conversion_metrics(artist_id)
        if metrics['total_users'] > 0:
            print(f"   {artist_name}:")
            print(f"     Users: {metrics['total_users']}, Revenue: ${metrics['total_revenue']:.2f}")
            print(f"     Conversion: {metrics['conversion_rates']['overall_conversion']:.1%}")
    
    print("\n✅ Pipeline test completed successfully!")
    print("\nKey Features Demonstrated:")
    print("  ✓ Clean database schema with proper relationships")
    print("  ✓ Multi-channel interaction tracking")
    print("  ✓ Attribution scoring with engagement and purchase factors")
    print("  ✓ Conversion funnel analysis (view → click → purchase → stream)")
    print("  ✓ Revenue tracking and metrics")
    print("  ✓ User-artist relationship attribution")
    
    # Close database
    db.close()

if __name__ == "__main__":
    test_pipeline()