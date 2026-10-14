# CivicPulse AI Frontend — Setup Instructions

## 🚀 Quick Start (5 minutes)

### Step 1: Install Dependencies
```bash
cd c:\seva_hackthon\civicpulse\frontend-react
npm install
```

This will install:
- React 18.3.1
- React Router 7.18.4
- Vite 6.0.5
- **Leaflet 1.9.4** (NEW)
- **React-Leaflet 4.2.6** (NEW)
- Lucide React icons
- TypeScript 5.6.2

### Step 2: Run Development Server
```bash
npm run dev
```

You'll see output like:
```
  VITE v6.0.5

  ➜  Local:   http://localhost:5173/
  ➜  press h + enter to show help
```

### Step 3: Open in Browser
Navigate to `http://localhost:5173` and you should see the CivicPulse AI application.

---

## 📍 What's New

### Map Features
- **Infrastructure Map** on `/issues` page showing 12 geolocated sample complaints
- **Location Selector** on `/report` page for selecting complaint location
- **Interactive markers** with popups showing complaint details
- **Map filtering** by priority, status, and category
- **Responsive design** for desktop and mobile

### Sample Data
All sample complaints now include latitude/longitude coordinates representing locations in Coimbatore, India:
- Critical priority complaints
- High priority complaints
- Mixed statuses (Open, In Progress, Resolved)
- Different asset categories

---

## ✅ Verification Checklist

After running `npm run dev`, verify these features:

### Home Page (`/`)
- [ ] Page loads without errors
- [ ] Dashboard metrics display correctly
- [ ] Recent reports list shows 4 sample complaints
- [ ] "View all issues" link works

### All Issues Page (`/issues`)
- [ ] Page loads with map visible
- [ ] 12 sample complaints appear as markers on map
- [ ] Markers are color-coded (red, orange, blue, green)
- [ ] Filters work (try "High Priority" filter)
- [ ] Complaint table displays filtered results
- [ ] Clicking marker opens popup
- [ ] "View Details" link in popup works

### Report Issue Page (`/report`)
- [ ] Page loads with form
- [ ] Can fill in complaint details
- [ ] **Section 02**: "Select Location on Map" button appears
- [ ] Clicking button opens map selector
- [ ] Can click on map to select location
- [ ] Coordinates display after selection
- [ ] Can submit form
- [ ] Success page shows complaint ID

### Track Complaint Page (`/track?id=CP-2026-0101`)
- [ ] Page loads with complaint details
- [ ] Timeline shows complaint status history
- [ ] Links back to issues page work

---

## 🐛 Troubleshooting

### Map doesn't appear
```
Error: Leaflet CSS not loaded
Solution: Clear browser cache (Ctrl+Shift+Delete) and reload
```

### Markers show as blue question marks
```
Error: Default marker icons not loading
Solution: This is handled by leaflet-defaulticon-compatibility
If still broken: Check browser console for 404 errors
```

### Coordinates not saving
```
Issue: localStorage full or blocked
Solution: Check browser settings → Privacy → Storage
Clear site data and try again
```

### TypeScript errors during build
```bash
# Run type check
npm run typecheck

# Build should still work despite type warnings
npm run build
```

### Port 5173 already in use
```bash
# Vite will automatically try next port (5174, 5175, etc.)
# Or manually specify port:
npm run dev -- --port 3000
```

---

## 📂 Project Structure

