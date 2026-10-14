# CivicPulse AI Backend - Complete API Documentation

## Overview

This document describes all available API endpoints for the CivicPulse AI Backend Phase 1. The backend provides a comprehensive REST API for managing infrastructure complaints, assets, repairs, and audit trails.

**Base URL:** `http://localhost:8000`  
**Documentation UI:** `http://localhost:8000/docs` (Swagger)  
**ReDoc:** `http://localhost:8000/redoc`

---

## Table of Contents

1. [Core Endpoints](#core-endpoints)
2. [Asset Management](#asset-management)
3. [Complaint Management](#complaint-management)
4. [Repair Tracking](#repair-tracking)
5. [History & Audit](#history--audit)
6. [Status Workflows](#status-workflows)
7. [Error Handling](#error-handling)
8. [Data Models](#data-models)

---

## Core Endpoints

### Root Endpoint

**GET** `/`

Returns API information.

**Response (200 OK):**
```json
{
  "message": "CivicPulse AI Backend",
  "version": "0.1.0",
  "docs": "http://localhost:8000/docs"
}
```

### Health Check

**GET** `/health`

Service health status.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "CivicPulse AI Backend"
}
```

---

## Asset Management

### List Assets

**GET** `/api/assets`

List all infrastructure assets with pagination and filtering.

**Query Parameters:**
- `skip` (integer, default: 0) - Number of items to skip
- `limit` (integer, default: 10, max: 100) - Number of items to return
- `ward` (string, optional) - Filter by ward
- `asset_type` (string, optional) - Filter by asset type

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "SL-W12-001",
      "asset_type": "Streetlight",
      "name": "Main Junction Light",
      "ward": "Ward 12",
      "latitude": 22.3152,
      "longitude": 73.1856,
      "installation_date": "2023-01-15T10:00:00",
      "condition": "Good",
      "created_at": "2026-01-10T08:00:00",
      "updated_at": "2026-01-10T08:00:00"
    }
  ],
  "total": 42,
  "skip": 0,
  "limit": 10
}
```

### Get Asset

**GET** `/api/assets/{asset_id}`

Retrieve a specific asset by ID.

**Path Parameters:**
- `asset_id` (string, required) - Asset identifier

**Response (200 OK):**
```json
{
  "id": "SL-W12-001",
  "asset_type": "Streetlight",
  "name": "Main Junction Light",
  "ward": "Ward 12",
  "latitude": 22.3152,
  "longitude": 73.1856,
  "installation_date": "2023-01-15T10:00:00",
  "condition": "Good",
  "created_at": "2026-01-10T08:00:00",
  "updated_at": "2026-01-10T08:00:00"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Asset SL-W12-999 not found"
}
```

### Create Asset

**POST** `/api/assets`

Create a new infrastructure asset.

**Request Body:**
```json
{
  "id": "SL-W12-001",
  "asset_type": "Streetlight",
  "name": "Main Junction Light",
  "ward": "Ward 12",
  "latitude": 22.3152,
  "longitude": 73.1856,
  "installation_date": "2023-01-15T10:00:00",
  "condition": "Good"
}
```

**Response (201 Created):**
```json
{
  "id": "SL-W12-001",
  "asset_type": "Streetlight",
  "name": "Main Junction Light",
  "ward": "Ward 12",
  "latitude": 22.3152,
  "longitude": 73.1856,
  "installation_date": "2023-01-15T10:00:00",
  "condition": "Good",
  "created_at": "2026-01-10T08:00:00",
  "updated_at": "2026-01-10T08:00:00"
}
```

### Update Asset (PATCH)

**PATCH** `/api/assets/{asset_id}`

Update specific asset fields.

**Path Parameters:**
- `asset_id` (string, required) - Asset identifier

**Request Body (any combination of fields):**
```json
{
  "name": "Updated Name",
  "condition": "Poor",
  "latitude": 22.3200,
  "longitude": 73.1900
}
```

**Response (200 OK):**
```json
{
  "id": "SL-W12-001",
  "asset_type": "Streetlight",
  "name": "Updated Name",
  "ward": "Ward 12",
  "latitude": 22.3200,
  "longitude": 73.1900,
  "installation_date": "2023-01-15T10:00:00",
  "condition": "Poor",
  "created_at": "2026-01-10T08:00:00",
  "updated_at": "2026-01-14T10:30:00"
}
```

---

## Complaint Management

### List Complaints

**GET** `/api/complaints`

List all complaints with pagination and filtering.

**Query Parameters:**
- `skip` (integer, default: 0) - Number of items to skip
- `limit` (integer, default: 10, max: 100) - Number of items to return
- `status` (string, optional) - Filter by status
- `priority` (string, optional) - Filter by priority
- `category` (string, optional) - Filter by category
- `ward` (string, optional) - Filter by ward

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "CP-2026-0001",
      "title": "Broken streetlight",
      "description": "Streetlight at main junction not working",
      "category": "Streetlight",
      "location_text": "Main Junction, Ward 12",
      "latitude": 22.3152,
      "longitude": 73.1856,
      "ward": "Ward 12",
      "priority": "High",
      "priority_score": 75,
      "status": "Assigned",
      "repeat_complaint_count": 2,
      "asset_id": "SL-W12-001",
      "assigned_team": "Maintenance Team A",
      "image_reference": null,
      "reported_at": "2026-01-10T09:30:00",
      "updated_at": "2026-01-11T14:00:00",
      "timeline_entries": []
    }
  ],
  "total": 156,
  "skip": 0,
  "limit": 10
}
```

### Get Complaint

**GET** `/api/complaints/{complaint_id}`

Retrieve a specific complaint with all details.

**Path Parameters:**
- `complaint_id` (string, required) - Complaint ID (e.g., CP-2026-0001)

**Response (200 OK):**
```json
{
  "id": "CP-2026-0001",
  "title": "Broken streetlight",
  "description": "Streetlight at main junction not working",
  "category": "Streetlight",
  "location_text": "Main Junction, Ward 12",
  "latitude": 22.3152,
  "longitude": 73.1856,
  "ward": "Ward 12",
  "priority": "High",
  "priority_score": 75,
  "status": "Assigned",
  "repeat_complaint_count": 2,
  "asset_id": "SL-W12-001",
  "assigned_team": "Maintenance Team A",
  "image_reference": null,
  "reported_at": "2026-01-10T09:30:00",
  "updated_at": "2026-01-11T14:00:00",
  "timeline_entries": [
    {
      "status": "Reported",
      "note": "Complaint received",
      "timestamp": "2026-01-10T09:30:00"
    },
    {
      "status": "Under Review",
      "note": "Now reviewing",
      "timestamp": "2026-01-10T10:00:00"
    }
  ]
}
```

### Create Complaint

**POST** `/api/complaints`

Create a new complaint for an infrastructure issue.

**Request Body:**
```json
{
  "title": "Broken streetlight",
  "description": "Streetlight at main junction is not working for 2 weeks",
  "category": "Streetlight",
  "location_text": "Main Junction, Ward 12",
  "latitude": 22.3152,
  "longitude": 73.1856,
  "ward": "Ward 12",
  "asset_id": "SL-W12-001",
  "image_reference": null
}
```

**Response (201 Created):**
```json
{
  "id": "CP-2026-0157",
  "title": "Broken streetlight",
  "description": "Streetlight at main junction is not working for 2 weeks",
  "category": "Streetlight",
  "location_text": "Main Junction, Ward 12",
  "latitude": 22.3152,
  "longitude": 73.1856,
  "ward": "Ward 12",
  "priority": "Medium",
  "priority_score": 50,
  "status": "Reported",
  "repeat_complaint_count": 0,
  "asset_id": "SL-W12-001",
  "assigned_team": null,
  "image_reference": null,
  "reported_at": "2026-01-14T10:35:00",
  "updated_at": "2026-01-14T10:35:00",
  "timeline_entries": []
}
```

### Update Complaint Fields (PATCH)

**PATCH** `/api/complaints/{complaint_id}`

Update allowed complaint fields (not status - see Status Update endpoint below).

**Path Parameters:**
- `complaint_id` (string, required) - Complaint ID

**Request Body (any combination of fields):**
```json
{
  "priority": "Critical",
  "priority_score": 95,
  "assigned_team": "Team A",
  "repeat_complaint_count": 3
}
```

**Response (200 OK):**
```json
{
  "id": "CP-2026-0001",
  "title": "Broken streetlight",
  "description": "Streetlight at main junction is not working for 2 weeks",
  "category": "Streetlight",
  "location_text": "Main Junction, Ward 12",
  "latitude": 22.3152,
  "longitude": 73.1856,
  "ward": "Ward 12",
  "priority": "Critical",
  "priority_score": 95,
  "status": "Reported",
  "repeat_complaint_count": 3,
  "asset_id": "SL-W12-001",
  "assigned_team": "Team A",
  "image_reference": null,
  "reported_at": "2026-01-10T09:30:00",
  "updated_at": "2026-01-14T10:40:00",
  "timeline_entries": []
}
```

### Update Complaint Status

**PATCH** `/api/complaints/{complaint_id}/status`

Update complaint status with workflow validation. Status transitions are strictly controlled.

**Path Parameters:**
- `complaint_id` (string, required) - Complaint ID

**Request Body:**
```json
{
  "status": "Under Review",
  "note": "Team reviewing the issue"
}
```

**Response (200 OK):**
```json
{
  "id": "CP-2026-0001",
  "title": "Broken streetlight",
  "description": "Streetlight at main junction is not working for 2 weeks",
  "category": "Streetlight",
  "location_text": "Main Junction, Ward 12",
  "latitude": 22.3152,
  "longitude": 73.1856,
  "ward": "Ward 12",
  "priority": "Critical",
  "priority_score": 95,
  "status": "Under Review",
  "repeat_complaint_count": 3,
  "asset_id": "SL-W12-001",
  "assigned_team": "Team A",
  "image_reference": null,
  "reported_at": "2026-01-10T09:30:00",
  "updated_at": "2026-01-14T10:41:00",
  "timeline_entries": [
    {
      "status": "Reported",
      "note": "Complaint received",
      "timestamp": "2026-01-10T09:30:00"
    },
    {
      "status": "Under Review",
      "note": "Team reviewing the issue",
      "timestamp": "2026-01-14T10:41:00"
    }
  ]
}
```

**Response (400 Bad Request - Invalid Transition):**
```json
{
  "detail": "Invalid status transition: Reported → In Progress. Allowed: {'Under Review', 'Assigned'}"
}
```

---

## Repair Tracking

### Create Repair Record

**POST** `/api/complaints/{complaint_id}/repairs`

Create a repair record for a complaint.

**Path Parameters:**
- `complaint_id` (string, required) - Complaint ID

**Request Body:**
```json
{
  "assigned_team": "Maintenance Team A",
  "description": "Replaced broken bulb with new LED",
  "repair_date": "2026-01-12T14:30:00"
}
```

**Response (201 Created):**
```json
{
  "id": "RP-20260114-0042",
  "complaint_id": "CP-2026-0001",
  "assigned_team": "Maintenance Team A",
  "description": "Replaced broken bulb with new LED",
  "repair_date": "2026-01-12T14:30:00",
  "verification_status": "Pending",
  "evidence_reference": null,
  "verified_at": null,
  "verified_by": null,
  "created_at": "2026-01-14T10:42:00",
  "updated_at": "2026-01-14T10:42:00"
}
```

### Get Complaint Repairs

**GET** `/api/complaints/{complaint_id}/repairs`

List all repair records for a complaint.

**Path Parameters:**
- `complaint_id` (string, required) - Complaint ID

**Response (200 OK):**
```json
[
  {
    "id": "RP-20260114-0042",
    "complaint_id": "CP-2026-0001",
    "assigned_team": "Maintenance Team A",
    "description": "Replaced broken bulb with new LED",
    "repair_date": "2026-01-12T14:30:00",
    "verification_status": "Pending",
    "evidence_reference": null,
    "verified_at": null,
    "verified_by": null,
    "created_at": "2026-01-14T10:42:00",
    "updated_at": "2026-01-14T10:42:00"
  }
]
```

### Update Repair Progress

**PATCH** `/api/complaints/{complaint_id}/repairs/{repair_id}/progress`

Update repair work progress (repair date and description).

**Path Parameters:**
- `complaint_id` (string, required) - Complaint ID
- `repair_id` (string, required) - Repair record ID

**Request Body:**
```json
{
  "repair_date": "2026-01-13T16:00:00",
  "description": "Replaced LED bulb, tested working correctly"
}
```

**Response (200 OK):**
```json
{
  "id": "RP-20260114-0042",
  "complaint_id": "CP-2026-0001",
  "assigned_team": "Maintenance Team A",
  "description": "Replaced LED bulb, tested working correctly",
  "repair_date": "2026-01-13T16:00:00",
  "verification_status": "Pending",
  "evidence_reference": null,
  "verified_at": null,
  "verified_by": null,
  "created_at": "2026-01-14T10:42:00",
  "updated_at": "2026-01-14T10:45:00"
}
```

### Verify Repair Completion

**PATCH** `/api/complaints/{complaint_id}/repairs/{repair_id}/verify`

Verify or reject repair completion. **Note:** This marks the repair as verified but does NOT automatically resolve the complaint. You must separately update the complaint status to "Resolved".

**Path Parameters:**
- `complaint_id` (string, required) - Complaint ID
- `repair_id` (string, required) - Repair record ID

**Request Body:**
```json
{
  "verification_status": "Verified",
  "evidence_reference": "https://s3.example.com/photos/repair-001.jpg",
  "verified_by": "Inspector A"
}
```

**Response (200 OK):**
```json
{
  "id": "RP-20260114-0042",
  "complaint_id": "CP-2026-0001",
  "assigned_team": "Maintenance Team A",
  "description": "Replaced LED bulb, tested working correctly",
  "repair_date": "2026-01-13T16:00:00",
  "verification_status": "Verified",
  "evidence_reference": "https://s3.example.com/photos/repair-001.jpg",
  "verified_at": "2026-01-14T10:50:00",
  "verified_by": "Inspector A",
  "created_at": "2026-01-14T10:42:00",
  "updated_at": "2026-01-14T10:50:00"
}
```

**Valid verification_status values:** `Verified`, `Failed`, `Rejected`

---

## History & Audit

### Get Complaint Timeline

**GET** `/api/complaints/{complaint_id}/timeline`

Get the status change timeline for a complaint (chronological order).

**Path Parameters:**
- `complaint_id` (string, required) - Complaint ID

**Response (200 OK):**
```json
[
  {
    "status": "Reported",
    "note": "Complaint received",
    "timestamp": "2026-01-10T09:30:00"
  },
  {
    "status": "Under Review",
    "note": "Team reviewing the issue",
    "timestamp": "2026-01-10T10:00:00"
  },
  {
    "status": "Assigned",
    "note": "Status updated",
    "timestamp": "2026-01-11T08:00:00"
  },
  {
    "status": "In Progress",
    "note": "Work started",
    "timestamp": "2026-01-12T09:00:00"
  },
  {
    "status": "Awaiting Verification",
    "note": "Repair complete",
    "timestamp": "2026-01-14T10:00:00"
  }
]
```

### Get Complaint History

**GET** `/api/complaints/{complaint_id}/history`

Get complete audit history for a complaint (all actions: creation, status changes, assignments, repairs, verifications).

**Query Parameters:**
- `skip` (integer, default: 0) - Number of items to skip
- `limit` (integer, default: 100, max: 500) - Number of items to return

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": 1,
      "complaint_id": "CP-2026-0001",
      "repair_id": null,
      "action": "create",
      "actor": null,
      "source": "api",
      "old_value": null,
      "new_value": "Reported",
      "details": "Complaint created via API",
      "timestamp": "2026-01-10T09:30:00"
    },
    {
      "id": 2,
      "complaint_id": "CP-2026-0001",
      "repair_id": null,
      "action": "status_change",
      "actor": null,
      "source": "api",
      "old_value": "Reported",
      "new_value": "Under Review",
      "details": "Team reviewing the issue",
      "timestamp": "2026-01-10T10:00:00"
    },
    {
      "id": 3,
      "complaint_id": "CP-2026-0001",
      "repair_id": "RP-20260114-0042",
      "action": "repair_start",
      "actor": null,
      "source": "api",
      "old_value": null,
      "new_value": "RP-20260114-0042",
      "details": "Repair record created: Replaced broken bulb with new LED",
      "timestamp": "2026-01-12T10:00:00"
    },
    {
      "id": 4,
      "complaint_id": "CP-2026-0001",
      "repair_id": "RP-20260114-0042",
      "action": "verification",
      "actor": "Inspector A",
      "source": "api",
      "old_value": "Pending",
      "new_value": "Verified",
      "details": "Repair verification: Verified. Evidence: https://s3.example.com/photos/repair-001.jpg",
      "timestamp": "2026-01-14T10:50:00"
    }
  ],
  "total": 4,
  "skip": 0,
  "limit": 100
}
```

---

## Status Workflows

### Valid Status Transitions

The complaint status workflow is strictly controlled. Only specific transitions are allowed:

```
┌─────────────┐
│  Reported   │◄─────────────────────────────────────┐
└──────┬──────┘                                       │
       │                                              │
       ├──► Under Review ◄──────────────────────────┼─┐
       │         │                                    │ │
       │         ├──► Assigned ◄──────────────────┐ │ │
       │         │      │                          │ │ │
       │         │      ├──► In Progress ◄──────┬─┼─┤ │
       │         │      │       │                │ │ │ │
       │         │      │       └─► Awaiting    │ │ │ │
       │         │      │           Verification  │ │ │
       │         │      │           │             │ │ │ │
       │         │      └───────────┘             │ │ │ │
       │         │       │                        │ │ │ │
       │         │       └──────► Resolved ───────┴─┴─┘
       │         │                  │
       └─────────┴──────────────────┘
(Can re-open from any status back to Under Review)
```

**Valid Transitions:**
- `Reported` → `Under Review`, `Assigned`
- `Under Review` → `Assigned`, `Reported` (back)
- `Assigned` → `In Progress`, `Under Review` (back)
- `In Progress` → `Awaiting Verification`, `Assigned` (back)
- `Awaiting Verification` → `Resolved`, `In Progress` (back)
- `Resolved` → `Under Review` (re-open if needed)

---

## Error Handling

The API returns appropriate HTTP status codes and error messages.

### Common Error Responses

**400 Bad Request - Invalid Input:**
```json
{
  "detail": "Invalid priority value. Must be one of {'Low', 'Medium', 'High', 'Critical'}"
}
```

**400 Bad Request - Invalid Status Transition:**
```json
{
  "detail": "Invalid status transition: Reported → In Progress. Allowed: {'Under Review', 'Assigned'}"
}
```

**404 Not Found:**
```json
{
  "detail": "Complaint CP-2026-9999 not found"
}
```

**422 Unprocessable Entity - Validation Error:**
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "description"],
      "msg": "Field required",
      "input": {"title": "Issue"}
    }
  ]
}
```

---

## Data Models

### Asset Model

```typescript
interface Asset {
  id: string;                    // Unique ID (e.g., "SL-W12-001")
  asset_type: string;            // Type: Streetlight, Road & pavement, Drainage, etc
  name: string;                  // Human-readable name
  ward: string;                  // Ward identifier
  latitude?: number;             // -90 to 90
  longitude?: number;            // -180 to 180
  installation_date?: DateTime;  // When asset was installed
  condition: string;             // Good, Fair, Poor, Critical
  created_at: DateTime;          // When record was created
  updated_at: DateTime;          // When record was last updated
}
```

### Complaint Model

```typescript
interface Complaint {
  id: string;                      // Unique ID (e.g., "CP-2026-0001")
  title: string;                   // Issue title
  description: string;             // Detailed description
  category: string;                // Streetlight, Road & pavement, Drainage, etc
  location_text: string;           // Human-readable location
  latitude?: number;               // -90 to 90 (unverified)
  longitude?: number;              // -180 to 180 (unverified)
  ward?: string;                   // Ward identifier
  priority: string;                // Low, Medium, High, Critical
  priority_score: number;          // 0-100 numeric value
  status: string;                  // Current workflow status
  repeat_complaint_count: number;  // Times this issue reported
  asset_id?: string;               // Related asset
  assigned_team?: string;          // Team handling
  image_reference?: string;        // Image URL or reference
  reported_at: DateTime;           // When reported
  updated_at: DateTime;            // When last updated
  timeline_entries: Timeline[];    // Status history
}
```

### Repair Record Model

```typescript
interface RepairRecord {
  id: string;                      // Unique ID (e.g., "RP-20260114-0001")
  complaint_id: string;            // Related complaint
  assigned_team?: string;          // Team doing repair
  description: string;             // Work description
  repair_date?: DateTime;          // When repair completed
  verification_status: string;     // Pending, Verified, Failed, Rejected
  evidence_reference?: string;     // Photo/document URL
  verified_at?: DateTime;          // When verified
  verified_by?: string;            // Who verified
  created_at: DateTime;            // When record created
  updated_at: DateTime;            // When record updated
}
```

### Audit Log Model

```typescript
interface AuditLog {
  id: number;                      // Sequential ID
  complaint_id?: string;           // Related complaint
  repair_id?: string;              // Related repair (if applicable)
  action: string;                  // create, status_change, update, repair_*, verification
  actor?: string;                  // User/system performing action
  source: string;                  // api, web, system, migration
  old_value?: string;              // Previous value (for updates)
  new_value?: string;              // New value (for updates)
  details?: string;                // Additional context
  timestamp: DateTime;             // When action occurred
}
```

---

## Integration with React Frontend

### Complaint to Frontend Mapping

The backend complains maps to the frontend complaint interface as follows:

| Backend | Frontend | Notes |
|---------|----------|-------|
| `id` | `id` | Format: CP-YYYY-NNNN |
| `title` | `title` | - |
| `description` | `description` | - |
| `category` | `category` | - |
| `location_text` | `location` | - |
| `latitude` | `latitude` | Optional, unverified |
| `longitude` | `longitude` | Optional, unverified |
| `ward` | `ward` | Optional |
| `priority` | `priorityLevel` | Mapped: Low/Medium/High/Critical |
| `priority_score` | `priorityScore` | 0-100 numeric |
| `status` | `status` | Maps to ComplaintStatus enum |
| `repeat_complaint_count` | `repeatComplaintCount` | - |
| `asset_id` | `assetId` | Optional |
| `assigned_team` | `assignedTeam` | Optional |
| `image_reference` | `imageReference` | Optional |
| `reported_at` | `reportedAt` | ISO 8601 datetime |
| `updated_at` | `updatedAt` | ISO 8601 datetime |
| `timeline_entries` | `timeline` | Maps to TimelineEvent[] |

### CORS Configuration

The backend is pre-configured for React frontend development:
- Allowed origins: `http://localhost:5173` (Vite dev server), `http://localhost:3000` (alternative)
- Allowed methods: GET, POST, PATCH, PUT, DELETE, OPTIONS
- Allowed headers: All

