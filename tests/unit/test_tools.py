import pytest
import os
import tempfile
from pathlib import Path
from tools.file_loader import load_files_from_directory, should_exclude
from tools.text_splitter import split_text
from tools.code_analyzer import CodeAnalyzer

class TestFileLoader:
    def test_should_exclude(self):
        assert should_exclude("venv/lib/python3.8/site-packages")
        assert should_exclude(".git/HEAD")
        assert should_exclude("__pycache__/module.cpython-38.pyc")
        assert not should_exclude("src/main.py")
        assert not should_exclude("README.md")

    def test_load_files_from_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create some test files
            with open(os.path.join(tmpdir, "test.py"), "w") as f:
                f.write("print('hello')")
            with open(os.path.join(tmpdir, "README.md"), "w") as f:
                f.write("# Test Repo")
            
            # Create excluded directory
            os.makedirs(os.path.join(tmpdir, "venv"))
            with open(os.path.join(tmpdir, "venv", "lib.py"), "w") as f:
                f.write("excluded")

            files = load_files_from_directory(tmpdir)
            
            assert len(files) == 2
            paths = [f["path"] for f in files]
            assert "test.py" in paths
            assert "README.md" in paths

class TestTextSplitter:
    def test_split_text(self):
        text = "a" * 1000
        chunks = split_text(text, chunk_size=100, chunk_overlap=10)
        assert len(chunks) > 1
        assert len(chunks[0]) <= 100

class TestCodeAnalyzer:
    def test_analyze_python_file(self):
        analyzer = CodeAnalyzer()
        content = """
import os
def hello():
    print("hello")
class MyClass:
    pass
async def main():
    pass
"""
        analysis = analyzer.analyze_file("test.py", content)
        assert analysis["language"] == "python"
        assert "hello" in analysis["functions"]
        assert "MyClass" in analysis["classes"]
        assert analysis["has_async"] is True
        assert analysis["imports_count"] == 1

    def test_analyze_repository(self):
        analyzer = CodeAnalyzer()
        files = [
            {"path": "test.py", "content": "def foo(): pass"},
            {"path": "README.md", "content": "# Hello"}
        ]
        analysis = analyzer.analyze_repository(files)
        assert analysis["total_files"] == 2
        assert analysis["languages"]["python"] == 1
        assert analysis["languages"]["markdown"] == 1
