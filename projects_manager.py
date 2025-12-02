import json
import os
from pathlib import Path
from datetime import datetime

PROJECTS_FILE = "projects_data.json"


def load_projects():
    """Load all saved projects"""
    if os.path.exists(PROJECTS_FILE):
        try:
            with open(PROJECTS_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_projects(projects):
    """Save projects to file"""
    with open(PROJECTS_FILE, "w") as f:
        json.dump(projects, f, indent=2)


def create_project(project_name, repo_url, repo_path, uploaded_files_count=0):
    """Create a new project entry"""
    projects = load_projects()
    
    project_id = project_name.lower().replace(" ", "_")
    
    projects[project_id] = {
        "id": project_id,
        "name": project_name,
        "repo_url": repo_url,
        "repo_path": repo_path,
        "uploaded_files": uploaded_files_count,
        "repository_files": 0,
        "analyzed": False,
        "created_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat()
    }
    
    save_projects(projects)
    return project_id


def update_project(project_id, repo_data, uploaded_files_count=0):
    """Update project with analysis data"""
    projects = load_projects()
    
    if project_id in projects:
        projects[project_id]["uploaded_files"] = uploaded_files_count
        projects[project_id]["repository_files"] = repo_data.get("structure", {}).get("total_files", 0)
        projects[project_id]["analyzed"] = True
        projects[project_id]["last_updated"] = datetime.now().isoformat()
        projects[project_id]["repo_data"] = repo_data
        
        save_projects(projects)
    
    return projects[project_id]


def get_project(project_id):
    """Get a specific project"""
    projects = load_projects()
    return projects.get(project_id)


def get_all_projects():
    """Get all projects"""
    return load_projects()


def delete_project(project_id):
    """Delete a project"""
    projects = load_projects()
    
    if project_id in projects:
        del projects[project_id]
        save_projects(projects)
        return True
    
    return False


def get_project_names_list():
    """Get list of project names for dropdown"""
    projects = load_projects()
    return {project["name"]: project_id for project_id, project in projects.items()}
