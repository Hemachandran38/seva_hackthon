"""
main.py — CivicPulse AI API  (Phase 4)

New in Phase 4:
  GET    /api/complaints/{id}/detail         — full lifecycle detail + audit trail
  POST   /api/complaints/{id}/transition     — validated lifecycle state change
  POST   /api/complaints/{id}/assign         — assign to maintenance team
  POST   /api/complaints/{id}/repair         — submit repair notes + optional image
  POST   /api/complaints/{id}/verify         — approve or reject a repair
  POST   /api/complaints/{id}/reopen         — reopen a resolved complaint
  GET    /api/complaints/{id}/audit          — audit trail for one complaint
  GET    /api/repair/pending                 — open assignments
  GET    /api/repair/overdue                 — overdue open assignments (> threshold days)
  POST   /api/complaints/{id}/repair/upload  — upload evidence image

Run with:
    uvicorn main:app --reload --port 8000
Swagger UI: http://localhost:8000/docs
"""

import os
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import (
    FastAPI, Depends, HTTPException, Query,
    UploadFile, File, Form
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session, joinedload

from database import engine, SessionLocal, Base
import models
import schemas
from lifecycle import validate_transition, derive_status, STATE_LABELS
from priority_engine import (
    calculate_priority, detect_recurrence,
    DEFAULT_WEIGHTS, DEFAULT_THRESHOLDS,
)

# ── Tables ─────────────────────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ── Upload directory ───────────────────────────────────────────────────────────
UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_BYTES = 5 * 1024 * 1024   # 5 MB

# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="CivicPulse AI API",
    description="Infrastructure fault monitoring — Phase 4: end-to-end repair tracking.",
    version="4.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded evidence images at /uploads/<filename>
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# ── In-memory scoring state ────────────────────────────────────────────────────
_last_calculated_at: Optional[datetime] = None
_active_weights: Dict[str, float]       = DEFAULT_WEIGHTS.copy()
_active_thresholds: Dict[str, float]    = DEFAULT_THRESHOLDS.copy()


# ── DB session ─────────────────────────────────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Audit helper ───────────────────────────────────────────────────────────────
def _log(db: Session, complaint_id: int, action: str,
         prev: Optional[str], new: Optional[str],
         actor: str, notes: Optional[str] = None):
    """Append an immutable audit entry. Never update or delete these rows."""
    entry = models.AuditLog(
        complaint_id=complaint_id,
        action=action,
        prev_status=prev,
        new_status=new,
        actor=actor,
        notes=notes,
    )
    db.add(entry)


# ── Complaint loader ───────────────────────────────────────────────────────────
def _get_complaint_or_404(complaint_id: int, db: Session) -> models.Complaint:
    c = (
        db.query(models.Complaint)
        .options(
            joinedload(models.Complaint.asset),
            joinedload(models.Complaint.repair_records),
            joinedload(models.Complaint.audit_logs),
        )
        .filter(models.Complaint.complaint_id == complaint_id)
        .first()
    )
    if not c:
        raise HTTPException(404, f"Complaint {complaint_id} not found.")
    return c


def _flatten_asset(out: schemas.ComplaintOut, c: models.Complaint):
    if c.asset:
        out.latitude   = c.asset.latitude
        out.longitude  = c.asset.longitude
        out.area_name  = c.asset.area_name
        out.asset_type = c.asset.asset_type


# =============================================================================
# ASSETS  (unchanged from Phase 3)
# =============================================================================

@app.get("/api/assets", response_model=List[schemas.AssetOut],
         summary="List all assets", tags=["Assets"])
def get_all_assets(
    asset_type: Optional[str] = Query(None),
    area_name:  Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(models.Asset).options(joinedload(models.Asset.complaints))
    if asset_type:
        q = q.filter(models.Asset.asset_type.ilike(f"%{asset_type}%"))
    if area_name:
        q = q.filter(models.Asset.area_name.ilike(f"%{area_name}%"))
    return q.all()


@app.get("/api/assets/{asset_id}", response_model=schemas.AssetOut,
         summary="Get one asset", tags=["Assets"])
def get_asset(asset_id: str, db: Session = Depends(get_db)):
    asset = (
        db.query(models.Asset)
        .options(joinedload(models.Asset.complaints))
        .filter(models.Asset.asset_id == asset_id)
        .first()
    )
    if not asset:
        raise HTTPException(404, f"Asset '{asset_id}' not found.")
    return asset


@app.get("/api/assets/{asset_id}/history", response_model=schemas.AssetHistoryOut,
         summary="Full complaint history for one asset", tags=["Assets"])
def get_asset_history(asset_id: str, db: Session = Depends(get_db)):
    asset = (
        db.query(models.Asset)
        .options(joinedload(models.Asset.complaints))
        .filter(models.Asset.asset_id == asset_id)
        .first()
    )
    if not asset:
        raise HTTPException(404, f"Asset '{asset_id}' not found.")
    total    = len(asset.complaints)
    open_c   = sum(1 for c in asset.complaints if c.status != "resolved")
    resolved = sum(1 for c in asset.complaints if c.status == "resolved")
    return schemas.AssetHistoryOut(
        asset_id=asset.asset_id, asset_type=asset.asset_type,
        area_name=asset.area_name, condition=asset.condition,
        total_complaints=total, open_complaints=open_c,
        resolved_complaints=resolved, recurrence_flag=(total > 1),
        complaints=[
            schemas.ComplaintSummary.model_validate(c)
            for c in sorted(asset.complaints, key=lambda x: x.reported_at, reverse=True)
        ],
    )


# =============================================================================
# COMPLAINTS — Phase 2/3 endpoints (preserved)
# =============================================================================

@app.get("/api/complaints", response_model=List[schemas.ComplaintOut],
         summary="List complaints with filters", tags=["Complaints"])
def get_complaints(
    priority:  Optional[str] = Query(None),
    status:    Optional[str] = Query(None),
    asset_id:  Optional[str] = Query(None),
    area_name: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    q = (
        db.query(models.Complaint)
        .join(models.Asset, models.Complaint.asset_id == models.Asset.asset_id)
        .options(joinedload(models.Complaint.asset))
    )
    if priority:  q = q.filter(models.Complaint.priority_level == priority)
    if status:    q = q.filter(models.Complaint.status == status)
    if asset_id:  q = q.filter(models.Complaint.asset_id == asset_id)
    if area_name: q = q.filter(models.Asset.area_name.ilike(f"%{area_name}%"))
    result = []
    for c in q.all():
        out = schemas.ComplaintOut.model_validate(c)
        _flatten_asset(out, c)
        result.append(out)
    return result


@app.get("/api/complaints/{complaint_id}", response_model=schemas.ComplaintOut,
         summary="Get one complaint (summary)", tags=["Complaints"])
def get_complaint(complaint_id: int, db: Session = Depends(get_db)):
    c = _get_complaint_or_404(complaint_id, db)
    out = schemas.ComplaintOut.model_validate(c)
    _flatten_asset(out, c)
    return out


@app.patch("/api/complaints/{complaint_id}/status", response_model=schemas.ComplaintOut,
           summary="Legacy status update (Phase 2 compatibility)", tags=["Complaints"])
def update_complaint_status_legacy(
    complaint_id: int,
    payload: schemas.ComplaintStatusUpdate,
    db: Session = Depends(get_db),
):
    """
    Phase 2 backward-compatible endpoint.
    Maps old status values to lifecycle states where possible.
    Prefer /api/complaints/{id}/transition for Phase 4 workflows.
    """
    c = _get_complaint_or_404(complaint_id, db)
    prev = c.lifecycle_status

    # Map old status → lifecycle_status
    mapping = {
        "open":        "reported",
        "in-progress": "in_progress",
        "resolved":    "resolved",
    }
    target_lifecycle = mapping.get(payload.status, payload.status)

    # Only apply if transition is valid; otherwise just update legacy field
    try:
        validate_transition(c.lifecycle_status, target_lifecycle)
        c.lifecycle_status = target_lifecycle
    except ValueError:
        pass  # Legacy callers: best-effort, don't break them

    c.status = payload.status
    if payload.status == "resolved":
        c.priority_level = "resolved"

    _log(db, complaint_id, "legacy_status_update", prev, target_lifecycle, "system")
    db.commit()
    db.refresh(c)
    out = schemas.ComplaintOut.model_validate(c)
    _flatten_asset(out, c)
    return out


# =============================================================================
# PHASE 4 — COMPLAINT DETAIL
# =============================================================================

@app.get("/api/complaints/{complaint_id}/detail",
         response_model=schemas.ComplaintDetailOut,
         summary="Full lifecycle detail with audit trail", tags=["Phase 4 — Lifecycle"])
def get_complaint_detail(complaint_id: int, db: Session = Depends(get_db)):
    c = _get_complaint_or_404(complaint_id, db)
    out = schemas.ComplaintDetailOut.model_validate(c)
    if c.asset:
        out.latitude   = c.asset.latitude
        out.longitude  = c.asset.longitude
        out.area_name  = c.asset.area_name
        out.asset_type = c.asset.asset_type
    return out


# =============================================================================
# PHASE 4 — LIFECYCLE TRANSITION
# =============================================================================

@app.post("/api/complaints/{complaint_id}/transition",
          response_model=schemas.ComplaintDetailOut,
          summary="Move complaint to next lifecycle state", tags=["Phase 4 — Lifecycle"])
def transition_complaint(
    complaint_id: int,
    payload: schemas.LifecycleTransitionRequest,
    db: Session = Depends(get_db),
):
    """
    Validates and applies a lifecycle state transition.
    Returns 422 if the transition is not permitted.
    """
    c = _get_complaint_or_404(complaint_id, db)
    prev = c.lifecycle_status

    try:
        validate_transition(prev, payload.target_status)
    except ValueError as e:
        raise HTTPException(422, str(e))

    c.lifecycle_status = payload.target_status
    c.status           = derive_status(payload.target_status)

    if payload.target_status == "resolved":
        c.priority_level = "resolved"
    elif payload.target_status == "reopened":
        c.reopened_count = (c.reopened_count or 0) + 1
        c.priority_level = c.severity  # restore severity-based priority

    _log(db, complaint_id,
         action=f"transition_to_{payload.target_status}",
         prev=prev, new=payload.target_status,
         actor=payload.actor, notes=payload.notes)

    db.commit()
    db.refresh(c)
    out = schemas.ComplaintDetailOut.model_validate(c)
    if c.asset:
        out.latitude = c.asset.latitude; out.longitude = c.asset.longitude
        out.area_name = c.asset.area_name; out.asset_type = c.asset.asset_type
    return out


# =============================================================================
# PHASE 4 — ASSIGNMENT
# =============================================================================

@app.post("/api/complaints/{complaint_id}/assign",
          response_model=schemas.ComplaintDetailOut,
          summary="Assign complaint to a maintenance team", tags=["Phase 4 — Assignment"])
def assign_complaint(
    complaint_id: int,
    payload: schemas.AssignmentRequest,
    db: Session = Depends(get_db),
):
    """
    Records team assignment and advances lifecycle to 'assigned'.
    Can re-assign: if already assigned, updates the existing assignment.
    """
    c = _get_complaint_or_404(complaint_id, db)
    prev = c.lifecycle_status

    # Allow assigning from: reported, under_inspection, reopened, or re-assigning from assigned
    allowed_from = {"reported", "under_inspection", "reopened", "assigned"}
    if prev not in allowed_from:
        raise HTTPException(422,
            f"Cannot assign from state '{STATE_LABELS.get(prev, prev)}'. "
            f"Complaint must be in one of: {list(allowed_from)}.")

    was_reassigned = (prev == "assigned")

    c.assigned_team    = payload.assigned_team
    c.assigned_at      = datetime.now(timezone.utc)
    c.assigned_by      = payload.assigned_by
    c.assignment_notes = payload.assignment_notes
    c.lifecycle_status = "assigned"
    c.status           = derive_status("assigned")

    action = "team_reassigned" if was_reassigned else "team_assigned"
    _log(db, complaint_id, action, prev, "assigned",
         payload.assigned_by, payload.assignment_notes)

    db.commit()
    db.refresh(c)
    out = schemas.ComplaintDetailOut.model_validate(c)
    if c.asset:
        out.latitude = c.asset.latitude; out.longitude = c.asset.longitude
        out.area_name = c.asset.area_name; out.asset_type = c.asset.asset_type
    return out


# =============================================================================
# PHASE 4 — REPAIR EVIDENCE SUBMISSION
# =============================================================================

@app.post("/api/complaints/{complaint_id}/repair",
          response_model=schemas.ComplaintDetailOut,
          summary="Submit repair notes (no image)", tags=["Phase 4 — Repair"])
def submit_repair(
    complaint_id: int,
    payload: schemas.RepairSubmitRequest,
    db: Session = Depends(get_db),
):
    """
    Records repair notes and advances lifecycle to 'in_progress'.
    Complaint must currently be in 'assigned' state.
    """
    c = _get_complaint_or_404(complaint_id, db)
    prev = c.lifecycle_status

    if prev != "assigned":
        raise HTTPException(422,
            f"Repair notes can only be submitted when status is 'Assigned'. "
            f"Current status: '{STATE_LABELS.get(prev, prev)}'.")

    repair = models.RepairRecord(
        complaint_id=complaint_id,
        assigned_team=c.assigned_team,
        repair_notes=payload.repair_notes,
        repaired_at=datetime.now(timezone.utc),
        submitted_for_verification=False,
    )
    db.add(repair)

    c.lifecycle_status = "in_progress"
    c.status           = derive_status("in_progress")

    _log(db, complaint_id, "repair_started", prev, "in_progress",
         payload.actor, payload.repair_notes[:120] if payload.repair_notes else None)

    db.commit()
    db.refresh(c)
    out = schemas.ComplaintDetailOut.model_validate(c)
    if c.asset:
        out.latitude = c.asset.latitude; out.longitude = c.asset.longitude
        out.area_name = c.asset.area_name; out.asset_type = c.asset.asset_type
    return out


@app.post("/api/complaints/{complaint_id}/repair/upload",
          response_model=schemas.ComplaintDetailOut,
          summary="Upload repair evidence image + submit for verification",
          tags=["Phase 4 — Repair"])
async def upload_repair_evidence(
    complaint_id: int,
    actor: str        = Form(...),
    repair_notes: str = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    """
    Accepts repair notes + optional image file.
    Validates file type (.jpg/.jpeg/.png/.webp) and size (max 5 MB).
    Advances lifecycle to 'awaiting_verification'.
    Stores only the filename (not the full path) in the database.
    """
    c = _get_complaint_or_404(complaint_id, db)
    prev = c.lifecycle_status

    allowed_from = {"in_progress", "assigned"}
    if prev not in allowed_from:
        raise HTTPException(422,
            f"Cannot submit evidence from state '{STATE_LABELS.get(prev, prev)}'. "
            f"Expected 'In Progress' or 'Assigned'.")

    # ── Image validation ──────────────────────────────────────────────────────
    saved_filename = None
    if image and image.filename:
        ext = Path(image.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(400,
                f"File type '{ext}' not allowed. "
                f"Accepted types: {list(ALLOWED_EXTENSIONS)}.")

        content = await image.read()
        if len(content) > MAX_FILE_BYTES:
            raise HTTPException(400,
                f"File exceeds maximum size of {MAX_FILE_BYTES // (1024*1024)} MB.")

        # Store with a UUID name to prevent path traversal / filename collisions
        saved_filename = f"{uuid.uuid4().hex}{ext}"
        (UPLOAD_DIR / saved_filename).write_bytes(content)

    # ── Repair record ─────────────────────────────────────────────────────────
    repair = models.RepairRecord(
        complaint_id=complaint_id,
        assigned_team=c.assigned_team,
        repair_notes=repair_notes,
        evidence_image_path=saved_filename,   # filename only, never abs path
        repaired_at=datetime.now(timezone.utc),
        submitted_for_verification=True,
    )
    db.add(repair)

    c.lifecycle_status = "awaiting_verification"
    c.status           = derive_status("awaiting_verification")

    _log(db, complaint_id, "repair_evidence_submitted", prev, "awaiting_verification",
         actor, f"Evidence image: {saved_filename or 'none'}")

    db.commit()
    db.refresh(c)
    out = schemas.ComplaintDetailOut.model_validate(c)
    if c.asset:
        out.latitude = c.asset.latitude; out.longitude = c.asset.longitude
        out.area_name = c.asset.area_name; out.asset_type = c.asset.asset_type
    return out


# =============================================================================
# PHASE 4 — VERIFICATION
# =============================================================================

@app.post("/api/complaints/{complaint_id}/verify",
          response_model=schemas.ComplaintDetailOut,
          summary="Approve or reject a repair", tags=["Phase 4 — Verification"])
def verify_repair(
    complaint_id: int,
    payload: schemas.VerificationRequest,
    db: Session = Depends(get_db),
):
    """
    Only callable when lifecycle_status == 'awaiting_verification'.
    Approved  → resolved  (verified closure)
    Rejected  → in_progress  (returned for rework)

    Only this endpoint may set lifecycle_status to 'resolved'.
    The legacy PATCH /status endpoint cannot bypass this rule for
    complaints that have gone through the full lifecycle.
    """
    c = _get_complaint_or_404(complaint_id, db)
    prev = c.lifecycle_status

    if prev != "awaiting_verification":
        raise HTTPException(422,
            f"Verification requires status 'Awaiting Verification'. "
            f"Current: '{STATE_LABELS.get(prev, prev)}'.")

    c.verified_by         = payload.reviewer
    c.verified_at         = datetime.now(timezone.utc)
    c.verification_result = payload.result
    c.verification_notes  = payload.notes

    if payload.result == "approved":
        c.lifecycle_status = "resolved"
        c.status           = "resolved"
        c.priority_level   = "resolved"
        action = "verification_approved"
    else:
        c.lifecycle_status = "in_progress"
        c.status           = derive_status("in_progress")
        action = "verification_rejected"

    _log(db, complaint_id, action, prev, c.lifecycle_status,
         payload.reviewer, payload.notes)

    db.commit()
    db.refresh(c)
    out = schemas.ComplaintDetailOut.model_validate(c)
    if c.asset:
        out.latitude = c.asset.latitude; out.longitude = c.asset.longitude
        out.area_name = c.asset.area_name; out.asset_type = c.asset.asset_type
    return out


# =============================================================================
# PHASE 4 — REOPEN
# =============================================================================

@app.post("/api/complaints/{complaint_id}/reopen",
          response_model=schemas.ComplaintDetailOut,
          summary="Reopen a resolved complaint", tags=["Phase 4 — Lifecycle"])
def reopen_complaint(
    complaint_id: int,
    payload: schemas.ReopenRequest,
    db: Session = Depends(get_db),
):
    c = _get_complaint_or_404(complaint_id, db)
    prev = c.lifecycle_status

    if prev != "resolved":
        raise HTTPException(422,
            f"Only resolved complaints can be reopened. "
            f"Current status: '{STATE_LABELS.get(prev, prev)}'.")

    c.lifecycle_status = "reopened"
    c.status           = derive_status("reopened")
    c.priority_level   = c.severity   # restore severity-based priority
    c.reopened_count   = (c.reopened_count or 0) + 1

    _log(db, complaint_id, "complaint_reopened", prev, "reopened",
         payload.actor, payload.notes)

    db.commit()
    db.refresh(c)
    out = schemas.ComplaintDetailOut.model_validate(c)
    if c.asset:
        out.latitude = c.asset.latitude; out.longitude = c.asset.longitude
        out.area_name = c.asset.area_name; out.asset_type = c.asset.asset_type
    return out


# =============================================================================
# PHASE 4 — AUDIT LOG
# =============================================================================

@app.get("/api/complaints/{complaint_id}/audit",
         response_model=List[schemas.AuditLogOut],
         summary="Audit trail for one complaint", tags=["Phase 4 — Audit"])
def get_audit_log(complaint_id: int, db: Session = Depends(get_db)):
    """Returns all audit events for a complaint, oldest first."""
    logs = (
        db.query(models.AuditLog)
        .filter(models.AuditLog.complaint_id == complaint_id)
        .order_by(models.AuditLog.timestamp.asc())
        .all()
    )
    if not logs:
        # Check complaint exists
        if not db.query(models.Complaint).filter(
            models.Complaint.complaint_id == complaint_id
        ).first():
            raise HTTPException(404, f"Complaint {complaint_id} not found.")
    return logs


# =============================================================================
# PHASE 4 — REPAIR QUEUE ENDPOINTS
# =============================================================================

@app.get("/api/repair/pending",
         response_model=List[schemas.ComplaintDetailOut],
         summary="Open complaints awaiting repair action", tags=["Phase 4 — Repair Queue"])
def get_pending_repairs(
    priority: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Returns assigned or in-progress complaints, sorted by priority score desc."""
    q = (
        db.query(models.Complaint)
        .options(
            joinedload(models.Complaint.asset),
            joinedload(models.Complaint.repair_records),
            joinedload(models.Complaint.audit_logs),
        )
        .filter(models.Complaint.lifecycle_status.in_(
            ["assigned", "in_progress", "awaiting_verification"]
        ))
    )
    if priority:
        q = q.filter(models.Complaint.priority_level == priority)
    complaints = q.order_by(models.Complaint.priority_score.desc()).all()

    result = []
    for c in complaints:
        out = schemas.ComplaintDetailOut.model_validate(c)
        if c.asset:
            out.latitude = c.asset.latitude; out.longitude = c.asset.longitude
            out.area_name = c.asset.area_name; out.asset_type = c.asset.asset_type
        result.append(out)
    return result


@app.get("/api/repair/overdue",
         response_model=List[schemas.ComplaintDetailOut],
         summary="Overdue open complaints", tags=["Phase 4 — Repair Queue"])
def get_overdue_repairs(
    days: int = Query(7, description="Complaints open longer than this many days are overdue"),
    db: Session = Depends(get_db),
):
    """Complaints still open/assigned after `days` days."""
    from datetime import timedelta
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    q = (
        db.query(models.Complaint)
        .options(
            joinedload(models.Complaint.asset),
            joinedload(models.Complaint.repair_records),
            joinedload(models.Complaint.audit_logs),
        )
        .filter(models.Complaint.status != "resolved")
        .filter(models.Complaint.reported_at <= cutoff)
        .order_by(models.Complaint.priority_score.desc())
    )
    result = []
    for c in q.all():
        out = schemas.ComplaintDetailOut.model_validate(c)
        if c.asset:
            out.latitude = c.asset.latitude; out.longitude = c.asset.longitude
            out.area_name = c.asset.area_name; out.asset_type = c.asset.asset_type
        result.append(out)
    return result


# =============================================================================
# AI PRIORITY (Phase 3 — unchanged)
# =============================================================================

def _build_recommendations(db, priority_filter=None, status_filter=None,
                            recurring_only=False, weights=None, thresholds=None):
    w = weights    or _active_weights
    t = thresholds or _active_thresholds
    all_complaints = (
        db.query(models.Complaint)
        .options(joinedload(models.Complaint.asset))
        .all()
    )
    recurrence_map = detect_recurrence(all_complaints)
    results = []
    for c in all_complaints:
        if not c.asset:
            continue
        if c.status == "resolved":
            rec = schemas.RecommendationOut(
                complaint_id=c.complaint_id, asset_id=c.asset_id,
                asset_type=c.asset.asset_type, area_name=c.asset.area_name,
                latitude=c.asset.latitude, longitude=c.asset.longitude,
                issue_description=c.issue_description, status=c.status,
                reported_at=c.reported_at, ai_score=0.0, priority_level="resolved",
                explanation="Resolved — no further action required.",
                suggested_action="No action required.",
                days_pending=0.0, recurrence_count=recurrence_map.get(c.asset_id, 1), factors={},
            )
        else:
            scored = calculate_priority(
                severity=c.severity,
                recurrence_count=recurrence_map.get(c.asset_id, 1),
                reported_at=c.reported_at,
                asset_condition=c.asset.condition or "fair",
                asset_type=c.asset.asset_type,
                weights=w, thresholds=t,
            )
            rec = schemas.RecommendationOut(
                complaint_id=c.complaint_id, asset_id=c.asset_id,
                asset_type=c.asset.asset_type, area_name=c.asset.area_name,
                latitude=c.asset.latitude, longitude=c.asset.longitude,
                issue_description=c.issue_description, status=c.status,
                reported_at=c.reported_at,
                ai_score=scored["score"], priority_level=scored["priority_level"],
                explanation=scored["explanation"], suggested_action=scored["suggested_action"],
                days_pending=scored["days_pending"], recurrence_count=scored["recurrence_count"],
                factors=scored["factors"],
            )
        results.append(rec)
    if priority_filter: results = [r for r in results if r.priority_level == priority_filter]
    if status_filter:   results = [r for r in results if r.status == status_filter]
    if recurring_only:  results = [r for r in results if r.recurrence_count > 1]
    results.sort(key=lambda r: (r.priority_level == "resolved", -r.ai_score))
    return results


@app.get("/api/priority/recommendations",
         response_model=List[schemas.RecommendationOut],
         summary="AI-scored fault recommendations", tags=["AI Priority"])
def get_recommendations(
    priority:       Optional[str] = Query(None),
    status:         Optional[str] = Query(None),
    recurring_only: bool          = Query(False),
    db: Session = Depends(get_db),
):
    return _build_recommendations(db, priority, status, recurring_only)


@app.post("/api/priority/recalculate",
          response_model=schemas.RecalculateResponse,
          summary="Re-run priority scoring", tags=["AI Priority"])
def recalculate_priorities(
    payload: schemas.RecalculateRequest,
    db: Session = Depends(get_db),
):
    global _last_calculated_at, _active_weights, _active_thresholds
    w = payload.weights    or _active_weights
    t = payload.thresholds or _active_thresholds
    if t and not {"high", "medium"}.issubset(t.keys()):
        raise HTTPException(422, "Thresholds must include 'high' and 'medium' keys.")
    all_c = (
        db.query(models.Complaint)
        .options(joinedload(models.Complaint.asset))
        .filter(models.Complaint.status != "resolved")
        .all()
    )
    recurrence_map = detect_recurrence(all_c)
    updated = 0
    for c in all_c:
        if not c.asset: continue
        scored = calculate_priority(
            severity=c.severity, recurrence_count=recurrence_map.get(c.asset_id, 1),
            reported_at=c.reported_at, asset_condition=c.asset.condition or "fair",
            asset_type=c.asset.asset_type, weights=w, thresholds=t,
        )
        c.priority_score = int(scored["score"])
        c.priority_level = scored["priority_level"]
        updated += 1
    db.commit()
    _last_calculated_at = datetime.now(timezone.utc)
    _active_weights     = w
    _active_thresholds  = t
    return schemas.RecalculateResponse(
        message=f"Priority scores recalculated for {updated} open complaints.",
        updated_count=updated, calculated_at=_last_calculated_at,
        weights_used=w, thresholds_used=t,
    )


# =============================================================================
# DASHBOARD STATS (Phase 4 extended)
# =============================================================================

@app.get("/api/dashboard/stats",
         response_model=schemas.DashboardStatsV3,
         summary="Dashboard summary", tags=["Dashboard"])
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_assets = db.query(models.Asset).count()
    all_c        = db.query(models.Complaint).all()
    total    = len(all_c)
    open_c   = sum(1 for c in all_c if c.status == "open")
    in_prog  = sum(1 for c in all_c if c.status == "in-progress")
    resolved = sum(1 for c in all_c if c.status == "resolved")
    high     = sum(1 for c in all_c if c.priority_level == "high")
    medium   = sum(1 for c in all_c if c.priority_level == "medium")
    low      = sum(1 for c in all_c if c.priority_level == "low")
    asset_counts = Counter(c.asset_id for c in all_c)
    recurring_assets = sum(1 for cnt in asset_counts.values() if cnt > 1)
    top3 = (
        db.query(models.Complaint)
        .options(joinedload(models.Complaint.asset))
        .filter(models.Complaint.status != "resolved")
        .order_by(models.Complaint.priority_score.desc())
        .limit(3).all()
    )
    top_priority_assets = [
        {"complaint_id": c.complaint_id, "asset_id": c.asset_id,
         "area_name": c.asset.area_name if c.asset else "—",
         "priority_score": c.priority_score, "priority_level": c.priority_level,
         "status": c.status, "lifecycle_status": c.lifecycle_status}
        for c in top3
    ]
    return schemas.DashboardStatsV3(
        total_assets=total_assets, total_complaints=total,
        open_complaints=open_c, in_progress=in_prog, resolved=resolved,
        high_priority=high, medium_priority=medium, low_priority=low,
        recurring_assets=recurring_assets, last_calculated_at=_last_calculated_at,
        top_priority_assets=top_priority_assets,
    )


# =============================================================================
# HEALTH CHECK
# =============================================================================

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "CivicPulse AI API v4"}
