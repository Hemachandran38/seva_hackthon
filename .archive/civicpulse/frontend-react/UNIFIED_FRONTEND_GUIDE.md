# 🎯 Complete Unified Frontend Guide

## Overview

Your CivicPulse AI frontend is now a fully integrated, interconnected application with all pages working together as one cohesive system.

---

## 📍 All Routes (Fully Connected)

| Route | Name | Purpose | Navigation From | Leads To |
|-------|------|---------|-----------------|----------|
| `/` | **Home** | Welcome, quick search, metrics, recent complaints, process explanation | Header logo, Footer "Home" link | All other pages |
| `/dashboard` | **Dashboard** | Map-primary view with filters & metrics (like your standalone demo) | Header nav "Dashboard", Footer "Dashboard" | All other pages via header |
| `/issues` | **Explore Issues** | Table with search/filters, CSV export, embedded map | Header nav "Explore Issues", Footer "Issue Explorer", Home "View all issues" link | Track individual complaints via table rows, Create new reports via Report button |
| `/report` | **Report Issue** | Multi-step form to submit new infrastructure complaints | Header "Report an Issue" button (primary), Footer link, ReportIssuePage success screen | Track new complaint, Browse all issues, View issue registry |
| `/track` | **Track Complaint** | View complaint timeline, details, progress, prioritization | Quick-search on Home page, Complaint table rows (AllIssuesPage), Dashboard map popups, Quick-demo buttons on TrackPage itself | Report another issue, Browse all issues, Return home |

---

## 🧭 Navigation Structure

### Header Navigation (Desktop & Mobile)
```
CivicPulse AI Logo [Home]
├─ Home
├─ Dashboard            ← NEW! Connected
├─ Explore Issues
└─ Track Complaint

[Report an Issue Button] [Sign In] [Menu]
```

### Footer Navigation
```
CivicPulse AI
├─ Citizen Services
│  ├─ Home
│  ├─ Report an Issue
│  ├─ Dashboard         ← NEW! Connected
│  ├─ Track Complaint
│  └─ Issue Explorer
└─ Governance & Trust
   ├─ About
   └─ Privacy
```

---

## 🔄 Complete User Journeys

### Journey 1: New Citizen Reports an Issue
```
Home Page
  ↓ (clicks "Report an Issue" button)
Report Issue Form
  ├─ Fill Section 01: Category, Fault Type, Title, Description
  ├─ Fill Section 02: Ward, Asset ID, Location, Optional: Set location on map
  ├─ Fill Section 03: Upload photo (optional)
  └─ Submit
      ↓
   Success Screen → "Track this complaint" link
      ↓
Track Complaint Page (shows new complaint's timeline & details)
  ├─ Can click "Report another issue" to create more
  └─ Can use header nav to browse all issues or return home
```

### Journey 2: Citizen Searches for Existing Complaint
```
Home Page → Quick Search Form
  ├─ User types complaint ID (CP-2026-0101)
  └─ Press "Track Status"
      ↓
Track Complaint Page
  ├─ View full timeline
  ├─ See priority score breakdown
  └─ Can report new issue or browse all from header
```

### Journey 3: Citizen Browses All Infrastructure Issues
```
Home Page → "View all issues" link
  ├─ OR Header nav → "Explore Issues"
  ├─ OR Footer → "Issue Explorer"
      ↓
Explore Issues Page (Table View)
  ├─ Search by ID/title/location
  ├─ Filter by category, status, priority, ward
  ├─ Sort by priority or recency
  ├─ See embedded map showing filtered results
  ├─ Click table row → Track individual complaint
  ├─ Click map marker → See popup with complaint info
  └─ Download filtered results as CSV
      ↓
(Click row to go to) Track Complaint Page
```

