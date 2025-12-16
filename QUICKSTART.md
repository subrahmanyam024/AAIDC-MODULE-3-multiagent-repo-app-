# Quick Start Guide - Flask + Frontend

**⏱️ Setup Time**: ~15 minutes

---

## 5-Minute Setup (Development)

### 1. Install Backend Dependencies
```bash
pip install -r backend/requirements.txt
```

### 2. Create `.env` File
```bash
FLASK_ENV=development
FLASK_PORT=5000
JWT_SECRET_KEY=dev-secret-key-change-in-production

QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=admin-key
COHERE_API_KEY=your_key_here
JINA_API_KEY=your_key_here
```

### 3. Start Qdrant
```bash
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant:latest
```

### 4. Start Backend
```bash
python backend/app.py
```

### 5. Start Frontend
```bash
cd frontend
python -m http.server 8000
```

### 6. Open Browser
```
http://localhost:8000
```

**Done!** 🎉

---

## Docker Quick Start (Production)

### 1. Clone and Setup
```bash
git clone <repo-url>
cd AAIDC-Module-3
cp .env.sample .env
# Edit .env with your API keys
```

### 2. Build and Run
```bash
docker-compose -f docker-compose.new.yml up --build
```

### 3. Access Application
```
http://localhost:3000
```

---

## First Time Usage

### 1. Register Account
- Click "Create Account"
- Fill in username, email, password
- Click "Register"

### 2. Login
- Enter credentials
- Click "Login"

### 3. Create Project
- Go to "Projects" tab
- Click "New Project"
- Enter GitHub URL (e.g., https://github.com/torvalds/linux)
- Click "Create Project"

### 4. Analyze Repository
- Click "Analyze" on project card
- Wait for analysis to complete (1-5 minutes)

### 5. Generate Article
- Go to "Generate" tab
- Select your project
- Write instructions (e.g., "Write a technical overview")
- Click "Generate Full Article"
- Download as Markdown or JSON

---

## Common Commands

### Development
```bash
# Start backend
python backend/app.py

# Start frontend (in frontend folder)
python -m http.server 8000

# Start Qdrant
docker run -p 6333:6333 qdrant/qdrant:latest
```

### Docker
```bash
# Build
docker-compose -f docker-compose.new.yml build

# Start
docker-compose -f docker-compose.new.yml up -d

# View logs
docker-compose -f docker-compose.new.yml logs -f backend

# Stop
docker-compose -f docker-compose.new.yml down
```

### Testing
```bash
# Test backend health
curl http://localhost:5000/api/health

# Test frontend
curl http://localhost:8000

# Test Qdrant
curl http://localhost:6333/health
```

---

## API Testing

### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "password"}'
```

### Create Project (with token)
```bash
curl -X POST http://localhost:5000/api/projects \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Project",
    "github_url": "https://github.com/user/repo"
  }'
```

### Get Projects
```bash
curl -X GET http://localhost:5000/api/projects \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Port 5000 in use** | `netstat -tulpn \| grep 5000` then kill process |
| **CORS error** | Check `CORS()` in backend/app.py is configured |
| **Frontend can't reach API** | Update API_BASE_URL in frontend/js/api.js |
| **JWT token error** | Clear localStorage and login again |
| **Qdrant connection failed** | Check Qdrant container is running |
| **ModuleNotFoundError** | Run `pip install -r requirements.txt` |

---

## File Structure Summary

```
├── backend/
│   ├── app.py                  # Flask app entry
│   ├── routes/                 # API endpoints
│   └── requirements.txt         # Python deps
├── frontend/
│   ├── index.html              # Main page
│   ├── css/style.css           # Styling
│   └── js/                      # Logic
├── docker-compose.new.yml       # Docker setup
├── MIGRATION_GUIDE.md           # Detailed guide
├── QUICKSTART.md                # This file
└── .env                         # Configuration
```

---

## Next Steps

1. ✅ **Complete**: Follow "5-Minute Setup" above
2. 📖 **Learn**: Read MIGRATION_GUIDE.md for details
3. 🚀 **Deploy**: Use Docker Compose
4. 🔐 **Secure**: 
   - Change JWT_SECRET_KEY
   - Update API keys
   - Enable HTTPS

---

## Environment Variables Needed

Get these from:
- **Cohere**: https://dashboard.cohere.ai/api-keys
- **Jina**: https://dashboard.jina.ai/
- **Qdrant**: https://cloud.qdrant.io/ (or local)

---

## Health Checks

```bash
# Frontend
curl http://localhost:8000

# Backend
curl http://localhost:5000/api/health

# Qdrant
curl http://localhost:6333/health
```

All should return 200 OK.

---

## Testing

Run the test suite to verify everything works correctly:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=backend --cov-report=html

# Run specific test types
pytest tests/unit/ -v            # Unit tests
pytest tests/integration/ -v     # Integration tests
pytest tests/e2e/ -v             # End-to-end tests
```

See [Testing Strategy](docs/TESTING.md) for detailed information.

---

**Need Help?** See MIGRATION_GUIDE.md for detailed troubleshooting.