To modify CORS settings, edit `.env`:
```
ALLOWED_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
```

---

## Development Notes

### ID Generation Strategy

IDs are generated server-side to ensure uniqueness:
- **Complaints**: `CP-YYYY-NNNN` (Year + sequential number)
- **Assets**: `TYPE-WARD-NNN` (Asset type + ward + sequential)
- **Repairs**: `RP-YYYYMMDD-NNNN` (Date + sequential)

### Timestamps

All timestamps are in UTC (ISO 8601 format). The frontend should convert to local time for display.

### Coordinates

Latitude/Longitude are optional and unverified. They are validated for range (-90 to 90 for lat, -180 to 180 for lng) but are never trusted for security purposes. Location verification should happen at the verification stage.

### Audit Trail

All significant actions are logged in the audit trail:
- Complaint creation
- Status changes
- Priority updates
- Assignment changes
- Repair records created
- Repair completions
- Verification results

The audit trail is append-only and should never be modified through the API.

---

## Testing

Run tests with:
```bash
pytest tests/ -v
```

Test coverage includes:
- ✅ All CRUD operations
- ✅ Status transitions
- ✅ Repair workflows
- ✅ Audit logging
- ✅ Validation
- ✅ Error handling
- ✅ Pagination and filtering

---

## Authentication & Authorization

**Current Phase 1 Note:** Phase 1 does not implement authentication. All endpoints are public.

For Phase 2+, we recommend:
- JWT token-based authentication
- Role-based access control (RBAC)
- Restrict verification endpoints to authorized personnel
- Audit logging of all user actions

---

## Performance Considerations

- Pagination maximum limit: 100 items
- History maximum limit: 500 items
- Database queries use indexed lookups (status, priority, ward, category)
- Consider adding caching for GET /health for load balancer healthchecks

---

## Migration to PostgreSQL

This backend is designed for easy migration from SQLite to PostgreSQL:
1. SQLModel ORM abstracts database operations
2. No database-specific features used
3. Simply change `DATABASE_URL` in `.env` to PostgreSQL connection string
4. All models will work unchanged

Example PostgreSQL connection string:
```
DATABASE_URL=postgresql://user:password@localhost/civicpulse_db
```

---

## Support & Questions

For issues or questions about the API:
1. Check the Swagger documentation at `/docs`
2. Review this documentation
3. Check test cases in `tests/test_endpoints.py`
4. Review backend source code in `app/routers/`

