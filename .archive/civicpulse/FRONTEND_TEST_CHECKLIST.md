# Phase 4 Frontend Integration Test Checklist

**Purpose:** Verify that the frontend correctly displays Phase 4 lifecycle information (assignment, verification, audit logs, repair history) alongside Phase 3 AI scoring.

**Prerequisites:**
- Backend running at `http://localhost:8000` with all Phase 1–4 endpoints live
- Frontend running (e.g., via `python -m http.server` in the frontend directory)
- Test data: at least 12 sample complaints with mixed lifecycle states

---

## 1. Map & Markers Rendering

- [ ] Map loads in browser at `http://localhost:5000` (or your server URL)
- [ ] Markers appear on map for all 12 sample assets
- [ ] Marker colors correctly reflect AI priority level:
  - [ ] Red: High priority (AI score ≥ 70)
  - [ ] Orange: Medium priority (40–69)
  - [ ] Blue: Low priority (< 40)
  - [ ] Green: Resolved complaints
- [ ] Recurring faults (recurrence_count > 1) have purple ring indicator (⟳)
- [ ] API status badge shows "● API Live" (green) in top-right

---

## 2. Basic Popup Functionality (Phase 1–3)

Click on a marker to open popup:

- [ ] Popup card displays correctly with:
  - [ ] Asset ID
  - [ ] Priority badge (High/Medium/Low/Resolved)
  - [ ] Asset type & area name
  - [ ] Status (Open / In Progress / Resolved)
  - [ ] Reported date
  - [ ] Days pending
  - [ ] AI score & score bar
  - [ ] AI explanation text
  - [ ] Issue description & suggested action
  - [ ] Scoring factors (for non-resolved complaints)
- [ ] Status dropdown works: can change status to Open / In Progress / Resolved
- [ ] After status change, toast appears ("Complaint #X → updated")
- [ ] Map re-renders after status update

---

## 3. Phase 4 Lifecycle Modal Link

In popup, locate the **"View Lifecycle & Audit →"** button:

- [ ] Button is visible and clickable
- [ ] Click opens a modal overlay
- [ ] Modal has a close (✕) button in top-right
- [ ] Modal closes when clicking the close button
- [ ] Modal closes when clicking outside the modal (on overlay)

---

## 4. Lifecycle Modal Content — Overview Section

Once modal is open, verify the overview cards:

- [ ] **Asset** card shows the asset ID
- [ ] **Lifecycle Status** card shows lifecycle_status as a colored badge:
  - [ ] "reported" = blue badge
  - [ ] "under_inspection" = orange/yellow badge
  - [ ] "assigned" = blue badge
  - [ ] "in_progress" = yellow/orange badge
  - [ ] "awaiting_verification" = orange badge
  - [ ] "resolved" = green badge
  - [ ] "reopened" = red badge
- [ ] **Reopened** card shows reopened_count (0 or higher)

---

## 5. Lifecycle Modal Content — Assignment Section

- [ ] If **assigned_team** is set:
  - [ ] Assignment section shows "Team", "Assigned By", "Assigned At"
  - [ ] Assignment notes display (if present)
  - [ ] Dates format as "dd Mon yyyy" (e.g., "13 Oct 2026")
- [ ] If **not assigned**:
  - [ ] Section shows placeholder: "Not yet assigned."

---

## 6. Lifecycle Modal Content — Verification Section

- [ ] If **verified_by** is set:
  - [ ] Verification Result shows as badge: "Approved" (green) or "Rejected" (red)
  - [ ] Shows "Verified By" name
  - [ ] Shows "Verified At" date
  - [ ] Verification notes display (if present)
- [ ] If **not verified**:
  - [ ] Section shows placeholder: "Not yet verified."

---

## 7. Lifecycle Modal Content — Repair Records

- [ ] Repair records section header shows count (e.g., "Repair Records (2)")
- [ ] For each repair record:
  - [ ] Displays "Repair #1", "Repair #2", etc.
  - [ ] Shows assigned_team
  - [ ] Shows repaired_at date
  - [ ] Shows status: "Submitted for Verification" (teal badge) or "Draft" (purple badge)
  - [ ] Shows repair_notes (if present)
  - [ ] If evidence_image_path present:
    - [ ] Shows "View Image ↗" link
    - [ ] Link is clickable and opens image in new tab
