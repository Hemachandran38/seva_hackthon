# Frontend Integration Guide

This guide explains how to integrate the CivicPulse AI React frontend with the backend API.

## Quick Start

### 1. Backend Setup

Ensure the backend is running:

```bash
cd civicpulse-backend
source venv/bin/activate  # or venv\Scripts\Activate.ps1 on Windows
uvicorn app.main:app --reload
```

Backend will be available at: `http://localhost:8000`

### 2. Frontend CORS Configuration

The backend is pre-configured for the React dev server at `http://localhost:5173`. 

No frontend configuration needed for local development!

### 3. API Base URL

Set your API base URL in the React frontend:

```typescript
const API_BASE_URL = "http://localhost:8000";
```

---

## API Integration Patterns

### Creating a Complaint

**Frontend sends:**
```typescript
const complaintData = {
  title: "Broken streetlight",
  description: "The streetlight at main junction is not working",
  category: "Streetlight",
  location_text: "Main Junction, Ward 12",
  latitude: 22.3152,
  longitude: 73.1856,
  ward: "Ward 12",
  asset_id: null,
  image_reference: null
};

fetch("http://localhost:8000/api/complaints", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(complaintData)
})
.then(r => r.json())
.then(complaint => {
  // complaint.id will be auto-generated (e.g., "CP-2026-0001")
  console.log("Created complaint:", complaint.id);
});
```

**Backend returns:**
```json
{
  "id": "CP-2026-0001",
  "title": "Broken streetlight",
  "status": "Reported",
  "priority": "Medium",
  "priority_score": 50,
  "reported_at": "2026-01-14T10:35:00",
  "timeline_entries": [
    {
      "status": "Reported",
      "note": "Complaint received",
      "timestamp": "2026-01-14T10:35:00"
    }
  ]
}
```

### Listing Complaints with Filters

```typescript
// Get high-priority complaints in Ward 12
fetch("http://localhost:8000/api/complaints?priority=High&ward=Ward%2012&limit=20")
  .then(r => r.json())
  .then(data => {
    console.log(`Found ${data.total} complaints`);
    console.log(`Showing ${data.items.length} items (page 1)`);
  });
```

### Updating Complaint Priority

```typescript
const updateData = {
  priority: "Critical",
  priority_score: 90,
  assigned_team: "Emergency Response Team"
};

fetch("http://localhost:8000/api/complaints/CP-2026-0001", {
  method: "PATCH",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(updateData)
})
.then(r => r.json())
.then(complaint => console.log("Updated:", complaint));
```

### Updating Complaint Status

Status updates have strict validation:

```typescript
const statusUpdate = {
  status: "Under Review",
  note: "Team is looking into this"
};

fetch("http://localhost:8000/api/complaints/CP-2026-0001/status", {
  method: "PATCH",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(statusUpdate)
})
.then(r => {
  if (r.status === 400) {
    // Invalid transition
    return r.json().then(err => {
      console.error("Invalid status transition:", err.detail);
    });
  }
  return r.json();
})
.then(complaint => console.log("Status updated:", complaint.status));
```

### Creating a Repair Record

```typescript
const repairData = {
  assigned_team: "Maintenance Team A",
  description: "Replaced broken LED bulb",
  repair_date: new Date().toISOString()
};

fetch("http://localhost:8000/api/complaints/CP-2026-0001/repairs", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(repairData)
})
.then(r => r.json())
.then(repair => {
  console.log("Repair record created:", repair.id);
  // repair.id will be like "RP-20260114-0001"
});
```

### Verifying Repair Completion

```typescript
const verifyData = {
  verification_status: "Verified",
  evidence_reference: "https://s3.example.com/photos/repair-001.jpg",
  verified_by: "Inspector A"
};

fetch("http://localhost:8000/api/complaints/CP-2026-0001/repairs/RP-20260114-0001/verify", {
  method: "PATCH",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(verifyData)
})
.then(r => r.json())
.then(repair => console.log("Repair verified:", repair));

// Then separately update complaint status to Resolved
const statusUpdate = { status: "Resolved" };
fetch("http://localhost:8000/api/complaints/CP-2026-0001/status", {
  method: "PATCH",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(statusUpdate)
})
.then(r => r.json())
.then(complaint => console.log("Complaint resolved"));
```

### Getting Complaint Timeline

```typescript
fetch("http://localhost:8000/api/complaints/CP-2026-0001/timeline")
  .then(r => r.json())
  .then(timeline => {
    // Array of status changes chronologically
    console.log("Status history:", timeline);
  });
```

### Getting Complaint Audit History

```typescript
fetch("http://localhost:8000/api/complaints/CP-2026-0001/history?limit=50")
  .then(r => r.json())
  .then(data => {
    console.log("Audit entries:", data.items);
    console.log("Total actions:", data.total);
  });
```

---

## Data Mapping Reference

### Status Mapping

| Backend | Frontend | Description |
|---------|----------|-------------|
| `Reported` | Open | Newly reported |
| `Under Review` | In Review | Being reviewed |
| `Assigned` | Assigned | Assigned to team |
| `In Progress` | In Progress | Work underway |
| `Awaiting Verification` | Pending Verification | Waiting for verification |
| `Resolved` | Closed | Fixed and verified |

### Priority Mapping

| Backend | Frontend |
|---------|----------|
| `Low` | `"Low"` |
| `Medium` | `"Medium"` |
| `High` | `"High"` |
| `Critical` | `"Critical"` |

