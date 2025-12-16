from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
import os
from datetime import datetime
import logging
import re
import uuid

projects_bp = Blueprint('projects', __name__)
logger = logging.getLogger(__name__)

PROJECTS_FILE = 'backend/data/projects.json'

def load_projects():
    """Load all projects"""
    if not os.path.exists(PROJECTS_FILE):
        os.makedirs(os.path.dirname(PROJECTS_FILE), exist_ok=True)
        return {}
    try:
        with open(PROJECTS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading projects: {e}")
        return {}

def save_projects(projects):
    """Save projects"""
    try:
        os.makedirs(os.path.dirname(PROJECTS_FILE), exist_ok=True)
        with open(PROJECTS_FILE, 'w') as f:
            json.dump(projects, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving projects: {e}")
        raise

def validate_github_url(url):
    """Validate GitHub URL format"""
    github_pattern = r'^https://github\.com/[\w\-]+/[\w\-\.]+/?$'
    if not re.match(github_pattern, url):
        return False, "Invalid GitHub URL format (expected: https://github.com/user/repo)"
    if len(url) > 255:
        return False, "GitHub URL cannot exceed 255 characters"
    return True, None

def validate_project_name(name):
    """Validate project name"""
    if not name or len(name) < 1:
        return False, "Project name is required"
    if len(name) > 100:
        return False, "Project name cannot exceed 100 characters"
    return True, None

@projects_bp.route('', methods=['GET'])
@jwt_required()
def get_projects():
    """Get all projects for current user"""
    try:
        username = get_jwt_identity()
        projects = load_projects()
        
        user_projects = projects.get(username, [])
        
        logger.debug(f"Retrieved {len(user_projects)} projects for user: {username}")
        
        return jsonify({
            'projects': user_projects,
            'total': len(user_projects)
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving projects: {e}", exc_info=True)
        return jsonify({'error': 'Failed to retrieve projects'}), 500

@projects_bp.route('/<project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    """Get single project"""
    try:
        username = get_jwt_identity()
        projects = load_projects()
        
        user_projects = projects.get(username, [])
        project = next((p for p in user_projects if p['id'] == project_id), None)
        
        if not project:
            logger.warning(f"Project not found: {project_id} for user: {username}")
            return jsonify({'error': 'Project not found'}), 404
        
        logger.debug(f"Retrieved project: {project_id} for user: {username}")
        
        return jsonify(project), 200
        
    except Exception as e:
        logger.error(f"Error retrieving project {project_id}: {e}", exc_info=True)
        return jsonify({'error': 'Failed to retrieve project'}), 500

@projects_bp.route('', methods=['POST'])
@jwt_required()
def create_project():
    """Create new project"""
    try:
        username = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            logger.warning("Project creation attempt with no data")
            return jsonify({'error': 'No data provided'}), 400
        
        project_name = data.get('name', '').strip()
        github_url = data.get('github_url', '').strip()
        description = data.get('description', '').strip()
        
        # Validate project name
        is_valid, error_msg = validate_project_name(project_name)
        if not is_valid:
            logger.warning(f"Invalid project name: {error_msg}")
            return jsonify({'error': error_msg}), 400
        
        # Validate GitHub URL
        is_valid, error_msg = validate_github_url(github_url)
        if not is_valid:
            logger.warning(f"Invalid GitHub URL: {error_msg}")
            return jsonify({'error': error_msg}), 400
        
        projects = load_projects()
        
        if username not in projects:
            projects[username] = []
        
        # Create project with unique ID
        project = {
            'id': str(uuid.uuid4()),
            'name': project_name,
            'github_url': github_url,
            'description': description,
            'created_at': datetime.now().isoformat(),
            'status': 'pending',
            'repo_data': None,
            'analysis': None
        }
        
        projects[username].append(project)
        save_projects(projects)
        
        logger.info(f"Project created successfully: {project['id']} by {username}")
        
        return jsonify({
            'message': 'Project created successfully',
            'id': project['id'],
            'name': project['name'],
            'status': project['status']
        }), 201
        
    except Exception as e:
        logger.error(f"Project creation error: {e}", exc_info=True)
        return jsonify({'error': 'Failed to create project'}), 500

@projects_bp.route('/<project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    """Update project"""
    try:
        username = get_jwt_identity()
        data = request.get_json()
        
        projects = load_projects()
        user_projects = projects.get(username, [])
        
        project = next((p for p in user_projects if p['id'] == project_id), None)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Update allowed fields
        if 'name' in data:
            project['name'] = data['name'].strip()
        if 'description' in data:
            project['description'] = data['description'].strip()
        if 'status' in data:
            project['status'] = data['status']
        if 'analysis' in data:
            project['analysis'] = data['analysis']
        
        project['updated_at'] = datetime.now().isoformat()
        
        save_projects(projects)
        
        return jsonify({
            'message': 'Project updated successfully',
            'project': project
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/<project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    """Delete project"""
    try:
        username = get_jwt_identity()
        projects = load_projects()
        
        user_projects = projects.get(username, [])
        
        initial_count = len(user_projects)
        projects[username] = [p for p in user_projects if p['id'] != project_id]
        
        if len(projects[username]) == initial_count:
            return jsonify({'error': 'Project not found'}), 404
        
        save_projects(projects)
        
        return jsonify({'message': 'Project deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/<project_id>/status', methods=['GET'])
@jwt_required()
def get_project_status(project_id):
    """Get project analysis status"""
    try:
        username = get_jwt_identity()
        projects = load_projects()
        
        user_projects = projects.get(username, [])
        project = next((p for p in user_projects if p['id'] == project_id), None)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        return jsonify({
            'project_id': project_id,
            'status': project.get('status', 'pending'),
            'analysis': project.get('analysis'),
            'created_at': project.get('created_at')
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
