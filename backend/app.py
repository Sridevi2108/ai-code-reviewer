from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from routes.review_routes import review_bp
from models import init_db
import os

# Create Flask app
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Configure rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour"],
    storage_uri="memory://"
)

# Apply rate limit to review endpoint
@limiter.limit("10 per minute")
@app.before_request
def rate_limit_review():
    """Rate limit the review endpoint specifically"""
    from flask import request
    if request.path == '/api/review' and request.method == 'POST':
        pass  # Rate limit will be applied by decorator

# Register blueprints
app.register_blueprint(review_bp)

# Serve frontend
@app.route('/')
def serve_frontend():
    """Serve the frontend HTML"""
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('../frontend', path)

# Error handlers
@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return {'error': 'Endpoint not found'}, 404

@app.errorhandler(429)
def rate_limit_exceeded(e):
    """Handle rate limit errors"""
    return {'error': 'Rate limit exceeded. Please try again later.'}, 429

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors"""
    return {'error': 'Internal server error'}, 500

# Initialize database
with app.app_context():
    init_db()
    print("Database initialized successfully")

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print(f"Starting Code Review API on port {port}")
    print(f"Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)