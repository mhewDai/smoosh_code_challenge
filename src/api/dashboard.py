from flask import Blueprint, render_template_string, jsonify
from ..pipeline import ConversionCalculator, AttributionEngine
from ..models import Artist, User, Concert, Interaction, Attribution

dashboard_bp = Blueprint('dashboard', __name__)

attribution_engine = AttributionEngine()
conversion_calculator = ConversionCalculator()

@dashboard_bp.route('/')
def dashboard():
    """Main dashboard page"""
    
    # Get basic stats
    stats = {
        'total_artists': Artist.query.count(),
        'total_users': User.query.count(),
        'total_concerts': Concert.query.count(),
        'total_interactions': Interaction.query.count(),
        'total_attributions': Attribution.query.count()
    }
    
    # Get top converting artists
    top_artists = conversion_calculator.get_top_converting_artists(limit=5)
    
    # Get top attributions
    top_attributions = attribution_engine.get_top_attributions(limit=10)
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Smoosh Concert Attribution Dashboard</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 10px;
                margin-bottom: 30px;
                text-align: center;
            }
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .stat-card {
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                text-align: center;
            }
            .stat-number {
                font-size: 2em;
                font-weight: bold;
                color: #667eea;
                margin-bottom: 5px;
            }
            .stat-label {
                color: #666;
                font-size: 0.9em;
            }
            .section {
                background: white;
                padding: 25px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }
            .section h2 {
                margin-top: 0;
                color: #333;
                border-bottom: 2px solid #667eea;
                padding-bottom: 10px;
            }
            .table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
            }
            .table th, .table td {
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }
            .table th {
                background-color: #f8f9fa;
                font-weight: 600;
            }
            .score {
                font-weight: bold;
                color: #28a745;
            }
            .conversion-rate {
                font-weight: bold;
                color: #dc3545;
            }
            .btn {
                background: #667eea;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
                margin: 5px;
            }
            .btn:hover {
                background: #5a67d8;
            }
            .actions {
                text-align: center;
                margin: 30px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎵 Smoosh Concert Attribution Dashboard</h1>
                <p>Track user engagement and artist attribution across multiple touchpoints</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{{ stats.total_artists }}</div>
                    <div class="stat-label">Artists</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ stats.total_users }}</div>
                    <div class="stat-label">Users</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ stats.total_concerts }}</div>
                    <div class="stat-label">Concerts</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ stats.total_interactions }}</div>
                    <div class="stat-label">Interactions</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ stats.total_attributions }}</div>
                    <div class="stat-label">Attributions</div>
                </div>
            </div>
            
            <div class="actions">
                <button class="btn" onclick="generateSampleData()">Generate Sample Data</button>
                <button class="btn" onclick="recalculateAttributions()">Recalculate Attributions</button>
                <a href="/api/stats" class="btn">View API Stats</a>
            </div>
            
            <div class="section">
                <h2>🏆 Top Converting Artists (Last 30 Days)</h2>
                <table class="table">
                    <thead>
                        <tr>
                            <th>Artist</th>
                            <th>Users</th>
                            <th>CTR</th>
                            <th>Purchase Rate</th>
                            <th>Overall Conversion</th>
                            <th>Revenue</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for artist in top_artists %}
                        <tr>
                            <td><strong>{{ artist.artist_name or 'Unknown' }}</strong></td>
                            <td>{{ artist.total_users }}</td>
                            <td><span class="conversion-rate">{{ "%.1f" | format(artist.conversion_rates.ctr * 100) }}%</span></td>
                            <td><span class="conversion-rate">{{ "%.1f" | format(artist.conversion_rates.purchase_rate * 100) }}%</span></td>
                            <td><span class="conversion-rate">{{ "%.1f" | format(artist.conversion_rates.overall_conversion * 100) }}%</span></td>
                            <td>${{ "%.2f" | format(artist.revenue_metrics.total_revenue) }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            
            <div class="section">
                <h2>⭐ Top User-Artist Attributions</h2>
                <table class="table">
                    <thead>
                        <tr>
                            <th>User</th>
                            <th>Artist</th>
                            <th>Total Score</th>
                            <th>Interactions</th>
                            <th>Total Spent</th>
                            <th>Funnel Stage</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for attr in top_attributions %}
                        <tr>
                            <td>{{ attr.user.email if attr.user else 'Unknown' }}</td>
                            <td><strong>{{ attr.artist.name if attr.artist else 'Unknown' }}</strong></td>
                            <td><span class="score">{{ "%.1f" | format(attr.total_score) }}</span></td>
                            <td>{{ attr.total_interactions }}</td>
                            <td>${{ "%.2f" | format(attr.total_spent) }}</td>
                            <td>
                                {% if attr.has_purchased %}Purchase{% elif attr.has_clicked %}Click{% elif attr.has_viewed %}View{% endif %}
                                {% if attr.has_streamed %} + Stream{% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
        
        <script>
            async function generateSampleData() {
                try {
                    const response = await fetch('/api/data/sample', { method: 'POST' });
                    const result = await response.json();
                    alert('Sample data generated: ' + result.concerts_created + ' concerts, ' + result.interactions_created + ' interactions');
                    location.reload();
                } catch (error) {
                    alert('Error generating sample data: ' + error.message);
                }
            }
            
            async function recalculateAttributions() {
                try {
                    const response = await fetch('/api/attributions/recalculate', { method: 'POST' });
                    const result = await response.json();
                    alert('Attributions recalculated: ' + result.total_attributions + ' total');
                    location.reload();
                } catch (error) {
                    alert('Error recalculating attributions: ' + error.message);
                }
            }
        </script>
    </body>
    </html>
    """
    
    return render_template_string(
        html_template, 
        stats=stats, 
        top_artists=top_artists, 
        top_attributions=top_attributions
    )