# CivicPulse Backend - Project Structure & Module Guide

**Quick Overview:** FastAPI backend serving a React frontend for complaint management with AI-powered priority scoring.

---

## 📁 Directory Structure

```
civicpulse-backend/
├── app/                          # Main application package
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI app setup & router registration
│   ├── config.py                # Environment configuration (Pydantic Settings)
│   ├── database.py              # SQLite/database initialization & session management
│   ├── seed.py                  # Demo data seeding script
│   │
│   ├── models/                  # SQLModel ORM definitions (database schemas)
│   │   ├── complaint.py         # Complaint model with status & priority
│   │   ├── asset.py             # Infrastructure asset model
│   │   ├── repair.py            # Repair record model
│   │   └── audit.py             # Audit logging model
│   │
│   ├── routers/                 # API endpoint handlers (organized by domain)
│   │   ├── complaints.py        # POST/GET/PUT complaints
│   │   ├── assets.py            # Asset CRUD endpoints
│   │   ├── priority.py          # AI priority evaluation endpoints
│   │   ├── dashboard.py         # Statistics & map data endpoints
│   │   └── health.py            # Health check endpoint
│   │
│   ├── schemas/                 # Pydantic validation schemas (request/response)
│   │   ├── complaint.py         # ComplaintCreateSchema, ComplaintSchema, etc.
│   │   ├── asset.py             # Asset schemas
│   │   ├── repair.py            # Repair schemas
│   │   ├── priority.py          # Priority evaluation schema
│   │   ├── audit.py             # Audit log schema
│   │   └── common.py            # Shared schemas (PaginatedResponse, etc.)
│   │
│   └── services/                # Business logic layer (reusable utilities)
│       ├── id_generator.py      # Generate unique complaint/asset IDs
│       ├── priority_engine.py   # Priority evaluation interface & implementations
│       ├── ai_model_service.py  # Load & use AI model (Member 3's trained model)
│       └── __init__.py
│
├── tests/                       # Automated test suite
│   ├── test_endpoints.py        # API endpoint tests
│   ├── test_e2e_workflows.py    # End-to-end workflow tests
│   ├── test_phase2_features.py  # Phase 2 feature tests
│   ├── test_models.py           # Model validation tests
│   └── conftest.py              # Pytest configuration
│
├── requirements.txt             # Python dependencies
├── civicpulse.db               # SQLite database (auto-created on first run)
├── SETUP_AND_RUN.md            # Quick start guide
├── API_DOCUMENTATION.md        # API reference
├── BACKEND_STRUCTURE.md        # This file
├── PHASE_2_DEPLOYMENT.md       # Deployment guide
│
└── venv/                        # Virtual environment (optional)
```

---

## 🎯 Module Breakdown

### 1️⃣ Configuration & Initialization

#### `config.py` - Application Settings
**Purpose:** Centralized configuration using Pydantic Settings  
**Use:** Import `settings` from this module for config values

```python
from app.config import settings

print(settings.database_url)      # "sqlite:///civicpulse.db"
print(settings.allowed_origins)   # ["http://localhost:5173"]
print(settings.app_version)       # "0.2.0"
```

**Key Values:**
- `database_url` - SQLite connection string
- `environment` - "development" or "production"
- `allowed_origins` - CORS whitelisted domains
- `log_level` - Logging level

#### `database.py` - Database Setup
**Purpose:** SQLite initialization, session management, migrations  
**Key Functions:**
- `get_engine()` - Create SQLAlchemy engine
- `init_db()` - Create all tables on startup
- `get_session()` - FastAPI dependency for database sessions

```python
from app.database import get_session
from fastapi import Depends

@app.get("/data")
def get_data(session: Session = Depends(get_session)):
    # session is a SQLModel Session
    complaints = session.exec(select(Complaint)).all()
    return complaints
```

#### `main.py` - Application Entry Point
**Purpose:** Create FastAPI app, register routers, set up CORS and lifespan  
**Key Elements:**
- FastAPI app initialization
- CORS middleware configuration
- Router registration (`include_router()`)
- Lifespan startup/shutdown

**How to run:**
```bash
uvicorn app.main:app --reload
```

---

### 2️⃣ Data Models (ORM Layer)

**Location:** `models/` directory  
**Technology:** SQLModel (combines SQLAlchemy + Pydantic)  
**Purpose:** Define database tables and relationships

#### `complaint.py` - Complaint Model
**Represents:** Infrastructure issue reports from citizens

