# CivicPulse AI — Deployment Checklist

Use this checklist to ensure your system is production-ready.

## Pre-Flight Checks

### ✅ Frontend

- [ ] Navigate to `c:\seva_hackthon\frontend`
- [ ] Run `npm install` (completes without errors)
- [ ] Run `npm run dev` (starts on http://localhost:5173)
- [ ] Open http://localhost:5173 in browser
- [ ] All pages load without errors (check console F12)
- [ ] Header & navigation visible
- [ ] Responsive design works on mobile viewport

### ✅ Backend

- [ ] Navigate to `c:\seva_hackthon\civicpulse-backend`
- [ ] Run `pip install -r requirements.txt` (completes without errors)
- [ ] Run `python -m uvicorn app.main:app --host 127.0.0.1 --port 9000`
- [ ] Backend starts successfully (no import errors)
- [ ] Database initialized (civicpulse.db created)
- [ ] Test API endpoint: `curl http://127.0.0.1:9000/api/complaints`
- [ ] Returns valid JSON (not 500 error)

### ✅ AI Model

- [ ] Model file exists: `c:\seva_hackthon\model\civicpulse_priority_model.pkl`
- [ ] Backend can load model (check startup logs)
- [ ] If model fails to load, fallback mock engine works
- [ ] Submit a complaint and verify priority is assigned

### ✅ Database

- [ ] SQLite database created: `c:\seva_hackthon\civicpulse-backend\civicpulse.db`
- [ ] Database has tables: complaints, repair_tasks, status_history
- [ ] Can insert complaint and retrieve it

---

## Functional Testing

### 1️⃣ Report New Issue

- [ ] Click "Report Issue" link
- [ ] Form displays all fields
- [ ] Fill required fields:
  - Title: "Test Issue"
  - Category: "Streetlight" (dropdown works)
  - Description: "This is a test"
- [ ] Submit button enabled
- [ ] Click Submit
- [ ] Success message shown
- [ ] Complaint ID generated and displayed
- [ ] ⚠️ Note: Save the ID for next tests

### 2️⃣ Track Complaint

- [ ] Click "Track Complaint" link
- [ ] Input field visible
- [ ] Paste ID from test 1️⃣
- [ ] Click "Track" or "Search"
- [ ] Complaint details display
- [ ] **AI Priority Score visible** (most important!)
- [ ] Status shows "Open" or same as submitted
- [ ] All fields match what was submitted

### 3️⃣ View Dashboard

- [ ] Click "Dashboard" link
- [ ] Page loads without errors
- [ ] **Interactive map displays** (most important!)
- [ ] Statistics cards show:
  - Total Assets: 1+ (from test 1️⃣)
  - Open Complaints: 1+
  - High Priority: Shows count
  - Resolved: Shows count
- [ ] Filter controls visible (Priority, Status)
- [ ] Filter by "High Priority" works
- [ ] Map updates to show only high priority
- [ ] "Reset Filters" button works

### 4️⃣ Browse All Issues

- [ ] Click "All Issues" link
- [ ] Complaint list displays
- [ ] Complaint from test 1️⃣ is in list
- [ ] Each item shows: ID, Title, Priority, Status
- [ ] Pagination works (if 10+ items)
- [ ] Click on item shows details

### 5️⃣ API Connectivity

- [ ] Test GET /api/complaints:
  ```bash
  curl http://127.0.0.1:9000/api/complaints
  ```
  Expected: JSON array of complaints

- [ ] Test POST /api/complaints (create new):
  ```bash
  curl -X POST http://127.0.0.1:9000/api/complaints \
    -H "Content-Type: application/json" \
    -d '{"title":"Test","category":"Streetlight","description":"Test"}'
  ```
  Expected: 201 response with new complaint ID

- [ ] Test GET /api/dashboard/stats:
  ```bash
  curl http://127.0.0.1:9000/api/dashboard/stats
  ```
  Expected: JSON with stats

- [ ] Test GET /api/dashboard/map-data:
  ```bash
  curl http://127.0.0.1:9000/api/dashboard/map-data
  ```
  Expected: JSON array of complaints with lat/lng

---

## Performance Testing

- [ ] Frontend loads in < 2 seconds (dev) / < 500ms (prod)
- [ ] Dashboard map loads in < 1 second
- [ ] API responses < 200ms (check Network tab in F12)
- [ ] No console errors or warnings
- [ ] Memory usage stable (not increasing over time)

---

## Cross-Browser Testing

- [ ] ✅ Chrome/Chromium
- [ ] ✅ Firefox
- [ ] ✅ Safari (if Mac available)
- [ ] ✅ Edge

---

## Responsive Testing

- [ ] Desktop (1920x1080) — All layouts correct
- [ ] Tablet (768x1024) — Sidebar responsive
- [ ] Mobile (375x667) — Single column layout
- [ ] Check each page on mobile:
  - Home
  - Report Issue
  - Track Complaint
  - All Issues
  - Dashboard

---

## Backend Tests

### Run Full Test Suite

```bash
cd c:\seva_hackthon\civicpulse-backend
pytest
```

- [ ] All 53 tests pass
- [ ] No errors or failures
- [ ] Coverage > 80% (if applicable)

### Test Categories

- [ ] Endpoint tests (POST /api/complaints, GET /api/complaints, etc.)
- [ ] AI Model tests (feature extraction, priority evaluation)
- [ ] Database tests (insert, query, update)
- [ ] Error handling tests (invalid input, missing fields)

---

## Integration Tests

### End-to-End Workflow

1. [ ] User submits complaint form
2. [ ] Backend receives and validates
3. [ ] AI model evaluates priority
4. [ ] Data stored in database
5. [ ] Dashboard loads with new complaint
6. [ ] Map shows new marker with correct color
7. [ ] User can search by ID and find it
8. [ ] User can update status and see change

---

## Configuration Checks

### Frontend `.env.local`

```env
VITE_API_BASE_URL=http://127.0.0.1:9000
```

- [ ] File exists
- [ ] Backend URL correct
- [ ] No hardcoded API URLs in source code

### Backend `.env`

```env
DATABASE_URL=sqlite:///civicpulse.db
FRONTEND_URL=http://localhost:5173
```

- [ ] File exists
- [ ] Database path correct
- [ ] CORS frontend URL matches

---

## Security Checklist

- [ ] No hardcoded secrets in code
- [ ] .env files not committed to git
- [ ] API validates all input (form validation)
- [ ] CORS properly configured (only allow trusted origins)
- [ ] Database uses parameterized queries (SQL injection prevention)
- [ ] Error messages don't leak sensitive info
- [ ] HTTPS ready for production (not required for demo)

---

## Production Build

### Frontend Build

```bash
cd c:\seva_hackthon\frontend
npm run build
```

- [ ] Build completes successfully
- [ ] dist/ folder created
- [ ] dist/ folder < 1MB (check with `du -sh dist/`)
- [ ] No build errors or warnings

### Preview Production Build

```bash
cd c:\seva_hackthon\frontend
npm run preview
```

- [ ] Preview runs successfully
- [ ] All pages load and work same as dev
- [ ] Map displays correctly
- [ ] API calls work (if backend running)

### Deployment

- [ ] dist/ folder ready to upload
- [ ] Hosting service configured (Netlify, Vercel, AWS S3, etc.)
- [ ] Backend deployed or accessible
- [ ] CORS headers updated for production domain
- [ ] Frontend .env.production has correct backend URL

---

## Documentation Checks

- [ ] ✅ `c:\seva_hackthon\SETUP_COMPLETE.md` — Overview
- [ ] ✅ `c:\seva_hackthon\frontend\README.md` — Frontend guide
- [ ] ✅ `c:\seva_hackthon\frontend\QUICK_START.md` — 5-minute setup
- [ ] ✅ `c:\seva_hackthon\frontend\UNIFIED_FRONTEND_GUIDE.md` — Architecture
- [ ] ✅ `c:\seva_hackthon\frontend\FRONTEND_STRUCTURE.md` — Code guide
- [ ] ✅ `c:\seva_hackthon\civicpulse-backend\README.md` — Backend guide
- [ ] ✅ `c:\seva_hackthon\civicpulse-backend\BACKEND_STRUCTURE.md` — Backend structure
- [ ] ✅ `c:\seva_hackthon\civicpulse-backend\API_DOCUMENTATION.md` — API reference

---

## Hackathon Demo Readiness

### ✅ 5-Minute Demo Ready?

1. [ ] Frontend starts in < 10 seconds (`npm run dev`)
2. [ ] Backend starts in < 10 seconds (`python -m uvicorn ...`)
3. [ ] Both services stay running without crashes
4. [ ] Can complete demo script in 5 minutes:
   - Report issue (1 min)
   - Track complaint with AI priority (1 min)
   - View dashboard (1 min)
   - Show filters & interactivity (1 min)
   - Q&A buffer (1 min)

### ✅ Presentation Materials

- [ ] Demo script written (step-by-step)
- [ ] Backup screenshots/video recorded
- [ ] Terminal commands saved in text file
- [ ] Sample data prepared (optional)

---

## Common Issues & Fixes

### Issue: npm modules not found
```bash
cd c:\seva_hackthon\frontend
rm -r node_modules
npm install
```

### Issue: Backend port already in use
```bash
# Find process using port 9000
netstat -ano | findstr :9000

# Kill process
taskkill /PID <PID> /F

# Try different port
python -m uvicorn app.main:app --host 127.0.0.1 --port 9001
```

### Issue: Model not loading
- Check model file exists
- Check scikit-learn installed: `pip install scikit-learn`
- Backend falls back to mock engine (should still work)

### Issue: CORS errors
- Verify frontend URL in backend CORS config
- Verify backend URL in frontend `.env.local`

### Issue: Map won't display
- Check internet connection (Leaflet CDN)
- Check browser console for errors
- Verify Leaflet CSS/JS loaded in Network tab

---

## Rollback Plan

If issues found during testing:

1. [ ] Identify root cause
2. [ ] Document issue in ISSUES.md
3. [ ] Create fix branch in git
4. [ ] Fix code & test locally
5. [ ] Commit with descriptive message
6. [ ] Push and verify in production

---

## Sign-Off

**When ALL items checked:**

- [ ] System is production-ready ✅
- [ ] All tests pass ✅
- [ ] Demo works without issues ✅
- [ ] Documentation complete ✅
- [ ] Ready for hackathon judges ✅

---

**Status:** Ready for deployment 🚀

**Last Updated:** October 2026
**Team:** CivicPulse AI
**Demo Time:** 5 minutes