### Journey 4: View Dashboard Analytics
```
Home Page → Header nav "Dashboard"
  ├─ OR Direct URL: /dashboard
      ↓
Dashboard Page (Map-Primary View)
  ├─ See metrics: Total reports, Open, High Priority, Resolved
  ├─ Filter by priority level: All/Critical/High/Medium/Low
  ├─ Filter by status: All/Reported/Under Review/Assigned/In Progress/Awaiting Verification/Resolved
  ├─ Interactive map shows filtered markers
  ├─ Click marker → See popup with full complaint details
  ├─ Can also access via header nav on any page
  └─ From here: Report issue, browse table, track complaint (all accessible via header)
```

### Journey 5: Full Workflow (Complete Loop)
```
Home → Report Issue → Success (get ID) → Track Complaint
  ↓
(From Track page or header)
→ Explore Issues → See it in table
  ↓
(From header)
→ Dashboard → See marker on map
  ↓
(From any page via header)
→ Back to Home → See metric updated
  ↓
(Loop continues: can report more, track more, filter more)
```

---

## 🎨 Page-by-Page Breakdown

### Home Page (`/`)
**What It Shows:**
- Hero section with mission statement
- Quick search form for complaint IDs
- Metrics dashboard (total, open, high priority, resolved)
- Four-step process explanation (Report → Assess → Repair → Verify)
- Table of 4 most recent complaints
- Prioritization transparency section

**How It Connects:**
- "Report an Issue" button → `/report`
- Quick search form → `/track?id=X`
- "View all issues" link → `/issues`
- Dashboard link in nav → `/dashboard`
- Table rows → `/track?id=X`

**Key Actions:**
- Search for complaint ID
- View metrics overview
- Understand the process
- See recent complaints
- Access all other pages via header

---

### Dashboard Page (`/dashboard`)
**What It Shows:**
- Header with CivicPulse branding
- Left sidebar with:
  - Metrics (total, open, high priority, resolved)
  - Priority filter (All/Critical/High/Medium/Low)
  - Status filter (All/Reported/Under Review/Assigned/In Progress/Awaiting Verification/Resolved)
  - Reset Filters button
  - Map legend
  - Visible count
- Right side: Interactive Leaflet map with markers

**How It Connects:**
- Every page accessible via header nav
- Report button in header → `/report`
- Can click Dashboard link from any page
- Map markers show real-time filtered data

**Key Actions:**
- Filter by priority level (radio buttons)
- Filter by status (radio buttons)
- Click markers to see complaint popups
- Reset filters to see all
- Navigate to any other page via header

**Design Note:** This page mirrors your standalone map demo but uses live React data

---

### Explore Issues Page (`/issues`)
**What It Shows:**
- Advanced search & filter panel:
  - Search by ID/title/location/asset
  - Filter by category, status, priority, ward
  - Sort by priority or recency
- Metrics strip (total, open, critical/high, resolved)
- Paginated complaint table (6 per page)
- Pagination controls
- CSV download button
- Embedded Leaflet map below table
- Critical spotlight card

**How It Connects:**
- Accessible from Home ("View all issues"), Header nav, Footer
- Table rows link to `/track?id=X`
- Map markers link to track page via popup
- New reports created on `/report` appear here immediately

**Key Actions:**
- Search issues by any field
- Filter by 5 different dimensions
- Sort by priority or recency
- Paginate through results
- Click any row to track it
- Download filtered data as CSV
- See filtered results on embedded map

---

### Report Issue Page (`/report`)
**What It Shows:**
- Multi-section form:
  - **Section 01**: Category & Fault Type dropdowns, Title & Description text fields
  - **Section 02**: Ward, Asset ID, Location, Optional location picker button
  - **Section 03**: Photo upload with preview
  - **Section 04**: Citizen contact info notice
- Submit button
- Cancel/Back link
- On success:
  - Confirmation message with new complaint ID
  - Links to "Track this complaint" or "View issue registry"

**How It Connects:**
- "Report an Issue" button from any page → `/report`
- Form submit (success) → Shows new ID, links to `/track?id=NEW_ID` or `/issues`
- Cancel button → Returns to previous page or Home

**Key Actions:**
- Fill out multi-step form
- Set location on map (optional)
- Upload photo (optional)
- Submit to create complaint
- Track new complaint immediately
- Report another issue without leaving form

