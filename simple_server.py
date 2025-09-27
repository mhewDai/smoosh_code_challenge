#!/usr/bin/env python3
"""
Simple HTTP server for Smoosh Concert Attribution Pipeline
Uses only Python standard library for maximum compatibility
"""

import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from test_core import SimpleDB, SimplePipeline
import os

class APIHandler(BaseHTTPRequestHandler):
    
    def __init__(self, *args, **kwargs):
        self.db = SimpleDB('smoosh_pipeline.db')  # Persistent database
        self.pipeline = SimplePipeline(self.db)
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        path = self.path.split('?')[0]  # Remove query parameters
        
        if path == '/':
            self.serve_dashboard()
        elif path == '/api/stats':
            self.serve_stats()
        elif path == '/api/artists':
            self.serve_artists()
        elif path.startswith('/api/artists/') and path.endswith('/conversions'):
            artist_id = int(path.split('/')[3])
            self.serve_artist_conversions(artist_id)
        elif path == '/api/attributions':
            self.serve_attributions()
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests"""
        path = self.path
        
        if path == '/api/sample-data':
            self.generate_sample_data()
        elif path == '/api/interactions':
            self.create_interaction()
        else:
            self.send_error(404, "Not Found")
    
    def serve_dashboard(self):
        """Serve the main dashboard"""
        
        # Get basic stats
        artists = self.db.fetch_all("SELECT * FROM artists")
        users = self.db.fetch_all("SELECT * FROM users")
        concerts = self.db.fetch_all("SELECT * FROM concerts")
        interactions = self.db.fetch_all("SELECT * FROM interactions")
        attributions = self.db.fetch_all("SELECT * FROM attributions ORDER BY total_score DESC LIMIT 10")
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>🎵 Smoosh Concert Attribution Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        .stat-label {{
            color: #666;
            font-size: 0.9em;
        }}
        .section {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        .section h2 {{
            margin-top: 0;
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        .table th, .table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .table th {{
            background-color: #f8f9fa;
            font-weight: 600;
        }}
        .score {{
            font-weight: bold;
            color: #28a745;
        }}
        .btn {{
            background: #667eea;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin: 5px;
        }}
        .btn:hover {{
            background: #5a67d8;
        }}
        .actions {{
            text-align: center;
            margin: 30px 0;
        }}
        pre {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
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
                <div class="stat-number">{len(artists)}</div>
                <div class="stat-label">Artists</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(users)}</div>
                <div class="stat-label">Users</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(concerts)}</div>
                <div class="stat-label">Concerts</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(interactions)}</div>
                <div class="stat-label">Interactions</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(attributions)}</div>
                <div class="stat-label">Attributions</div>
            </div>
        </div>
        
        <div class="actions">
            <button class="btn" onclick="generateSampleData()">Generate Sample Data</button>
            <a href="/api/stats" class="btn" target="_blank">View API Stats</a>
        </div>
        
        <div class="section">
            <h2>🎤 Artists</h2>
            <table class="table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Genre</th>
                        <th>External ID</th>
                    </tr>
                </thead>
                <tbody>
"""

        for artist in artists:
            html += f"""
                    <tr>
                        <td>{artist['id']}</td>
                        <td><strong>{artist['name']}</strong></td>
                        <td>{artist['genre'] or 'N/A'}</td>
                        <td>{artist['external_id'] or 'N/A'}</td>
                    </tr>
"""

        html += """
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>⭐ Top User-Artist Attributions</h2>
            <table class="table">
                <thead>
                    <tr>
                        <th>User ID</th>
                        <th>Artist ID</th>
                        <th>Total Score</th>
                        <th>Interactions</th>
                        <th>Total Spent</th>
                        <th>Funnel Stage</th>
                    </tr>
                </thead>
                <tbody>
"""

        for attr in attributions:
            funnel_stage = "View"
            if attr['has_purchased']:
                funnel_stage = "Purchase"
            elif attr['has_clicked']:
                funnel_stage = "Click"
            if attr['has_streamed']:
                funnel_stage += "+Stream"
            
            html += f"""
                    <tr>
                        <td>{attr['user_id']}</td>
                        <td><strong>{attr['artist_id']}</strong></td>
                        <td><span class="score">{attr['total_score']:.1f}</span></td>
                        <td>{attr['total_interactions']}</td>
                        <td>${attr['total_spent']:.2f}</td>
                        <td>{funnel_stage}</td>
                    </tr>
"""

        html += """
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>🔗 API Endpoints</h2>
            <p>Available REST API endpoints:</p>
            <ul>
                <li><code>GET /api/stats</code> - System statistics</li>
                <li><code>GET /api/artists</code> - List all artists</li>
                <li><code>GET /api/artists/{id}/conversions</code> - Artist conversion metrics</li>
                <li><code>GET /api/attributions</code> - Top attributions</li>
                <li><code>POST /api/sample-data</code> - Generate sample data</li>
            </ul>
        </div>
    </div>
    
    <script>
        async function generateSampleData() {
            try {
                const response = await fetch('/api/sample-data', { method: 'POST' });
                const result = await response.text();
                alert('Sample data generated successfully!');
                location.reload();
            } catch (error) {
                alert('Error generating sample data: ' + error.message);
            }
        }
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_stats(self):
        """Serve system statistics"""
        stats = {
            'total_artists': len(self.db.fetch_all("SELECT * FROM artists")),
            'total_users': len(self.db.fetch_all("SELECT * FROM users")),
            'total_concerts': len(self.db.fetch_all("SELECT * FROM concerts")),
            'total_interactions': len(self.db.fetch_all("SELECT * FROM interactions")),
            'total_attributions': len(self.db.fetch_all("SELECT * FROM attributions")),
            'server': 'Simple Python HTTP Server',
            'database': 'SQLite'
        }
        
        self.send_json_response(stats)
    
    def serve_artists(self):
        """Serve list of artists"""
        artists = self.db.fetch_all("SELECT * FROM artists")
        artists_list = []
        for artist in artists:
            artists_list.append({
                'id': artist['id'],
                'name': artist['name'],
                'genre': artist['genre'],
                'external_id': artist['external_id']
            })
        
        self.send_json_response(artists_list)
    
    def serve_artist_conversions(self, artist_id):
        """Serve conversion metrics for a specific artist"""
        metrics = self.pipeline.get_conversion_metrics(artist_id)
        self.send_json_response(metrics)
    
    def serve_attributions(self):
        """Serve top attributions"""
        attributions = self.db.fetch_all("SELECT * FROM attributions ORDER BY total_score DESC LIMIT 20")
        attributions_list = []
        for attr in attributions:
            attributions_list.append({
                'user_id': attr['user_id'],
                'artist_id': attr['artist_id'],
                'total_score': attr['total_score'],
                'engagement_score': attr['engagement_score'],
                'purchase_score': attr['purchase_score'],
                'total_interactions': attr['total_interactions'],
                'total_spent': attr['total_spent'],
                'has_viewed': bool(attr['has_viewed']),
                'has_clicked': bool(attr['has_clicked']),
                'has_purchased': bool(attr['has_purchased']),
                'has_streamed': bool(attr['has_streamed'])
            })
        
        self.send_json_response(attributions_list)
    
    def generate_sample_data(self):
        """Generate sample data"""
        # Create sample artists
        taylor_id = self.pipeline.create_artist("Taylor Swift", "Pop", "taylor_swift_1")
        stones_id = self.pipeline.create_artist("The Rolling Stones", "Rock", "rolling_stones_1")
        drake_id = self.pipeline.create_artist("Drake", "Hip-Hop", "drake_1")
        
        # Create sample users
        user1_id = self.pipeline.create_user("fan1@example.com", "John Doe", "25-34")
        user2_id = self.pipeline.create_user("fan2@example.com", "Jane Smith", "18-24")
        user3_id = self.pipeline.create_user("fan3@example.com", "Bob Wilson", "35-44")
        
        # Create sample concerts
        concert1_id = self.pipeline.create_concert(taylor_id, "Eras Tour", "Madison Square Garden", "New York", 75.0, 400.0)
        concert2_id = self.pipeline.create_concert(stones_id, "World Tour 2024", "Wembley Stadium", "London", 50.0, 250.0)
        
        # Create sample interactions
        self.pipeline.create_interaction(user1_id, taylor_id, "view", "website")
        self.pipeline.create_interaction(user1_id, taylor_id, "click", "website")
        self.pipeline.create_interaction(user1_id, taylor_id, "ticket_purchase", "website", 150.0, concert1_id)
        self.pipeline.create_interaction(user1_id, taylor_id, "stream", "spotify", 45.0)
        
        self.pipeline.create_interaction(user2_id, stones_id, "view", "website")
        self.pipeline.create_interaction(user2_id, stones_id, "stream", "spotify", 30.0)
        
        self.pipeline.create_interaction(user3_id, taylor_id, "view", "website")
        self.pipeline.create_interaction(user3_id, drake_id, "view", "website")
        self.pipeline.create_interaction(user3_id, drake_id, "click", "website")
        self.pipeline.create_interaction(user3_id, drake_id, "merch_purchase", "website", 25.0)
        
        # Calculate attributions
        user_artist_pairs = [
            (user1_id, taylor_id),
            (user2_id, stones_id),
            (user3_id, taylor_id),
            (user3_id, drake_id)
        ]
        
        for user_id, artist_id in user_artist_pairs:
            self.pipeline.calculate_attribution(user_id, artist_id)
        
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Sample data generated successfully!')
    
    def send_json_response(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        json_str = json.dumps(data, indent=2)
        self.wfile.write(json_str.encode())

def run_server(port=8000):
    """Run the server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, APIHandler)
    
    print(f"🎵 Smoosh Concert Attribution Pipeline Server")
    print(f"Dashboard: http://localhost:{port}")
    print(f"API: http://localhost:{port}/api/stats")
    print(f"Press Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\\nServer stopped.")
        httpd.server_close()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    run_server(port)