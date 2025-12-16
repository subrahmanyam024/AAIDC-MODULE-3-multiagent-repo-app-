from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, InvalidTokenError
from datetime import timedelta
import os
from dotenv import load_dotenv
import logging
from werkzeug.exceptions import RequestEntityTooLarge

load_dotenv()

app = Flask(__name__)

# Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max request size
app.config['JSON_SORT_KEYS'] = False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize extensions
CORS(app, resources={r"/api/*": {"origins": "*"}})
jwt = JWTManager(app)

# Import routes
from routes.auth import auth_bp
from routes.projects import projects_bp
from routes.analysis import analysis_bp
from routes.generation import generation_bp

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(projects_bp, url_prefix='/api/projects')
app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
app.register_blueprint(generation_bp, url_prefix='/api/generation')

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Multi-Agent Repository Assistant API',
        'version': '1.0.0'
    }), 200

# Comprehensive Error Handlers
@app.errorhandler(400)
def bad_request(error):
    """Handle bad request errors"""
    logger.warning(f"Bad request: {error}")
    return jsonify({
        'error': 'Bad request',
        'message': 'The request was invalid or malformed'
    }), 400

@app.errorhandler(401)
def unauthorized(error):
    """Handle unauthorized access"""
    logger.warning(f"Unauthorized access attempt")
    return jsonify({
        'error': 'Unauthorized',
        'message': 'Authentication is required'
    }), 401

@app.errorhandler(403)
def forbidden(error):
    """Handle forbidden access"""
    logger.warning(f"Forbidden access attempt")
    return jsonify({
        'error': 'Forbidden',
        'message': 'You do not have permission to access this resource'
    }), 403

@app.errorhandler(404)
def not_found(error):
    """Handle not found errors"""
    logger.info(f"Resource not found: {request.path}")
    return jsonify({
        'error': 'Not found',
        'message': f'The requested resource was not found'
    }), 404

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle request too large"""
    logger.warning(f"Request entity too large from {request.remote_addr}")
    return jsonify({
        'error': 'Request too large',
        'message': 'The request payload exceeds the maximum allowed size (50MB)'
    }), 413

@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors"""
    logger.error(f"Internal server error: {error}", exc_info=True)
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred. Please try again later'
    }), 500

@app.errorhandler(Exception)
def handle_generic_exception(error):
    """Handle all other exceptions"""
    logger.error(f"Unhandled exception: {type(error).__name__}: {error}", exc_info=True)
    return jsonify({
        'error': 'Server error',
        'message': 'An unexpected error occurred'
    }), 500

# JWT error handlers
@app.errorhandler(InvalidTokenError)
def handle_invalid_token(error):
    """Handle invalid JWT tokens"""
    logger.warning(f"Invalid token: {error}")
    return jsonify({
        'error': 'Invalid token',
        'message': 'The provided authentication token is invalid or expired'
    }), 401

@app.before_request
def log_request():
    """Log incoming requests"""
    if request.method != 'OPTIONS':
        logger.info(f"[{request.method}] {request.path} from {request.remote_addr}")

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('FLASK_PORT', 5000)),
        debug=os.getenv('FLASK_ENV', 'production') == 'development'
    )
