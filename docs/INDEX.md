# CivicPulse AI — Documentation Index

**Navigate the complete CivicPulse AI system documentation.**

---

## 🚀 START HERE

### For Everyone
1. **[SETUP_COMPLETE.md](./SETUP_COMPLETE.md)** ⭐ **READ FIRST**
   - System overview
   - What's installed
   - Quick start (5 minutes)
   - Deployment paths
   - Support resources

2. **[PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md)**
   - Executive summary
   - Technology stack
   - Key features
   - Demo script
   - Success criteria

---

## 👨‍💻 DEVELOPER GUIDES

### Frontend (React)

**Setup & Quick Start**
- **[frontend/QUICK_START.md](./frontend/QUICK_START.md)** — 5-minute setup
- **[frontend/README.md](./frontend/README.md)** — User guide & features

**Architecture & Code**
- **[frontend/UNIFIED_FRONTEND_GUIDE.md](./frontend/UNIFIED_FRONTEND_GUIDE.md)** — Architecture, design decisions, data flow
- **[frontend/FRONTEND_STRUCTURE.md](./frontend/FRONTEND_STRUCTURE.md)** — Code organization, navigation, examples

**Inside the Code**
- `src/App.tsx` — Route definitions
- `src/pages/` — Page components (HomePage, ReportIssuePage, etc.)
- `src/components/` — Reusable UI components
- `src/services/api.ts` — Backend API client (all API calls)
- `src/types/` — TypeScript interfaces
- `src/styles/` — CSS & design tokens

### Backend (FastAPI)

**Setup & Running**
- **[civicpulse-backend/README.md](./civicpulse-backend/README.md)** — Backend user guide
- **[civicpulse-backend/SETUP_AND_RUN.md](./civicpulse-backend/SETUP_AND_RUN.md)** — Deployment guide

**Architecture & Code**
- **[civicpulse-backend/BACKEND_STRUCTURE.md](./civicpulse-backend/BACKEND_STRUCTURE.md)** — Code organization, request flows, patterns
- **[civicpulse-backend/API_DOCUMENTATION.md](./civicpulse-backend/API_DOCUMENTATION.md)** — Complete API reference

**Inside the Code**
- `app/main.py` — FastAPI app, routes, middleware
- `app/models.py` — SQLModel schemas
- `app/database.py` — Database configuration
- `app/services/ai_model_service.py` — AI model loader & inference
- `app/services/priority_engine.py` — Priority evaluation (AI + mock)
- `app/routers/complaints.py` — Complaint endpoints
- `app/routers/dashboard.py` — Dashboard endpoints
- `tests/` — 53 passing tests

### AI Model

**Model Details**
- **File:** `c:\seva_hackthon\model\civicpulse_priority_model.pkl`
- **Type:** scikit-learn Logistic Regression
- **Features:** Category, repeat count, description length, location, time
- **Output:** Priority score (1-100)
- **Fallback:** Mock engine if model unavailable

---

## 🧪 TESTING & VERIFICATION

- **[DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)** — Complete testing checklist
  - Pre-flight checks
  - Functional testing
  - Performance testing
  - Cross-browser testing
  - Security checklist
  - Production build verification

### Running Tests

**Backend tests:**
```bash
cd c:\seva_hackthon\civicpulse-backend
pytest
```
✅ 53 tests passing

**Manual testing:**
- Report issue → Track complaint → View dashboard
- Test all filters and functionality
- Check API endpoints with curl

---

## 📊 SYSTEM OVERVIEW

### Architecture
```
User → Frontend (React) → Backend (FastAPI) → Database (SQLite)
                              ↓
                         AI Model (scikit-learn)
                              ↓
                         Priority Evaluation
```

### Data Flow
1. User reports issue (frontend form)
2. Frontend sends POST to `/api/complaints`
3. Backend validates and stores in database
4. Backend runs AI model for priority
5. Response with ID and priority returned
6. Frontend displays success
7. User can track or view dashboard

### Key Endpoints
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/complaints` | Create complaint + AI eval |
| GET | `/api/complaints` | List all complaints |
| GET | `/api/complaints/{id}` | Get complaint details |
| PUT | `/api/complaints/{id}/status` | Update status |
| GET | `/api/dashboard/stats` | Dashboard stats |
| GET | `/api/dashboard/map-data` | Map data |

---

## 🎯 QUICK REFERENCE

### Frontend Commands
```bash
cd c:\seva_hackthon\frontend

npm install                 # Install dependencies
npm run dev                 # Start dev server (5173)
npm run build               # Build for production
npm run preview             # Preview production build
npm run typecheck           # Check TypeScript
```

### Backend Commands
```bash
cd c:\seva_hackthon\civicpulse-backend

