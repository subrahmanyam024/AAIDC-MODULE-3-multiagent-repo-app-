import os
import tempfile
import shutil
import stat
from pathlib import Path
from git import Repo


class RepoDownloader:
    """Downloads and manages GitHub repositories."""
    
    EXCLUDE_DIRS = {
        'venv', 'env', '.venv', 'node_modules', '.git', '__pycache__',
        '.pytest_cache', 'build', 'dist', '.egg-info', '.tox', '.next',
        'out', '.svelte-kit', '.DS_Store', '.idea', '.vscode',
        'target', '.gradle', '__pycache__'
    }
    
    MAX_FILE_SIZE = 500 * 1024  # 500KB
    
    def __init__(self, cache_dir: str = None):
        """Initialize downloader with optional cache directory."""
        if cache_dir is None:
            cache_dir = os.path.join(tempfile.gettempdir(), "repo_cache")
        
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def _handle_remove_readonly(self, func, path, exc):
        """Handle read-only files on Windows during deletion."""
        if not os.access(path, os.W_OK):
            os.chmod(path, stat.S_IWUSR | stat.S_IREAD)
            func(path)
        else:
            raise
    
    def clone_repo(self, github_url: str) -> str:
        """Clone GitHub repository and return local path."""
        
        # Validate URL
        if not github_url.startswith(('https://', 'http://')):
            raise ValueError("Invalid GitHub URL")
        
        # Extract repo name
        repo_name = github_url.rstrip('/').split('/')[-1].replace('.git', '')
        repo_path = os.path.join(self.cache_dir, repo_name)
        
        # Remove if exists (with proper Windows handling)
        if os.path.exists(repo_path):
            try:
                shutil.rmtree(repo_path, onerror=self._handle_remove_readonly)
            except Exception as e:
                pass
        
        try:
            Repo.clone_from(github_url, repo_path)
            
            # Remove .git directory to save space and avoid permission issues
            git_dir = os.path.join(repo_path, '.git')
            if os.path.exists(git_dir):
                try:
                    shutil.rmtree(git_dir, onerror=self._handle_remove_readonly)
                except Exception:
                    pass
            
            return repo_path
        except Exception as e:
            raise Exception(f"Failed to clone repository: {str(e)}")
    
    def get_repo_structure(self, repo_path: str, max_depth: int = 3) -> dict:
        """Get repository structure and file listing."""
        
        structure = {
            "path": repo_path,
            "files": [],
            "directories": [],
            "total_files": 0,
            "languages": set()
        }
        
        for root, dirs, files in os.walk(repo_path):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if d not in self.EXCLUDE_DIRS]
            
            # Get relative path
            rel_path = os.path.relpath(root, repo_path)
            depth = rel_path.count(os.sep)
            
            if depth > max_depth:
                continue
            
            for file in files:
                if file.startswith('.'):
                    continue
                
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                
                if file_size > self.MAX_FILE_SIZE:
                    continue
                
                rel_file_path = os.path.relpath(file_path, repo_path)
                ext = os.path.splitext(file)[1]
                
                structure["files"].append({
                    "path": rel_file_path,
                    "name": file,
                    "extension": ext,
                    "size": file_size
                })
                
                structure["total_files"] += 1
                if ext:
                    structure["languages"].add(ext)
        
        structure["languages"] = sorted(list(structure["languages"]))
        return structure
    
    def read_important_files(self, repo_path: str) -> dict:
        """Read key files from repository."""
        
        important_files = {
            "README.md": None,
            "setup.py": None,
            "requirements.txt": None,
            "package.json": None,
            "Cargo.toml": None,
            "go.mod": None,
            "docker-compose.yml": None,
            "Dockerfile": None,
            ".github/workflows": None
        }
        
        content = {}
        
        for file in important_files:
            file_path = os.path.join(repo_path, file)
            
            if os.path.isfile(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        file_content = f.read()
                        if len(file_content) < 50000:  # Limit to 50KB
                            content[file] = file_content
                        else:
                            content[file] = file_content[:50000] + "\n... (truncated)"
                except Exception as e:
                    content[file] = f"[Error reading file: {str(e)}]"
        
        return content
    
    def cleanup(self):
        """Clean up cache directory."""
        if os.path.exists(self.cache_dir):
            try:
                shutil.rmtree(self.cache_dir, onerror=self._handle_remove_readonly)
            except Exception as e:
                pass
