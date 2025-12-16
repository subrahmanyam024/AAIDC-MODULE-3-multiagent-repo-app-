# Testing Strategy & Coverage

## Overview

This document outlines the comprehensive testing strategy for the Multi-Agent Repository Assistant, including unit tests, integration tests, and end-to-end tests with clear coverage targets and execution guidelines.

## Testing Pyramid

```
        ┌─────────────────────┐
        │  End-to-End Tests   │  <5%  (High cost, critical paths)
        ├─────────────────────┤
        │  Integration Tests  │ ~20%  (Medium cost, API interactions)
        ├─────────────────────┤
        │   Unit Tests        │ ~75%  (Low cost, isolated components)
        └─────────────────────┘
```

## Coverage Targets

| Component | Target Coverage | Current | Status |
|-----------|-----------------|---------|--------|
| **Agents** | ≥85% | 80% | In Progress |
| **Tools** | ≥80% | 78% | In Progress |
| **Routes** | ≥75% | 72% | In Progress |
| **Validators** | ≥90% | 88% | ✅ Good |
| **Overall** | ≥70% | 72% | ✅ Good |

## Unit Tests

### Test Location
```
tests/unit/
├── test_agents.py           # Agent functionality tests
├── test_tools.py            # Tool utility tests
├── test_validators.py       # Input validation tests
└── conftest.py              # Pytest fixtures
```

### Running Unit Tests

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run with coverage report
pytest tests/unit/ --cov=agents --cov=tools --cov-report=html

# Run specific test file
pytest tests/unit/test_agents.py -v

# Run specific test class
pytest tests/unit/test_agents.py::TestRepoAnalyzer -v
```

### Key Unit Test Suites

#### 1. Agent Tests (`test_agents.py`)
- **Repository Analyzer**:
  - Test project type detection (Python, Node.js, Java, etc.)
  - Test file structure analysis
  - Test dependency extraction
  - Test README parsing

- **QA Agent**:
  - Test question answering with mocked embeddings
  - Test context retrieval accuracy
  - Test fallback mechanisms
  - Test error handling for missing context

- **Article Generator**:
  - Test outline generation
  - Test full article generation
  - Test content formatting
  - Test metadata extraction

#### 2. Tool Tests (`test_tools.py`)
- **File Loader**:
  - Test file reading across formats (.py, .md, .txt, .ipynb)
  - Test ZIP extraction
  - Test error handling for missing files
  - Test recursive directory loading

- **Text Splitter**:
  - Test chunk size adherence
  - Test overlap calculation
  - Test edge cases (empty text, very long text)

- **Code Analyzer**:
  - Test function extraction
  - Test class detection
  - Test import tracking
  - Test multi-language support

#### 3. Validator Tests (`test_validators.py`)
- Test URL validation (GitHub URLs)
- Test input sanitization (XSS prevention)
- Test path validation
- Test instruction length validation

### Example Unit Test

```python
def test_detect_project_type_python():
    """Test Python project detection"""
    files = [{"path": "requirements.txt", "content": ""}]
    langs = {".py": 10}
    assert detect_project_type(files, langs) == "Python Library"

def test_text_splitter_chunk_size():
    """Test text splitter respects chunk size"""
    text = "x" * 2000  # 2000 character string
    chunks = split_text(text, chunk_size=500, overlap=50)
    for chunk in chunks:
        assert len(chunk) <= 500
```

## Integration Tests

### Test Location
```
tests/integration/
├── test_api_endpoints.py      # API endpoint integration
├── test_agent_pipeline.py     # Multi-agent workflow
└── test_qdrant_integration.py # Vector database integration
```

### Running Integration Tests

```bash
# Run all integration tests
pytest tests/integration/ -v

# Run with external service mocking
pytest tests/integration/ -v --mock-external-services

