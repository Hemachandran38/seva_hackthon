# CivicPulse AI Backend - Phase 2 Deployment Guide

## Status

✅ **Phase 2 Complete**  
**Test Results:** 53 passing tests  
**New Features:** AI Priority Integration, Dashboard APIs, Map Support, End-to-End Tests  
**Backward Compatibility:** All Phase 1 endpoints and functionality preserved

---

## Phase 2 Features Implemented

### 1. AI Priority Integration

#### Modular Priority Engine
- **File:** `app/services/priority_engine.py`
- **Interface:** Abstract `PriorityEngine` base class
- **Mock Implementation:** `MockPriorityEngine` for development
- **Production Ready:** Can be replaced with actual AI model without changing API

#### Priority Endpoints
- `POST /api/complaints/{complaint_id}/priority/evaluate` - Evaluate priority
- `GET /api/complaints/{complaint_id}/priority` - Get priority evaluation

#### Response Format
```json
{
  "complaint_id": "CP-2026-0001",
  "priority_category": "High",
  "priority_score": 75,
  "explanation": "Mock priority evaluation...",
  "contributing_factors": { "category_weight": 15, "repeat_boost": 5 },
  "model_version": "development-mock-v1",
  "evaluated_at": "2026-01-14T10:35:00"
}
```

**Important:** Mock scores are explicitly marked as prototypes. Never represent mock data as actual model predictions.

### 2. Dashboard Statistics APIs

#### Endpoints
- `GET /api/dashboard/stats` - Overall dashboard statistics
- `GET /api/dashboard/priority-summary` - Priority distribution
- `GET /api/dashboard/asset-summary` - Asset inventory and health
- `GET /api/dashboard/map-data` - Geographic data for maps

#### Stats Endpoint Response
```json
{
  "timestamp": "2026-01-14T10:35:00",
  "period_days": 30,
  "complaints": {
    "total": 42,
    "open": 15,
    "resolved": 25,
    "recent": 8,
    "high_repeat_issues": 2,
    "average_priority_score": 65.3
  },
  "status_distribution": { "Reported": 2, "In Progress": 3, "Resolved": 25 },
  "category_distribution": { "Streetlight": 15, "Drainage": 10, "Road & pavement": 17 },
  "repairs": {
    "total_records": 28,
    "verified": 25,
    "failed": 2,
    "pending": 1,
    "rejected": 0
  },
  "teams_active": 3
}
```

#### Map Data Endpoint
Returns complaints and assets with coordinates for map rendering:
```json
{
  "complaints": [
    {
      "id": "CP-2026-0001",
      "type": "complaint",
      "title": "Broken streetlight",
      "latitude": 22.3152,
      "longitude": 73.1856,
      "status": "In Progress",
      "priority": "High"
    }
  ],
  "assets": [ ... ],
  "total_markers": 42,
  "filters_applied": { ... }
}
```

**Filters Supported:**
- `priority_filter` - Filter complaints by priority
- `status_filter` - Filter complaints by status
- `asset_type_filter` - Filter assets by type
- `ward_filter` - Filter both by ward
- `coordinates_only` - Only return items with valid coordinates

### 3. Complete End-to-End Testing

#### Test Coverage
- **Unit Tests:** 32 tests for Phase 1 endpoints (preserved)
- **Phase 2 Feature Tests:** 16 tests for new features
- **End-to-End Workflows:** 5 tests for complete complaint lifecycle
- **Total:** 53 passing tests

#### Tested Workflows
1. Complete complaint workflow: Create → Prioritize → Repair → Verify → Resolve
2. Multiple repair attempts with failure and success
3. Dashboard stats reflecting actual workflow data
4. Map data with mixed complaints and assets
5. Priority distribution with real data

### 4. Production-Ready Configuration

All Phase 1 features maintained with Phase 2 additions.

---

## Deployment Checklist

### Pre-Deployment

