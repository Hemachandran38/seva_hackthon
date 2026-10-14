# Unified Frontend Architecture Guide

## Overview

This is the **single, authoritative frontend** for CivicPulse AI. It consolidates all frontend code into one cohesive React application.

## Why Unified?

Previously, CivicPulse had multiple frontend implementations:
- **Vanilla Frontend** — HTML/CSS/JS (static demo)
- **React Frontend** — TypeScript/Vite (production-ready)
- **Root Scripts** — index.html, script.js, style.css (legacy)

**Now:** All frontend code is here. This is the only frontend you need.

## Directory Consolidation

| Old Location | New Location | Status |
|---|---|---|
| `c:\seva_hackthon\civicpulse\frontend\` | `c:\seva_hackthon\frontend\` | ✅ Consolidated |
| `c:\seva_hackthon\civicpulse\frontend-react\` | `c:\seva_hackthon\frontend\` | ✅ Consolidated |
| `c:\seva_hackthon\index.html` | Reference only | ⚠️ Archive |
| `c:\seva_hackthon\script.js` | Reference only | ⚠️ Archive |
| `c:\seva_hackthon\style.css` | Reference only | ⚠️ Archive |

**Action:** Delete or archive the old directories once verified this frontend works.

## Getting Started

### 1. Install & Run

```bash
cd c:\seva_hackthon\frontend
npm install
npm run dev
```

Frontend runs on: **http://localhost:5173**

### 2. Start Backend

In another terminal:

```bash
cd c:\seva_hackthon\civicpulse-backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 9000
```

Backend runs on: **http://127.0.0.1:9000**

### 3. Verify Connection

In frontend, navigate to:
- **Dashboard:** http://localhost:5173/dashboard
- Should load map and complaints from backend
- Check browser console (F12) for any errors

## Frontend Architecture

### Core Pages

**Home** (`src/pages/HomePage.tsx`)
- Landing page with system overview
- Navigation to other pages

**Report Issue** (`src/pages/ReportIssuePage.tsx`)
- Form to submit new complaints
- POST to `/api/complaints`
- Auto-evaluates AI priority

**Track Complaint** (`src/pages/TrackComplaintPage.tsx`)
- Search complaint by ID
- Real-time status tracking

**All Issues** (`src/pages/AllIssuesPage.tsx`)
- Browse all complaints
- Filter by priority/status
- Pagination

**Dashboard** (`src/pages/DashboardPage.tsx`)
- **Interactive map** (Leaflet)
- **Real-time stats** (total, open, high priority, resolved)
- **Filter controls** (priority, status)
- AI priority scores on each marker

### Components

**Layout**
- `components/layout/PublicLayout.tsx` — Main layout wrapper
- `components/common/Header.tsx` — Top navigation
- `components/common/Footer.tsx` — Footer

**Map**
- `components/map/InteractiveMap.tsx` — Leaflet map wrapper
- `components/map/MapControls.tsx` — Filter and view controls
- `components/map/MapMarker.tsx` — Individual complaint marker

**Common UI**
- Buttons, cards, modals
- Filter chips
- Metric cards
- Status badges

### Services

**API Client** (`src/services/api.ts`)
- Centralized backend communication
- All endpoints documented
- Error handling & fallbacks
- Example:

```typescript
import { apiClient } from '../services/api';

// Get all complaints
const complaints = await apiClient.getComplaints();

// Create new complaint
const newComplaint = await apiClient.createComplaint({
  title: 'Broken Streetlight',
  category: 'Streetlight',
  description: '...',
  // ...
});

// Get complaint by ID
const complaint = await apiClient.getComplaintById('CBE-2026-001');
```

### Types

**TypeScript Interfaces** (`src/types/`)
- `Complaint` — Full complaint data structure
- `Priority` — Priority level enum
- `Status` — Complaint status enum
- `FilterOptions` — Dashboard filter state

All API responses are typed for type safety.

### Styling

**Design Tokens** (`src/styles/tokens.css`)
```css
--color-primary: #1a56db;
--color-high: #e53e3e;
--color-medium: #dd6b20;
--color-low: #3182ce;
--color-resolved: #38a169;
```

**Global Styles** (`src/styles/global.css`)
- Layout framework
- Header/footer
- Sidebar
- Responsive design

**Component Styles** (`src/styles/components.css`)
- Card, button, badge styles
- Form elements
- Modal/popup styles

## Data Flow

### 1. Report a New Issue

```
User fills form in ReportIssuePage
    ↓
Validates input (frontend)
    ↓
POST /api/complaints (backend)
    ↓
Backend runs AI model on complaint
    ↓
AI priority evaluation stored in DB
    ↓
Response returned to frontend
    ↓
