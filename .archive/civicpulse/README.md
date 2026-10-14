# CivicPulse AI — Public Infrastructure Fault Monitoring

> **AI-assisted maintenance prioritization and repair tracking for municipal infrastructure**

![Status](https://img.shields.io/badge/Phase-4_Complete-green)
![Demo](https://img.shields.io/badge/Demo_Ready-Yes-brightgreen)
![License](https://img.shields.io/badge/License-MIT-blue)

---

## 🎯 Overview

CivicPulse AI is a civic-tech platform that empowers municipal authorities to manage public infrastructure maintenance through intelligent prioritization and end-to-end repair tracking. Citizens report infrastructure faults (e.g., broken streetlights), the system calculates transparent priority scores using configurable AI logic, and authorised teams track repairs from assignment through verified closure.

**Key Capabilities:**
- 🗺️ **Interactive map** displaying fault locations, priorities, and status
- 🤖 **AI-driven prioritization** based on severity, recurrence, pending time, and public impact
- 📋 **Lifecycle tracking** from initial report through verification and closure
- 📊 **Transparent audit logs** of all maintenance actions
- 📱 **Responsive design** for desktop, tablet, and mobile

**All data shown is sample/demo data only.** CivicPulse AI is a proof-of-concept prototype not intended for real-world deployment without validation and adaptation.

---

## 🚀 Quick Start (5 minutes)

### Prerequisites
- Python 3.10+
- pip
- Modern browser (Chrome, Edge, Firefox)
- Internet connection (for CDN: Leaflet.js, Esri tiles)

### Run Locally

#### 1. Start Backend
```bash
cd civicpulse/backend
pip install -r requirements.txt
python migrate.py          # Apply database schema
python seed_data.py        # Load 12 sample complaints
uvicorn main:app --reload --port 8000
```
Backend is live at: `http://localhost:8000`  
API Docs (Swagger): `http://localhost:8000/docs`

#### 2. Open Frontend
```bash
# Option A: Direct file (simple but may have CORS quirks)
open civicpulse/frontend/index.html

# Option B: Local web server (recommended)
cd civicpulse/frontend
python -m http.server 8080
# Then open http://localhost:8080 in browser
```

---

## 📋 Features

### Phase 1: Interactive Map
- Display infrastructure complaints as markers on Leaflet map
- Priority-based colors: Red (high) → Orange (medium) → Blue (low) → Green (resolved)
- Filter by priority and status
- Search by asset ID or area name
- Responsive design for all screen sizes

### Phase 2: Backend Integration
- RESTful API endpoints for assets, complaints, and dashboards
- Status updates with real-time marker refresh
- Dashboard metrics: total assets, open complaints, high-priority, resolved
- Sample data: 12 streetlight complaints across Coimbatore

### Phase 3: AI Priority Scoring
- Transparent scoring formula combining 4 factors:
  - Severity (40% weight)
  - Recurrence count (25%)
  - Days pending (20%)
  - Public service impact (15%)
- Explainable reasoning: each complaint shows which factors drove its score
- Recurrence detection and flagging
- Configurable weights via API

### Phase 4: Repair Lifecycle & Verification
- 7-state workflow: reported → under_inspection → assigned → in_progress → awaiting_verification → resolved
- Team assignment and tracking
- Repair evidence submission (notes + optional images)
- Mandatory verification by authorised reviewer
- Immutable audit trail of all actions

---

## 🏗️ Architecture

```
┌──────────────────┐
│   Frontend       │ HTML/CSS/JS + Leaflet.js
│  (Interactive    │ Displays map, filters,
│   Map)           │ status updates
└────────┬─────────┘
         │ fetch()
         ↓
┌──────────────────┐
│   FastAPI        │ REST endpoints:
│   Backend        │ /api/assets
│                  │ /api/complaints
│   Endpoints:     │ /api/priority/recommendations
│   6 main +       │ /api/complaints/{id}/assign
│   6 Phase 4      │ /api/complaints/{id}/verify
│   + AI scoring   │ /api/repair/pending
└────────┬─────────┘
         │ SQLAlchemy
         ↓
┌──────────────────┐
│   SQLite (dev)   │ Tables:
│   PostgreSQL(prd)│ - assets
│                  │ - complaints (+ lifecycle fields)
│                  │ - repair_records
│                  │ - audit_log
└──────────────────┘

┌──────────────────┐
│   AI Priority    │ Scoring engine:
│   Engine         │ - Severity normalisation
│                  │ - Recurrence detection
│                  │ - Pending time calculation
│                  │ - Public impact assessment
└──────────────────┘
```

---

## 📚 API Reference

### Assets
```
GET /api/assets                    List all assets
GET /api/assets/{asset_id}         Get one asset with complaints
GET /api/assets/{asset_id}/history Full complaint history
```

### Complaints
```
GET /api/complaints                List with filters (priority, status, area_name)
GET /api/complaints/{id}           Get one complaint
PATCH /api/complaints/{id}/status  Update status (legacy)
```

### AI Priority (Phase 3)
```
GET /api/priority/recommendations  All complaints AI-scored
POST /api/priority/recalculate     Re-score with custom weights
```

### Lifecycle (Phase 4)
```
GET /api/complaints/{id}/detail    Full lifecycle detail + audit
POST /api/complaints/{id}/assign   Assign to team
POST /api/complaints/{id}/transition Move between states
POST /api/complaints/{id}/repair   Submit repair notes
POST /api/complaints/{id}/repair/upload Upload evidence image
POST /api/complaints/{id}/verify   Approve/reject repair
POST /api/complaints/{id}/reopen   Reopen resolved complaint
GET /api/complaints/{id}/audit     Audit trail
GET /api/repair/pending            Open assignments
GET /api/repair/overdue            Overdue (> N days)
```

### Dashboard
```
GET /api/dashboard/stats           Summary metrics + top priorities
```

**Full documentation:** `http://localhost:8000/docs` (Swagger UI)

---

## 🧪 Testing

### Run Test Checklist
See `TEST_CHECKLIST.md` for comprehensive manual testing steps covering:
- Map loading and responsiveness
- Marker display and filtering
- API integration
- AI scoring and explanations
- Lifecycle state transitions
- Error handling
- End-to-end workflow

### Sample Tests
```bash
# Check backend health
curl http://localhost:8000/health

# List all complaints
curl http://localhost:8000/api/complaints

# Get priority recommendations
curl http://localhost:8000/api/priority/recommendations

# Check dashboard metrics
curl http://localhost:8000/api/dashboard/stats

# Assign complaint
curl -X POST http://localhost:8000/api/complaints/1/assign \
  -H "Content-Type: application/json" \
  -d '{"assigned_team":"Team A","assigned_by":"admin"}'
```

---

## 📖 Documentation

| Document | Purpose |
|---|---|
| `README.md` (this file) | Overview and quick start |
| `DEPLOYMENT_GUIDE.md` | Production setup, Docker, migrations |
| `DEMO_SCRIPT.md` | Hackathon presentation walkthrough |
| `TEST_CHECKLIST.md` | Complete manual test suite |
| `/api/docs` | Swagger UI (when backend running) |

---

## 🎬 Demo & Hackathon

### Quick Demo (5 minutes)

1. **Start backend:** `uvicorn main:app --reload --port 8000`
2. **Open frontend:** `civicpulse/frontend/index.html`
3. **Show the map:** 12 markers across Coimbatore
4. **Click a red marker:** Pop details, AI explanation, factors
5. **Apply filters:** Show high-priority only
6. **Explain lifecycle:** Show assigned team, lifecycle state
7. **Mention audit log:** Every action tracked

See `DEMO_SCRIPT.md` for full talking points and Q&A responses.

### Known Limitations

- **Demo data only:** All 12 complaints are sample data, not real citizen reports
- **No real citizen interface:** Data is pre-seeded; no web form to submit new complaints
- **SQLite in development:** No concurrency; PostgreSQL required for production
- **File uploads to local disk:** No cloud storage integration
- **AI model not trained:** Priority scores use transparent rule-based logic, not machine learning
- **No authentication:** No user login or role-based access control yet

---

## 🔧 Deployment

### Heroku (Recommended for demo)

```bash
cd civicpulse/backend
heroku create civicpulse-api
echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile
git push heroku main
# Backend deployed to: https://civicpulse-api.herokuapp.com
```

### Vercel (Frontend)

```bash
npm i -g vercel
cd civicpulse/frontend
vercel --prod
# Frontend deployed to: https://civicpulse.vercel.app
```

Then update `frontend/script.js`:
```javascript
const API_BASE_URL = "https://civicpulse-api.herokuapp.com";
```

See `DEPLOYMENT_GUIDE.md` for detailed steps.

---

## 🛠️ Development

### Project Structure
```
civicpulse/
├── frontend/
│   ├── index.html      Main dashboard
│   ├── style.css       Responsive design (Phases 1–4)
│   ├── script.js       Map, filters, API integration
│   └── config.js       Environment-specific settings
├── backend/
│   ├── main.py         FastAPI app + all 12 endpoints
│   ├── models.py       SQLAlchemy ORM (assets, complaints, repairs, audit)
│   ├── schemas.py      Pydantic validation models
│   ├── database.py     SQLAlchemy session management
│   ├── lifecycle.py    State machine for repair workflow
│   ├── priority_engine.py AI scoring (Phase 3)
│   ├── seed_data.py    Demo data loader
│   ├── migrate.py      DB schema migrations
│   ├── requirements.txt Dependencies
│   ├── civicpulse.db   SQLite (dev only)
│   └── uploads/        Repair evidence images
├── README.md           This file
├── DEMO_SCRIPT.md      Hackathon walkthrough
├── DEPLOYMENT_GUIDE.md Production setup
└── TEST_CHECKLIST.md   Manual test suite
```

### Tech Stack
- **Frontend:** HTML5, CSS3, Vanilla JavaScript, Leaflet.js, Esri/OpenStreetMap tiles
- **Backend:** Python, FastAPI, SQLAlchemy, SQLite/PostgreSQL
- **Deployment:** Heroku (backend), Vercel/Netlify (frontend)
- **Version Control:** Git, GitHub

### Running Tests
```bash
# Check backend starts without errors
cd backend && python -c "import main"

# Run sample data loader
python seed_data.py

# Verify 12 complaints loaded
curl http://localhost:8000/api/complaints | python -m json.tool | head -20
```

---

## ❓ FAQ

**Q: Is this a real municipal system?**  
No. CivicPulse AI is a proof-of-concept prototype using sample data to demonstrate the workflow. Deployment requires municipal validation, real citizen reporting channels, and integration with existing systems.

**Q: How does the AI work?**  
The AI priority score combines 4 transparent factors (severity, recurrence, pending time, public impact) with configurable weights (40/25/20/15%). It's rule-based, not machine learning. Judges can see exactly why each complaint got its score.

**Q: Can I modify the AI weights?**  
Yes. Call `POST /api/priority/recalculate` with custom weights (must sum to 1.0). The system re-scores all open complaints and persists the result.

**Q: What happens after a repair is verified?**  
A verified repair sets the complaint to "resolved" and the marker turns green on the map. The audit log records the verifier, timestamp, and notes. If the issue recurs, the complaint can be reopened.

**Q: Is the demo data confidential?**  
No. All 12 sample complaints are entirely fictional. None represent real infrastructure or citizens.

**Q: Can I deploy this?**  
Yes, with caveats: (1) This is an educational prototype, not production-ready; (2) Add authentication and role-based access; (3) Replace SQLite with PostgreSQL; (4) Integrate with real citizen complaint channels; (5) Validate with municipal authorities.

---

## 📝 License

MIT License. See LICENSE file.

---

## 👥 Team

- **Member 1:** Frontend reporting interface
- **Member 2:** Backend APIs, lifecycle, audit logs
- **Member 3:** AI priority scoring and explanations
- **Member 4 (Maps & Integration Lead):** Interactive map, API integration, testing, demo

---

## 🎯 Next Steps

1. **Test:** Run through `TEST_CHECKLIST.md`
2. **Deploy:** Follow `DEPLOYMENT_GUIDE.md`
3. **Demo:** Use `DEMO_SCRIPT.md` for hackathon presentation
4. **Iterate:** Gather feedback, fix bugs, improve UX

---

## 📞 Support

- Backend API docs: `http://localhost:8000/docs` (when running)
- GitHub Issues: [Create an issue](https://github.com/your-org/civicpulse/issues)
- Email: support@civicpulse.dev (demo only)

---

**Last Updated:** 2026-10-13  
**Version:** 4.0.0 (Final Phase Complete)  
**Status:** ✅ Demo Ready