### Category Mapping

Backend uses the same categories as frontend:
- "Streetlight"
- "Road & pavement"
- "Drainage"
- "Public space"
- "Electrical Hazard"

---

## Common Frontend Patterns

### React Hook for Fetching Complaints

```typescript
import { useState, useEffect } from 'react';

function useComplaints(filter = {}) {
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const params = new URLSearchParams({
      skip: filter.skip || 0,
      limit: filter.limit || 10,
      ...(filter.status && { status: filter.status }),
      ...(filter.priority && { priority: filter.priority }),
      ...(filter.ward && { ward: filter.ward }),
    });

    fetch(`http://localhost:8000/api/complaints?${params}`)
      .then(r => {
        if (!r.ok) throw new Error(`API error: ${r.status}`);
        return r.json();
      })
      .then(data => {
        setComplaints(data.items);
        setError(null);
      })
      .catch(err => {
        setError(err.message);
        setComplaints([]);
      })
      .finally(() => setLoading(false));
  }, [filter]);

  return { complaints, loading, error };
}

// Usage:
const { complaints, loading, error } = useComplaints({ 
  priority: 'High',
  limit: 20 
});
```

### React Hook for Updating Status

```typescript
async function updateComplaintStatus(complaintId, newStatus, note = "") {
  const response = await fetch(
    `http://localhost:8000/api/complaints/${complaintId}/status`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        status: newStatus,
        note: note
      })
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to update status");
  }

  return response.json();
}

// Usage:
try {
  const updated = await updateComplaintStatus("CP-2026-0001", "Under Review");
  console.log("Status updated to:", updated.status);
} catch (error) {
  console.error("Update failed:", error.message);
  // Show error to user
}
```

---

## Error Handling

The backend returns consistent error responses:

```typescript
async function handleApiError(response) {
  if (response.ok) return response.json();

  const error = await response.json();
  
  switch (response.status) {
    case 400:
      // Bad request - validation error or invalid transition
      console.error("Invalid request:", error.detail);
      throw new Error(error.detail);
    
    case 404:
      // Not found
      console.error("Resource not found:", error.detail);
      throw new Error("The requested item was not found");
    
    case 422:
      // Validation error
      console.error("Validation failed:", error.detail);
      throw new Error("Please check your input");
    
    default:
      throw new Error(`API error: ${response.status}`);
  }
}
```

---

## Testing the Integration

### 1. Check Backend Health

```typescript
fetch("http://localhost:8000/health")
  .then(r => r.json())
  .then(data => console.log("Backend status:", data));
```

### 2. Create Test Complaint

```typescript
fetch("http://localhost:8000/api/complaints", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    title: "Test Issue",
    description: "This is a test complaint from frontend",
    category: "Streetlight",
    location_text: "Test Location",
    ward: "Ward 1"
  })
})
.then(r => r.json())
.then(data => console.log("Test complaint created:", data.id));
```

### 3. Verify CORS

Open browser DevTools and check Network tab. The response should include:
```
Access-Control-Allow-Origin: http://localhost:5173
Access-Control-Allow-Methods: GET, POST, PATCH, PUT, DELETE, OPTIONS
```

---

## Environment Variables

For production deployment, configure these environment variables on the backend:

```
ALLOWED_ORIGINS=["https://app.example.com", "https://www.example.com"]
ENVIRONMENT=production
DEBUG=false
```

Then in React frontend:

```typescript
const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";
```

---

## Production Considerations

### Before Going to Production

1. **Switch to PostgreSQL:**
   ```
   DATABASE_URL=postgresql://user:pass@localhost/civicpulse
   ```

2. **Enable Authentication** (Phase 2+):
   - Implement JWT tokens
   - Restrict verification endpoints to authorized users
   - Add role-based access control

3. **Set CORS appropriately:**
   ```
   ALLOWED_ORIGINS=["https://yourdomain.com"]
   ```

4. **Enable HTTPS:**
   - Use proper SSL certificates
   - Update CORS origins to `https://`

5. **Set DEBUG=false:**
   ```
   ENVIRONMENT=production
   DEBUG=false
   ```

6. **Set strong SECRET_KEY** (when implemented)

### Deployment

The backend can be deployed to:
- **Heroku**: `Procfile` included
- **AWS**: Lambda, EC2, or ECS
- **Google Cloud**: Cloud Run or App Engine
- **Docker**: See Dockerfile (to be created in Phase 2)
- **Nginx + Gunicorn**: Traditional server deployment

---

## Troubleshooting

### CORS Errors

**Error:** `Access to XMLHttpRequest has been blocked by CORS policy`

**Solution:**
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check frontend URL matches CORS configuration
3. Check browser console for exact error message
4. Ensure request includes `Content-Type: application/json` header

### 404 Errors

**Error:** `Complaint CP-2026-9999 not found`

**Solution:**
1. Verify complaint ID is correct
2. Use `/api/complaints` to list all complaints
3. Check if data was created in the current session

### Status Transition Errors

**Error:** `Invalid status transition: Reported → In Progress`

**Solution:**
Review the [Status Workflows](./API_DOCUMENTATION.md#status-workflows) section in API_DOCUMENTATION.md for valid transitions.

---

## Support

For integration questions:
1. Review this guide
2. Check API_DOCUMENTATION.md for endpoint details
3. Use Swagger UI at `http://localhost:8000/docs`
4. Review React test files in `civicpulse/frontend-react/`
5. Check backend test files in `tests/test_endpoints.py`

