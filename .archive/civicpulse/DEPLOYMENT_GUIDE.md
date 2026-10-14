# CivicPulse AI — Deployment Guide

## Local Development

### Prerequisites
- Python 3.10+
- pip
- Modern browser (Chrome, Edge, Firefox, Safari)
- Internet connection (for CDN: Leaflet, Esri tiles)

### Step 1: Backend Setup

```bash
cd civicpulse/backend
pip install -r requirements.txt
python migrate.py          # Apply Phase 4 schema changes
python seed_data.py        # Load 12 sample complaints
uvicorn main:app --reload --port 8000
```

Backend is now live at: `http://localhost:8000`  
Swagger UI: `http://localhost:8000/docs`

### Step 2: Frontend

Open in your browser:
```
file:///c:/seva_hackthon/civicpulse/frontend/index.html
```

Or serve locally (recommended to avoid CORS quirks):
```bash
cd civicpulse/frontend
python -m http.server 8080 --directory .
# Then open http://localhost:8080 in browser
```

---

## Production Deployment

### Backend Deployment (Example: Heroku)

1. **Create `Procfile`:**
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

2. **Create `runtime.txt`:**
```
python-3.11.0
```

3. **Add to `requirements.txt`:**
```
gunicorn==21.2.0
```

4. **Deploy:**
```bash
heroku login
heroku create civicpulse-api
git push heroku main
```

Backend will be at: `https://civicpulse-api.herokuapp.com`

### Frontend Deployment (Example: Vercel/Netlify)

1. **Update API URL in `frontend/script.js`:**
```javascript
const API_BASE_URL = "https://civicpulse-api.herokuapp.com";
```

2. **Deploy to Vercel:**
```bash
npm install -g vercel
vercel --prod
```

3. **Or Netlify:**
```bash
netlify deploy --prod --dir civicpulse/frontend
```

Frontend will be at: `https://civicpulse.vercel.app` (or Netlify URL)

---

## Environment Configuration

### Backend `.env` (do NOT commit to Git)

```
DATABASE_URL=postgresql+psycopg2://user:password@host:5432/civicpulse
API_PORT=8000
CORS_ORIGINS=https://civicpulse.vercel.app,https://civicpulse.netlify.app
UPLOAD_DIR=/tmp/civicpulse_uploads
```

Load in `main.py`:
```python
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///civicpulse.db")
API_PORT = int(os.getenv("API_PORT", 8000))
```

### Frontend `config.js` (dynamic API URL)

Create `civicpulse/frontend/config.js`:
```javascript
const CONFIG = {
  API_BASE: window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : 'https://civicpulse-api.herokuapp.com',
  DEMO_MODE: true,
};

export default CONFIG;
```

Update `script.js`:
```javascript
import CONFIG from './config.js';
const API_BASE_URL = CONFIG.API_BASE;
```

---

## Database Migration (SQLite → PostgreSQL)

For production, migrate to PostgreSQL:

1. **Dump SQLite:**
```bash
sqlite3 civicpulse.db .dump > dump.sql
```

2. **Create PostgreSQL database:**
```bash
psql -U postgres
CREATE DATABASE civicpulse;
\q
```

3. **Load into PostgreSQL:**
```bash
psql -U postgres -d civicpulse < dump.sql
```

4. **Update connection string:**
```python
DATABASE_URL = "postgresql+psycopg2://postgres:password@localhost:5432/civicpulse"
```

---

## Docker Deployment (Optional)

### Dockerfile (Backend)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/ .
RUN pip install -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: sqlite:///civicpulse.db
  frontend:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./frontend:/usr/share/nginx/html
```

Run:
```bash
docker-compose up -d
```

---

## CORS Configuration

If frontend and backend are on different origins:

**Backend (`main.py`):**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://civicpulse.vercel.app",
        "https://civicpulse.netlify.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Health Checks

**Backend health:**
```bash
curl http://localhost:8000/health
# Expected: {"status":"ok","service":"CivicPulse AI API v4"}
```

**Frontend loads:**
```bash
curl -I http://localhost:8080/index.html
# Expected: HTTP/1.1 200 OK
```

---

## Monitoring & Logging

### Backend Logs

```bash
# Heroku
heroku logs --tail

# Docker
docker logs civicpulse-backend
```

### Frontend Analytics (Optional)

Add Google Analytics or Sentry:
```javascript
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_ID');
</script>
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| CORS error | Check backend CORS origins, use proxy or deployment on same domain |
| 404 on complaint endpoints | Verify migration ran, seed data was loaded |
| Map doesn't load | Check browser console, CDN URLs are accessible (Leaflet, Esri) |
| API returns 500 | Check backend logs, database connection string |
| Filters don't work | Verify API query parameters are sent correctly |
| Markers not updating | Refresh page, check API response structure |

---

## Backup & Recovery

### Database Backup

```bash
# SQLite
cp civicpulse.db civicpulse_backup_$(date +%Y%m%d).db

# PostgreSQL
pg_dump civicpulse > civicpulse_$(date +%Y%m%d).sql
```

### Restore

```bash
# PostgreSQL
psql civicpulse < civicpulse_20261013.sql
```

---

## Security Checklist

- [ ] No API keys, database passwords in frontend code
- [ ] Use HTTPS in production (automatic with Vercel/Heroku)
- [ ] Validate all user inputs on backend
- [ ] Sanitize file uploads
- [ ] Rate limit API endpoints (optional)
- [ ] Rotate database credentials regularly
- [ ] Enable CORS only for trusted origins
- [ ] No sensitive data in demo complaints
- [ ] Keep dependencies up-to-date

---

## Support

For issues or questions:
1. Check the README.md
2. Review test results in TEST_CHECKLIST.md
3. Inspect browser console (F12)
4. Check backend logs (`http://localhost:8000/docs` for endpoint testing)
5. Open an issue on GitHub with logs and reproduction steps

