# 🏗️ Domain-Based Architecture

## File Structure Overview

The application is organized by **domain/feature** rather than by technical layer. This makes it easier to find related files and understand the business logic.

```
src/
├── domains/
│   ├── complaint/                          # Core complaint domain
│   │   ├── types/
│   │   │   ├── complaint.ts               # Complaint interfaces & types
│   │   │   └── enums.ts                   # Status, Priority enums
│   │   ├── services/
│   │   │   ├── complaintService.ts        # CRUD operations
│   │   │   └── storageService.ts          # localStorage persistence
│   │   ├── components/
│   │   │   ├── ComplaintTable.tsx         # Reusable table
│   │   │   ├── ComplaintCard.tsx          # Summary card
│   │   │   └── TimelineView.tsx           # Timeline display
│   │   ├── hooks/
│   │   │   ├── useComplaints.ts           # Data fetching hook
│   │   │   └── useComplaintSearch.ts      # Search logic
│   │   └── pages/
│   │       ├── ComplaintListPage.tsx      # All complaints view
│   │       ├── ComplaintDetailPage.tsx    # Single complaint view
│   │       └── ComplaintCreatePage.tsx    # Create new complaint
│   │
│   ├── map/                                # Map/geolocation domain
│   │   ├── components/
│   │   │   ├── InfrastructureMap.tsx      # Main map component
│   │   │   ├── LocationSelector.tsx       # Location picker
│   │   │   └── MapLegend.tsx              # Legend display
│   │   ├── hooks/
│   │   │   └── useMapFilters.ts           # Map filtering logic
│   │   ├── services/
│   │   │   └── geoService.ts              # Geolocation utilities
│   │   └── pages/
│   │       └── DashboardPage.tsx          # Map-based dashboard
│   │
│   ├── home/                               # Home/landing page domain
│   │   ├── components/
│   │   │   ├── HeroSection.tsx
│   │   │   ├── MetricCard.tsx
│   │   │   ├── RecentComplaints.tsx
│   │   │   └── ProcessFlow.tsx
│   │   └── pages/
│   │       └── HomePage.tsx
│   │
│   └── shared/                             # Shared across domains
│       ├── components/
│       │   ├── PageIntro.tsx
│       │   ├── StatusBadge.tsx
│       │   ├── PriorityBadge.tsx
│       │   └── EmptyState.tsx
│       ├── layout/
│       │   ├── PublicLayout.tsx
│       │   ├── Header.tsx
│       │   └── Footer.tsx
│       ├── utils/
│       │   ├── formatting.ts
│       │   ├── validation.ts
│       │   └── constants.ts
│       └── hooks/
│           └── useNavigation.ts
│
├── styles/                                  # Global styles
│   ├── tokens.css                          # Design tokens
│   ├── global.css                          # Reset + base
│   ├── components.css                      # Component styles
│   └── dashboard.css                       # Dashboard layout
│
├── App.tsx                                  # Root component
├── main.tsx                                 # Entry point
└── vite-env.d.ts
```

---

## Domain Breakdown

### **Complaint Domain** 
**Responsibility:** Manage complaint lifecycle (create, read, update, display)

**Files:**
- `domains/complaint/types/complaint.ts` — Data models
- `domains/complaint/services/complaintService.ts` — Data operations
- `domains/complaint/components/ComplaintTable.tsx` — Display complaints
- `domains/complaint/pages/ComplaintListPage.tsx` — Browse all
- `domains/complaint/pages/ComplaintDetailPage.tsx` — View one complaint
- `domains/complaint/pages/ComplaintCreatePage.tsx` — Create new

**Used by:** All pages

---

### **Map Domain**
**Responsibility:** Geographic visualization and location selection

**Files:**
- `domains/map/components/InfrastructureMap.tsx` — Main map
- `domains/map/components/LocationSelector.tsx` — Pick location
- `domains/map/pages/DashboardPage.tsx` — Map analytics

**Used by:** Dashboard, Issues explorer, Report form

---

### **Home Domain**
**Responsibility:** Landing page and overview

**Files:**
- `domains/home/pages/HomePage.tsx` — Hero + metrics
- `domains/home/components/HeroSection.tsx` — Welcome
- `domains/home/components/MetricCard.tsx` — Stats

**Used by:** Homepage route

---

### **Shared Domain**
**Responsibility:** Common components, utilities, layout

**Files:**
- `domains/shared/layout/PublicLayout.tsx` — App wrapper
- `domains/shared/components/StatusBadge.tsx` — Status display
- `domains/shared/utils/formatting.ts` — Format utilities

**Used by:** All pages

---

## Navigation Between Domains

