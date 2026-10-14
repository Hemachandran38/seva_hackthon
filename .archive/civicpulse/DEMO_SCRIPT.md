# CivicPulse AI — Hackathon Demo Script

**Duration:** 5–7 minutes  
**Audience:** Judges, attendees  
**Equipment:** Laptop, projector, browser

---

## Opening (30 seconds)

> "CivicPulse AI is a public infrastructure monitoring platform designed to help municipal authorities identify and prioritize infrastructure faults—like broken streetlights—and track repairs from initial complaint through verified closure.
>
> Today we'll walk through a complete workflow: a citizen complaint comes in, the system prioritizes it using AI, assigns it to a repair team, and tracks the repair until it's verified and resolved."

---

## Demo Sequence

### 1. Show the Map (1 minute)

**Action:** Open `civicpulse/frontend/index.html` in browser

> "This is CivicPulse AI's main dashboard. You're looking at Coimbatore, Tamil Nadu. The colored markers represent infrastructure complaints:
>
> - **Red markers** = High priority (needs urgent repair)
> - **Orange** = Medium priority
> - **Blue** = Low priority
> - **Green** = Resolved (repair verified and closed)
>
> All of this data comes from our backend database, and all location data is displayed in real-time on the map."

**Point out:** 12 markers spread across the map area.

---

### 2. Click a High-Priority Marker (2 minutes)

**Action:** Click the red marker at RS Puram (top-left area)

> "When I click a marker, a popup appears with full details about that complaint:
>
> - **Asset ID**: SL-CBE-001 — this is a streetlight
> - **Issue**: 'Streetlight completely non-functional; dark stretch creates safety hazard'
> - **Status**: Currently 'In Progress'
> - **Priority**: High (based on AI analysis)
> - **Priority Score**: 57.5 out of 100
> 
> Below that, you see the **AI explanation**:"

**Read the explanation box aloud.**

> "This AI score breaks down into 4 factors:
>
> 1. **Severity** (100/100) — The bulb is completely dead, not just dim
> 2. **Recurrence** (0/100) — This is the first complaint on this asset
> 3. **Days Pending** (12/100) — It's been reported 3+ days
> 4. **Public Impact** (100/100) — Streetlights are public safety-critical
>
> These factors combine with weights (40%, 25%, 20%, 15%) to calculate the overall score.
>
> **Crucially:** This score is not a failure prediction. It's a decision-support tool to help maintenance teams focus on the most urgent repairs first."

**Show the factor breakdown chips.** Point to each one.

---

### 3. Show Sidebar Features (1 minute)

**Action:** Close popup, point to sidebar

> "On the left, you see our **dashboard overview**:
> - 12 total assets in the city
> - 6 currently open complaints
> - 3 high-priority issues that need immediate attention
> - 3 already resolved and verified
>
> The **Top Priority** panel shows the 3 most urgent complaints. Clicking one pans the map to that location instantly.
>
> **Filters** let you focus on specific subsets. For example:"

**Click "High" priority filter.**

> "Now the map shows only the 3 red markers — all high-priority complaints. If I click 'Resolved'..."

**Click "Resolved" filter.**

> "...only the green markers appear — repairs that have been verified and completed."

**Reset filters.**

---

### 4. Show the Repair Lifecycle (1 minute)

**Action:** Explain the workflow (no click needed, just narrate)

> "Behind the scenes, each complaint follows a **repair lifecycle**:
>
> 1. **Reported** — A citizen submits a complaint
> 2. **Under Inspection** — The municipality inspects the asset
> 3. **Assigned** — A repair team is assigned
> 4. **In Progress** — The team begins repair work
> 5. **Awaiting Verification** — Repair is done, awaiting inspection
> 6. **Resolved** — Inspector verifies the repair, complaint closed
> 7. **Reopened** (if needed) — If the fault recurs, reopen for rework
>
> Each state transition is recorded in an **audit trail** with timestamps, who made the change, and notes. This creates a complete, immutable record of the repair process."

---

### 5. Show Filters & Search (1 minute)

**Action:** Demonstrate filter combinations

> "Let's filter by **Medium priority** and **In Progress** status to see repairs actively happening:"

**Select Medium + In Progress filters.**

> "We see 3 complaints being worked on right now. The counter at the bottom shows 'Showing 3 of 12' — these are real-time, dynamic filters connected to our database."

**Try a search.**

> "We can also search by asset ID. Let me search for 'SL-CBE-005':"

**Type in search box, show 1 result.**

> "One match found. This narrows the view instantly."

