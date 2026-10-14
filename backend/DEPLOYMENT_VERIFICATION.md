# Backend Deployment Verification Checklist

This document provides a complete verification checklist to ensure the backend is properly deployed and functioning.

## Pre-Deployment Checklist

### Requirements
- [ ] Python 3.8+ installed
- [ ] pip available
- [ ] Virtual environment not activated yet
- [ ] Working directory: `C:\seva_hackthon\civicpulse-backend`

## Installation Verification

### Step 1: Virtual Environment

```bash
# Navigate to backend
cd C:\seva_hackthon\civicpulse-backend

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Verify activation (should show (venv) prefix in terminal)
echo %VIRTUAL_ENV%
```

**Expected Output**: Path containing `venv`

### Step 2: Dependencies Installation

```bash
# Install from requirements.txt
pip install -r requirements.txt

# Verify installation
pip list | findstr fastapi uvicorn sqlmodel pydantic pytest
```

**Expected Output**: All packages listed

### Step 3: Database Initialization

```bash
# Initialize database
python -c "from app.database import init_db; init_db()"

# Verify database created
dir civicpulse.db
```

**Expected Output**: 
```
Database initialized at civicpulse.db
civicpulse.db         <file exists>
```

## Server Startup Verification

### Step 1: Start Server

```bash
uvicorn app.main:app --reload
```

**Expected Output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete
```

### Step 2: Health Check (in new terminal)

```bash
# With curl
curl http://localhost:8000/health

# Or with PowerShell
Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET

# Or just open in browser
Start-Process "http://localhost:8000/health"
```

**Expected Output** (JSON):
```json
{
  "status": "healthy",
  "service": "CivicPulse AI Backend",
  "version": "0.1.0"
}
```

### Step 3: API Documentation Check

```bash
# Open in browser
Start-Process "http://localhost:8000/docs"

# Or manually navigate to:
# http://localhost:8000/docs
```

**Expected**: 
- Swagger UI loads
- All endpoints listed
- Schemas visible
- "Try it out" buttons available

## API Functionality Verification

### Endpoint Testing (with server running)

#### Test 1: List Assets
```bash
curl "http://localhost:8000/api/assets?limit=5"
```

**Expected**: 
- Status: 200
- Response: `{"items":[],"total":0,...}`

#### Test 2: Create Asset
```bash
curl -X POST http://localhost:8000/api/assets ^
  -H "Content-Type: application/json" ^
  -d "{\"id\":\"TEST-001\",\"asset_type\":\"Streetlight\",\"name\":\"Test\",\"ward\":\"W1\"}"
```

**Expected**:
- Status: 200
- Response includes created asset

#### Test 3: Get Asset
```bash
curl "http://localhost:8000/api/assets/TEST-001"
```

**Expected**:
- Status: 200
- Response: Asset data

#### Test 4: List Complaints
```bash
curl "http://localhost:8000/api/complaints?limit=5"
```

**Expected**:
- Status: 200
- Response: Paginated complaints list

#### Test 5: Create Complaint
```bash
curl -X POST http://localhost:8000/api/complaints ^
  -H "Content-Type: application/json" ^
  -d "{\"title\":\"Test\",\"description\":\"Test\",\"category\":\"Streetlight\",\"location_text\":\"Test Location\"}"
```

**Expected**:
- Status: 200
- Response: Created complaint with generated ID

#### Test 6: Get Complaint
```bash
# Get the ID from previous response
curl "http://localhost:8000/api/complaints/CP-2026-0001"
```

**Expected**:
- Status: 200
- Response: Complaint details

#### Test 7: Update Complaint
```bash
curl -X PUT http://localhost:8000/api/complaints/CP-2026-0001 ^
  -H "Content-Type: application/json" ^
  -d "{\"status\":\"In Progress\"}"
```

**Expected**:
- Status: 200
- Response: Updated complaint with new status

#### Test 8: Pagination
```bash
curl "http://localhost:8000/api/complaints?skip=0&limit=10"
```

**Expected**:
- Status: 200
- Response includes: `skip`, `limit`, `total`, `items`

#### Test 9: Filtering
```bash
curl "http://localhost:8000/api/complaints?priority=High"
```

**Expected**:
- Status: 200
- Response: Only complaints with High priority

#### Test 10: Error Handling
```bash
curl "http://localhost:8000/api/complaints/NONEXISTENT"
```

**Expected**:
- Status: 404
- Response: `{"detail":"Complaint NONEXISTENT not found"}`

## Testing Verification

### Run All Tests

```bash
pytest
```

**Expected Output**:
```
tests/test_models.py ............... [50%]
tests/test_endpoints.py ........... [100%]

============= X passed in X.XXs =============
```

### Run with Coverage

```bash
pytest --cov=app tests/
```

**Expected**: Coverage report showing >80% coverage

### Run Specific Test

```bash
pytest tests/test_models.py::test_asset_creation -v
```

**Expected**: Single test passes

## Demo Data Verification

### Load Demo Data

```bash
# Stop server first (Ctrl+C)

# Load demo
python app/seed.py

# When prompted, type: yes
```

**Expected Output**:
```
Creating 5 demo assets...
Created 5 assets
Creating 5 demo complaints...
Created 5 complaints with timeline entries
Creating demo repair record...
Created demo repair record
Database seeding completed successfully!
```

### Verify Demo Data

```bash
# Restart server
uvicorn app.main:app --reload

