# Frontend Code Structure & Navigation Guide

This guide helps developers understand the React frontend codebase and navigate it efficiently.

## Directory Tree

```
frontend/
├── src/
│   ├── pages/                      # Page components (routes)
│   │   ├── HomePage.tsx            # Landing page
│   │   ├── ReportIssuePage.tsx      # Submit new complaint form
│   │   ├── TrackComplaintPage.tsx   # Track complaint by ID
│   │   ├── AllIssuesPage.tsx        # Browse all complaints
│   │   ├── DashboardPage.tsx        # Main dashboard with map
│   │   └── NotFoundPage.tsx         # 404 page
│   │
│   ├── components/
│   │   ├── layout/
│   │   │   └── PublicLayout.tsx     # Main layout (header, footer, sidebar)
│   │   │
│   │   ├── common/
│   │   │   ├── Header.tsx           # Top navigation bar
│   │   │   ├── Footer.tsx           # Footer with links/info
│   │   │   ├── Button.tsx           # Reusable button component
│   │   │   ├── Card.tsx             # Reusable card component
│   │   │   ├── Badge.tsx            # Status/priority badges
│   │   │   ├── MetricCard.tsx        # Dashboard metric display
│   │   │   └── LoadingSpinner.tsx    # Loading indicator
│   │   │
│   │   └── map/
│   │       ├── InteractiveMap.tsx    # Leaflet map wrapper
│   │       ├── MapControls.tsx       # Map filter controls
│   │       ├── MapMarker.tsx         # Individual complaint marker
│   │       └── MapLegend.tsx         # Map key/legend
│   │
│   ├── services/
│   │   └── api.ts                   # Backend API client
│   │       ├── getComplaints()
│   │       ├── createComplaint()
│   │       ├── getComplaintById()
│   │       ├── getDashboardStats()
│   │       └── ...more
│   │
│   ├── types/
│   │   ├── complaint.ts             # Complaint interface
│   │   ├── priority.ts              # Priority type definitions
│   │   ├── status.ts                # Status type definitions
│   │   └── api.ts                   # API response types
│   │
│   ├── utils/
│   │   ├── formatters.ts            # Format dates, numbers, etc.
│   │   ├── validators.ts            # Form validation helpers
│   │   ├── constants.ts             # App constants
│   │   └── helpers.ts               # General utilities
│   │
│   ├── styles/
│   │   ├── tokens.css               # Design tokens (colors, spacing)
│   │   ├── global.css               # Global layout & typography
│   │   └── components.css           # Component-specific styles
│   │
│   ├── data/
│   │   └── demo.ts                  # Demo/sample data (optional)
│   │
│   ├── App.tsx                      # Route definitions
│   ├── main.tsx                     # React entry point
│   └── vite-env.d.ts                # Vite type declarations
│
├── public/                          # Static assets (if any)
├── dist/                            # Build output (generated)
├── node_modules/                    # Dependencies
├── index.html                       # HTML template
├── package.json                     # Dependencies & scripts
├── vite.config.ts                   # Vite configuration
├── tsconfig.json                    # TypeScript configuration
├── .env.local                       # Local environment (not in git)
├── README.md                        # User-friendly guide
├── QUICK_START.md                   # 5-minute setup
├── UNIFIED_FRONTEND_GUIDE.md        # Architecture & deployment
└── FRONTEND_STRUCTURE.md            # This file
```

## Key Files Explained

### `src/App.tsx`
The main app component. Defines all routes and layout.

```typescript
<Route element={<PublicLayout/>}>
  <Route index element={<HomePage/>} />
  <Route path="report" element={<ReportIssuePage/>} />
  <Route path="dashboard" element={<DashboardPage/>} />
  ...
</Route>
```

### `src/main.tsx`
Entry point for React. Don't modify unless needed.

### `src/services/api.ts`
**Most important file for backend integration.**

All backend communication happens here:
- `getComplaints()` → `GET /api/complaints`
- `createComplaint(data)` → `POST /api/complaints`
- `getComplaintById(id)` → `GET /api/complaints/{id}`
- etc.

**Usage:**
```typescript
import { apiClient } from '@/services/api';

const complaints = await apiClient.getComplaints();
```

### `src/types/complaint.ts`
TypeScript interface for complaint data.

```typescript
interface Complaint {
  id: string;
  title: string;
  category: string;
  priority: Priority;
  status: Status;
  description: string;
  // ...
}
```

### `src/styles/tokens.css`
Design tokens — colors, spacing, fonts.

```css
--color-primary: #1a56db;
--color-high: #e53e3e;
--color-medium: #dd6b20;
--color-low: #3182ce;
--color-resolved: #38a169;
```

Change these to update the entire app's look & feel.

## Data Flow Examples

### Adding a New Feature

**Scenario:** Add "Export to Excel" button on dashboard.

1. **Add API method** in `src/services/api.ts`:
   ```typescript
   export async function exportToExcel(): Promise<Blob> {
     const response = await fetch(`${BASE_URL}/api/complaints/export`);
     return response.blob();
   }
   ```

2. **Add type** in `src/types/api.ts`:
   ```typescript
   interface ExportResponse {
     filename: string;
     size: number;
   }
   ```

3. **Create component** in `src/components/common/ExportButton.tsx`:
   ```typescript
   export function ExportButton() {
     const handleExport = async () => {
       const blob = await exportToExcel();
       // Download logic...
     };
     return <button onClick={handleExport}>Export</button>;
   }
   ```

4. **Add to page** in `src/pages/DashboardPage.tsx`:
   ```typescript
   import { ExportButton } from '@/components/common/ExportButton';
   
   export function DashboardPage() {
     return (
       <>
         <ExportButton />
         {/* ...rest of dashboard */}
       </>
     );
   }
   ```

