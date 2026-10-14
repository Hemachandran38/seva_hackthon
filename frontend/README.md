# CivicPulse AI — React Frontend

The unified, production-ready React frontend for the CivicPulse AI infrastructure management system.

## Quick Start

### Prerequisites
- Node.js 18+ 
- npm 9+

### Setup

```bash
# Navigate to frontend directory
cd c:\seva_hackthon\frontend

# Install dependencies
npm install

# Start development server (runs on http://localhost:5173)
npm run dev

# Build for production
npm build
```

### Backend Configuration

The frontend connects to the backend API. Configure the connection in `.env.local`:

```env
VITE_API_BASE_URL=http://127.0.0.1:9000
```

**Default:** `http://127.0.0.1:9000` (localhost backend on port 9000)

If your backend is on a different machine or port, update this variable.

## Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── common/         # Shared UI components (Header, Footer, etc.)
│   │   ├── layout/         # Layout components (PublicLayout)
│   │   └── map/            # Interactive map components
│   ├── pages/              # Page components (routes)
│   │   ├── HomePage.tsx
│   │   ├── ReportIssuePage.tsx
│   │   ├── TrackComplaintPage.tsx
│   │   ├── AllIssuesPage.tsx
│   │   ├── DashboardPage.tsx
│   │   └── NotFoundPage.tsx
│   ├── services/           # API services
│   │   └── api.ts          # Backend API client
│   ├── types/              # TypeScript type definitions
│   ├── styles/             # Global CSS
│   │   ├── tokens.css      # Design tokens (colors, spacing)
│   │   ├── global.css      # Global styles
│   │   └── components.css  # Component-specific styles
│   ├── utils/              # Utility functions
│   ├── App.tsx             # Main app component
│   ├── main.tsx            # React entry point
│   └── vite-env.d.ts       # Vite type definitions
├── index.html              # HTML template
├── package.json            # Dependencies and scripts
├── vite.config.ts          # Vite configuration
├── tsconfig.json           # TypeScript configuration
└── .env.local              # Local environment variables (not in git)
```

## Features

### Pages

1. **Home Page** (`/`)
   - Overview of the system
   - Call to action for reporting issues

2. **Report Issue** (`/report`)
   - Form to submit new complaints
   - Category selection (Electrical, Drainage, Road, Streetlight, Public)
   - Location picker with map
   - Description input

3. **Track Complaint** (`/track`)
   - Search for complaint by ID
   - View real-time status updates
   - Track AI priority evaluation

4. **All Issues** (`/issues`)
   - Browse all reported issues
   - Filter by priority and status
   - Pagination support

5. **Dashboard** (`/dashboard`)
   - Interactive map visualization
   - Real-time statistics
   - Filter and drill-down capabilities
   - AI-evaluated priority scores

### API Integration

The frontend connects to the backend API for all data operations:

- **Base URL:** `http://127.0.0.1:9000`
- **Endpoints used:**
  - `GET /api/complaints` — List complaints
  - `POST /api/complaints` — Create complaint
  - `GET /api/complaints/{id}` — Get complaint details
  - `PUT /api/complaints/{id}/status` — Update status
  - `GET /api/dashboard/stats` — Dashboard statistics
  - `GET /api/dashboard/map-data` — Map data with filters

See `src/services/api.ts` for full API client.

## Development

### Adding a New Page

1. Create a new file in `src/pages/MyPage.tsx`:

```typescript
import React from 'react';

export function MyPage() {
  return (
    <div>
      <h1>My New Page</h1>
    </div>
  );
}
```

2. Add route to `src/App.tsx`:

```typescript
import { MyPage } from './pages/MyPage';

<Route path="mypage" element={<MyPage />} />
```

3. Visit `http://localhost:5173/mypage`

### Adding a Component

1. Create file in `src/components/mycomponent/MyComponent.tsx`
2. Export from `src/components/index.ts` (if applicable)
3. Import and use in pages

### Styling

- Global styles: `src/styles/global.css`
- Design tokens: `src/styles/tokens.css` (colors, spacing, etc.)
- Component styles: Inline CSS Modules or `src/styles/components.css`

### Environment Variables

Create `.env.local` in the frontend root:

```env
# Backend API base URL
VITE_API_BASE_URL=http://127.0.0.1:9000

# Optional: analytics or other services
VITE_APP_NAME=CivicPulse AI
```

## Deployment

### Development
```bash
npm run dev
```
Runs on `http://localhost:5173` with hot module reload.

### Production Build
```bash
npm run build
```
Creates optimized bundle in `dist/` directory.

### Preview Production Build
```bash
npm run preview
```
Runs the production build locally to verify it works.

### Deploy to Hosting
The `dist/` folder can be deployed to any static hosting service:
- Netlify
- Vercel
- AWS S3 + CloudFront
- GitHub Pages
- Apache/Nginx

Just ensure CORS is configured on the backend to allow requests from your frontend domain.

## Troubleshooting

### "Cannot find module" errors
```bash
npm install
```

### Backend connection fails
- Verify backend is running: `http://127.0.0.1:9000/api/complaints`
- Check `VITE_API_BASE_URL` in `.env.local`
- Verify CORS headers in backend (backend is configured for `http://localhost:5173`)

### Map doesn't load
- Check internet connection (Leaflet and tiles are from CDN)
- Browser console for errors (F12 → Console)
- Verify Leaflet is loaded: `L` in console

### TypeScript errors
```bash
npm run typecheck
```

## Tech Stack

- **Framework:** React 18.3 with TypeScript
- **Build Tool:** Vite 6
- **Routing:** React Router v7
- **Maps:** Leaflet + React Leaflet
- **UI Icons:** Lucide React
- **Styling:** CSS 3 with design tokens

## Performance Optimization

- Code splitting via Vite
- Lazy-loaded routes
- Optimized images
- CSS minification
- Tree-shaking of unused code

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Create a feature branch
2. Make changes in `src/`
3. Test locally with `npm run dev`
4. Build for production with `npm run build`
5. Submit PR

## License

Part of CivicPulse AI project — Seva Hackathon 2026

## Support

For issues, questions, or contributions, refer to the main project README.
