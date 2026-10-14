# CivicPulse AI frontend

A responsive React, TypeScript and Vite demonstration frontend based on the supplied Google Stitch export. The original Stitch HTML, screenshots and design-system files remain in the parent directory.

## Run locally

```sh
npm install
npm run dev
```

Open the local URL printed by Vite. The supported routes are `/`, `/report`, `/track` and `/issues`.

```sh
npm run typecheck
npm run build
npm run preview
```

## Demonstration data

The initial complaint records are fictional examples shared by all screens. New reports are stored under `civicpulse_demo_complaints_v1` in browser localStorage. They stay in that browser profile and do not sync across people or devices. Invalid saved JSON is discarded and the sample dataset is restored. When localStorage is blocked or full, new submission reports a save error instead of claiming it was saved.

Photos are validated and previewed for the active session. Image data is intentionally not placed in localStorage, and report images are not persisted after refresh.

All sample statuses, crew information, locations and priority scores are demonstration content. The score utility contains a bounded rule-based formula for future use; no trained or validated model or live municipal telemetry is connected.

## Future FastAPI integration

Page components call `src/services/complaintService.ts`. Replace its local data implementation with typed API calls there while retaining the complaint model in `src/types/complaint.ts`. No API base URL or credential is assumed.
