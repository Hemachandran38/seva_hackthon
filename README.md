# CivicPulse AI — Infrastructure Management Platform

A complete, production-ready system for managing public infrastructure complaints with AI-powered priority evaluation.

## 📁 Project Structure

```
c:\seva_hackthon\
├── frontend/                 ← React 18 + TypeScript web application
│   ├── src/
│   │   ├── pages/           # 6 main pages
│   │   ├── components/      # Reusable UI components
│   │   ├── services/        # API client
│   │   ├── types/           # TypeScript interfaces
│   │   └── styles/          # CSS files
│   ├── package.json
│   ├── vite.config.ts
│   └── index.html
│
├── backend/                  ← Python FastAPI backend
│   ├── app/
│   │   ├── main.py          # FastAPI app
│   │   ├── models/          # SQLModel schemas
│   │   ├── routers/         # API endpoints
│   │   ├── services/        # Business logic
│   │   └── database.py      # SQLite setup
│   ├── tests/               # 53 passing tests
│   ├── requirements.txt
│   └── civicpulse.db        # SQLite database
│
├── model/                    ← AI Models (scikit-learn)
│   └── civicpulse_priority_model.pkl
│
├── docs/                     ← Documentation
│   ├── START_HERE.md        # Read first (2 min)
│   ├── SETUP_COMPLETE.md    # Full overview
│   ├── API_DOCUMENTATION.md # API reference
│   ├── BACKEND_STRUCTURE.md # Backend guide
│   └── ... (8 more guides)
│
└── .archive/                 ← Legacy code (archived)
    └── civicpulse/          # Old project versions
```

## 🚀 Quick Start (5 Minutes)

### Terminal 1: Start Frontend
```bash
cd c:\seva_hackthon\frontend
npm install
npm run dev
```
Opens: **http://localhost:5173**

### Terminal 2: Start Backend
```bash
cd c:\seva_hackthon\backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 9000
```
Runs on: **http://127.0.0.1:9000**

### Browser
Open: **http://localhost:5173**

Try this:
1. Click "Report Issue"
2. Fill form (Title, Category, Description)
3. Click Submit
4. Copy generated ID
5. Click "Track Complaint"
6. Paste ID → See AI priority score!

## 📖 Documentation

**New users:** Start with `docs/START_HERE.md`

**Full setup:** Read `docs/SETUP_COMPLETE.md`

**For developers:**
- Frontend code: Read `docs/FRONTEND_STRUCTURE.md`
- Backend code: Read `docs/BACKEND_STRUCTURE.md`
- API endpoints: Read `docs/API_DOCUMENTATION.md`

**For deployment:** Read `docs/DEPLOYMENT_CHECKLIST.md`

**All docs:** See `docs/INDEX.md`

## ✅ What's Included

### Frontend (React + TypeScript + Vite)
- 6 pages (Home, Report, Track, Issues, Dashboard, 404)
- Interactive Leaflet map
- Real-time statistics
- Responsive design (desktop + mobile)
- ✅ Production ready

### Backend (Python FastAPI)
- 6 REST API endpoints (all working)
- SQLite database (auto-initialized)
- 53 passing tests
- AI model integration
- Full error handling
- ✅ Production ready

### AI Model (scikit-learn)
- Priority scoring (1-100)
- Automatic evaluation
- Graceful fallback
- ✅ Integrated

### Documentation
- 12 comprehensive guides
- Copy/paste setup commands
- Clear navigation
- ✅ Complete

## 🛠️ Commands

### Frontend
```bash
cd frontend
npm install      # Install dependencies
npm run dev      # Start dev server (5173)
npm run build    # Build for production
npm run preview  # Preview prod build
```

### Backend
```bash
cd backend
pip install -r requirements.txt              # Install deps
python -m uvicorn app.main:app --host 127.0.0.1 --port 9000  # Start
pytest           # Run all tests (53 passing)
```

## 📊 System Status

| Component | Status | Details |
|-----------|--------|---------|
| Frontend | ✅ Ready | React 18, Vite, TypeScript |
| Backend | ✅ Ready | 53 tests passing |
| AI Model | ✅ Integrated | scikit-learn |
| Database | ✅ Ready | SQLite auto-init |
| Documentation | ✅ Complete | 12 guides |
| Tests | ✅ All passing | 53/53 ✓ |

## 🔗 Key Directories

| Directory | Purpose | Status |
|-----------|---------|--------|
| `frontend/` | React web application | ✅ Production |
| `backend/` | Python FastAPI server | ✅ Production |
| `model/` | AI models (pickle files) | ✅ Integrated |
| `docs/` | Documentation | ✅ Complete |
| `.archive/` | Legacy code (old versions) | ⚠️ Archive |

## 🎯 Features

✅ Report infrastructure issues (forms with validation)
✅ AI-powered priority evaluation (1-100 scores)
✅ Interactive map visualization (Leaflet)
✅ Real-time dashboard (statistics, filters)
✅ Track complaints by ID (real-time status)
✅ Browse all issues (pagination, filters)
✅ Complete REST API (6 endpoints)
✅ Database persistence (SQLite)
✅ Comprehensive tests (53 passing)
✅ Responsive design (desktop + mobile)

## ❓ Need Help?

**New to this project?**
→ Read `docs/START_HERE.md` (2 minutes)

**Want to understand the system?**
→ Read `docs/SETUP_COMPLETE.md` (5 minutes)

**Ready to code?**
→ Read `docs/FRONTEND_STRUCTURE.md` or `docs/BACKEND_STRUCTURE.md`

**Ready to deploy?**
→ Read `docs/DEPLOYMENT_CHECKLIST.md`

**Can't find something?**
→ Check `docs/INDEX.md` (documentation index)

## 🚀 Next Steps

1. **Read:** `docs/START_HERE.md`
2. **Run:** Quick Start commands above
3. **Try:** Demo workflow (report → track → dashboard)
4. **Build:** `npm run build` (when ready)
5. **Deploy:** Upload to hosting service

## 📊 Project Stats

- **Frontend:** React 18, 6 pages, 20+ components, 2000+ lines
- **Backend:** Python FastAPI, 6 endpoints, 53 tests, 1500+ lines
- **AI Model:** scikit-learn, trained on infrastructure data
- **Database:** SQLite, auto-initialized with schema
- **Documentation:** 12 guides, 5000+ lines
- **Setup time:** 5 minutes
- **Test coverage:** 80%+

## 📝 License

CivicPulse AI - Seva Hackathon 2026

---

**Ready to go?** Read `docs/START_HERE.md` and follow the Quick Start above! 🚀
