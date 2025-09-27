# 🎵 Smoosh Concert Attribution Pipeline

A comprehensive data pipeline that scrapes/ingests concert and ticketing data, attributes users to artists, and calculates conversion funnels across multiple touchpoints.

## 🎯 Features

- **Clean Database Schema**: Concerts, users, artists, and interactions with proper relationships
- **Attribution Logic**: Sophisticated scoring system that assigns users to artists based on engagement
- **Conversion Funnels**: Track user journey from view → click → purchase → stream
- **Multi-Channel Support**: Website, mobile app, social media, streaming platforms
- **RESTful API**: Complete API for data ingestion and insights retrieval
- **Interactive Dashboard**: Real-time visualization of key metrics and insights
- **Sample Data Generator**: Built-in test data for immediate exploration

## 🏗️ Architecture

### Database Schema
- **Artists**: Artist information with external IDs for data source integration
- **Users**: User profiles with demographic and platform information
- **Concerts**: Concert events with venue, pricing, and availability data
- **Interactions**: User touchpoints across all channels with metadata
- **Attributions**: Calculated user-artist relationships with composite scores

### Attribution Engine
Calculates user-artist attribution using multiple factors:
- **Engagement Score**: Weighted by interaction type and channel
- **Purchase Score**: Based on transaction value and frequency
- **Loyalty Score**: Repeat engagement patterns over time
- **Recency Score**: Time-decay function for recent activity

### Conversion Calculator
Tracks conversion funnels and metrics:
- **CTR**: Click-through rates from views to clicks
- **Purchase Rate**: Conversion from clicks to purchases
- **Stream Lift**: Streaming activity following other touchpoints
- **Revenue Metrics**: Total revenue, AOV, and revenue by type

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/mhewDai/smoosh_code_challenge.git
cd smoosh_code_challenge

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### Access Points
- **Dashboard**: http://localhost:5000
- **API Documentation**: http://localhost:5000/api/stats
- **Sample Data**: Click "Generate Sample Data" in dashboard

### API Endpoints

#### Core Data
- `GET /api/artists` - List all artists
- `GET /api/artists/{id}` - Get specific artist
- `POST /api/data/ingest` - Bulk data ingestion
- `POST /api/data/sample` - Generate sample data

#### Attribution & Insights
- `GET /api/artists/{id}/attributions` - Top attributions for artist
- `GET /api/users/{id}/attributions` - User's artist attributions
- `GET /api/attributions/top` - Top attributions globally
- `POST /api/attributions/recalculate` - Recalculate all scores

#### Conversion Analytics
- `GET /api/artists/{id}/conversions` - Artist conversion metrics
- `GET /api/conversions/funnel` - Overall conversion funnel
- `GET /api/conversions/top-artists` - Top converting artists

## 📊 Sample Usage

### Data Ingestion
```python
from src.pipeline import DataIngestionPipeline

pipeline = DataIngestionPipeline()

# Ingest concert data
concerts_data = [{
    'artist': {'name': 'Taylor Swift', 'genre': 'Pop'},
    'title': 'Eras Tour',
    'venue': 'Madison Square Garden',
    'date': '2024-06-15 20:00:00',
    'ticket_price_min': 75.0,
    'ticket_price_max': 300.0
}]

concerts = pipeline.ingest_concert_data(concerts_data)

# Ingest user interactions
interactions_data = [{
    'user': {'email': 'fan@example.com'},
    'artist': {'name': 'Taylor Swift'},
    'type': 'ticket_purchase',
    'channel': 'website',
    'value': 150.0,
    'timestamp': '2024-01-15 10:35:00'
}]

interactions = pipeline.ingest_user_interactions(interactions_data)
```

### Attribution Calculation
```python
from src.pipeline import AttributionEngine

engine = AttributionEngine()

# Calculate attributions for all users
attributions = engine.calculate_all_attributions()

# Get top attributions
top_attributions = engine.get_top_attributions(limit=10)
```

### Conversion Analysis
```python
from src.pipeline import ConversionCalculator

calculator = ConversionCalculator()

# Get artist conversion metrics
conversions = calculator.calculate_artist_conversions(artist_id=1, days=30)

# Get conversion funnel
funnel = calculator.calculate_conversion_funnel(days=30)
```

## 🧪 Testing

```bash
# Run tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_pipeline.py::TestPipeline::test_attribution_calculation -v
```

## 📈 Key Metrics Tracked

### Conversion Funnel
- **View Rate**: Users who viewed artist content
- **Click-Through Rate**: Views that resulted in clicks
- **Purchase Rate**: Clicks that converted to purchases
- **Stream Lift**: Streaming activity increase post-engagement

### Attribution Scores
- **Engagement Score**: Weighted interaction frequency and types
- **Purchase Score**: Monetary value and purchase frequency
- **Loyalty Score**: Repeat engagement patterns
- **Recency Score**: Time-decay based on last interaction

### Revenue Metrics
- **Total Revenue**: Sum of all purchases
- **Average Order Value**: Revenue per transaction
- **Revenue by Type**: Ticket vs merchandise sales
- **Revenue per User**: Customer lifetime value

## 🔧 Configuration

### Environment Variables
- `PORT`: Server port (default: 5000)
- `DEBUG`: Debug mode (default: True)
- `DATABASE_URL`: Database connection string

### Database
Default uses SQLite for simplicity. For production:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:pass@host:port/db'
```

## 🎨 Dashboard Features

The interactive dashboard provides:
- **Real-time Statistics**: Live counts of artists, users, concerts, interactions
- **Top Converting Artists**: Ranked by conversion rates and revenue
- **Attribution Leaderboard**: Highest-scoring user-artist relationships
- **Quick Actions**: Generate sample data, recalculate attributions
- **API Integration**: Direct links to API endpoints

## 🚀 Production Deployment

For production deployment:

1. **Database**: Upgrade to PostgreSQL or similar
2. **Environment**: Set proper environment variables
3. **Scaling**: Use WSGI server like Gunicorn
4. **Monitoring**: Add logging and error tracking
5. **Security**: Implement authentication and rate limiting

## 📝 Data Model

### Interaction Types
- `view`: Content/artist page views
- `click`: Clicks on artist content or links
- `ticket_purchase`: Concert ticket purchases
- `merch_purchase`: Merchandise purchases
- `social_share`: Social media shares/posts
- `stream`: Music streaming activity

### Channels
- `website`: Official website
- `mobile_app`: Mobile application
- `social_media`: Social platforms
- `streaming_platform`: Spotify, Apple Music, etc.
- `email`: Email campaigns

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.