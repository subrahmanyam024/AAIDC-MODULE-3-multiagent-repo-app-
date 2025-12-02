# Multi-Agent Repository Assistant

A production-ready multi-agent system that analyzes software repositories, generates comprehensive documentation, and provides intelligent question-answering capabilities. Built with **LangGraph**, integrated with **Cohere LLM**, **Jina embeddings**, and **Qdrant vector database**.

## 📚 Documentation
- [System Architecture](docs/ARCHITECTURE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## ✨ Key Features
- **Production Ready**: Comprehensive testing (>70% coverage), input validation, and error handling.
- **Resilient**: Exponential backoff retries for API calls and robust logging.
- **Secure**: Input sanitization and secure API key management.
- **Multi-Agent Architecture**: 7 specialized agents working collaboratively.
- **Interactive Web UI**: Streamlit-based interface for easy interaction.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- API Keys (Cohere, Jina AI, Qdrant)
- API Keys for:
  - [Cohere](https://cohere.ai/) - LLM API
  - [Jina AI](https://jina.ai/) - Embeddings API
  - [Qdrant Cloud](https://qdrant.tech/) - Vector Database

### Installation

1. **Clone and setup environment**:
```bash
cd multiagent-repo-assistant
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment variables** (create `.env` file):
```env
# Qdrant Cloud
QDRANT_URL=https://your-instance.qdrant.io
QDRANT_API_KEY=your_api_key
QDRANT_COLLECTION=repo_chunks
EMBEDDING_DIM=1024

# Cohere
COHERE_API_KEY=your_api_key

# Jina
JINA_API_KEY=your_api_key
JINA_EMBEDDING_MODEL=jina-embeddings-v3
```

## 📖 Usage

### Command-Line Interface

#### 1. Analyze Repository
```bash
# Using LangGraph orchestrator (default)
python main.py analyze --repo path/to/repo

# Save results to JSON
python main.py analyze --repo path/to/repo --output results.json

# Use simple orchestrator
python main.py analyze --repo path/to/repo --orchestrator simple
```

#### 2. Ask Questions
```bash
# Interactive QA
python main.py ask --repo path/to/repo --query "how to install?"

# Specify number of context results
python main.py ask --repo path/to/repo --query "what is this project?" --top-k 10
```

#### 3. Full Pipeline
```bash
# Run complete analysis pipeline
python main.py pipeline --repo path/to/repo --output analysis.json
```

#### 4. Interactive Mode
```bash
# Start interactive Q&A session
python main.py interactive --repo path/to/repo
```

### Python API

```python
from orchestrator.langgraph_flow import run_langgraph_pipeline
from agents.qa_agent import QAAgent

# Run complete pipeline
result = run_langgraph_pipeline("path/to/repo")

# Use QA agent
qa = QAAgent()
answer = qa.answer("How to use this project?", top_k=5)
print(answer)
```

## 🏗️ Architecture

### System Flow

```
┌─────────────────┐
│  Repository    │
│   Input        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│ Repo Analyzer   │─────→│ File Processing  │
└────────┬────────┘      └──────────────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│ Text Splitter   │─────→│ Chunk Content    │
└────────┬────────┘      └──────────────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│ Embedding Agent │─────→│ Jina Embeddings  │
└────────┬────────┘      └──────────────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│ Vector Store    │─────→│ Qdrant Cloud     │
└────────┬────────┘      └──────────────────┘
         │
    ┌────┴────┬─────────┬──────────┐
    ▼         ▼         ▼          ▼
┌─────────┐┌──────┐┌──────┐┌─────────┐
│Metadata │Content│Review │QA Agent │
│Recomm.  │Improver      │        │
└─────────┘└──────┘└──────┘└─────────┘
    │         │         │        │
    └────┬────┴────┬────┴────┬───┘
         ▼         ▼         ▼
    ┌─────────────────────────────┐
    │  Analysis Results JSON       │
    └─────────────────────────────┘
```

### LangGraph Pipeline

```
Analyze Repo
    ↓
Embed Repository Content
    ↓
Suggest Metadata
    ↓
Improve Content
    ↓
Review Results
    ↓
Complete
```

## 📁 Project Structure

```
multiagent-repo-assistant/
├── agents/                      # 7 specialized agents
│   ├── repo_analyzer.py        # Repository structure analysis
│   ├── embedding_agent.py      # Semantic embeddings
│   ├── metadata_recommender.py # Metadata suggestions
│   ├── content_improver.py     # README enhancement
│   ├── reviewer.py             # Content validation
│   ├── qa_agent.py            # Question answering
│   └── __init__.py
├── tools/                       # 5 utility tools
│   ├── file_loader.py          # File extraction
│   ├── text_splitter.py        # Text chunking
│   ├── code_analyzer.py        # Code analysis
│   ├── web_search.py           # Web search integration
│   ├── test_llm_embeddings.py  # LLM testing
│   └── test_qdrant.py          # Database testing
├── orchestrator/                # Workflow orchestration
│   ├── langgraph_flow.py       # LangGraph pipeline
│   └── simple_pipeline.py      # Alternative pipeline
├── config/                      # Configuration
│   └── config.py               # Service initialization
├── data/                        # Sample data
│   └── sample_repo/            # Test repository
├── main.py                      # CLI entry point
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables
└── README.md                    # This file
```

## 🔧 Technology Stack

### Core Framework
- **LangGraph** - Multi-agent orchestration
- **LangChain** - Text processing and utilities
- **Python 3.10** - Programming language

### AI/ML Services
- **Cohere API** - Large Language Models
- **Jina AI** - Text embeddings
- **Qdrant Cloud** - Vector database

### Libraries
- `qdrant-client` - Vector DB client
- `cohere` - LLM SDK
- `requests` - HTTP client
- `python-dotenv` - Environment management

## 📊 Agents Overview

### 1. Repository Analyzer
Extracts and analyzes repository structure, files, languages, and metadata.

### 2. Embedding Agent
Manages text embeddings using Jina API, stores vectors in Qdrant for semantic search.

### 3. Metadata Recommender
Suggests project metadata, titles, and tags based on README content.

### 4. Content Improver
Enhances README using Cohere LLM with structured suggestions.

### 5. Reviewer Agent
Validates improved content and identifies gaps (installation, usage, etc.).

### 6. QA Agent
Retrieves context from vector database and generates answers using LLM.

### 7. Integration Agent
Coordinates communication between agents and external services.

## 🛠️ Tools Overview

### File Loader
- Recursively loads files from directories
- Supports: .py, .md, .txt, .ipynb
- Handles ZIP extraction

### Text Splitter
- Chunks text using LangChain
- Configurable chunk size (default: 800)
- Overlap for context preservation (default: 100)

### Code Analyzer
- Extracts functions, classes, imports
- Analyzes code complexity
- Detects async patterns
- Multi-language support

### Web Search Tool
- GitHub repository search
- Documentation search capability
- Fallback to cached results

### Vector Store Tool
- Manages Qdrant collections
- Batch embedding operations
- Semantic similarity search

## 🧪 Testing

### Run Tests
```bash
# Test LLM and embeddings
python tools/test_llm_embeddings.py

# Test Qdrant integration
python tools/test_qdrant.py
```

### Integration Tests
```bash
# Full pipeline test
python main.py analyze --repo data/sample_repo --output test_results.json
```

## 📈 Example Output

### Metadata Recommendations
```json
{
  "title_alternatives": ["Repo Assistant", "Multi-Agent Analyzer"],
  "one_line_summary": "Intelligent repository analysis system",
  "tags": ["python", "multi-agent", "langchain", "ai"]
}
```

### Review Results
```json
{
  "issues": [
    "README lacks Installation section",
    "No usage examples provided"
  ],
  "evidence": [...]
}
```

## 🔐 Security & Best Practices

- **API Keys**: Store in `.env`, never commit to repository
- **Environment Variables**: Use `python-dotenv` for configuration
- **Error Handling**: Graceful fallbacks for service failures
- **Rate Limiting**: Respects API rate limits
- **Logging**: Detailed error messages for debugging

## 📝 Configuration

### Environment Variables
```env
QDRANT_URL          # Qdrant Cloud instance URL
QDRANT_API_KEY      # Qdrant authentication
QDRANT_COLLECTION   # Collection name (default: repo_chunks)
EMBEDDING_DIM       # Vector dimension (default: 1024)
COHERE_API_KEY      # Cohere API key
JINA_API_KEY        # Jina API key
JINA_EMBEDDING_MODEL # Model name (default: jina-embeddings-v3)
```

## 🚀 Deployment

### Docker (Optional)
```bash
docker build -t multiagent-repo-assistant .
docker run -e COHERE_API_KEY=xxx -e QDRANT_URL=xxx multiagent-repo-assistant
```

### API Server (Optional)
FastAPI-based REST API can be added for:
- Repository analysis endpoints
- QA endpoints
- Health checks

## 📚 Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Cohere API Docs](https://docs.cohere.ai/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Jina Embeddings](https://jina.ai/)

## 🤝 Contributing

This project demonstrates core multi-agent concepts. Areas for enhancement:
- Human-in-the-loop interactions
- MCP (Model Context Protocol) integration
- Additional analysis tools
- Performance benchmarking
- Web UI interface

## 📄 License

Educational project demonstrating Module 2 concepts of multi-agent systems.

## 🙏 Acknowledgments

Built with:
- LangChain ecosystem
- LangGraph orchestration framework
- Cohere API
- Jina AI embeddings
- Qdrant vector database