Success message shown
    ↓
User redirected to /track?id=<new-id>
```

### 2. View Dashboard

```
User navigates to /dashboard
    ↓
GET /api/dashboard/stats (backend)
    ↓
GET /api/dashboard/map-data (backend)
    ↓
Populate metrics cards
    ↓
Initialize Leaflet map
    ↓
Add complaint markers to map
    ↓
Color by priority (red=high, orange=medium, blue=low, green=resolved)
```

### 3. Filter Complaints

```
User clicks "High Priority" filter
    ↓
Update filterState in component
    ↓
Re-query /api/complaints?priority=high (optional)
    ↓
OR filter locally from cached data
    ↓
Re-render map with matching markers only
```

## API Endpoints

The frontend uses these backend endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/complaints` | List all complaints |
| POST | `/api/complaints` | Create new complaint |
| GET | `/api/complaints/{id}` | Get complaint details |
| PUT | `/api/complaints/{id}/status` | Update status |
| GET | `/api/dashboard/stats` | Dashboard statistics |
| GET | `/api/dashboard/map-data` | Map data with pagination |

**Base URL:** `http://127.0.0.1:9000` (configurable in `.env.local`)

## Development Workflow

### Adding a New Feature

1. **Create page component** in `src/pages/`
2. **Add route** in `src/App.tsx`
3. **Create API call** in `src/services/api.ts`
4. **Add types** in `src/types/`
5. **Style** in `src/styles/`
6. **Test** with `npm run dev`

### Example: Add "Export as CSV" Feature

1. Create `src/pages/ExportPage.tsx`
2. Add route: `<Route path="export" element={<ExportPage />} />`
3. Add API: `export async function exportComplaints() { ... }`
4. Add types: `interface ExportFormat { ... }`
5. Add styles: Add `.export-container { ... }` to components.css
6. Test at `http://localhost:5173/export`

## Environment Configuration

### Development (.env.local)

```env
VITE_API_BASE_URL=http://127.0.0.1:9000
VITE_APP_NAME=CivicPulse AI - Dev
```

### Production (.env.production)

```env
VITE_API_BASE_URL=https://api.civicpulse.io
VITE_APP_NAME=CivicPulse AI
```

Build process automatically selects correct `.env` file.

## Deployment Options

### Option 1: Local Development
```bash
npm run dev
```
Runs on `http://localhost:5173` with hot reload.

### Option 2: Production Build
```bash
npm run build
npm run preview
```
Creates optimized `dist/` folder. Test with `npm run preview`.

### Option 3: Deploy to Netlify
```bash
npm run build
# Upload dist/ folder to Netlify
```

### Option 4: Deploy to Vercel
```bash
# Connect GitHub repo to Vercel
# Auto-deploys on push to main
```

## Troubleshooting

### Issue: "Cannot GET /api/complaints"

**Cause:** Backend not running or wrong base URL

**Fix:**
1. Start backend: `python -m uvicorn app.main:app --host 127.0.0.1 --port 9000`
2. Check `.env.local`: `VITE_API_BASE_URL=http://127.0.0.1:9000`
3. Verify backend is accessible: `curl http://127.0.0.1:9000/api/complaints`

### Issue: Map won't load

**Cause:** Leaflet CDN blocked or internet issue

**Fix:**
1. Check internet connection
2. Open browser DevTools → Network tab
3. Look for failed leaflet requests
4. Try on different network if blocked

### Issue: "CORS error"

**Cause:** Frontend and backend on different origins

**Fix:** Backend already configured for `http://localhost:5173`. If deploying to different URL, update backend CORS:

```python
# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    # ...
)
```

## Performance Tips

1. **Lazy load routes** (already done with React.lazy)
2. **Cache API responses** (use React Query or SWR)
3. **Optimize images** (compress before adding)
4. **Minimize bundle** (tree-shake unused code)
5. **Monitor performance** (Lighthouse in DevTools)

## Next Steps

1. ✅ Install dependencies: `npm install`
2. ✅ Start frontend: `npm run dev`
3. ✅ Start backend: `python -m uvicorn app.main:app --host 127.0.0.1 --port 9000`
4. ✅ Test workflow: Report issue → See on dashboard
5. ✅ Build for production: `npm run build`
6. ✅ Deploy to hosting service

## Questions?

- Check `README.md` for quick start
- Check `src/services/api.ts` for API client documentation
- Check `src/types/` for data structure definitions
- Check browser console (F12) for runtime errors
- Check network tab (F12 → Network) for API request issues

---

**Status:** ✅ Production-ready unified frontend
**Last Updated:** October 2026
**Backend:** Fully integrated via API
**Database:** SQLite (backend-managed)
