# System Architecture

## Overview
The Multi-Agent Repository Assistant is a full-stack application that analyzes software repositories and generates technical articles using a multi-agent AI system. It features a modern Flask REST API backend with JWT authentication and a responsive HTML/CSS/JavaScript frontend, all containerized with Docker.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│          Frontend (HTML/CSS/JavaScript)                  │
│  • User Interface: Dashboard, Projects, Generate, Articles
│  • API Client: RESTful communication                      │
│  • State Management: Session-based (localStorage)         │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST (Port 3000/8000)
┌────────────────────▼────────────────────────────────────┐
│          Backend (Flask REST API - Port 5000)            │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Routes: /auth, /projects, /analysis, /generation │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Multi-Agent Orchestrator (LangGraph)              │   │
│  │  • Repo Analyzer → Code Analysis                  │   │
│  │  • Embedding Agent → Vector Storage               │   │
│  │  • Article Generator → Content Creation           │   │
│  │  • Content Improver → Quality Enhancement         │   │
│  │  • Reviewer → Final QA                            │   │
│  └──────────────────────────────────────────────────┘   │
└────────────┬───────────────┬───────────────┬───────────┘
             │               │               │
    ┌────────▼──────┐ ┌─────▼────────┐ ┌───▼─────────┐
    │ Qdrant         │ │ Cohere LLM   │ │ GitHub      │
    │ (Vector DB)    │ │ (Generation) │ │ (Clone Repos)
    │ Port 6333      │ │ API          │ │             │
    └────────────────┘ └──────────────┘ └─────────────┘
```

## Components

### 1. Frontend (HTML/CSS/JavaScript)
**Location**: `frontend/`
- **Pages**:
  - Dashboard: Overview and quick stats
  - Projects: Create, manage, analyze repositories
  - Generate: Create article outlines and full articles
  - Articles: View and manage generated articles
- **Features**:
  - JWT-based authentication (login/register/logout)
  - Real-time project analysis status
  - Article generation with custom instructions
  - Markdown download support
  - Responsive design (Mobile/Desktop)

### 2. Backend REST API (Flask)
**Location**: `backend/`
- **Endpoints** (23 total):
  - **Auth** (5): Register, Login, Logout, Profile, Change Password
  - **Projects** (6): CRUD operations, status tracking
  - **Analysis** (4): Download repo, analyze, structure, dependencies
  - **Generation** (7): Generate outline, full article, download, manage articles
  - **Health** (1): API health check

### 3. Authentication & Security
- **JWT Tokens**: Secure bearer token authentication
- **Password Hashing**: Bcrypt for password security
- **CORS**: Configured for frontend-backend communication
- **Input Validation**: All endpoints validate user inputs

### 4. Multi-Agent Orchestrator (LangGraph)
**Location**: `orchestrator/`
- Manages workflow between analysis and generation agents
- Handles agent-to-agent communication
- Manages state across pipeline stages

### 5. Agents
**Location**: `agents/`
- **Repo Analyzer** (`repo_analyzer.py`): 
  - Extracts file structure, dependencies, code metrics
  - Identifies programming languages and frameworks
  
- **Embedding Agent** (`embedding_agent.py`):
  - Generates vector embeddings from analyzed code
  - Stores in Qdrant for semantic search
  
- **Article Generator** (`article_generator.py`):
  - Creates article outlines using Cohere LLM
  - Generates full articles based on repository analysis
  
- **Content Improver** (`content_improver.py`):
  - Enhances generated content quality
  - Refines formatting and coherence
  
- **Reviewer** (`reviewer.py`):
  - Quality assurance for generated articles
  - Validates technical accuracy

### 6. Tools
**Location**: `tools/`
- **repo_downloader.py**: Clones GitHub repositories
- **file_loader.py**: Loads and parses repository files
- **code_analyzer.py**: Analyzes code structure and metrics
- **text_splitter.py**: Chunks text for embeddings
- **web_search.py**: Web search capabilities

### 7. Data Storage
- **User Data**: JSON-based local storage (`backend/data/users.json`)
- **Projects**: JSON-based storage with metadata (`backend/data/projects.json`)
- **Articles**: JSON-based storage with generated content (`backend/data/articles.json`)
- **Vector Store**: Qdrant database for semantic embeddings (Port 6333)

## Database Schema

### Users
```json
{
  "id": "uuid",
  "username": "string",
  "email": "string",
  "password_hash": "string",
  "created_at": "timestamp"
}
```

### Projects
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "name": "string",
  "github_url": "string",
  "description": "string",
  "status": "pending|analyzed|analyzing",
  "repo_data": {
    "analysis": { ... },
    "structure": { ... },
    "dependencies": { ... }
  },
  "created_at": "timestamp"
}
```

### Articles
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "project_id": "uuid",
  "instructions": "string",
  "description": "string",
  "content": "markdown string",
  "created_at": "timestamp"
}
```

## Security & Resilience
- **Input Validation**: All endpoints validate URLs, paths, and instructions (XSS/injection prevention)
- **Retry Logic**: Exponential backoff for external API calls (Cohere, GitHub, Qdrant)
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Logging**: Centralized logging in `utils/logger.py` tracking system activity and errors
- **Authentication**: JWT tokens with expiration for secure API access
- **CORS**: Properly configured cross-origin requests

## Deployment Architecture
- **Docker**: Multi-container setup with Dockerfile.backend, Dockerfile.frontend
- **Docker Compose**: Orchestrates backend (Flask), frontend (Nginx), and Qdrant services
- **Nginx**: Reverse proxy for frontend serving static files
- **Health Checks**: All services include health check endpoints
