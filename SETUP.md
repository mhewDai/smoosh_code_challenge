# 🚀 Quick Start Guide

## Option 1: Simple Python Server (Recommended)

The simplest way to run the Smoosh Concert Attribution Pipeline:

```bash
# Clone the repository
git clone https://github.com/mhewDai/smoosh_code_challenge.git
cd smoosh_code_challenge

# Run the simple server (no dependencies required)
python simple_server.py
```

**Access the application:**
- 🌐 **Dashboard**: http://localhost:8000
- 🔗 **API**: http://localhost:8000/api/stats

## Option 2: Core Testing

Test the pipeline logic directly:

```bash
# Run the core pipeline test
python test_core.py
```

This will demonstrate:
- ✅ Database schema creation
- ✅ Sample data ingestion
- ✅ Attribution score calculations
- ✅ Conversion funnel analysis
- ✅ Revenue tracking

## Option 3: Full Flask Application

For production deployment with Flask:

```bash
# Install dependencies
pip install flask flask-sqlalchemy flask-cors

# Run the Flask application
python app.py
```

## 🎯 Key Features

### Dashboard Features
- **Real-time Statistics**: Live view of artists, users, concerts, and interactions
- **Attribution Leaderboard**: Top user-artist relationships ranked by engagement score
- **Artist Management**: View all artists with their genres and external IDs
- **API Integration**: Direct access to REST endpoints
- **Sample Data Generator**: One-click test data creation

### API Endpoints
- `GET /api/stats` - System statistics
- `GET /api/artists` - List all artists
- `GET /api/artists/{id}/conversions` - Artist-specific conversion metrics
- `GET /api/attributions` - Top user-artist attributions
- `POST /api/sample-data` - Generate test data

### Attribution Scoring
- **Engagement Score**: Weighted by interaction type (views=1, clicks=2, purchases=8, streams=4)
- **Purchase Score**: Based on transaction value and frequency
- **Multi-channel Support**: Website, mobile app, social media, streaming platforms
- **Funnel Tracking**: View → Click → Purchase → Stream progression

### Conversion Analytics
- **CTR**: Click-through rates from views to clicks
- **Purchase Rate**: Conversion from clicks to purchases
- **Revenue Metrics**: Total revenue, average order value, revenue by type
- **User Journey**: Complete touchpoint analysis across channels

## 🔧 Configuration

### Database
- **Default**: SQLite (smoosh_pipeline.db)
- **Production**: Configure PostgreSQL connection in app.py

### Sample Data
The system includes realistic sample data:
- **3 Artists**: Taylor Swift (Pop), The Rolling Stones (Rock), Drake (Hip-Hop)
- **3 Users**: Different age groups and engagement patterns
- **2 Concerts**: Major venue events with pricing
- **10+ Interactions**: Complete user journeys from view to purchase

## 📊 Example Results

After generating sample data, you'll see:
- **Attribution Scores**: User 1 → Taylor Swift (10.2 points, $150 spent)
- **Conversion Rates**: 66.7% CTR, 66.7% overall conversion
- **Revenue Tracking**: $175 total across tickets and merchandise
- **Funnel Analysis**: View → Click → Purchase → Stream progression

## 🧪 Testing

The pipeline includes comprehensive testing:
- **Core Logic**: test_core.py demonstrates all features
- **API Testing**: Use curl or browser to test endpoints
- **Database**: SQLite for development, easily upgradeable
- **Error Handling**: Robust error handling throughout

## 🔄 Data Flow

1. **Data Ingestion**: Concert and interaction data from multiple sources
2. **Attribution Calculation**: Real-time scoring based on user behavior
3. **Conversion Analysis**: Funnel metrics and revenue tracking
4. **API Serving**: RESTful endpoints for external integration
5. **Dashboard Display**: Interactive visualization of insights