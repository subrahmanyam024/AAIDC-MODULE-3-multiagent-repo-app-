from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
import sys
import json
from datetime import datetime

generation_bp = Blueprint('generation', __name__)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from agents.article_generator import ArticleGeneratorAgent
from utils.validators import sanitize_input

PROJECTS_FILE = 'backend/data/projects.json'
ARTICLES_FILE = 'backend/data/articles.json'

def load_projects():
    """Load projects"""
    if not os.path.exists(PROJECTS_FILE):
        return {}
    try:
        with open(PROJECTS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def load_articles():
    """Load generated articles"""
    if not os.path.exists(ARTICLES_FILE):
        return {}
    try:
        with open(ARTICLES_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_articles(articles):
    """Save articles"""
    os.makedirs(os.path.dirname(ARTICLES_FILE), exist_ok=True)
    with open(ARTICLES_FILE, 'w') as f:
        json.dump(articles, f, indent=2)

@generation_bp.route('/outline', methods=['POST'])
@jwt_required()
def generate_outline():
    """Generate article outline"""
    try:
        username = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        project_id = data.get('project_id', '').strip()
        instructions = sanitize_input(data.get('instructions', ''))
        
        if not project_id or not instructions:
            return jsonify({'error': 'Project ID and instructions required'}), 400
        
        projects = load_projects()
        user_projects = projects.get(username, [])
        project = next((p for p in user_projects if p['id'] == project_id), None)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        if not project.get('repo_data'):
            return jsonify({'error': 'Repository not analyzed yet'}), 400
        
        # Prepare context
        repo_data = project['repo_data']
        repo_context = f"""
Repository: {repo_data.get('url', 'Unknown')}
Project Type: {repo_data['analysis'].get('project_type', 'Unknown')}
Total Files: {repo_data['analysis'].get('total_files', 0)}
Languages: {', '.join(repo_data['analysis'].get('languages', {}).keys())}
Dependencies: {repo_data['analysis'].get('dependencies', {})}
"""
        
        # Generate outline
        agent = ArticleGeneratorAgent()
        outline = agent.generate_outline(repo_context, instructions)
        
        return jsonify({
            'message': 'Outline generated successfully',
            'outline': outline,
            'project_id': project_id
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@generation_bp.route('/article', methods=['POST'])
@jwt_required()
def generate_article():
    """Generate full article"""
    try:
        username = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        project_id = data.get('project_id', '').strip()
        instructions = sanitize_input(data.get('instructions', ''))
        description = sanitize_input(data.get('description', ''))
        
        if not project_id or not instructions:
            return jsonify({'error': 'Project ID and instructions required'}), 400
        
        projects = load_projects()
        user_projects = projects.get(username, [])
        project = next((p for p in user_projects if p['id'] == project_id), None)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        if not project.get('repo_data'):
            return jsonify({'error': 'Repository not analyzed yet'}), 400
        
        # Prepare context
        repo_data = project['repo_data']
        repo_context = f"""
Repository: {repo_data.get('url', 'Unknown')}
Project Type: {repo_data['analysis'].get('project_type', 'Unknown')}
Total Files: {repo_data['analysis'].get('total_files', 0)}
Languages: {', '.join(repo_data['analysis'].get('languages', {}).keys())}
Dependencies: {repo_data['analysis'].get('dependencies', {})}
"""
        
        # Generate article
        agent = ArticleGeneratorAgent()
        article = agent.generate(repo_context, instructions, description)
        
        # Save article
        articles = load_articles()
        if username not in articles:
            articles[username] = []
        
        article_id = f"art_{len(articles[username])}_{int(datetime.now().timestamp())}"
        
        article_obj = {
            'id': article_id,
            'project_id': project_id,
            'content': article,
            'instructions': instructions,
            'description': description,
            'created_at': datetime.now().isoformat()
        }
        
        articles[username].append(article_obj)
        save_articles(articles)
        
        return jsonify({
            'message': 'Article generated successfully',
            'article_id': article_id,
            'article': article,
            'project_id': project_id
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@generation_bp.route('/articles/user/all', methods=['GET'])
@jwt_required()
def get_all_user_articles():
    """Get all articles for current user"""
    try:
        username = get_jwt_identity()
        articles = load_articles()
        
        user_articles = articles.get(username, [])
        
        return jsonify({
            'articles': user_articles,
            'total': len(user_articles)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@generation_bp.route('/articles/<project_id>', methods=['GET'])
@jwt_required()
def get_project_articles(project_id):
    """Get all articles for a project"""
    try:
        username = get_jwt_identity()
        articles = load_articles()
        
        user_articles = articles.get(username, [])
        project_articles = [a for a in user_articles if a['project_id'] == project_id]
        
        return jsonify({
            'project_id': project_id,
            'articles': project_articles,
            'total': len(project_articles)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@generation_bp.route('/article/<article_id>', methods=['GET'])
@jwt_required()
def get_article(article_id):
    """Get single article"""
    try:
        username = get_jwt_identity()
        articles = load_articles()
        
        user_articles = articles.get(username, [])
        article = next((a for a in user_articles if a['id'] == article_id), None)
        
        if not article:
            return jsonify({'error': 'Article not found'}), 404
        
        return jsonify(article), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@generation_bp.route('/article/<article_id>/download', methods=['GET'])
@jwt_required()
def download_article(article_id):
    """Download article as markdown or JSON"""
    try:
        username = get_jwt_identity()
        articles = load_articles()
        
        user_articles = articles.get(username, [])
        article = next((a for a in user_articles if a['id'] == article_id), None)
        
        if not article:
            return jsonify({'error': 'Article not found'}), 404
        
        format_type = request.args.get('format', 'markdown')  # markdown or json
        
        if format_type == 'json':
            return jsonify(article), 200
        else:
            # Return as markdown file
            return {
                'content': article['content'],
                'filename': f"article_{article_id}.md"
            }, 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@generation_bp.route('/article/<article_id>', methods=['DELETE'])
@jwt_required()
def delete_article(article_id):
    """Delete article"""
    try:
        username = get_jwt_identity()
        articles = load_articles()
        
        user_articles = articles.get(username, [])
        initial_count = len(user_articles)
        
        articles[username] = [a for a in user_articles if a['id'] != article_id]
        
        if len(articles[username]) == initial_count:
            return jsonify({'error': 'Article not found'}), 404
        
        save_articles(articles)
        
        return jsonify({'message': 'Article deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