```python
class Complaint(SQLModel, table=True):
    id: str                              # Auto-generated ID (e.g., "CP-2026-0001")
    title: str                           # Issue title
    description: str                     # Detailed problem
    category: str                        # Category (Streetlight, Road, etc.)
    location_text: str                   # Human-readable location
    latitude: Optional[float]            # Geographic coordinate (-90 to 90)
    longitude: Optional[float]           # Geographic coordinate (-180 to 180)
    status: str                          # Current status (Reported, Assigned, etc.)
    priority: str                        # Priority level (Low, Medium, High, Critical)
    priority_score: int                  # AI model score (0-100)
    repeat_complaint_count: int          # How many times this was reported
    asset_id: Optional[str]              # Link to Asset if known
    reported_at: datetime                # When created
    updated_at: datetime                 # Last modified
    
    # Relationships
    asset: Optional["Asset"]             # Related asset
    timeline_entries: List["ComplaintTimeline"]
    repair_records: List["RepairRecord"]
    audit_logs: List["AuditLog"]
```

#### `asset.py` - Infrastructure Asset Model
**Represents:** Physical infrastructure (streetlights, roads, drainage, etc.)

#### `repair.py` - Repair Record Model
**Represents:** Work done to fix a complaint

#### `audit.py` - Audit Log Model
**Represents:** Record of all changes for compliance

---

### 3️⃣ API Validation Schemas

**Location:** `schemas/` directory  
**Technology:** Pydantic v2  
**Purpose:** Validate incoming requests and type outgoing responses

#### Key Schemas

```python
# Request schema (what client sends)
class ComplaintCreateSchema(BaseModel):
    title: str
    description: str
    category: str
    location_text: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

# Response schema (what server returns)
class ComplaintSchema(BaseModel):
    id: str
    title: str
    status: str
    priority: str
    priority_score: int
    reported_at: datetime
    # ... all fields
    
    class Config:
        from_attributes = True  # Map SQLModel to schema
```

#### Shared Schemas (`common.py`)

```python
class PaginatedResponse(BaseModel, Generic[T]):
    """Standard pagination wrapper for list endpoints"""
    items: List[T]
    total: int
    skip: int
    limit: int
```

---

### 4️⃣ API Endpoints (Routers)

**Location:** `routers/` directory  
**Technology:** FastAPI APIRouter  
**Purpose:** Handle HTTP requests and return responses

#### `complaints.py` - Complaint Management

```python
# List complaints (with pagination & filters)
GET /api/complaints?skip=0&limit=10&status=Reported&priority=High

# Create new complaint
POST /api/complaints
Body: { "title": "...", "description": "...", ... }

# Get single complaint
GET /api/complaints/{complaint_id}

# Update complaint (PATCH fields)
PATCH /api/complaints/{complaint_id}

# Update status (with validation)
PUT /api/complaints/{complaint_id}/status
Body: { "status": "Assigned" }

# Create repair record
POST /api/complaints/{complaint_id}/repair

# Get repair records
GET /api/complaints/{complaint_id}/repairs

# Get timeline
GET /api/complaints/{complaint_id}/timeline
```

#### `priority.py` - AI Priority Evaluation

```python
# Evaluate priority using AI model
POST /api/complaints/{complaint_id}/priority/evaluate

# Get stored priority evaluation
GET /api/complaints/{complaint_id}/priority
```

#### `dashboard.py` - Statistics & Analytics

```python
# Dashboard statistics
GET /api/dashboard/stats?days=30

# Priority distribution
GET /api/dashboard/priority-summary

# Asset inventory health
GET /api/dashboard/asset-summary

# Map data (geolocated complaints)
GET /api/dashboard/map-data?priority_filter=High&status_filter=Reported
```

#### `assets.py` - Infrastructure Asset Management

```python
GET /api/assets              # List all assets
POST /api/assets             # Create asset
GET /api/assets/{id}         # Get asset details
PATCH /api/assets/{id}       # Update asset
```

#### `health.py` - System Health

```python
GET /health                  # Health check
```

---

### 5️⃣ Business Logic (Services)

**Location:** `services/` directory  
**Purpose:** Reusable logic not tied to HTTP

#### `id_generator.py` - ID Generation

```python
from app.services.id_generator import generate_complaint_id

complaint_id = generate_complaint_id()  # Returns "CP-2026-0001"
```

#### `priority_engine.py` - Priority Evaluation

**Two Implementations:**

