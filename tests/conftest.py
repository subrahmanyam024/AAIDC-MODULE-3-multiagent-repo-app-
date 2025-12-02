import pytest
import os
import sys
from pathlib import Path

# Add project root to python path
sys.path.append(str(Path(__file__).parent.parent))

@pytest.fixture
def sample_repo_path():
    """Returns path to the sample repository for testing"""
    return Path(__file__).parent.parent / "data" / "sample_repo"

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Sets up mock environment variables"""
    monkeypatch.setenv("COHERE_API_KEY", "mock_key")
    monkeypatch.setenv("QDRANT_URL", "http://localhost:6333")
    monkeypatch.setenv("QDRANT_API_KEY", "mock_key")
    monkeypatch.setenv("JINA_API_KEY", "mock_key")
