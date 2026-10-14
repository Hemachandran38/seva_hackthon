# CivicPulse AI Backend - Phase 1

A FastAPI-based backend for the CivicPulse AI infrastructure maintenance platform. This is Phase 1: Foundation and Database implementation.

## 🎯 Project Goals

- Create a REST API backend for infrastructure complaint management
- Implement persistent SQLite database with proper schema
- Provide endpoints for assets and complaints CRUD operations
- Enable integration with existing React frontend
- Establish foundation for future AI integration

## ✨ Features

### Database Models
- **Assets**: Infrastructure assets (streetlights, roads, drainage, etc.)
- **Complaints**: Infrastructure issues reported by citizens
- **Repair Records**: Tracking of repairs and maintenance
- **Audit Logs**: Action tracking for accountability
- **Timeline**: Status change history for complaints

### API Endpoints
- `GET /` - Root endpoint with API info
- `GET /health` - Health check
- `GET /api/assets` - List assets (paginated, filterable)
- `GET /api/assets/{asset_id}` - Get specific asset
- `POST /api/assets` - Create new asset
- `PUT /api/assets/{asset_id}` - Update asset
- `GET /api/complaints` - List complaints (paginated, filterable)
- `GET /api/complaints/{complaint_id}` - Get specific complaint
- `POST /api/complaints` - Create new complaint
- `PUT /api/complaints/{complaint_id}` - Update complaint

### Features
- ✅ Pagination with skip/limit parameters
- ✅ Filtering by multiple dimensions
- ✅ CORS configured for React frontend
- ✅ Automatic ID generation
- ✅ Coordinate validation
- ✅ Priority and status validation
- ✅ Comprehensive error handling
- ✅ Development data seeding
- ✅ Detailed API documentation (Swagger)

## 📋 Requirements

- Python 3.8+
- pip

## 🚀 Quick Start

### 1. Set Up Environment

```bash
# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies

```bash
cd civicpulse-backend
pip install -r requirements.txt
```

### 3. Configure Environment (Optional)

```bash
# Copy example env file
cp .env.example .env

# Edit .env if needed (defaults are provided)
```

### 4. Initialize Database

```bash
# Database auto-initializes on first run
# Or manually initialize:
python -c "from app.database import init_db; init_db()"
```

### 5. Load Demo Data (Optional)

```bash
# Interactive seeding with confirmation
python -m app.seed

# Or run directly:
python app/seed.py
```

### 6. Start Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs (Swagger UI)
- ReDoc: http://localhost:8000/redoc

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_models.py

# Run with verbose output
pytest -v
```

## 📁 Project Structure

```
civicpulse-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app setup
│   ├── config.py               # Configuration & settings
│   ├── database.py             # Database setup
│   ├── seed.py                 # Demo data seeding
│   ├── models/
│   │   ├── __init__.py
│   │   ├── asset.py            # Asset model
│   │   ├── complaint.py        # Complaint & Timeline models
│   │   ├── repair.py           # Repair record model
│   │   └── audit.py            # Audit log model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── common.py           # Common schemas
│   │   ├── asset.py            # Asset schemas
│   │   ├── complaint.py        # Complaint schemas
│   │   └── repair.py           # Repair schemas
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── health.py           # Health check routes
│   │   ├── assets.py           # Asset routes
│   │   └── complaints.py       # Complaint routes
│   └── services/
│       ├── __init__.py
│       └── id_generator.py     # ID generation logic
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Test fixtures
│   ├── test_models.py          # Model tests
│   └── test_endpoints.py       # Endpoint tests
├── .env.example                # Environment template
├── requirements.txt            # Dependencies
├── README.md                   # This file
└── civicpulse.db              # SQLite database (auto-created)
```

## 🔌 Integration with Frontend

The backend is designed to integrate seamlessly with the existing React frontend:

