import pytest
from unittest.mock import MagicMock, patch
from agents.repo_analyzer import analyze_repo, detect_project_type, analyze_structure
from agents.qa_agent import QAAgent

class TestRepoAnalyzer:
    def test_detect_project_type_python(self):
        files = [{"path": "requirements.txt", "content": ""}]
        langs = {".py": 10}
        assert detect_project_type(files, langs) == "Python Library"

    def test_detect_project_type_node(self):
        files = [{"path": "package.json", "content": ""}]
        langs = {".js": 10}
        assert detect_project_type(files, langs) == "Node.js/JavaScript"

    def test_analyze_structure(self):
        files = [
            {"path": "src/main.py", "content": ""},
            {"path": "tests/test_main.py", "content": ""},
            {"path": "docs/index.md", "content": ""}
        ]
        structure = analyze_structure(files)
        assert structure["has_src"] is True
        assert structure["has_tests"] is True
        assert structure["has_docs"] is True
        assert structure["has_docker"] is False

    @patch("agents.repo_analyzer.load_files_from_directory")
    def test_analyze_repo(self, mock_load):
        mock_load.return_value = [
            {"path": "README.md", "content": "# Test Repo", "size": 100},
            {"path": "main.py", "content": "print('hello')", "size": 50}
        ]
        
        result = analyze_repo("dummy_path")
        
        assert result["total_files"] == 2
        assert result["repo_size"] == 150
        assert result["readme"] == "# Test Repo"
        assert result["project_type"] == "Python"

class TestQAAgent:
    @patch("agents.qa_agent.EmbeddingAgent")
    @patch("agents.qa_agent.co")
    def test_answer(self, mock_co, mock_emb_cls):
        # Mock EmbeddingAgent instance
        mock_emb = MagicMock()
        mock_emb.search.return_value = [
            {"payload": {"text": "context 1"}},
            {"payload": {"text": "context 2"}}
        ]
        mock_emb_cls.return_value = mock_emb
        
        # Mock Cohere response
        mock_response = MagicMock()
        mock_response.text = "This is the answer."
        mock_co.chat.return_value = mock_response
        
        agent = QAAgent()
        answer = agent.answer("question")
        
        assert answer == "This is the answer."
        mock_emb.search.assert_called_once()
        mock_co.chat.assert_called_once()
