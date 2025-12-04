# Deployment Guide

## Prerequisites
- **Python**: 3.10+
- **Docker & Docker Compose**: Latest versions
- **API Keys**:
  - Cohere (https://dashboard.cohere.ai/api-keys)
  - Jina AI (https://dashboard.jina.ai/)
  - Qdrant (https://cloud.qdrant.io/ or local instance)
- **GitHub Token** (optional, for higher rate limits)

## Environment Variables

Create a `.env` file in the project root:
```env
COHERE_API_KEY=your_cohere_api_key
JINA_API_KEY=your_jina_api_key
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=admin-key
GITHUB_TOKEN=your_github_token
JWT_SECRET_KEY=your-secret-key-change-in-production
FLASK_ENV=production
```

## Development Deployment

### 1. Setup Local Environment

```bash
git clone <repository-url>
cd AAIDC-Module-3
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 2. Install Backend Dependencies

```bash
pip install -r backend/requirements.txt
```

### 3. Start Services

**Terminal 1 - Qdrant Vector Database**:
```bash
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant:latest
```

**Terminal 2 - Flask Backend** (from project root):
```bash
python backend/app.py
# API runs on http://localhost:5000
```

**Terminal 3 - Frontend** (from project root):
```bash
cd frontend
python -m http.server 8000
# Frontend runs on http://localhost:8000
```

### 4. Access Application

- **Frontend**: http://localhost:8000
- **Backend API**: http://localhost:5000
- **API Docs**: http://localhost:5000/api/health

## Docker Deployment (Production)

### 1. Build Images

```bash
docker-compose -f docker-compose.new.yml build
```

### 2. Start All Services

```bash
docker-compose -f docker-compose.new.yml up -d
```

This starts:
- **Backend**: Flask API on port 5000
- **Frontend**: Nginx on port 3000
- **Qdrant**: Vector database on port 6333

### 3. Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000

### 4. View Logs

```bash
docker-compose -f docker-compose.new.yml logs -f backend
docker-compose -f docker-compose.new.yml logs -f frontend
```

### 5. Stop Services

```bash
docker-compose -f docker-compose.new.yml down
```

## Docker Configuration Details

### Backend Service (Dockerfile.backend)
- **Base Image**: python:3.10-slim
- **Port**: 5000
- **Features**: 
  - Health check endpoint
  - Environment variable support
  - Auto-restart on failure

### Frontend Service (Dockerfile.frontend)
- **Base Image**: nginx:alpine
- **Port**: 3000
- **Features**:
  - Static file serving
  - Health check endpoint
  - Minimal image size

### Qdrant Service (docker-compose.new.yml)
- **Image**: qdrant/qdrant:latest
- **Port**: 6333 (API), 6334 (gRPC)
- **Volume**: Persistent data storage
- **Health Check**: Built-in

## Production Considerations

### Security
- **Environment Variables**: Use `.env` file (never commit secrets)
- **JWT Secret**: Generate strong JWT_SECRET_KEY for token signing
- **HTTPS**: Setup reverse proxy (Nginx/Apache) with SSL certificates
- **Input Validation**: All endpoints validate user inputs
- **CORS**: Configure allowed origins

### Performance
- **Caching**: Frontend uses localStorage for session management
- **Rate Limiting**: Consider implementing API rate limiting
- **Database**: Use Qdrant Cloud for managed service
- **Load Balancing**: Use reverse proxy for multiple backend instances

### Monitoring & Logging
- **Logs**: Check application logs in Docker containers
  ```bash
  docker-compose logs backend
  ```
- **Health Checks**: All services have health endpoints
  ```bash
  curl http://localhost:5000/api/health
  ```
- **Error Tracking**: Implement centralized error logging

### Data Management
- **Backups**: Regularly backup `backend/data/` directory
- **Qdrant Data**: Persist Qdrant data volume to avoid loss
- **Database Migration**: Update data schema versions as needed

### Scaling
- **Database**: Use managed Qdrant Cloud instead of local instance
- **Multiple Backends**: Deploy multiple Flask instances behind load balancer
- **CDN**: Serve frontend static files via CDN for faster delivery
- **Async Processing**: Consider Celery for long-running analysis tasks

## Troubleshooting

### Port Already in Use
```bash
# Find and kill process using port
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :5000
kill -9 <PID>
```

### CORS Errors
- Check `backend/app.py` CORS configuration
- Ensure frontend URL matches backend CORS settings

### Qdrant Connection Failed
- Verify Qdrant is running: `curl http://localhost:6333/health`
- Check QDRANT_URL in `.env` file

### API Not Responding
- Check backend logs: `docker-compose logs backend`
- Verify JWT_SECRET_KEY is set
- Ensure all API keys are valid

### Frontend Not Loading
- Check frontend logs: `docker-compose logs frontend`
- Verify API_BASE_URL in `frontend/js/api.js`
- Check Nginx configuration
