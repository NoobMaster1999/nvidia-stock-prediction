
import os
import sys
import logging
from datetime import datetime
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify, request, abort
from flask_cors import CORS
from werkzeug.exceptions import RequestEntityTooLarge
from src.models.user import db
from src.routes.user import user_bp
from src.routes.prediction import prediction_bp

# Configure secure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Security configurations
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default_secret_key_change_in_production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enable CORS with security settings
CORS(app, 
     origins=["*"],  # In production, specify exact origins
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE"])

# Security headers middleware
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    return response

# Request validation middleware
@app.before_request
def validate_request():
    # Log all requests for monitoring
    logger.info(f"Request: {request.method} {request.path} from {request.remote_addr}")
    
    # Block requests with suspicious user agents
    user_agent = request.headers.get('User-Agent', '').lower()
    suspicious_agents = ['sqlmap', 'nikto', 'nmap', 'masscan', 'nessus']
    if any(agent in user_agent for agent in suspicious_agents):
        logger.warning(f"Blocked suspicious user agent: {user_agent}")
        abort(403)
    
    # Rate limiting basic check (in production use proper rate limiting)
    if request.endpoint and request.method == 'POST':
        content_type = request.headers.get('Content-Type', '')
        if content_type and 'application/json' in content_type:
            try:
                if request.content_length and request.content_length > app.config['MAX_CONTENT_LENGTH']:
                    abort(413)
            except Exception as e:
                logger.error(f"Request validation error: {str(e)}")
                abort(400)

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
    logger.error(f"Database initialization failed: {str(e)}")

# Error handlers
@app.errorhandler(400)
def bad_request(error):
    logger.warning(f"Bad request: {error}")
    return jsonify({"error": "Bad request", "message": "Invalid request format"}), 400

@app.errorhandler(403)
def forbidden(error):
    logger.warning(f"Forbidden access attempt: {error}")
    return jsonify({"error": "Forbidden", "message": "Access denied"}), 403

@app.errorhandler(404)
def not_found(error):
    logger.info(f"Resource not found: {request.path}")
    return jsonify({"error": "Not found", "message": "Resource not found"}), 404

@app.errorhandler(413)
def request_too_large(error):
    logger.warning(f"Request too large from {request.remote_addr}")
    return jsonify({"error": "Request too large", "message": "File size exceeds limit"}), 413

@app.errorhandler(429)
def rate_limit_exceeded(error):
    logger.warning(f"Rate limit exceeded from {request.remote_addr}")
    return jsonify({"error": "Rate limit exceeded", "message": "Too many requests"}), 429

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({"error": "Internal server error", "message": "Something went wrong"}), 500

# Secure file serving with path validation
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    try:
        static_folder_path = app.static_folder
        if static_folder_path is None:
            logger.error("Static folder not configured")
            return jsonify({"error": "Static folder not configured"}), 404

        # Prevent directory traversal attacks
        if '..' in path or path.startswith('/') or '\\' in path:
            logger.warning(f"Directory traversal attempt blocked: {path}")
            return jsonify({"error": "Invalid path"}), 403
        
        # Sanitize path
        path = path.strip().lstrip('/')
        
        if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
            # Additional security check - ensure file is within static folder
            full_path = os.path.abspath(os.path.join(static_folder_path, path))
            static_abs_path = os.path.abspath(static_folder_path)
            
            if not full_path.startswith(static_abs_path):
                logger.warning(f"Path traversal attempt blocked: {path}")
                return jsonify({"error": "Invalid path"}), 403
                
            return send_from_directory(static_folder_path, path)
        else:
            index_path = os.path.join(static_folder_path, 'index.html')
            if os.path.exists(index_path):
                return send_from_directory(static_folder_path, 'index.html')
            else:
                logger.error("index.html not found")
                return jsonify({"error": "index.html not found"}), 404
                
    except Exception as e:
        logger.error(f"File serving error: {str(e)}")
        return jsonify({"error": "File serving error"}), 500

# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

if __name__ == '__main__':
    # Production-ready configuration
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    if debug_mode:
        logger.warning("Running in DEBUG mode - not recommended for production!")
    
    logger.info("Starting Flask application...")
    app.run(host='0.0.0.0', port=8080, debug=debug_mode, threaded=True)
