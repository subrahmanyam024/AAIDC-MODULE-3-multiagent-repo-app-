import re
import os
from urllib.parse import urlparse
from pathlib import Path

def validate_github_url(url: str) -> bool:
    """
    Validates if the given URL is a valid GitHub repository URL.
    """
    if not url:
        return False
    
    # Basic pattern for GitHub URLs
    pattern = r"^https?://(www\.)?github\.com/[\w-]+/[\w.-]+/?$"
    return bool(re.match(pattern, url))

def validate_file_path(path: str, base_dir: str = None) -> bool:
    """
    Validates if a file path is safe and within the allowed directory.
    """
    try:
        # Resolve absolute path
        abs_path = os.path.abspath(path)
        
        # Check for traversal attempts
        if ".." in path.split(os.sep):
            return False
            
        # If base_dir is provided, ensure path is within it
        if base_dir:
            abs_base = os.path.abspath(base_dir)
            return abs_path.startswith(abs_base)
            
        return True
    except Exception:
        return False

def sanitize_input(text: str) -> str:
    """
    Sanitizes input text to remove potentially harmful characters or patterns.
    """
    if not text:
        return ""
        
    # Remove null bytes
    text = text.replace("\0", "")
    
    # Strip whitespace
    text = text.strip()
    
    return text

def validate_project_name(name: str) -> bool:
    """
    Validates project name (alphanumeric, spaces, hyphens, underscores).
    """
    if not name:
        return False
    
    pattern = r"^[\w\s-]+$"
    return bool(re.match(pattern, name))