- [ ] All tests passing: `pytest tests/ -v`
- [ ] No security issues: Review `.env.example` for all required variables
- [ ] Database plan: Decide between SQLite (prototype) or PostgreSQL (production)
- [ ] Frontend CORS: Verify `ALLOWED_ORIGINS` matches frontend domains
- [ ] AI model: Prepare replacement for `MockPriorityEngine` if needed
- [ ] Logging: Configure log level for production (`LOG_LEVEL=info`)

### Database Setup

#### SQLite (Prototype/Development)
```bash
# Existing setup - database auto-creates on first run
DATABASE_URL=sqlite:///civicpulse.db
```

#### PostgreSQL (Production Recommended)
```bash
# Create database
createdb civicpulse_prod

# Set environment variable
DATABASE_URL=postgresql://user:password@localhost:5432/civicpulse_prod

# Run application - schema auto-creates via SQLModel
```

**Migration Steps:**
1. Test schema with PostgreSQL locally
2. Backup SQLite data if needed: `sqlite3 civicpulse.db ".dump" > backup.sql`
3. Update DATABASE_URL to PostgreSQL connection string
4. Start backend - SQLModel will create all tables automatically
5. Migrate data using scripts (if needed)

### Environment Variables

Required `.env` file for production:
```bash
# Core Configuration
DATABASE_URL=postgresql://user:pass@host:5432/db
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info

# API Configuration
APP_NAME=CivicPulse AI Backend
APP_VERSION=0.2.0

# CORS - Set to your production domain
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Server Configuration
ALLOW_CREDENTIALS=true

# AI Configuration (optional - for custom AI implementation)
AI_ENGINE_TYPE=production  # Replace MockPriorityEngine with actual implementation
```

### Docker Deployment (Optional)

Create `Dockerfile` for containerization:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY .env.example .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t civicpulse-backend:0.2.0 .
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e ALLOWED_ORIGINS=https://yourdomain.com \
  civicpulse-backend:0.2.0
```

### Health Check Endpoint

Use for load balancer / deployment verification:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "CivicPulse AI Backend"
}
```

### Startup Verification

1. **Start backend:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

2. **Verify API responds:**
   ```bash
   curl http://localhost:8000/
   curl http://localhost:8000/health
   ```

3. **Check Swagger docs:**
   ```
   http://localhost:8000/docs
   ```

4. **Test critical endpoints:**
   ```bash
   # Create complaint
   curl -X POST http://localhost:8000/api/complaints \
     -H "Content-Type: application/json" \
     -d '{"title":"Test","description":"Test issue","category":"Streetlight","location_text":"Test"}'
   
   # Get dashboard stats
   curl http://localhost:8000/api/dashboard/stats
   ```

---

## Production Recommendations

### 1. AI Priority Engine

**For Production:**
- Implement custom `PriorityEngine` subclass
- Replace `MockPriorityEngine` in initialization
- Add error handling for model unavailability
- Implement caching for repeated evaluations
- Log all priority evaluations for audit trail

**Example Custom Implementation:**
```python
from app.services.priority_engine import PriorityEngine, PriorityEvaluation

class ProductionAIPriorityEngine(PriorityEngine):
    def __init__(self, model_path: str):
        self.model = load_your_model(model_path)
        self.name = "ProductionAIPriorityEngine"
        self.model_version = "v1.0.0"
    
    def evaluate(self, complaint_data: dict) -> PriorityEvaluation:
        # Your actual AI logic here
        score = self.model.predict(complaint_data)
        return PriorityEvaluation(...)
    
    def health_check(self) -> bool:
        return self.model.is_loaded()

# In app/main.py during startup:
from app.services.priority_engine import set_evaluator
engine = ProductionAIPriorityEngine("/path/to/model.pkl")
set_evaluator(engine)
```

### 2. Database Optimization

