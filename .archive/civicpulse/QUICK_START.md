# CivicPulse AI — Quick Start Guide

## 5-Minute Setup & Demo

### Prerequisites

- **Python 3.9+** installed
- **pip** available
- Windows, macOS, or Linux

### Step 1: Install Dependencies

```bash
cd civicpulse/backend
pip install -r requirements.txt
```

### Step 2: Start the Backend API

From `civicpulse/backend/`:

```bash
uvicorn main:app --reload --port 8000
```

You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

Open http://localhost:8000/docs in your browser to see interactive Swagger documentation.

### Step 3: Start the Frontend Server

In a new terminal, from `civicpulse/frontend/`:

**Using Python:**
```bash
python -m http.server 5000
```

Or **using npm** (if you have Node.js):
```bash
npx http-server -p 5000
```

You should see:

```
Serving HTTP on http://127.0.0.1:5000
```

### Step 4: Open the Map

Go to **http://localhost:5000** in your browser.

You should see:
- Interactive map with 12 sample streetlight markers
- Markers colored by AI priority (red=high, orange=medium, blue=low, green=resolved)
- Left sidebar with dashboard metrics, filters, search
- Top priority complaints list

---

## Quick Demo Walkthrough (2 minutes)

### 1. Explore the Map

- Zoom in/out using scroll wheel
- Click on any marker to open a popup
- Popup shows AI score, issue description, and suggested action

### 2. View Lifecycle & Audit

- In the popup, click **"View Lifecycle & Audit →"** button
- Modal opens showing:
  - **Assignment** info (team, dates, notes)
  - **Verification** status (approved/rejected)
  - **Repair Records** with evidence images
  - **Audit Log** with full action history
- Close modal with ✕ button

### 3. Test Filters

- In the left sidebar, select **Priority: High** to show only high-priority complaints
- Select **Status: Open** to show only open issues
- Click **Reset Filters** to restore all

### 4. Search

- Type an asset ID (e.g., `SL-001`) in the search box
- Press Enter or click 🔍
- Map pans to that asset and opens its popup

### 5. Update Status

- In any popup, change the status dropdown
- Click to update (e.g., Open → In Progress)
- Toast notification confirms the change
- Dashboard metrics update automatically

---

## What Each Phase Shows

### Phase 1: Map & Markers
- Interactive Leaflet map centered on Coimbatore
- 12 streetlight assets with real coordinates
- Recurring fault indicators (purple ring ⟳)

### Phase 2: Backend API & Status Management
- 12 REST API endpoints for complaints
- Status updates (open, in-progress, resolved)
- Full complaint history

### Phase 3: AI Priority Scoring
- Machine learning priority calculation (1–100 scale)
- Explainable AI factors (recurrence, pending days, severity, public impact)
- Risk scoring shown in popup

### Phase 4: Repair Lifecycle & Verification
- **7-state workflow**: reported → under_inspection → assigned → in_progress → awaiting_verification → resolved (+ reopen)
- **Assignment** tracking: which team, when, by whom
- **Repair records**: notes, evidence photos, verification status
- **Audit log**: immutable action trail with timestamps
- **Verification**: approve/reject repairs with feedback

---

## API Endpoints (Quick Reference)

### Asset Management
- `GET /api/assets` — List all assets
- `GET /api/assets/{asset_id}` — Get one asset
- `GET /api/assets/{asset_id}/history` — Full complaint history

### Complaints (Phase 1–3)
- `GET /api/complaints` — List with filters
- `PATCH /api/complaints/{id}/status` — Update status (legacy)

### Lifecycle & Verification (Phase 4)
- `GET /api/complaints/{id}/detail` — Full lifecycle detail + audit
- `POST /api/complaints/{id}/assign` — Assign to team
- `POST /api/complaints/{id}/transition` — Change lifecycle state
- `POST /api/complaints/{id}/repair` — Submit repair notes
- `POST /api/complaints/{id}/repair/upload` — Upload evidence image
- `POST /api/complaints/{id}/verify` — Approve/reject repair
- `POST /api/complaints/{id}/reopen` — Reopen resolved complaint
- `GET /api/complaints/{id}/audit` — View audit trail

### AI Scoring
- `GET /api/priority/recommendations` — AI-ranked complaints
- `POST /api/priority/recalculate` — Re-run scoring

### Dashboard
- `GET /api/dashboard/stats` — Overall metrics

---

## Key Features

✅ **7-state repair lifecycle** enforces authorization (only verifier can mark resolved)  
✅ **Immutable audit log** tracks every action with actor & timestamp  
✅ **Evidence photos** can be uploaded during repair submission  
✅ **Explainable AI** shows factors contributing to priority score  
✅ **Recurring fault detection** automatically identifies repeat issues  
✅ **Responsive UI** works on desktop and mobile  
✅ **SQLite database** with automatic migrations (11 new columns in Phase 4)  

---

## Troubleshooting

### "API Offline" banner appears

**Backend not running?**
- Check terminal where you ran `uvicorn`
- Ensure http://localhost:8000/health returns 200
- Restart: `uvicorn main:app --reload --port 8000`

**Wrong port?**
- Frontend hardcodes `http://localhost:8000` in `script.js`
- Change `API_BASE_URL` if backend is on different port

### Markers not appearing

- Check browser console (F12 → Console)
- Ensure `/api/priority/recommendations` returns data
- Try refreshing the page

### Lifecycle modal is empty

- Check that backend returned data from `/api/complaints/{id}/detail`
- Verify audit_logs array is not empty
- Check browser console for JavaScript errors

### Database locked error

- Ensure only one backend process is running
- Stop any other `uvicorn` or `python main.py` processes

---

## Next Steps

1. **Deployment:** See `DEPLOYMENT_GUIDE.md` for production setup (Heroku, Vercel)
2. **Testing:** Run through `FRONTEND_TEST_CHECKLIST.md` manually
3. **Customization:** Modify seed data in `backend/seed_data.py`
4. **API Integration:** Use Swagger UI at http://localhost:8000/docs to test endpoints

---

## Files

```
civicpulse/
├── README.md                      # Project overview
├── QUICK_START.md                 # This file
├── DEMO_SCRIPT.md                 # 7-minute hackathon walkthrough
├── DEPLOYMENT_GUIDE.md            # Production deployment
├── FRONTEND_TEST_CHECKLIST.md    # Frontend integration tests
├── TEST_CHECKLIST.md              # Comprehensive 100+ test steps
├── backend/
│   ├── main.py                    # FastAPI app (12 endpoints)
│   ├── models.py                  # SQLAlchemy ORM (Complaint, Asset, RepairRecord, AuditLog)
│   ├── schemas.py                 # Pydantic request/response models
│   ├── database.py                # SQLAlchemy setup
│   ├── lifecycle.py               # 7-state machine validation
│   ├── priority_engine.py         # ML priority scoring
│   ├── migrate.py                 # SQLite schema migration
│   ├── seed_data.py               # 12 sample complaints
│   ├── civicpulse.db              # SQLite database
│   └── requirements.txt            # Python dependencies
└── frontend/
    ├── index.html                 # Main UI
    ├── script.js                  # Vanilla JS (Phase 1–4)
    └── style.css                  # Responsive styling
```

---

**Happy testing!** Questions? Check `README.md` for more details.