1. **AIModelPriorityEngine** (Production)
   - Uses Member 3's trained model
   - Real AI predictions

2. **MockPriorityEngine** (Development)
   - Heuristic-based scoring
   - For testing without model

```python
from app.services.priority_engine import get_evaluator

evaluator = get_evaluator()  # Auto-selects AI or Mock
result = evaluator.evaluate(complaint_data)
# Returns PriorityEvaluation with category, score, explanation
```

#### `ai_model_service.py` - Model Loading & Inference

**Handles:**
- Loading scikit-learn model from pickle
- Feature extraction
- Model inference
- Error handling

```python
from app.services.ai_model_service import get_ai_service

ai_service = get_ai_service()
prediction = ai_service.predict({
    'category': 'Streetlight',
    'repeat_complaint_count': 2,
    'description_length': 150,
    'has_coordinates': 1,
    'hour_reported': 14
})
# Returns: {'priority_category': 'High', 'priority_score': 75, ...}
```

---

## 🔄 Request Flow Example

### When a user submits a complaint:

```
1. Frontend POST /api/complaints
   └─ Body: { title, description, category, location_text, lat, lng }

2. Endpoint: routers/complaints.py :: create_complaint()
   ├─ Validate input using ComplaintCreateSchema
   ├─ Call services/id_generator.generate_complaint_id()
   ├─ Create Complaint model instance
   ├─ Save to database (models/complaint.py)
   ├─ Create ComplaintTimeline entry
   ├─ Create AuditLog entry
   └─ Return Complaint via ComplaintSchema

3. Frontend shows success
   └─ Displays new complaint ID

4. Later, when Frontend GET /api/complaints/{id}/priority:
   ├─ Endpoint: routers/priority.py :: get_complaint_priority()
   ├─ Fetch complaint from database
   ├─ Call services/priority_engine.get_evaluator()
   ├─ Call services/ai_model_service to load model & run inference
   ├─ Get PriorityEvaluation
   └─ Return PriorityEvaluationSchema

5. Frontend displays priority on map/dashboard
```

---

## 🧪 Testing Structure

**Location:** `tests/` directory

```python
# conftest.py - Pytest configuration
├─ Database setup
├─ Test fixtures
└─ Client fixture for API testing

# test_endpoints.py - API route testing
├─ CREATE complaint
├─ GET complaint
├─ LIST complaints with filters
├─ UPDATE status
└─ Error handling

# test_e2e_workflows.py - Full workflow testing
├─ Complete complaint lifecycle
├─ Repair workflow
└─ Dashboard statistics

# test_phase2_features.py - AI & advanced features
├─ Priority evaluation
├─ Map data
└─ Dashboard integration

# test_models.py - Data model validation
└─ SQLModel field validation
```

**Run tests:**
```bash
pytest tests/              # Run all tests
pytest tests/test_endpoints.py  # Run specific test file
pytest -v                 # Verbose output
pytest --cov             # Coverage report
```

---

## 📊 Database Schema

### Tables

```sql
-- Complaints
CREATE TABLE complaints (
    id TEXT PRIMARY KEY,
    title TEXT,
    description TEXT,
    category TEXT,
    location_text TEXT,
    latitude FLOAT,
    longitude FLOAT,
    status TEXT,
    priority TEXT,
    priority_score INT,
    repeat_complaint_count INT,
    asset_id TEXT FOREIGN KEY,
    reported_at DATETIME,
    updated_at DATETIME
);

-- Assets
CREATE TABLE assets (
    id TEXT PRIMARY KEY,
    asset_type TEXT,
    name TEXT,
    ward TEXT,
    latitude FLOAT,
    longitude FLOAT
);

-- Repair Records
CREATE TABLE repair_records (
    id INT PRIMARY KEY,
    complaint_id TEXT FOREIGN KEY,
    status TEXT,
    assigned_team TEXT,
    started_at DATETIME,
    completed_at DATETIME
);

-- Complaint Timeline
CREATE TABLE complaint_timeline (
    id INT PRIMARY KEY,
    complaint_id TEXT FOREIGN KEY,
    status TEXT,
    note TEXT,
    timestamp DATETIME
);

-- Audit Logs
CREATE TABLE audit_logs (
    id INT PRIMARY KEY,
    complaint_id TEXT FOREIGN KEY,
    action TEXT,
    actor TEXT,
    old_value TEXT,
    new_value TEXT,
    timestamp DATETIME
);
```