---

### Track Complaint Page (`/track`)
**What It Shows:**
- Search form at top (find any complaint by ID)
- Quick-demo buttons (links to sample complaints)
- Complaint summary card (status, priority, title, metadata)
- Location card showing address/coordinates
- Timeline showing all 6 workflow stages
- Asset & technical context panel
- Prioritization rationale explanation
- Action panel with link to report more

**How It Connects:**
- Accessible via:
  - Home quick search
  - AllIssuesPage table rows
  - DashboardPage map popups
  - Direct URL: `/track?id=COMPLAINT_ID`
- Form submit → `/track?id=X`
- "Report another issue" link → `/report`
- Header nav accessible from anywhere

**Key Actions:**
- Search for any complaint
- View full timeline & history
- See prioritization explanation
- Report another issue
- Navigate to Dashboard, Issues, or Home

---

### Not Found Page (`/404`)
**What It Shows:**
- Simple 404 message
- Link back to Home

**How It Connects:**
- Shown when accessing invalid routes
- "Return home" link → `/`

---

## 🔗 Cross-Page Data Sharing

### Data Synchronization
All pages share the same data via `complaintService`:

```
complaintService (in-memory from localStorage)
├─ HomePage ─ reads all complaints ─ shows recent 4
├─ Dashboard ─ reads & filters ─ shows on map
├─ AllIssues ─ reads & filters ─ shows in table + map
├─ TrackComplaint ─ reads & searches ─ shows details
└─ ReportIssue ─ creates & saves ─ adds to shared data
```

### When Data Changes
1. **New complaint created** on `/report`:
   - Immediately saved to localStorage
   - `complaintService.getAllComplaints()` returns updated list
   - All pages see it on next data fetch
   - Redirects to `/track?id=NEW_ID` so user can see their submission

2. **User navigates pages**:
   - Each page calls `complaintService.getAllComplaints()`
   - Always gets fresh data from localStorage
   - No stale data issues

3. **Filters applied**:
   - Filters are local state on that page
   - Don't affect other pages
   - Clicking nav to different page resets filters (by design)

---

## 🎯 Key Features (Unified)

### 1. Report Infrastructure Issues
- Multi-step form with validation
- Optional map-based location selection
- Photo upload with preview
- Instant ID generation
- Auto-track new complaint

### 2. Track Complaint Progress
- View full timeline (6 workflow stages)
- See priority score breakdown
- Understand prioritization factors
- Search by complaint ID
- Quick-access demo complaints

### 3. Explore & Analyze
- Advanced search (query + 5 filters)
- Sorting options
- Pagination
- Interactive map showing geolocated complaints
- CSV export for analysis

### 4. Dashboard Analytics
- Real-time metrics (total, open, high-priority, resolved)
- Map-based visualization
- Priority & status filters
- Legend explaining color coding
- Responsive design

### 5. Navigation & Discovery
- Consistent header on all pages
- Footer with all links
- Cross-page linking
- Breadcrumb trails (via page context)
- Quick access buttons

---

## 💻 How to Use (Complete Workflow)

### Step 1: Start at Home
- Visit `http://localhost:5173/`
- See overview, metrics, recent complaints
- Choose your path

### Step 2: One of Four Options

**Option A: Report New Issue**
- Click "Report an Issue" button (anywhere)
- Fill out 4-section form
- Submit
- View your new complaint's timeline

**Option B: Search for Complaint**
- Use quick search on Home with complaint ID
- Or use search form on Track page
- Or browse all on Explore Issues

**Option C: Browse All Issues**
- Click "Explore Issues" (header or footer)
- Use filters & search
- See table and embedded map
- Click any row to view details

**Option D: View Dashboard**
- Click "Dashboard" (header or footer)
- See analytics with filters
- Click map markers for details

### Step 3: Navigate Anywhere
- Use header nav to go to any page
- All data syncs automatically
- Create reports, track progress, explore data

---

## ✅ Verification Checklist

Test these to verify everything is connected:

