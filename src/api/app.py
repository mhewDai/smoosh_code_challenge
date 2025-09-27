from flask import Flask
from flask_cors import CORS
from ..models import init_db

def create_app(config=None):
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smoosh_pipeline.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev-secret-key'  # Change in production
    
    if config:
        app.config.update(config)
    
    # Enable CORS
    CORS(app)
    
    # Initialize database
    init_db(app)
    
    # Register blueprints
    from .routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Register dashboard routes
    from .dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)
    
    return app