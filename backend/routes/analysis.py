from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
import sys
import json
from datetime import datetime

analysis_bp = Blueprint('analysis', __name__)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from agents.repo_analyzer import analyze_repo
from tools.repo_downloader import RepoDownloader
from utils.validators import validate_github_url

PROJECTS_FILE = 'backend/data/projects.json'

def load_projects():
    """Load projects"""
    if not os.path.exists(PROJECTS_FILE):
        return {}
    try:
        with open(PROJECTS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_projects(projects):
    """Save projects"""
    os.makedirs(os.path.dirname(PROJECTS_FILE), exist_ok=True)
    with open(PROJECTS_FILE, 'w') as f:
        json.dump(projects, f, indent=2)

@analysis_bp.route('/download-repo', methods=['POST'])
@jwt_required()
def download_repo():
    """Download and analyze GitHub repository"""
    try:
        username = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        github_url = data.get('github_url', '').strip()
        project_id = data.get('project_id', '').strip()
        
        # Validate URL
        if not validate_github_url(github_url):
            return jsonify({'error': 'Invalid GitHub URL'}), 400
        
        # Download repository
        downloader = RepoDownloader()
        repo_path = downloader.clone_repo(github_url)
        
        if not repo_path:
            return jsonify({'error': 'Failed to download repository'}), 500
        
        # Analyze repository
        analysis = analyze_repo(repo_path)
        
        # Store in project
        projects = load_projects()
        user_projects = projects.get(username, [])
        
        project = next((p for p in user_projects if p['id'] == project_id), None)
        if project:
            project['repo_data'] = {
                'path': repo_path,
                'url': github_url,
                'analysis': {
                    'total_files': analysis.get('total_files'),
                    'repo_size': analysis.get('repo_size'),
                    'project_type': analysis.get('project_type'),
                    'languages': analysis.get('langs'),
                    'dependencies': analysis.get('dependencies'),
                    'structure': analysis.get('structure'),
                    'missing_sections': analysis.get('missing'),
                    'best_practices': analysis.get('best_practices')
                }
            }
            project['status'] = 'analyzed'
            project['analyzed_at'] = datetime.now().isoformat()
            save_projects(projects)
        
        return jsonify({
            'message': 'Repository analyzed successfully',
            'analysis': analysis.get('analysis', {}),
            'repo_path': repo_path,
            'total_files': analysis.get('total_files'),
            'project_type': analysis.get('project_type'),
            'languages': list(analysis.get('langs', {}).keys())
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/analyze-repo/<project_id>', methods=['GET'])
@jwt_required()
def get_repo_analysis(project_id):
    """Get repository analysis for a project"""
    try:
        username = get_jwt_identity()
        projects = load_projects()
        
        user_projects = projects.get(username, [])
        project = next((p for p in user_projects if p['id'] == project_id), None)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        if not project.get('repo_data'):
            return jsonify({'error': 'Repository not analyzed yet'}), 400
        
        analysis = project['repo_data'].get('analysis', {})
        
        return jsonify({
            'project_id': project_id,
            'url': project['repo_data'].get('url'),
            'analysis': analysis,
            'analyzed_at': project.get('analyzed_at')
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/structure/<project_id>', methods=['GET'])
@jwt_required()
def get_repo_structure(project_id):
    """Get repository structure and files"""
    try:
        username = get_jwt_identity()
        projects = load_projects()
        
        user_projects = projects.get(username, [])
        project = next((p for p in user_projects if p['id'] == project_id), None)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        if not project.get('repo_data'):
            return jsonify({'error': 'Repository not analyzed yet'}), 400
        
        repo_path = project['repo_data'].get('path')
        
        # Get file structure
        structure = {
            'total_files': project['repo_data']['analysis'].get('total_files', 0),
            'languages': project['repo_data']['analysis'].get('languages', {}),
            'directory_tree': project['repo_data']['analysis'].get('structure', {})
        }
        
        return jsonify(structure), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/dependencies/<project_id>', methods=['GET'])
@jwt_required()
def get_dependencies(project_id):
    """Get project dependencies"""
    try:
        username = get_jwt_identity()
        projects = load_projects()
        
        user_projects = projects.get(username, [])
        project = next((p for p in user_projects if p['id'] == project_id), None)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        if not project.get('repo_data'):
            return jsonify({'error': 'Repository not analyzed yet'}), 400
        
        dependencies = project['repo_data']['analysis'].get('dependencies', {})
        
        return jsonify({
            'project_id': project_id,
            'dependencies': dependencies
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
