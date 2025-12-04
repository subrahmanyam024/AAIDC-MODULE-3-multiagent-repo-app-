# tools/file_loader.py
import os
import zipfile
import json

EXCLUDE_DIRS = {
    'venv', 'env', '.venv', 'node_modules', '.git', '__pycache__', 
    '.pytest_cache', 'build', 'dist', '.egg-info', '.tox',
    'site-packages', '.next', 'out', '.svelte-kit'
}

EXCLUDE_FILES = {'.DS_Store', 'Thumbs.db', '.gitkeep'}

def should_exclude(path):
    path = path.replace('/', os.sep).replace('\\', os.sep)
    for excluded in EXCLUDE_DIRS:
        if os.sep + excluded + os.sep in path or path.startswith(excluded + os.sep):
            return True
    return False

def load_files_from_directory(directory, extensions=(".py", ".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".lock", ".xml")):
    files = []
    max_file_size = 500_000
    
    try:
        for root, dirs, filenames in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            
            for fname in filenames:
                if fname in EXCLUDE_FILES:
                    continue
                    
                path = os.path.join(root, fname)
                rel_path = os.path.relpath(path, directory).replace("\\", "/")
                
                if should_exclude(rel_path):
                    continue
                
                if fname.lower().endswith(extensions) or fname in ('README', 'LICENSE', 'Dockerfile', 'Makefile', '.gitignore'):
                    try:
                        file_size = os.path.getsize(path)
                        if file_size > max_file_size:
                            continue
                            
                        with open(path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                        
                        files.append({
                            "path": rel_path,
                            "content": content,
                            "size": file_size,
                            "content_size": len(content)
                        })
                    except Exception:
                        continue
    except Exception as e:
        print(f"Error scanning directory: {e}")
    
    return files

def extract_zip_to_dir(zip_path, dest_dir):
    os.makedirs(dest_dir, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(dest_dir)
    return dest_dir