**Reset all filters.**

---

### 6. Closing: Key Takeaways (30 seconds)

> "CivicPulse AI brings three major capabilities to municipal infrastructure management:
>
> 1. **Visibility** — Citizens can report faults anywhere, and we map them instantly.
> 2. **Intelligence** — Our AI system scores and ranks complaints by urgency, so repair teams focus on what matters most.
> 3. **Accountability** — Every action from complaint to verified resolution is tracked and timestamped.
>
> This is a **demonstration** using sample data. Real-world deployment would integrate actual citizen complaint channels and municipal repair databases.
>
> Thank you!"

---

## Q&A Talking Points

**Q: How does the AI actually work?**
> "It weighs four factors: issue severity, whether we've seen the same fault before (recurrence), how long it's been pending, and public impact of the asset. These combine with configurable weights to create a transparent, explainable score. It's not a black box — judges and managers can see exactly why a complaint got its priority."

**Q: Is this real data?**
> "No, this is **demo data only** — all complaints are synthetic samples. We clearly label it as demo data in the UI. In production, this would connect to real citizen reporting channels (e.g., a mobile app, SMS, web form) and real municipal repair systems."

**Q: Can the system handle scale?**
> "Yes. The backend is built on FastAPI and SQLAlchemy, which can handle thousands of concurrent users. We use a PostgreSQL database in production (we showed SQLite for demo simplicity). Map rendering is handled by Leaflet.js and OpenStreetMap, proven at scale."

**Q: What happens if a repair is done incorrectly?**
> "The system supports a **'Reopened'** state. If a citizen reports the same fault again within a time window, the complaint can be reopened, and the repair team is flagged for rework. Every reopening is logged in the audit trail."

**Q: How is this different from a simple complaint form?**
> "Three ways: (1) spatial visualization — you see WHERE faults cluster, (2) intelligent prioritization — you don't treat all complaints equally, and (3) auditable workflow — you can't mark a repair 'done' without an actual inspector verification."

---

## Backup Demo (if backend is down)

If the live API is unavailable:

1. Open the frontend in a browser
2. It will show "API Offline" but the map will still display cached demo data
3. Explain: "Normally this connects to our live backend API, but even if the backend is temporarily down, we have graceful fallback and clear error messaging."
4. Use screenshots or a video to show the full workflow

---

## Demo Recording Checklist

Before the hackathon:

- [ ] Record a 2–3 minute video showing the complete workflow (complaint → map → filter → priority details → lifecycle explanation)
- [ ] Use QuickTime (Mac) or OBS (Windows/Linux) to capture screen + audio
- [ ] Include opening intro and closing remarks
- [ ] Save as MP4, upload to YouTube unlisted or include in GitHub repo
- [ ] Test on projector and audio system beforehand

---

## Slides (Optional PowerPoint)

If you want to accompany the demo:

1. **Title Slide:** "CivicPulse AI — Public Infrastructure Monitoring"
2. **Problem:** Map of a city with broken streetlights, "Who decides repair priority?"
3. **Solution:** Screenshot of CivicPulse map with markers
4. **Architecture Diagram:** Frontend → Backend → Database, with AI scoring module
5. **Workflow:** 7-state lifecycle diagram
6. **Demo Results:** Screenshot of full workflow end-to-end
7. **Impact:** "Faster repairs, smarter prioritization, full accountability"
8. **Closing:** GitHub link, team names

---

## Physical Demo Setup

**Minimum requirements:**
- Laptop with browser (Chrome/Edge recommended)
- Internet connection (for CDN: Leaflet.js, Esri tiles)
- Local backend running on `http://localhost:8000` (or deployed)
- Projector / large monitor
- 30-second backup video on USB (just in case)

**Best practice:**
- Open the app in browser BEFORE judges arrive
- Have browser tabs ready (backend Swagger UI + frontend)
- Have a terminal open showing backend logs (for technical judges)
- Have README.md and GitHub repo link visible

---

## Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| Map doesn't show | Reload browser, check internet connection |
| API shows offline | Restart backend: `uvicorn main:app --reload --port 8000` |
| Markers all same color | Check that priority scores were calculated: `POST /api/priority/recalculate` |
| Popup doesn't appear | Try clicking a different marker, clear browser cache |
| Search doesn't work | Check that the asset ID exactly matches (e.g., "SL-CBE-001") |
| Filters reset unexpectedly | Refresh page, restart backend if API errors occur |

---

**Last Updated:** 2026-10-13  
**Demo Ready:** ✓