- [ ] If no repair records:
  - [ ] Shows placeholder: "No repair records yet."

---

## 8. Lifecycle Modal Content — Audit Log

- [ ] Audit log section header shows count (e.g., "Audit Log (8 actions)")
- [ ] For each audit log entry:
  - [ ] Shows timestamp (date)
  - [ ] Shows action and actor (e.g., "status_update by System Admin")
  - [ ] Shows new_status (if action involved status change)
  - [ ] Shows notes (if present)
  - [ ] Each entry has left border in primary color
  - [ ] Background is slightly different from main body
- [ ] If no audit logs:
  - [ ] Shows placeholder: "No audit log entries."

---

## 9. Dashboard Metrics

In the left sidebar, verify:

- [ ] **Total Assets** shows correct count
- [ ] **Open** count includes only "open" status complaints
- [ ] **High Priority** shows complaints with priority_level = "high"
- [ ] **Resolved** shows resolved complaints
- [ ] **Recurring** shows assets with recurrence_count > 1
- [ ] **In Progress** shows "in-progress" status complaints
- [ ] All metrics update after status changes

---

## 10. Filters & Search

- [ ] Priority filter (All, High, Medium, Low) correctly filters markers
- [ ] Status filter (All, Open, In Progress, Resolved) correctly filters markers
- [ ] Recurrence filter (All, Recurring Only) correctly filters markers
- [ ] Search by asset ID (e.g., "SL-001") finds correct complaint
- [ ] Search by area name filters markers correctly
- [ ] "Reset Filters" button clears all filters

---

## 11. Top Priority List

In the "🔴 Top Priority" panel:

- [ ] Displays up to 10 high-priority complaints
- [ ] Each item shows asset ID, area name, and priority score
- [ ] Clicking an item pans the map to that marker and opens popup
- [ ] If no high-priority complaints, shows placeholder text

---

## 12. Error Handling

- [ ] When backend is offline:
  - [ ] API error banner appears at top of map
  - [ ] Badge shows "● API Offline" (red)
  - [ ] "Retry" button is clickable
  - [ ] Retry attempts to reconnect
- [ ] When a request fails:
  - [ ] Toast error message appears (e.g., "Failed to load lifecycle data: ...")
  - [ ] Toast has red background

---

## 13. Loading & Performance

- [ ] Initial page load shows spinner overlay briefly
- [ ] Loading text reads "Loading AI recommendations…"
- [ ] After ~2–3 seconds, map and markers render
- [ ] Toggling filters re-runs query and updates markers smoothly
- [ ] Opening lifecycle modal shows loading spinner briefly (especially for large audit logs)
- [ ] No console errors in browser DevTools (F12)

---

## 14. Responsive Design (Optional)

- [ ] Frontend looks good at desktop width (1200px+)
- [ ] Sidebar panels scroll independently
- [ ] Lifecycle modal is readable on mobile (max-width 768px)
- [ ] Modal closes properly on touch devices

---

## 15. End-to-End Scenario

**Scenario:** A complaint progresses through the full lifecycle.

1. [ ] Start with complaint in "reported" state
2. [ ] Use backend POST `/api/complaints/{id}/assign` to assign to a team
   - Modal modal shows assignment info
3. [ ] Use backend POST `/api/complaints/{id}/transition` to move to "in_progress"
   - Modal updates to show in_progress state
4. [ ] Use backend POST `/api/complaints/{id}/repair/upload` to submit repair with evidence
   - Modal shows repair record with status "Submitted for Verification"
5. [ ] Use backend POST `/api/complaints/{id}/verify` to approve repair
   - Modal shows verification result as "Approved"
   - Lifecycle status changes to "resolved"
   - Marker color changes to green
6. [ ] Use backend POST `/api/complaints/{id}/reopen` to reopen
   - Modal shows lifecycle status as "reopened"
   - reopened_count increments to 1
   - Audit log shows new "reopen" entry
   - Marker color reverts to priority-based color

---

## Notes

- Frontend uses ES6 vanilla JavaScript (no frameworks)
- API calls are async with proper error handling
- All timestamps from backend are ISO 8601 format (converted to locale date in frontend)
- Modal content is dynamically generated from API response
- Ensure CORS is configured correctly in backend (already set to `*` for demo)

