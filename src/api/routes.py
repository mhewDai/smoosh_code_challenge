from flask import Blueprint, jsonify, request
from datetime import datetime
from ..models import Artist, User, Concert, Interaction, Attribution
from ..pipeline import AttributionEngine, ConversionCalculator, DataIngestionPipeline

api_bp = Blueprint('api', __name__)

# Initialize pipeline components
attribution_engine = AttributionEngine()
conversion_calculator = ConversionCalculator()
data_pipeline = DataIngestionPipeline()

@api_bp.route('/artists', methods=['GET'])
def get_artists():
    """Get all artists"""
    artists = Artist.query.all()
    return jsonify([artist.to_dict() for artist in artists])

@api_bp.route('/artists/<int:artist_id>', methods=['GET'])
def get_artist(artist_id):
    """Get specific artist"""
    artist = Artist.query.get_or_404(artist_id)
    return jsonify(artist.to_dict())

@api_bp.route('/artists/<int:artist_id>/attributions', methods=['GET'])
def get_artist_attributions(artist_id):
    """Get top attributions for an artist"""
    limit = request.args.get('limit', 50, type=int)
    attributions = attribution_engine.get_artist_attributions(artist_id, limit)
    
    result = []
    for attr in attributions:
        attr_dict = attr.to_dict()
        attr_dict['user'] = attr.user.to_dict() if attr.user else None
        result.append(attr_dict)
    
    return jsonify(result)

@api_bp.route('/artists/<int:artist_id>/conversions', methods=['GET'])
def get_artist_conversions(artist_id):
    """Get conversion metrics for an artist"""
    days = request.args.get('days', 30, type=int)
    conversions = conversion_calculator.calculate_artist_conversions(artist_id, days)
    return jsonify(conversions)

@api_bp.route('/users/<int:user_id>/attributions', methods=['GET'])
def get_user_attributions(user_id):
    """Get all attributions for a user"""
    attributions = attribution_engine.get_user_attributions(user_id)
    
    result = []
    for attr in attributions:
        attr_dict = attr.to_dict()
        attr_dict['artist'] = attr.artist.to_dict() if attr.artist else None
        result.append(attr_dict)
    
    return jsonify(result)

@api_bp.route('/attributions/top', methods=['GET'])
def get_top_attributions():
    """Get top attributions across all users and artists"""
    limit = request.args.get('limit', 100, type=int)
    attributions = attribution_engine.get_top_attributions(limit)
    
    result = []
    for attr in attributions:
        attr_dict = attr.to_dict()
        attr_dict['user'] = attr.user.to_dict() if attr.user else None
        attr_dict['artist'] = attr.artist.to_dict() if attr.artist else None
        result.append(attr_dict)
    
    return jsonify(result)

@api_bp.route('/conversions/funnel', methods=['GET'])
def get_conversion_funnel():
    """Get overall conversion funnel"""
    artist_id = request.args.get('artist_id', type=int)
    days = request.args.get('days', 30, type=int)
    
    funnel = conversion_calculator.calculate_conversion_funnel(artist_id, days)
    return jsonify(funnel)

@api_bp.route('/conversions/top-artists', methods=['GET'])
def get_top_converting_artists():
    """Get artists with highest conversion rates"""
    limit = request.args.get('limit', 10, type=int)
    days = request.args.get('days', 30, type=int)
    
    top_artists = conversion_calculator.get_top_converting_artists(limit, days)
    return jsonify(top_artists)

@api_bp.route('/interactions', methods=['POST'])
def create_interaction():
    """Create new interaction"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        interactions = data_pipeline.ingest_user_interactions([data])
        if interactions:
            # Recalculate attribution for this user-artist pair
            interaction = interactions[0]
            attribution_engine.calculate_user_artist_attribution(
                interaction.user_id, 
                interaction.artist_id
            )
            return jsonify(interactions[0].to_dict()), 201
        else:
            return jsonify({'error': 'Failed to create interaction'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/data/ingest', methods=['POST'])
def ingest_data():
    """Ingest bulk data (concerts and interactions)"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        result = {'concerts': [], 'interactions': []}
        
        # Ingest concerts if provided
        if 'concerts' in data:
            concerts = data_pipeline.ingest_concert_data(data['concerts'])
            result['concerts'] = [c.to_dict() for c in concerts]
        
        # Ingest interactions if provided
        if 'interactions' in data:
            interactions = data_pipeline.ingest_user_interactions(data['interactions'])
            result['interactions'] = [i.to_dict() for i in interactions]
            
            # Recalculate attributions for affected user-artist pairs
            user_artist_pairs = set((i.user_id, i.artist_id) for i in interactions)
            for user_id, artist_id in user_artist_pairs:
                attribution_engine.calculate_user_artist_attribution(user_id, artist_id)
        
        return jsonify(result), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/data/sample', methods=['POST'])
def generate_sample_data():
    """Generate and ingest sample data for testing"""
    try:
        sample_data = data_pipeline.generate_sample_data()
        
        # Ingest the sample data
        concerts = data_pipeline.ingest_concert_data(sample_data['concerts'])
        interactions = data_pipeline.ingest_user_interactions(sample_data['interactions'])
        
        # Calculate attributions
        attributions = attribution_engine.calculate_all_attributions()
        
        return jsonify({
            'message': 'Sample data generated successfully',
            'concerts_created': len(concerts),
            'interactions_created': len(interactions),
            'attributions_calculated': len(attributions)
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/attributions/recalculate', methods=['POST'])
def recalculate_attributions():
    """Recalculate all attribution scores"""
    try:
        attributions = attribution_engine.calculate_all_attributions()
        return jsonify({
            'message': 'Attributions recalculated successfully',
            'total_attributions': len(attributions)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get overall system statistics"""
    try:
        stats = {
            'total_artists': Artist.query.count(),
            'total_users': User.query.count(),
            'total_concerts': Concert.query.count(),
            'total_interactions': Interaction.query.count(),
            'total_attributions': Attribution.query.count(),
            'last_updated': datetime.utcnow().isoformat()
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500