pip install -r requirements.txt                           # Install dependencies
python -m uvicorn app.main:app --host 127.0.0.1 --port 9000  # Start server
pytest                      # Run all tests
pytest -v                   # Verbose output
pytest -k "test_name"       # Run specific test
```

### Environment Setup

**Frontend (.env.local):**
```env
VITE_API_BASE_URL=http://127.0.0.1:9000
```

**Backend (.env):**
```env
DATABASE_URL=sqlite:///civicpulse.db
FRONTEND_URL=http://localhost:5173
```

---

## 📁 PROJECT STRUCTURE

```
c:\seva_hackthon/
├── frontend/                          ✅ UNIFIED REACT FRONTEND
│   ├── src/                           React source code
│   ├── package.json                   Dependencies
│   ├── README.md                      Frontend guide
│   ├── QUICK_START.md                 5-minute setup
│   ├── UNIFIED_FRONTEND_GUIDE.md      Architecture
│   └── FRONTEND_STRUCTURE.md          Code navigation
│
├── civicpulse-backend/                ✅ FASTAPI BACKEND
│   ├── app/                           Python source code
│   ├── tests/                         53 passing tests
│   ├── requirements.txt               Dependencies
│   ├── civicpulse.db                  SQLite database
│   ├── README.md                      Backend guide
│   ├── BACKEND_STRUCTURE.md           Code organization
│   ├── API_DOCUMENTATION.md           API reference
│   └── SETUP_AND_RUN.md               Deployment
│
├── model/                             ✅ AI MODEL
│   ├── civicpulse_priority_model.pkl  Trained model
│   └── civicpulse_resolution_model.pkl
│
├── civicpulse/                        📦 LEGACY (archive)
│   ├── frontend/
│   ├── frontend-react/
│   └── backend/
│
├── SETUP_COMPLETE.md                  ⭐ System overview
├── PROJECT_SUMMARY.md                 Executive summary
├── DEPLOYMENT_CHECKLIST.md            Testing checklist
├── INDEX.md                           This file
└── TEST_CHECKLIST.md                  Old testing guide
```

---

## 🎨 FEATURES

### ✅ Pages

| Page | Route | Features |
|------|-------|----------|
| Home | `/` | Landing page, navigation |
| Report Issue | `/report` | Form submission, AI eval |
| Track Complaint | `/track` | Search by ID, view status |
| All Issues | `/issues` | Paginated list, filters |
| Dashboard | `/dashboard` | Map, stats, filters, analytics |

### ✅ API Features

| Feature | Endpoint | Status |
|---------|----------|--------|
| Create Complaint | POST /api/complaints | ✅ With AI eval |
| List Complaints | GET /api/complaints | ✅ Paginated |
| Get Details | GET /api/complaints/{id} | ✅ Full data |
| Update Status | PUT /api/complaints/{id}/status | ✅ Tracked |
| Dashboard Stats | GET /api/dashboard/stats | ✅ Real-time |
| Map Data | GET /api/dashboard/map-data | ✅ With filters |

---

## 🚀 DEPLOYMENT

### Development (Local)
```bash
# Terminal 1
cd frontend && npm install && npm run dev

# Terminal 2
cd civicpulse-backend && pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 9000

# Browser
http://localhost:5173
```

### Production
```bash
# Build frontend
cd frontend && npm run build
# Upload dist/ to Netlify, Vercel, AWS S3, etc.

# Backend options:
# 1. Docker: Build Dockerfile and deploy to cloud
# 2. PaaS: Deploy to Heroku, AWS Lambda, Google Cloud Run
# 3. VPS: Deploy to server with systemd/nginx
```

### Environment Variables

**Frontend production:**
```env
VITE_API_BASE_URL=https://api.civicpulse.io
```

**Backend production:**
```env
DATABASE_URL=postgresql://user:pass@host/db
FRONTEND_URL=https://civicpulse.io
```

---

## 🧠 AI MODEL

### How It Works
1. **Input:** Complaint data (category, description, location, time)
2. **Feature Extraction:** Convert to numerical features
3. **Prediction:** scikit-learn model scores priority
4. **Output:** Priority score (1-100)

### Features Used
- `category_encoded` (0-4)
- `repeat_complaint_count` (0+)
- `description_length` (characters)
- `has_coordinates` (0 or 1)
- `hour_reported` (0-23)

### Priority Mapping
- 80-100: High Priority (red) 🔴
- 50-79: Medium Priority (orange) 🟠
- 1-49: Low Priority (blue) 🔵
- 0: Resolved (green) 🟢

### Fallback
- If model fails to load, uses mock engine
- Still returns valid priority scores
- System gracefully degrades

---

## 📚 LEARNING RESOURCES

### Understand Frontend
1. Read `frontend/QUICK_START.md` (5 min)
2. Open `frontend/README.md` (understand architecture)
3. Explore `frontend/src/` (understand code)
4. Read `frontend/FRONTEND_STRUCTURE.md` (detailed guide)

### Understand Backend
1. Read `civicpulse-backend/README.md` (overview)
2. Check `civicpulse-backend/API_DOCUMENTATION.md` (endpoints)
3. Explore `civicpulse-backend/app/` (code)
4. Read `civicpulse-backend/BACKEND_STRUCTURE.md` (detailed guide)

### Understand AI
1. Check model file: `model/civicpulse_priority_model.pkl`
2. Review feature extraction in `app/services/ai_model_service.py`
3. Check priority engine in `app/services/priority_engine.py`

### Run Locally
1. `cd frontend && npm install && npm run dev`
2. `cd civicpulse-backend && pip install -r requirements.txt && python -m uvicorn app.main:app --host 127.0.0.1 --port 9000`
3. Visit `http://localhost:5173`

