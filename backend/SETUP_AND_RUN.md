# Setup and Run Guide - CivicPulse AI Backend

Complete step-by-step guide to set up, run, and test the backend.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Windows, macOS, or Linux

## Installation Steps

### 1. Navigate to Backend Directory

```powershell
cd C:\seva_hackthon\civicpulse-backend
```

### 2. Create Virtual Environment

#### Windows:
```powershell
python -m venv venv
venv\Scripts\activate
```

#### macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` prefix in your terminal.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI (web framework)
- Uvicorn (ASGI server)
- SQLModel (ORM)
- Pydantic (validation)
- Pytest (testing)
- And dependencies

## Running the Backend

### 1. Initialize Database

```bash
python -c "from app.database import init_db; init_db()"
```

Output should show:
```
INFO - Database initialized at civicpulse.db
```

### 2. Start Development Server

```bash
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete
```

Server is now running at: **http://localhost:8000**

### 3. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Try the `/health` endpoint to verify it's working.

## Loading Demo Data

### Option 1: Interactive Mode

```bash
python app/seed.py
```

You'll see:
```
⚠️  WARNING: This script loads DEMO DATA into the database.
Only use this in development environments.

Continue? (yes/no): yes
```

Type `yes` and press Enter.

### Option 2: Direct Seeding

```bash
python -c "from app.seed import seed_database; seed_database()"
```

After seeding completes, you should see demo data in:
- http://localhost:8000/api/assets
- http://localhost:8000/api/complaints

## Running Tests

### 1. Run All Tests

```bash
pytest
```

Expected output:
```
tests/test_models.py ............. [XX%]
tests/test_endpoints.py .......... [XX%]

============= X passed in X.XXs =============
```

### 2. Run with Verbose Output

```bash
pytest -v
```

### 3. Run Specific Test File

```bash
pytest tests/test_models.py -v
```

### 4. Run Tests with Coverage

```bash
pytest --cov=app tests/
```

This shows which parts of code are covered by tests.

## Testing Endpoints

### Using curl (Command Line)

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Get Complaints
```bash
curl http://localhost:8000/api/complaints
```

#### Get Single Complaint
```bash
curl http://localhost:8000/api/complaints/CP-2026-0101
```

#### Create Complaint
```bash
curl -X POST http://localhost:8000/api/complaints ^
  -H "Content-Type: application/json" ^
  -d "{\"title\":\"Test Issue\",\"description\":\"Test\",\"category\":\"Streetlight\",\"location_text\":\"Test Location\"}"
```

#### Update Complaint
```bash
curl -X PUT http://localhost:8000/api/complaints/CP-2026-0101 ^
  -H "Content-Type: application/json" ^
  -d "{\"status\":\"In Progress\"}"
```

### Using Swagger UI (Browser)

1. Open http://localhost:8000/docs
2. Click on any endpoint
3. Click "Try it out"
4. Fill in parameters
5. Click "Execute"
6. See response

### Using PowerShell

```powershell
# Get complaints
Invoke-WebRequest -Uri "http://localhost:8000/api/complaints" -Method GET

# Create complaint
$body = @{
    title = "Streetlight broken"
    description = "Light not working"
    category = "Streetlight"
    location_text = "Main Road, Ward 12"
    latitude = 22.3152
    longitude = 73.1856
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/complaints" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

## Verifying Installation

### Checklist

- [ ] Virtual environment activated (venv in terminal)
- [ ] Dependencies installed (`pip list` shows fastapi, uvicorn, sqlmodel)
- [ ] Database created (civicpulse.db file exists)
- [ ] Server running (no errors in terminal)
- [ ] Health check works (`http://localhost:8000/health` returns 200)
- [ ] API docs load (`http://localhost:8000/docs` opens)
- [ ] Tests pass (`pytest` shows all passing)
- [ ] Demo data loaded (optional, but confirms database works)

## Configuration

### Environment Variables

Create `.env` file (copy from `.env.example`):

```
DATABASE_URL=sqlite:///civicpulse.db
ENVIRONMENT=development
DEBUG=true
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
APP_NAME=CivicPulse AI Backend
LOG_LEVEL=INFO
```

### Key Settings

| Setting | Default | Description |
|---------|---------|-------------|
| DATABASE_URL | sqlite:///civicpulse.db | Database connection string |
| ENVIRONMENT | development | environment (development/production) |
| DEBUG | true | Enable debug logging |
| ALLOWED_ORIGINS | localhost:5173, localhost:3000 | CORS allowed origins |

## Database Reset

### Delete All Data

```bash
# Stop the server first (Ctrl+C)

# Delete database file
# Windows:
del civicpulse.db

# macOS/Linux:
rm civicpulse.db

# Reinitialize
python -c "from app.database import init_db; init_db()"
```

### Reseed with Fresh Demo Data

```bash
python app/seed.py
```

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'app'"

**Solution**: 
```bash
# Make sure you're in the backend directory
cd civicpulse-backend

# And virtual environment is activated
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
```

### Issue: "Port 8000 already in use"

**Solution**:
```bash
# Use different port
uvicorn app.main:app --port 8001

# Or find and kill process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -i :8000
kill -9 <PID>
```

### Issue: "Database is locked"

**Solution**:
```bash
# Stop the server, delete database, and reinitialize
del civicpulse.db
python -c "from app.database import init_db; init_db()"
```

### Issue: Tests fail with "No module named 'app'"

**Solution**:
```bash
# Install in editable mode
pip install -e .

# Or run from project root
cd civicpulse-backend
pytest
```

### Issue: "Permission denied" when running script

**Solution**:
```bash
# Make sure virtual environment is activated
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
```

## Stopping the Server

Press `Ctrl + C` in the terminal where the server is running.

## Development Workflow

### 1. Start Session

```bash
cd C:\seva_hackthon\civicpulse-backend
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # macOS/Linux

uvicorn app.main:app --reload
```

### 2. Make Changes

Edit files in `app/` directory. The server auto-reloads on save (with `--reload`).

### 3. Test Changes

Option A: Use Swagger UI at http://localhost:8000/docs

Option B: Run tests
```bash
pytest -v
```

Option C: Use curl or PowerShell

### 4. Commit Changes

```bash
git add .
git commit -m "Description of changes"
```

### 5. Stop Server

Press `Ctrl + C`

## Production Deployment

### Before Production:

1. Set `DEBUG=false` in `.env`
2. Set `ENVIRONMENT=production`
3. Configure `ALLOWED_ORIGINS` for your domain
4. Use PostgreSQL instead of SQLite
5. Set up authentication
6. Use HTTPS
7. Configure logging
8. Set up monitoring

### Production Start Command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Next Steps

### Phase 1 Complete ✅
- Backend skeleton created
- Database models defined
- API endpoints implemented
- Tests written

### What's Next?

1. Run backend: `uvicorn app.main:app --reload`
2. Verify endpoints work
3. Load demo data
4. Connect React frontend to backend API
5. Test end-to-end workflow

## Support & Documentation

- **API Docs**: http://localhost:8000/docs (when server running)
- **README.md**: Full project documentation
- **README.md**: Detailed information
- **Tests**: Run `pytest -v` for testing examples

---

**Backend Status**: Ready for development and testing ✅
