# CivicPulse AI — Quick Start (5 minutes)

Get the entire system running in 5 minutes.

## Step 1: Start Frontend (Terminal 1)

```bash
cd c:\seva_hackthon\frontend
npm install
npm run dev
```

✅ Frontend runs on: **http://localhost:5173**

## Step 2: Start Backend (Terminal 2)

```bash
cd c:\seva_hackthon\civicpulse-backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 9000
```

✅ Backend runs on: **http://127.0.0.1:9000**

## Step 3: Access the App

Open browser and go to: **http://localhost:5173**

### Try These Workflows:

**Workflow 1: Report an Issue**
1. Click "Report Issue"
2. Fill the form:
   - Title: "Broken Streetlight on Main St"
   - Category: "Streetlight"
   - Description: "Light is completely dark at night"
3. Click "Submit"
4. Get complaint ID (e.g., `CBE-2026-001`)

**Workflow 2: Track the Complaint**
1. Click "Track Complaint"
2. Enter complaint ID from above
3. View:
   - AI priority score (e.g., 87/100)
   - Current status (Open/In Progress/Resolved)
   - All details

**Workflow 3: View Dashboard**
1. Click "Dashboard"
2. See:
   - Interactive map with all complaints
   - Real-time statistics (total, open, high priority)
   - Filter by priority or status
   - Color-coded markers (red=high, green=resolved)

**Workflow 4: Browse All Issues**
1. Click "All Issues"
2. See paginated list of all complaints
3. Click any complaint for details

## Configuration

### Change Backend URL

If backend is on different machine/port:

Edit `c:\seva_hackthon\frontend\.env.local`:
```env
VITE_API_BASE_URL=http://your-backend-ip:9000
```

Restart frontend with `npm run dev`

## Common Issues

### ❌ "Cannot connect to backend"
```bash
# Verify backend is running:
curl http://127.0.0.1:9000/api/complaints

# If fails, backend not running. Run Step 2 above.
```

### ❌ "Map won't load"
```
Check internet connection (Leaflet needs CDN access)
Open DevTools (F12) → Console for errors
```

### ❌ "npm command not found"
```
Install Node.js from nodejs.org
Restart terminal after install
```

### ❌ "Python not found"
```
Install Python 3.10+
Restart terminal after install
```

## Production Build

```bash
cd c:\seva_hackthon\frontend
npm run build
npm run preview
```

Creates optimized `dist/` folder. Use for hosting.

## Stop Services

Press `Ctrl+C` in each terminal to stop frontend/backend.

---

**Done!** You now have a fully functional CivicPulse AI system.

Report issues → AI priority evaluation → Dashboard tracking → Status updates.

Enjoy! 🚀