- [ ] Click "Report an Issue" from Home → Form appears
- [ ] Submit form → Success screen with new ID
- [ ] Click "Track this complaint" → See new complaint on Track page
- [ ] Go back Home → New complaint shows in metrics
- [ ] Click "Explore Issues" → New complaint shows in table
- [ ] Go to Dashboard → See new complaint on map (if has coordinates)
- [ ] Use filters on Dashboard → Map updates in real-time
- [ ] Click map marker → Popup shows complaint details
- [ ] Use quick search on Home → Find any complaint
- [ ] Use search on Track page → Find any complaint
- [ ] Click table row on Issues → Navigate to Track page
- [ ] Download CSV on Issues page → Get filtered data
- [ ] Click header nav "Dashboard" from any page → Dashboard loads
- [ ] Click footer links → Navigate between pages
- [ ] Refresh page → Data persists from localStorage

---

## 📊 Complete Feature Map

```
Home (/home)
├─ Quick Search → Track page
├─ Report Button → Report form
├─ View All Link → Issues explorer
└─ Metrics Visible → Updated in real-time

Dashboard (/dashboard)
├─ Metrics Panel → Shows totals
├─ Priority Filters → 5 levels
├─ Status Filters → 6 statuses
├─ Interactive Map → All geolocated complaints
└─ Reset Filters → Back to all

Explore Issues (/issues)
├─ Search Field → Query by ID/title/location
├─ Category Filter → All categories
├─ Status Filter → All statuses
├─ Priority Filter → All priorities
├─ Ward Filter → All wards
├─ Sort Options → Priority or recent
├─ Complaint Table → Paginated, 6 per page
├─ Embedded Map → Shows filtered results
├─ CSV Export → Download data
└─ Critical Spotlight → Featured complaint

Report Issue (/report)
├─ Section 01: Category & Type
├─ Section 02: Location (with optional map)
├─ Section 03: Photo upload
├─ Section 04: Contact info
├─ Submit Button → Create complaint
└─ Success Screen → Track or browse

Track Complaint (/track)
├─ Search Form → Find any complaint
├─ Demo Quick-Links → Popular complaints
├─ Summary Card → Status, priority, title
├─ Location Card → Address & coordinates
├─ Timeline View → All 6 workflow stages
├─ Asset Context → Technical details
├─ Priority Explanation → Scoring factors
└─ Report Another → Back to form

Header Navigation (all pages)
├─ Logo → Home
├─ Home → Home page
├─ Dashboard → Dashboard page
├─ Explore Issues → Issues page
├─ Track Complaint → Track page
├─ Report an Issue → Report form
└─ Sign In → Demo notice

Footer Navigation (all pages)
├─ All header links repeated
├─ Plus about/privacy/accessibility
└─ Copyright & demo badge
```

---

## 🚀 Running the Complete Frontend

```bash
# 1. Navigate to project
cd c:\seva_hackthon\civicpulse\frontend-react

# 2. Install dependencies
npm install

# 3. Start dev server
npm run dev

# 4. Open in browser
http://localhost:5173/
```

You'll see the complete, unified frontend with all pages interconnected!

---

## 📋 Summary

Your CivicPulse AI frontend is now a **fully integrated, complete application** with:

✅ **5 functional pages** (Home, Dashboard, Explore Issues, Report Issue, Track Complaint)
✅ **Unified navigation** (Header + Footer accessible from all pages)
✅ **Complete data flow** (All pages share same data via complaintService)
✅ **Interconnected workflows** (Report → Track → Explore → Dashboard → Home, in any order)
✅ **Responsive design** (Works on desktop and mobile)
✅ **Real-time updates** (New complaints appear immediately across all pages)
✅ **CSV export** (Download filtered data)
✅ **Interactive maps** (Two views: Dashboard analytics, Explore Issues embedded)
✅ **Advanced filtering** (Search + 5 filter dimensions)
✅ **Demo data** (12 sample complaints pre-loaded)

**All pages work together as one cohesive system.** 🎉