### Test Everything
1. `cd civicpulse-backend && pytest` (run all tests)
2. Try demo workflow (report → track → dashboard)
3. Check API with curl or Postman

---

## ❓ TROUBLESHOOTING

### Can't Connect to Backend
```bash
# Verify backend running
curl http://127.0.0.1:9000/api/complaints

# If fails, start backend:
cd civicpulse-backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 9000
```

### Frontend Won't Load
```bash
# Check npm installed
node --version
npm --version

# Reinstall dependencies
cd frontend && rm -r node_modules && npm install

# Start dev server
npm run dev
```

### Tests Failing
```bash
# Check Python installed
python --version

# Reinstall requirements
pip install -r requirements.txt --force-reinstall

# Run tests
pytest -v
```

### Map Won't Display
- Check internet connection (needs CDN)
- Browser console (F12 → Console) for errors
- Network tab (F12 → Network) for Leaflet CSS/JS

---

## 🔗 USEFUL LINKS

### Documentation
- [SETUP_COMPLETE.md](./SETUP_COMPLETE.md) — Overview
- [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md) — Executive summary
- [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) — Testing

### Frontend Docs
- [README.md](./frontend/README.md) — Frontend guide
- [QUICK_START.md](./frontend/QUICK_START.md) — 5-min setup
- [UNIFIED_FRONTEND_GUIDE.md](./frontend/UNIFIED_FRONTEND_GUIDE.md) — Architecture
- [FRONTEND_STRUCTURE.md](./frontend/FRONTEND_STRUCTURE.md) — Code guide

### Backend Docs
- [README.md](./civicpulse-backend/README.md) — Backend guide
- [BACKEND_STRUCTURE.md](./civicpulse-backend/BACKEND_STRUCTURE.md) — Code guide
- [API_DOCUMENTATION.md](./civicpulse-backend/API_DOCUMENTATION.md) — API reference

---

## 💡 QUICK TIPS

### Development
- Edit frontend code and save → Hot reload on 5173
- Edit backend code → Restart `python -m uvicorn` to see changes
- Use `F12` DevTools for debugging frontend
- Use `curl` or Postman for testing API

### Debugging
- Frontend: Browser console (F12 → Console)
- Backend: Terminal output / logs
- Database: Can query SQLite directly
- Network: F12 → Network tab

### Performance
- Frontend: Vite with code splitting
- Backend: SQLite for demo, PostgreSQL for scale
- Caching: Can add Redis for sessions
- CDN: Leaflet tiles cached automatically

### Security
- Frontend: No secrets in code
- Backend: .env files for config
- Database: SQLite (upgrade to PostgreSQL with encryption)
- CORS: Configured for localhost:5173

---

## 📋 CHECKLIST

### Before Demo
- [ ] Frontend running on 5173
- [ ] Backend running on 9000
- [ ] Can submit complaint
- [ ] Can track complaint
- [ ] Dashboard loads with map
- [ ] AI priority showing

### Before Deployment
- [ ] All tests pass (pytest)
- [ ] Frontend builds (npm run build)
- [ ] No console errors (F12)
- [ ] API endpoints working (curl)
- [ ] Environment variables set
- [ ] Database initialized

### Before Production
- [ ] HTTPS/SSL configured
- [ ] Database backed up
- [ ] Backend and frontend on same domain (or CORS updated)
- [ ] Error logging set up
- [ ] Monitoring configured
- [ ] Rate limiting enabled

---

## 📞 SUPPORT

### Getting Help
1. **Check documentation** — Use INDEX above
2. **Check code comments** — Developers add helpful comments
3. **Check git history** — `git log` shows what changed
4. **Debug with tools** — Browser DevTools, curl, Postman
5. **Review examples** — Code shows patterns to follow

### Common Issues
- Backend not running? Start in Terminal 2
- Frontend won't connect? Check VITE_API_BASE_URL
- Map won't load? Check internet connection
- Tests failing? Run `pip install -r requirements.txt`
- npm not found? Install Node.js 18+

---

**🎯 Ready to dive in?**

1. **Start here:** [SETUP_COMPLETE.md](./SETUP_COMPLETE.md)
2. **Quick setup:** [frontend/QUICK_START.md](./frontend/QUICK_START.md)
3. **Understand code:** [frontend/FRONTEND_STRUCTURE.md](./frontend/FRONTEND_STRUCTURE.md) or [civicpulse-backend/BACKEND_STRUCTURE.md](./civicpulse-backend/BACKEND_STRUCTURE.md)
4. **Run demo:** Follow QUICK_START walkthrough
5. **Deploy:** Build and upload to hosting

---

**CivicPulse AI — Making Infrastructure Management Intelligent 🚀**

Last Updated: October 2026
