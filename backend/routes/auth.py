from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import os
from functools import wraps
import json
import logging
import re

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

USERS_FILE = 'backend/data/users.json'

def load_users():
    """Load users from JSON file"""
    if not os.path.exists(USERS_FILE):
        os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
        return {}
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading users: {e}")
        return {}

def save_users(users):
    """Save users to JSON file"""
    try:
        os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving users: {e}")
        raise

def hash_password(password):
    """Hash password using SHA256 (use bcrypt in production)"""
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

def validate_username(username):
    """Validate username format and length"""
    if not username or len(username) < 3:
        return False, "Username must be at least 3 characters"
    if len(username) > 50:
        return False, "Username cannot exceed 50 characters"
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens"
    return True, None

def validate_email(email):
    """Validate email format"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not email or not re.match(email_pattern, email):
        return False, "Invalid email format"
    if len(email) > 100:
        return False, "Email cannot exceed 100 characters"
    return True, None

def validate_password(password):
    """Validate password strength"""
    if not password:
        return False, "Password is required"
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    if len(password) > 128:
        return False, "Password cannot exceed 128 characters"
    return True, None

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register new user"""
    try:
        data = request.get_json()
        
        if not data:
            logger.warning("Registration attempt with no data")
            return jsonify({'error': 'No data provided'}), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        email = data.get('email', '').strip()
        
        # Validate username
        is_valid, error_msg = validate_username(username)
        if not is_valid:
            logger.warning(f"Invalid username: {error_msg}")
            return jsonify({'error': error_msg}), 400
        
        # Validate password
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            logger.warning(f"Invalid password: {error_msg}")
            return jsonify({'error': error_msg}), 400
        
        # Validate email
        is_valid, error_msg = validate_email(email)
        if not is_valid:
            logger.warning(f"Invalid email: {error_msg}")
            return jsonify({'error': error_msg}), 400
        
        users = load_users()
        
        # Check if user exists
        if username in users:
            logger.warning(f"Registration attempt with existing username: {username}")
            return jsonify({'error': 'Username already exists'}), 409
        
        # Check if email already registered
        for user in users.values():
            if user.get('email') == email:
                logger.warning(f"Registration attempt with existing email: {email}")
                return jsonify({'error': 'Email already registered'}), 409
        
        # Create new user
        users[username] = {
            'email': email,
            'password': hash_password(password),
            'projects': [],
            'created_at': __import__('datetime').datetime.utcnow().isoformat()
        }
        
        save_users(users)
        logger.info(f"User registered successfully: {username}")
        
        return jsonify({
            'message': 'User registered successfully',
            'username': username
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {e}", exc_info=True)
        return jsonify({'error': 'Registration failed. Please try again'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT token"""
    try:
        data = request.get_json()
        
        if not data:
            logger.warning("Login attempt with no data")
            return jsonify({'error': 'No data provided'}), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            logger.warning("Login attempt without credentials")
            return jsonify({'error': 'Username and password required'}), 400
        
        users = load_users()
        
        # Check credentials (generic error message for security)
        if username not in users or users[username]['password'] != hash_password(password):
            logger.warning(f"Failed login attempt for username: {username}")
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create JWT token
        try:
            access_token = create_access_token(identity=username)
            user = users[username]
            
            logger.info(f"User logged in successfully: {username}")
            
            return jsonify({
                'message': 'Login successful',
                'access_token': access_token,
                'username': username,
                'email': user['email']
            }), 200
        except Exception as token_error:
            logger.error(f"Token creation error: {token_error}", exc_info=True)
            return jsonify({'error': 'Authentication failed'}), 500
        
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        return jsonify({'error': 'Login failed. Please try again'}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user info"""
    try:
        username = get_jwt_identity()
        users = load_users()
        
        if username not in users:
            logger.warning(f"User not found in token validation: {username}")
            return jsonify({'error': 'User not found'}), 404
        
        user = users[username]
        
        logger.debug(f"Retrieved user info for: {username}")
        
        return jsonify({
            'username': username,
            'email': user['email'],
            'projects': len(user.get('projects', [])),
            'created_at': user.get('created_at')
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving user info: {e}", exc_info=True)
        return jsonify({'error': 'Failed to retrieve user info'}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (just return success - JWT is stateless)"""
    try:
        username = get_jwt_identity()
        logger.info(f"User logged out: {username}")
        return jsonify({'message': 'Logout successful'}), 200
    except Exception as e:
        logger.error(f"Logout error: {e}", exc_info=True)
        return jsonify({'error': 'Logout failed'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        username = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            logger.warning("Password change attempt with no data")
            return jsonify({'error': 'No data provided'}), 400
        
        old_password = data.get('old_password', '').strip()
        new_password = data.get('new_password', '').strip()
        
        if not old_password or not new_password:
            logger.warning(f"Password change attempt without all passwords: {username}")
            return jsonify({'error': 'Both current and new passwords required'}), 400
        
        # Validate new password
        is_valid, error_msg = validate_password(new_password)
        if not is_valid:
            logger.warning(f"Invalid new password during change: {error_msg}")
            return jsonify({'error': error_msg}), 400
        
        # Check that new password is different from old
        if old_password == new_password:
            return jsonify({'error': 'New password must be different from current password'}), 400
        
        users = load_users()
        if username not in users:
            logger.warning(f"User not found during password change: {username}")
            return jsonify({'error': 'User not found'}), 404
        
        user = users[username]
        
        # Verify old password
        if user['password'] != hash_password(old_password):
            logger.warning(f"Failed password verification for user: {username}")
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Update password
        user['password'] = hash_password(new_password)
        save_users(users)
        
        logger.info(f"Password changed successfully for user: {username}")
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        logger.error(f"Password change error: {e}", exc_info=True)
        return jsonify({'error': 'Password change failed. Please try again'}), 500