For production with high complaint volume:
- Use PostgreSQL for concurrent access
- Create indexes on frequently queried fields:
  ```sql
  CREATE INDEX idx_complaint_status ON complaints(status);
  CREATE INDEX idx_complaint_priority ON complaints(priority);
  CREATE INDEX idx_complaint_ward ON complaints(ward);
  CREATE INDEX idx_complaint_created ON complaints(reported_at);
  CREATE INDEX idx_asset_type ON assets(asset_type);
  CREATE INDEX idx_asset_ward ON assets(ward);
  ```
- Implement connection pooling (PgBouncer)
- Set up automated backups

### 3. Monitoring & Logging

- **Application Logs:** Set `LOG_LEVEL=info` in production
- **Error Tracking:** Integrate Sentry or similar
- **Metrics:** Collect endpoint response times, error rates
- **Health Checks:** Monitor `/health` endpoint via load balancer
- **Database:** Monitor connection pool, query performance

### 4. Security

- **CORS:** Set explicitly to production domain only
- **HTTPS:** Use reverse proxy (Nginx) with SSL certificates
- **Database:** Use strong passwords, network isolation
- **API Keys:** Implement for external AI services
- **Input Validation:** All inputs validated via Pydantic (already done)
- **Logging:** Don't log sensitive data (PII, passwords)

### 5. Scaling

**Horizontal Scaling:**
```bash
# Run multiple instances behind load balancer
gunicorn app.main:app --workers 4 --bind 0.0.0.0:8000
gunicorn app.main:app --workers 4 --bind 0.0.0.0:8001
```

**Vertical Scaling:**
- Increase `--workers` parameter (CPUs × 2-4)
- Increase database connection pool
- Add Redis for caching (future enhancement)

### 6. Backup Strategy

```bash
# Daily PostgreSQL backup
pg_dump -U user -d civicpulse_prod > backup_$(date +%Y%m%d).sql

# Store offsite (S3, GCS, etc.)
aws s3 cp backup_*.sql s3://backups/civicpulse/

# Test restore procedure weekly
```

---

## Known Limitations & Future Work

### Phase 2 Limitations
- No AI model caching (each evaluation queries service)
- No file upload for repair evidence (URL reference only)
- No real-time notifications
- Dashboard stats query entire database (should add caching for large datasets)
- ID generation still in-memory (should use database sequences for production)

### Phase 3 Planned
- User authentication & role-based access control
- Real-time complaint updates via WebSockets
- File upload infrastructure (S3, GCS)
- Advanced search and filtering
- Bulk operations
- Performance optimizations
- Mobile app

---

## Rollback Procedure

If deployment fails:

1. **Check error logs:**
   ```bash
   journalctl -u civicpulse-backend -n 100
   ```

2. **Verify database:**
   ```bash
   # PostgreSQL
   psql -U user -d civicpulse_prod
   SELECT version();
   ```

3. **Restart with previous version:**
   ```bash
   systemctl stop civicpulse-backend
   # Revert code
   git checkout v0.1.0
   systemctl start civicpulse-backend
   ```

4. **Restore database backup if needed:**
   ```bash
   pg_restore -d civicpulse_prod backup_20260114.sql
   ```

---

## Testing After Deployment

```bash
# Run smoke tests
pytest tests/ -v -m smoke

# Verify API responses
./scripts/smoke_tests.sh

# Load test with real data
locust -f tests/load_test.py
```

---

## Support

- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **Error Logs:** Check application logs configured in `LOG_LEVEL`
- **Database Issues:** Verify PostgreSQL connection, check disk space

---

## Success Criteria

✅ Backend starts without errors  
✅ `/health` endpoint returns 200  
✅ Swagger docs load at `/docs`  
✅ Database schema created automatically  
✅ All 53 tests pass  
✅ Priority endpoints respond  
✅ Dashboard stats return data  
✅ Map data filters work correctly  
✅ CORS configured for frontend domain  
✅ Frontend can communicate with backend

---

**Deployment Date:** October 14, 2026  
**Phase 2 Version:** 0.2.0  
**Status:** Ready for Production

See `API_DOCUMENTATION.md` for complete endpoint reference.