# In new terminal:
curl "http://localhost:8000/api/assets" | findstr "SL-W"
curl "http://localhost:8000/api/complaints" | findstr "CP-2026"
```

**Expected**:
- Assets contain: SL-W12-001, RD-W13-002, DR-W12-003, etc.
- Complaints contain: CP-2026-0101, CP-2026-0102, etc.

## Database Verification

### Check Database File

```bash
# Verify database exists
if exist civicpulse.db (
    echo Database file exists
    dir civicpulse.db
) else (
    echo Database file not found
)
```

**Expected**: File size > 0 bytes

### Verify Persistence

```bash
# While server running, create a complaint via API

# Stop server (Ctrl+C)

# Restart server
uvicorn app.main:app --reload

# In new terminal, list complaints
curl "http://localhost:8000/api/complaints"

# Your complaint should still be there
```

**Expected**: Complaint persists across restarts

## Environment Configuration Verification

### Check .env File

```bash
# Verify .env exists or .env.example exists
if exist .env (
    echo .env file found
    type .env
) else if exist .env.example (
    echo .env.example found (create .env copy)
    copy .env.example .env
) else (
    echo No env file found - create .env
)
```

### Verify CORS Configuration

```bash
# Make request from React frontend origin
# (or simulate with curl headers)

curl -i -X OPTIONS http://localhost:8000/api/complaints ^
  -H "Origin: http://localhost:5173"

# Look for CORS headers in response
```

**Expected Headers**:
```
Access-Control-Allow-Origin: http://localhost:5173
Access-Control-Allow-Methods: *
Access-Control-Allow-Headers: *
```

## Frontend Integration Verification

### Test Frontend Connection

From React application or from browser console:

```javascript
// Test backend connectivity
fetch('http://localhost:8000/api/complaints')
  .then(r => r.json())
  .then(data => console.log('Backend connected:', data))
  .catch(e => console.error('Backend error:', e));

// Test creating complaint
fetch('http://localhost:8000/api/complaints', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    title: 'Test from Frontend',
    description: 'Testing integration',
    category: 'Streetlight',
    location_text: 'Test Location'
  })
})
  .then(r => r.json())
  .then(data => console.log('Complaint created:', data))
  .catch(e => console.error('Error:', e));
```

**Expected**:
- No CORS errors in console
- Backend responds with data
- Complaint successfully created

## Troubleshooting Guide

### Issue: "Module not found"

```bash
# Ensure virtual environment activated
venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Port already in use"

```bash
# Use different port
uvicorn app.main:app --port 8001

# Or kill process using 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Issue: "Database locked"

```bash
# Stop server, delete database
del civicpulse.db

# Reinitialize
python -c "from app.database import init_db; init_db()"
```

### Issue: "CORS error"

```bash
# Verify allowed origins in .env
# Should include: http://localhost:5173

# Add to .env if missing:
# ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Issue: "Tests failing"

```bash
# Run with verbose output
pytest -v --tb=short

# Check specific test
pytest tests/test_models.py::test_asset_creation -v

# Verify database isolation
# Tests should use in-memory SQLite
```

## Performance Verification

### Response Time Check

```bash
# Time a request
Measure-Command {
    curl "http://localhost:8000/api/complaints?limit=100" | Out-Null
} | Select-Object TotalMilliseconds

# Should be < 100ms for small dataset
```

### Load Test (Basic)

```bash
# Create multiple complaints quickly
for ($i=1; $i -le 10; $i++) {
    curl -X POST http://localhost:8000/api/complaints `
      -H "Content-Type: application/json" `
      -d "{\"title\":\"Test $i\",\"description\":\"Test\",\"category\":\"Streetlight\",\"location_text\":\"Location\"}"
}

# List all
curl "http://localhost:8000/api/complaints"

# Should handle gracefully without errors
```

## Final Verification Checklist

- [ ] Virtual environment created and activated
- [ ] All dependencies installed
- [ ] Database initialized (civicpulse.db exists)
- [ ] Server starts without errors
- [ ] Health check returns 200
- [ ] API docs load at /docs
- [ ] All 16 endpoints respond correctly
- [ ] CRUD operations work (Create, Read, Update)
- [ ] Pagination working (skip, limit)
- [ ] Filtering working (status, priority, category, ward)
- [ ] All tests pass (20+)
- [ ] Demo data loads successfully
- [ ] Data persists after server restart
- [ ] CORS configured for React (localhost:5173)
- [ ] Error handling returns proper status codes
- [ ] Frontend can connect to backend
- [ ] No console errors or warnings

## Deployment Success Criteria

✅ All items in "Final Verification Checklist" completed
✅ No error messages in server output
✅ No failed tests
✅ Database file created
✅ API responding on http://localhost:8000
✅ Swagger docs available
✅ Can CRUD all entities
✅ Frontend can connect

## Next Steps After Verification

1. Run `uvicorn app.main:app --reload` to start backend
2. Start React frontend (`npm run dev` in frontend directory)
3. Test end-to-end workflow through UI
4. Verify data sync between frontend and backend
5. Load and explore demo data
6. Begin Phase 2 development (authentication, advanced features)

## Support Commands

```bash
# Start server with logging
uvicorn app.main:app --reload --log-level debug

# Run tests with coverage report
pytest --cov=app --cov-report=html tests/

# Check Python version
python --version

# Check installed packages
pip list

# View running processes on port 8000
netstat -ano | findstr :8000

# Get full error traceback
pytest -v --tb=long

# List all API endpoints
curl http://localhost:8000/openapi.json

# Test CORS headers
curl -i -X OPTIONS http://localhost:8000/api/complaints
```

---

**Verification Status**: Use this document to ensure all components are working correctly before proceeding to Phase 2.
