#!/usr/bin/env python3
"""
Smoosh Concert Attribution Pipeline
Main application entry point
"""

import os
from src.api import create_app

if __name__ == '__main__':
    app = create_app()
    
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    print("🎵 Starting Smoosh Concert Attribution Pipeline...")
    print(f"Dashboard: http://localhost:{port}")
    print(f"API: http://localhost:{port}/api")
    
    app.run(host='0.0.0.0', port=port, debug=debug)