```
frontend-react/
├── src/
│   ├── components/
│   │   ├── map/
│   │   │   ├── InfrastructureMap.tsx       (NEW - main map component)
│   │   │   ├── InfrastructureMap.css       (NEW - map styles)
│   │   │   ├── LocationSelector.tsx        (NEW - location picker)
│   │   │   └── LocationSelector.css        (NEW - location picker styles)
│   │   └── common/
│   │       └── Ui.tsx
│   ├── pages/
│   │   ├── HomePage.tsx
│   │   ├── AllIssuesPage.tsx               (MODIFIED - added map)
│   │   ├── ReportIssuePage.tsx             (MODIFIED - added location selector)
│   │   ├── TrackComplaintPage.tsx
│   │   └── NotFoundPage.tsx
│   ├── data/
│   │   ├── initialComplaints.ts            (MODIFIED - added coordinates)
│   │   ├── sampleComplaints.ts             (NEW - reference data)
│   │   └── [other data files]
│   ├── types/
│   │   └── complaint.ts                    (MODIFIED - added lat/lng)
│   ├── services/
│   │   ├── complaintService.ts
│   │   └── storageService.ts
│   ├── styles/
│   │   ├── global.css
│   │   ├── components.css
│   │   └── [other styles]
│   ├── App.tsx
│   ├── main.tsx
│   └── utils/
├── package.json                             (MODIFIED - added dependencies)
├── package-lock.json
├── vite.config.ts
├── tsconfig.json
├── tsconfig.app.json
├── tsconfig.node.json
├── index.html
├── README.md
├── LEAFLET_INTEGRATION_SUMMARY.md           (NEW - detailed summary)
└── SETUP_INSTRUCTIONS.md                    (NEW - this file)
```

---

## 🔨 Available Commands

```bash
# Development server with hot reload
npm run dev

# Type check (no build)
npm run typecheck

# Build for production
npm run build

# Preview production build locally
npm run preview

# Build with type checking
npm run build
```

---

## 📋 What Was Integrated

### New Dependencies
- `leaflet@^1.9.4` — Core mapping library
- `react-leaflet@^4.2.6` — React bindings for Leaflet
- `@types/leaflet@^1.9.12` — TypeScript types
- `leaflet-defaulticon-compatibility@^0.1.2` — Fix for bundled environments

### New Components
- `InfrastructureMap` — Displays complaints on map with filtering
- `LocationSelector` — Allows users to select location on map
- Both fully styled and responsive

### Updated Files
- Complaint type now supports optional latitude/longitude
- AllIssuesPage now displays interactive map
- ReportIssuePage now includes location selector
- Sample data updated with 12 geolocated complaints

### Preserved Features
- ✅ All existing routes work
- ✅ Home dashboard
- ✅ Issue search and filtering
- ✅ Complaint tracking
- ✅ localStorage persistence
- ✅ Responsive design
- ✅ Accessibility

---

## 🌐 OpenStreetMap Attribution

The map uses OpenStreetMap tiles. Attribution is automatically included in the map footer:

```
© OpenStreetMap contributors
```

This satisfies the attribution requirement for OSM tile usage.

---

## 🔐 Data Privacy

- All data is stored locally in **browser localStorage**
- No data is sent to external servers
- Sample coordinates are **fictional demonstration data**
- User-submitted reports stay in browser only
- Coordinates are optional and user-controlled

---

## 🚀 Next Steps

After setup works:

1. **Explore the Map**
   - Go to `/issues`
   - Try clicking markers
   - Use filters
   - Try zooming and panning

2. **Test Location Selection**
   - Go to `/report`
   - Scroll to "Geographic Location" section
   - Click "Select Location on Map"
   - Click anywhere to select
   - Submit and check if it appears on map

3. **Customize**
   - Edit sample coordinates in `src/data/initialComplaints.ts`
   - Adjust map colors in `InfrastructureMap.tsx`
   - Change default map center/zoom
   - Add your own complaint data

4. **Connect Backend** (Later)
   - When ready, update `complaintService.ts`
   - Replace localStorage calls with API calls
   - Connect to your FastAPI backend
   - No UI changes needed!

---

## 📞 Support

If you encounter issues:

1. **Check browser console** (F12 → Console tab)
2. **Clear cache** and reload
3. **Delete node_modules** and run `npm install` again
4. **Check Leaflet docs** at https://leafletjs.com/

---

## ✨ Summary

You now have a fully functional React + Leaflet application with:
- ✅ Interactive infrastructure complaint map
- ✅ Location selection during reporting
- ✅ Full integration with existing features
- ✅ Sample data with coordinates
- ✅ Responsive design
- ✅ TypeScript support

**Ready to build civic-tech solutions!** 🎉