# Run specific integration test
pytest tests/integration/test_api_endpoints.py::test_auth_flow -v
```

### Key Integration Test Scenarios

#### 1. API Endpoint Integration (`test_api_endpoints.py`)
```python
def test_auth_flow_complete():
    """Test complete authentication workflow"""
    # 1. Register user
    response = client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 201
    
    # 2. Login
    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'password123'
    })
    assert response.status_code == 200
    token = response.json['access_token']
    
    # 3. Access protected resource
    response = client.get('/api/projects',
        headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
```

#### 2. Agent Pipeline Integration (`test_agent_pipeline.py`)
- Test repository download and loading
- Test embeddings generation and storage
- Test article generation end-to-end
- Test Q&A pipeline with vector search

#### 3. Qdrant Integration (`test_qdrant_integration.py`)
- Test connection establishment
- Test collection creation/deletion
- Test embedding storage and retrieval
- Test semantic similarity search

## End-to-End Tests

### Test Location
```
tests/e2e/
├── test_full_workflow.py      # Complete analysis and generation
├── test_ui_flows.py           # Frontend interaction testing
└── test_performance.py        # Performance benchmarks
```

### Running End-to-End Tests

```bash
# Run all E2E tests (requires Docker and services running)
pytest tests/e2e/ -v --e2e

# Run with performance profiling
pytest tests/e2e/ -v --e2e --benchmark

# Run specific workflow test
pytest tests/e2e/test_full_workflow.py::test_analyze_and_generate -v --e2e
```

### Key End-to-End Test Scenarios

#### 1. Complete Analysis Workflow (`test_full_workflow.py`)
```python
@pytest.mark.e2e
def test_analyze_repository_to_article_generation():
    """Test full pipeline: upload → analyze → generate article"""
    
    # Setup: Create test repository
    repo_url = "https://github.com/torvalds/linux"
    
    # Step 1: Register and login
    user = setup_test_user()
    token = authenticate(user)
    
    # Step 2: Create project
    project = create_project(
        token=token,
        name="Linux Kernel Analysis",
        github_url=repo_url
    )
    assert project['status'] == 'pending'
    
    # Step 3: Trigger analysis
    analysis = trigger_analysis(token, project['id'])
    wait_for_completion(analysis['job_id'], timeout=300)
    
    # Step 4: Verify analysis results
    results = get_analysis_results(token, project['id'])
    assert results['total_files'] > 0
    assert results['languages'] is not None
    assert results['project_type'] is not None
    
    # Step 5: Generate article
    article = generate_article(
        token=token,
        project_id=project['id'],
        instructions="Create a technical overview of the kernel"
    )
    assert article['status'] == 'completed'
    assert len(article['content']) > 100
    
    # Step 6: Verify article quality
    assert validate_article_structure(article)
    assert article['has_introduction'] == True
    assert article['has_sections'] == True
```

#### 2. UI Interaction Testing (`test_ui_flows.py`)
- Test login/registration flows
- Test project creation and deletion
- Test article generation and download
- Test responsive design across devices

#### 3. Performance Testing (`test_performance.py`)
```python
@pytest.mark.e2e
@pytest.mark.benchmark
def test_analysis_performance():
    """Benchmark: Repository analysis should complete within SLA"""
    repo_size_mb = 100  # 100MB repository
    start_time = time.time()
    
    results = analyze_repository(test_repo_path)
    
    elapsed = time.time() - start_time
    
    # SLA: 5 minutes for 100MB repo
    assert elapsed < 300, f"Analysis took {elapsed}s, SLA is 300s"
    assert results['total_files'] > 0
```

## Continuous Integration

### GitHub Actions Configuration
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.10
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio
      
      - name: Run unit tests
        run: pytest tests/unit/ --cov=agents --cov=tools
      
      - name: Run integration tests
        run: pytest tests/integration/ -v
      
      - name: Upload coverage
        uses: codecov/codecov-action@v2
        with:
          files: ./coverage.xml
```

## Test Fixtures & Mocking

### Using Conftest.py
```python
# tests/conftest.py
import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_cohere():
    """Mock Cohere LLM API"""
    with patch('cohere.Client') as mock:
        mock.return_value.generate.return_value = MagicMock(
            generations=[MagicMock(text="Generated text")]
        )
        yield mock

@pytest.fixture
def mock_qdrant():
    """Mock Qdrant vector database"""
    with patch('qdrant_client.QdrantClient') as mock:
        yield mock

@pytest.fixture
def test_user():
    """Create test user"""
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    }
```

## Coverage Reports

### Generating Coverage Reports
```bash
# Generate HTML coverage report
pytest tests/ --cov=backend --cov=agents --cov-report=html

# View coverage in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Coverage Thresholds
- **Critical paths** (auth, analysis): ≥90% coverage required
- **Core agents**: ≥85% coverage required
- **Utility functions**: ≥80% coverage required
- **Overall project**: ≥70% coverage required

## Testing Best Practices

### 1. Isolation
- ✅ Tests should be independent and not depend on other tests
- ✅ Use fixtures for setup/teardown
- ✅ Mock external services (APIs, databases)

### 2. Clarity
- ✅ Use descriptive test names: `test_<function>_<scenario>_<expected_result>`
- ✅ Include docstrings explaining the test purpose
- ✅ One assertion per test when possible

### 3. Maintenance
- ✅ Avoid hardcoded values (use fixtures instead)
- ✅ Keep tests DRY using helper functions
- ✅ Update tests when requirements change

### 4. Performance
- ✅ Unit tests should complete in <1 second
- ✅ Integration tests should complete in <30 seconds
- ✅ E2E tests should complete in <5 minutes

## Troubleshooting Tests

### Common Issues

| Issue | Solution |
|-------|----------|
| **Import errors** | Run `pip install -r requirements.txt` and ensure PYTHONPATH is set |
| **Port conflicts** | Kill existing services or use different ports in test config |
| **Flaky tests** | Add retries for external API calls, increase timeouts |
| **Mock issues** | Verify mock patch paths match actual import locations |
| **Qdrant connection** | Start Qdrant: `docker run -p 6333:6333 qdrant/qdrant` |

## Future Improvements

1. **Visual Regression Testing**: Add screenshot comparison for UI tests
2. **Load Testing**: Implement k6/Locust for performance stress testing
3. **API Contract Testing**: Use Pact for API contract verification
4. **Security Testing**: Add OWASP ZAP integration for security scanning
5. **Accessibility Testing**: Add axe-core for automated a11y testing