---

## 🚀 How to Add a New Feature

### Example: Add a "comments" endpoint

1. **Create Schema** (`schemas/comment.py`)
   ```python
   class CommentCreateSchema(BaseModel):
       text: str
       complaint_id: str
   
   class CommentSchema(CommentCreateSchema):
       id: int
       created_at: datetime
   ```

2. **Create Model** (`models/comment.py`)
   ```python
   class Comment(SQLModel, table=True):
       id: Optional[int] = Field(primary_key=True)
       complaint_id: str = Field(foreign_key="complaints.id")
       text: str
       created_at: datetime
   ```

3. **Create Router** (`routers/comments.py`)
   ```python
   from fastapi import APIRouter
   router = APIRouter(prefix="/api/comments", tags=["comments"])
   
   @router.post("", response_model=CommentSchema)
   async def create_comment(data: CommentCreateSchema, session = Depends(get_session)):
       comment = Comment(**data.model_dump())
       session.add(comment)
       session.commit()
       return comment
   ```

4. **Register Router** (in `main.py`)
   ```python
   from app.routers.comments import router as comments_router
   app.include_router(comments_router)
   ```

5. **Write Tests** (`tests/test_comments.py`)
   ```python
   def test_create_comment(client):
       response = client.post("/api/comments", json={...})
       assert response.status_code == 200
   ```

---

## 🔗 Dependencies & Relationships

```
routers/
    ├─ Uses schemas/ (validation)
    ├─ Uses models/ (ORM)
    └─ Uses services/ (business logic)
         ├─ priority_engine.py (evaluation)
         │   └─ ai_model_service.py (model loading)
         └─ id_generator.py (ID creation)

All layers depend on:
    ├─ database.py (session management)
    ├─ config.py (settings)
    └─ models/ (database schema)
```

---

## 📚 File Organization Best Practices

✅ **Models** (`models/`) - Database schemas only
✅ **Schemas** (`schemas/`) - Pydantic validation only
✅ **Routers** (`routers/`) - HTTP handling only (request → service → response)
✅ **Services** (`services/`) - Business logic, reusable utilities
✅ **Config** - Settings, don't import heavy modules

❌ **Don't** put business logic in routers
❌ **Don't** put HTTP logic in services
❌ **Don't** import routers into routers (register in main.py instead)

---

## 🔍 Finding Things

- **"Where do I handle a POST /api/complaints?"** → `routers/complaints.py`
- **"What's the Complaint database structure?"** → `models/complaint.py`
- **"What data can I send to create a complaint?"** → `schemas/complaint.py :: ComplaintCreateSchema`
- **"How is priority calculated?"** → `services/priority_engine.py` or `services/ai_model_service.py`
- **"What tests exist?"** → `tests/` directory
- **"How do I add a new endpoint?"** → See "How to Add a New Feature" above

---

## 📖 Key Concepts

### Models vs Schemas
- **Model**: Database structure (SQLModel), persisted in SQLite
- **Schema**: HTTP request/response validation (Pydantic)
- Example: `Complaint` model has fields like `created_at`, but `ComplaintSchema` might only expose certain fields to clients

### Sessions
- Each HTTP request gets a fresh database session
- Sessions are injected via FastAPI dependency: `Depends(get_session)`
- ORM operations happen within sessions, commit/close happens automatically

### Error Handling
- Use HTTPException for HTTP errors
- Use custom exceptions for business logic errors
- All errors are logged

### Testing Strategy
- Unit tests in `test_models.py`
- Integration tests in `test_endpoints.py`
- E2E tests in `test_e2e_workflows.py`
- Use fixtures (conftest.py) to avoid repetition

---

## 🎓 Getting Started for New Team Members

1. **Read this file** - Understand structure
2. **Read `SETUP_AND_RUN.md`** - Get it running
3. **Read `API_DOCUMENTATION.md`** - Learn the API
4. **Explore `main.py`** - See how it all connects
5. **Read `routers/complaints.py`** - See endpoint example
6. **Run tests** - `pytest tests/`
7. **Make a small change** - Add a new field to a schema

---

## 🤝 Collaboration Tips

- **New router?** Follow the pattern in existing routers
- **New model?** Follow the pattern in existing models
- **Need to change API?** Update schema first, then model, then router
- **Tests failing?** Check conftest.py fixtures
- **Database issues?** Delete `civicpulse.db` and restart (will reinit)

---

**Questions? Check the code comments or ask the team!**

