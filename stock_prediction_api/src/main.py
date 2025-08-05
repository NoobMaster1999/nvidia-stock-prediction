
import os
import sys
import logging
import time
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.prediction import prediction_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Use environment variable for secret key with secure fallback
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'your-super-secret-key-change-this-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Security headers
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

# Enable CORS with specific configuration
CORS(app, origins=['http://localhost:5000', 'https://*.replit.dev', 'https://*.replit.com'])

# Input validation middleware
@app.before_request
def validate_json():
    if request.method in ['POST', 'PUT', 'PATCH'] and request.is_json:
        try:
            request.get_json()
        except Exception as e:
            logger.warning(f"Invalid JSON in request: {e}")
            return jsonify({"error": "Invalid JSON format"}), 400

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(prediction_bp, url_prefix='/api')

# Initialize the database with error handling
try:
    db.init_app(app)
    with app.app_context():
        db.create_all()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Database initialization failed: {e}")
    raise

# Error handlers
@app.errorhandler(400)
def bad_request(error):
    logger.warning(f"Bad request: {error}")
    return jsonify({"error": "Bad request"}), 400

@app.errorhandler(404)
def not_found(error):
    logger.info(f"Resource not found: {request.url}")
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {e}")
    return jsonify({"error": "An unexpected error occurred"}), 500

# Rate limiting helper (basic implementation)
request_counts = {}

@app.before_request
def limit_requests():
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    current_time = int(time.time())
    
    if client_ip not in request_counts:
        request_counts[client_ip] = []
    
    # Remove requests older than 1 minute
    request_counts[client_ip] = [req_time for req_time in request_counts[client_ip] if current_time - req_time < 60]
    
    # Allow max 100 requests per minute per IP
    if len(request_counts[client_ip]) >= 100:
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        return jsonify({"error": "Rate limit exceeded"}), 429
    
    request_counts[client_ip].append(current_time)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    try:
        static_folder_path = app.static_folder
        if static_folder_path is None:
            logger.error("Static folder not configured")
            return jsonify({"error": "Static folder not configured"}), 404

        # Prevent directory traversal attacks
        if '..' in path or path.startswith('/'):
            logger.warning(f"Potential directory traversal attempt: {path}")
            return jsonify({"error": "Invalid path"}), 400

        if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
            return send_from_directory(static_folder_path, path)
        else:
            index_path = os.path.join(static_folder_path, 'index.html')
            if os.path.exists(index_path):
                return send_from_directory(static_folder_path, 'index.html')
            else:
                logger.warning("index.html not found")
                return jsonify({"error": "index.html not found"}), 404
    except Exception as e:
        logger.error(f"Error serving static file: {e}")
        return jsonify({"error": "Error serving file"}), 500

if __name__ == '__main__':
    # Get configuration from environment variables
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 8080))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    logger.info(f"Starting Flask app on {host}:{port} (debug={debug})")
    app.run(host=host, port=port, debug=debug)