```
HomePage (home domain)
  ├─ Quick Search → ComplaintDetailPage (complaint domain)
  ├─ Report Button → ComplaintCreatePage (complaint domain)
  ├─ View All → ComplaintListPage (complaint domain)
  └─ Header Nav → Any page

ComplaintListPage (complaint domain)
  ├─ Table Row → ComplaintDetailPage (complaint domain)
  ├─ Embedded Map → DashboardPage (map domain)
  └─ Header Nav → Any page

ComplaintCreatePage (complaint domain)
  ├─ Location Picker → LocationSelector (map domain)
  ├─ Submit → ComplaintDetailPage (complaint domain)
  └─ Header Nav → Any page

DashboardPage (map domain)
  ├─ Map Click → ComplaintDetailPage (complaint domain)
  ├─ Filters → InfrastructureMap (map domain)
  └─ Header Nav → Any page

ComplaintDetailPage (complaint domain)
  ├─ Report More → ComplaintCreatePage (complaint domain)
  ├─ Browse All → ComplaintListPage (complaint domain)
  └─ Header Nav → Any page
```

---

## Data Flow (Cross-Domain)

```
complaintService (Shared)
  ├─ getAllComplaints() → Used by HomePage, ComplaintListPage, DashboardPage
  ├─ getComplaintById() → Used by ComplaintDetailPage
  ├─ createComplaint() → Used by ComplaintCreatePage
  └─ filterComplaints() → Used by ComplaintListPage, DashboardPage

LocationSelector (map domain)
  ├─ Returns: {latitude, longitude}
  └─ Used by: ComplaintCreatePage (complaint domain)

InfrastructureMap (map domain)
  ├─ Input: complaints[]
  └─ Used by: ComplaintListPage, DashboardPage
```

---

## File Organization Rationale

### **Why by Domain?**

✅ **Cohesion:** All complaint-related code is together
✅ **Discoverability:** Easy to find related files
✅ **Independence:** Domains can be modified independently
✅ **Scaling:** Easy to add new domains (e.g., admin, analytics)
✅ **Maintenance:** Clear boundaries and responsibilities

### **Why Shared Domain?**

✅ **Reusability:** Components used everywhere go here
✅ **Consistency:** Single source for common UI patterns
✅ **DRY:** No duplication of utilities

---

## Current File Mapping

| Old Path | New Domain Path | Notes |
|----------|-----------------|-------|
| `pages/HomePage.tsx` | `domains/home/pages/HomePage.tsx` | Move to home domain |
| `pages/ReportIssuePage.tsx` | `domains/complaint/pages/ComplaintCreatePage.tsx` | Rename for clarity |
| `pages/AllIssuesPage.tsx` | `domains/complaint/pages/ComplaintListPage.tsx` | Rename for clarity |
| `pages/TrackComplaintPage.tsx` | `domains/complaint/pages/ComplaintDetailPage.tsx` | Rename for clarity |
| `pages/DashboardPage.tsx` | `domains/map/pages/DashboardPage.tsx` | Move to map domain |
| `components/map/InfrastructureMap.tsx` | `domains/map/components/InfrastructureMap.tsx` | Move to map domain |
| `components/map/LocationSelector.tsx` | `domains/map/components/LocationSelector.tsx` | Move to map domain |
| `types/complaint.ts` | `domains/complaint/types/complaint.ts` | Move to complaint domain |
| `services/complaintService.ts` | `domains/complaint/services/complaintService.ts` | Move to complaint domain |
| `services/storageService.ts` | `domains/complaint/services/storageService.ts` | Move to complaint domain |
| `components/common/Ui.tsx` | Split across domains (badges, empty states) or `domains/shared/components/` | Split by component type |
| `components/layout/PublicLayout.tsx` | `domains/shared/layout/PublicLayout.tsx` | Move to shared |

---

## Benefits of This Structure

### For Development
- Clear separation of concerns
- Easier testing (mock one domain at a time)
- Simpler imports (e.g., `from '@/domains/complaint/services'`)

### For Navigation
- Know exactly where to find complaint-related code
- Know exactly where to find map-related code
- Know exactly where to find shared utilities

### For Growth
- Easy to add new domains (e.g., analytics, admin)
- Easy to extract a domain into a separate package/module
- Clear API boundaries between domains

---

## Implementation Phases

### Phase 1: Create Structure (This Guide)
✅ Define domain architecture
✅ Document file organization
✅ Map current files to new structure

### Phase 2: Refactor Code (Next Steps)
⏳ Move files to new structure
⏳ Update all imports
⏳ Verify all pages still work

### Phase 3: Optimize
⏳ Add hooks for data fetching
⏳ Extract reusable components
⏳ Add utility functions

---

## Example: Creating New Domain

To add a new domain (e.g., "Reports/Analytics"), follow this structure:

```
domains/reports/
├── types/
│   └── report.ts
├── services/
│   └── reportService.ts
├── components/
│   ├── ReportChart.tsx
│   └── ReportTable.tsx
├── hooks/
│   └── useReports.ts
└── pages/
    └── ReportsPage.tsx
```

Then integrate with other domains via shared services or shared components.

---

## Summary

The domain-based structure:
- ✅ Organizes code by business logic (complaint, map, home)
- ✅ Makes it easy to find related files
- ✅ Clear boundaries between features
- ✅ Shared domain for cross-cutting concerns
- ✅ Scales well as app grows

This replaces the old technical-layer structure (pages, components, services folders) with a feature-based structure that's easier to navigate and maintain.
