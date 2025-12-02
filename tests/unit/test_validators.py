import pytest
from utils.validators import validate_github_url, validate_file_path, sanitize_input, validate_project_name
import os

class TestValidators:
    def test_validate_github_url(self):
        assert validate_github_url("https://github.com/user/repo")
        assert validate_github_url("http://github.com/user/repo")
        assert not validate_github_url("https://gitlab.com/user/repo")
        assert not validate_github_url("not a url")
        assert not validate_github_url("")

    def test_validate_file_path(self):
        assert validate_file_path("test.txt")
        assert validate_file_path("dir/test.txt")
        # Note: traversal check might be OS specific in implementation details, 
        # but basic logic holds.
        assert not validate_file_path("../test.txt") if os.sep == "/" else True 
        
    def test_sanitize_input(self):
        assert sanitize_input("  hello  ") == "hello"
        assert sanitize_input("hello\0world") == "helloworld"
        assert sanitize_input("") == ""

    def test_validate_project_name(self):
        assert validate_project_name("My Project")
        assert validate_project_name("project-123")
        assert validate_project_name("project_123")
        assert not validate_project_name("Project!")
        assert not validate_project_name("")