### Fetching Data

```typescript
import { useEffect, useState } from 'react';
import { apiClient } from '@/services/api';
import { Complaint } from '@/types/complaint';

export function ComplaintList() {
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const data = await apiClient.getComplaints();
        setComplaints(data);
      } catch (error) {
        console.error('Failed to fetch complaints:', error);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) return <div>Loading...</div>;
  
  return (
    <div>
      {complaints.map(complaint => (
        <div key={complaint.id}>{complaint.title}</div>
      ))}
    </div>
  );
}
```

### Displaying on Map

Map component reads data and renders Leaflet markers:

```typescript
import { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';

export function InteractiveMap({ complaints }) {
  return (
    <MapContainer center={[11.0168, 76.9558]} zoom={13}>
      <TileLayer url="https://server.arcgisonline.com/..." />
      {complaints.map(complaint => (
        <Marker
          key={complaint.id}
          position={[complaint.latitude, complaint.longitude]}
          icon={createIcon(complaint.priority)}
        >
          <Popup>{complaint.title}</Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
```

## Component Communication

```
HomePage
  ↓
Navigation Link
  ↓
ReportIssuePage (or other page)
  ↓
Form Input
  ↓
apiClient.createComplaint()
  ↓
Backend /api/complaints
  ↓
Response to frontend
  ↓
Success message & redirect
```

## State Management

Currently using React hooks (useState, useEffect). For larger apps, consider:
- **React Query** — for server state (API data)
- **Context API** — for app state
- **Redux** — for complex state

## Styling Approach

1. **Global CSS** — `src/styles/global.css`
   - Layout, typography, colors
   - Applied to all pages

2. **Component CSS** — `src/styles/components.css`
   - `.complaint-card`, `.filter-chip`, etc.
   - Scoped by class name

3. **Inline Styles** — For dynamic styling
   ```typescript
   <div style={{ backgroundColor: getColorForPriority(priority) }}>
   ```

4. **Design Tokens** — `src/styles/tokens.css`
   - CSS variables (--color-primary, --radius-md, etc.)
   - Centralized theme values

## Environment Variables

Create `.env.local` in root:

```env
# Backend base URL
VITE_API_BASE_URL=http://127.0.0.1:9000

# App metadata
VITE_APP_NAME=CivicPulse AI
VITE_APP_VERSION=1.0.0
```

**Usage in code:**
```typescript
const apiUrl = import.meta.env.VITE_API_BASE_URL;
```

## Debugging

### Browser DevTools

**F12 → Console:**
```javascript
// Test API directly
fetch('http://127.0.0.1:9000/api/complaints')
  .then(r => r.json())
  .then(console.log)
```

**F12 → Network:**
- See all API requests
- Check response status & body
- Verify CORS headers

**F12 → React DevTools:**
- Inspect component tree
- View component props & state
- Profile performance

### Console Logging

```typescript
import { Complaint } from '@/types/complaint';

const complaint: Complaint = {...};
console.log('Complaint:', complaint);  // See full object
console.log('Priority:', complaint.priority);  // See specific field
```

### Common Errors

| Error | Cause | Fix |
|---|---|---|
| `Cannot read property 'title' of undefined` | Data not loaded yet | Use optional chaining: `complaint?.title` |
| `GET http://127.0.0.1:9000... failed (net::ERR_CONNECTION_REFUSED)` | Backend not running | Run backend on port 9000 |
| `CORS error` | Frontend/backend on different origins | Check backend CORS config |
| `Module not found '@/services/api'` | TypeScript alias not set | Check `vite.config.ts` |

## Performance Tips

1. **Lazy load pages:**
   ```typescript
   const DashboardPage = lazy(() => import('@/pages/DashboardPage'));
   ```

2. **Memoize expensive components:**
   ```typescript
   export const MapMarker = memo(function MapMarker({ ... }) { ... });
   ```

3. **Cache API responses:**
   ```typescript
   const [cache, setCache] = useState({});
   if (cache.complaints) return cache.complaints;
   ```

4. **Optimize re-renders:**
   ```typescript
   const memoizedComplaints = useMemo(() => complaints.filter(...), [complaints]);
   ```

## Testing (Optional)

Add tests with Vitest:

```typescript
// ComplaintList.test.tsx
import { render, screen } from '@testing-library/react';
import { ComplaintList } from './ComplaintList';

test('renders complaint list', async () => {
  render(<ComplaintList />);
  expect(screen.getByText(/complaints/i)).toBeInTheDocument();
});
```

## IDE Setup (VS Code)

Recommended extensions:
- **ES7+ React/Redux/React-Native snippets** — Code generation
- **Prettier** — Code formatting
- **ESLint** — Code quality
- **Thunder Client** — API testing (alternative to Postman)

## Deployment Checklist

- [ ] Environment variables set
- [ ] Backend URL correct
- [ ] `npm run build` succeeds
- [ ] `npm run preview` works
- [ ] All pages load without errors
- [ ] Map displays correctly
- [ ] API calls return data
- [ ] Dashboard stats accurate
- [ ] Forms submit successfully
- [ ] Responsive on mobile

## Next Steps

1. **Understand the pages** — Open each `.tsx` file in `src/pages/`
2. **Explore components** — Check `src/components/`
3. **Review API client** — Study `src/services/api.ts`
4. **Run locally** — `npm run dev`
5. **Make changes** — Experiment with components
6. **Deploy** — `npm run build` → Host the `dist/` folder

---

**Happy coding!** 🚀

For questions, refer to README.md or QUICK_START.md.