### CORS Configuration
- React dev server (http://localhost:5173) is pre-configured in allowed origins
- Configurable via `.env` file

### Data Compatibility
- Complaint model aligns with React Complaint interface
- ID format matches frontend expectations (CP-YYYY-NNNN)
- All timestamp formats use ISO 8601

### Example Frontend Integration

```typescript
// Fetch complaints from backend
const response = await fetch('http://localhost:8000/api/complaints');
const data = await response.json();

// Create new complaint
const newComplaint = await fetch('http://localhost:8000/api/complaints', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    title: "Streetlight broken",
    description: "Light is not working",
    category: "Streetlight",
    location_text: "Main Road",
    latitude: 22.3152,
    longitude: 73.1856,
    ward: "Ward 12"
  })
});
```

## 📊 API Examples

### List Complaints with Filters

```bash
# Basic list
curl http://localhost:8000/api/complaints

# With pagination
curl "http://localhost:8000/api/complaints?skip=0&limit=10"

# Filter by priority
curl "http://localhost:8000/api/complaints?priority=High"

# Filter by status
curl "http://localhost:8000/api/complaints?status=In%20Progress"

# Multiple filters
curl "http://localhost:8000/api/complaints?priority=Critical&status=Reported"
```

### Create Complaint

```bash
curl -X POST http://localhost:8000/api/complaints \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Streetlight not working",
    "description": "Complete blackout on Main Road",
    "category": "Streetlight",
    "location_text": "Main Ring Road, Ward 12",
    "latitude": 22.3152,
    "longitude": 73.1856,
    "ward": "Ward 12"
  }'
```

### Update Complaint Status

```bash
curl -X PUT http://localhost:8000/api/complaints/CP-2026-0101 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "In Progress",
    "assigned_team": "Municipal Crew Alpha"
  }'
```

### List Assets

```bash
# All assets
curl http://localhost:8000/api/assets

# Filter by ward
curl "http://localhost:8000/api/assets?ward=Ward%2012"

# Filter by type
curl "http://localhost:8000/api/assets?asset_type=Streetlight"
```

## 🔐 Data Validation

### Coordinates
- Latitude: -90 to 90 degrees
- Longitude: -180 to 180 degrees
- Both optional (for unreported/unlocated issues)

### Priority Levels
- Low
- Medium
- High
- Critical

### Complaint Status
- Reported
- Under Review
- Assigned
- In Progress
- Awaiting Verification
- Resolved

### Priority Score
- 0-100 (integer)

## 📚 Demo Data

The seed script creates:
- **5 demo assets** across different categories (Streetlight, Road, Drainage, Electrical, Public Space)
- **5 demo complaints** with varying priorities and statuses
- **1 demo repair record** tracking a completed repair
- **Complete timeline entries** for each complaint

Demo data is clearly labeled and only loaded with user confirmation.

## 🔍 Database

### SQLite Setup
- Persistent storage in `civicpulse.db`
- Foreign key constraints enabled
- Auto-initializes on first run
- Survives server restarts

### Schema Highlights
- Primary keys: Asset ID (string), Complaint ID (string)
- Foreign keys: Asset references, Complaint references
- Timestamps: UTC ISO 8601 format
- Validation: Constraints at database level

## 🚧 Future Phases

### Phase 2 (Planned)
- User authentication & authorization
- Advanced filtering & search
- Batch operations
- File upload support

### Phase 3 (Planned)
- AI prioritization engine
- Predictive analytics
- PostgreSQL migration support
- Real-time notifications

## 📝 Notes

### Development Mode
- Auto-reload enabled (`--reload` flag)
- Debug logging active
- CORS allows development origins

### Production Deployment
- Set `DEBUG=false` in `.env`
- Use PostgreSQL instead of SQLite
- Enable authentication
- Configure allowed origins carefully
- Use production CORS settings

## 🛠️ Troubleshooting

### Database Lock Error
```bash
# Delete and recreate database
rm civicpulse.db
python -c "from app.database import init_db; init_db()"
```

### Port Already in Use
```bash
# Use different port
uvicorn app.main:app --port 8001
```

### Import Errors
```bash
# Ensure you're in the virtual environment
# And have installed requirements
pip install -r requirements.txt
```

### Tests Failing
```bash
# Ensure pytest is installed
pip install pytest pytest-asyncio

# Run with verbose output for debugging
pytest -v --tb=short
```

## 📄 License

CivicPulse AI Backend - Phase 1
Development Project for Municipal Infrastructure Management

## 👥 Contact

For questions or contributions, please refer to project documentation.

---

**Status**: Phase 1 Complete ✅
**Version**: 0.1.0
**Last Updated**: January 2026
