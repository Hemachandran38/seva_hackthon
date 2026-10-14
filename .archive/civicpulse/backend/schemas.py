"""
schemas.py — Pydantic models for request validation and response serialisation.
"""

from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, field_validator


# ─────────────────────────── Asset ───────────────────────────

class AssetBase(BaseModel):
    asset_id:          str
    asset_type:        str
    latitude:          float
    longitude:         float
    area_name:         str
    installation_date: Optional[str] = None
    condition:         Optional[str] = "good"


class AssetOut(AssetBase):
    """Returned by GET /api/assets and GET /api/assets/{asset_id}."""
    complaints: List[ComplaintSummary] = []

    model_config = {"from_attributes": True}


# ─────────────────────────── Complaint ───────────────────────────

class ComplaintSummary(BaseModel):
    """Lightweight complaint shape nested inside AssetOut."""
    complaint_id:      int
    issue_description: str
    priority_level:    str
    priority_score:    int
    status:            str
    reported_at:       datetime

    model_config = {"from_attributes": True}


class ComplaintOut(BaseModel):
    """Full complaint shape returned by GET /api/complaints endpoints."""
    complaint_id:      int
    asset_id:          str
    issue_description: str
    severity:          str
    priority_score:    int
    priority_level:    str
    status:            str
    reported_at:       datetime

    # Flatten asset location so the frontend can place a marker directly
    latitude:   Optional[float] = None
    longitude:  Optional[float] = None
    area_name:  Optional[str]   = None
    asset_type: Optional[str]   = None

    model_config = {"from_attributes": True}


class ComplaintStatusUpdate(BaseModel):
    """Request body for PATCH /api/complaints/{id}/status."""
    status: str

    @field_validator("status")
    @classmethod
    def status_must_be_valid(cls, v: str) -> str:
        allowed = {"open", "in-progress", "resolved"}
        if v not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return v


# ─────────────────────────── RepairRecord ───────────────────────────

class RepairRecordOut(BaseModel):
    repair_id:           int
    complaint_id:        int
    assigned_team:       Optional[str]
    repair_notes:        Optional[str]
    evidence_image_path: Optional[str]
    repaired_at:         Optional[datetime]
    verified_at:         Optional[datetime]

    model_config = {"from_attributes": True}


# ─────────────────────────── Dashboard ───────────────────────────

class DashboardStats(BaseModel):
    total_assets:      int
    total_complaints:  int
    open_complaints:   int
    in_progress:       int
    resolved:          int
    high_priority:     int
    medium_priority:   int
    low_priority:      int


# ─────────────────────────── Generic responses ───────────────────────────

class MessageResponse(BaseModel):
    message: str


# Forward reference resolution (ComplaintSummary used inside AssetOut)
AssetOut.model_rebuild()


# ─────────────────────────── Phase 3 — AI Priority Schemas ───────────────────────────

class ScoringFactor(BaseModel):
    """One factor in the priority score breakdown."""
    label:        str
    raw_score:    float
    weight:       float
    contribution: float
    input:        Any  # the original value fed into this factor

    model_config = {"from_attributes": True}


class RecommendationOut(BaseModel):
    """
    Full AI-scored recommendation for one complaint.
    Returned by GET /api/priority/recommendations.
    """
    complaint_id:     int
    asset_id:         str
    asset_type:       Optional[str]
    area_name:        Optional[str]
    latitude:         Optional[float]
    longitude:        Optional[float]
    issue_description: str
    status:           str
    reported_at:      datetime

    # AI scoring outputs
    ai_score:          float           # 0–100 composite
    priority_level:    str             # high / medium / low / resolved
    explanation:       str             # plain-English rationale
    suggested_action:  str
    days_pending:      float
    recurrence_count:  int
    factors:          Dict[str, Any]   # full factor breakdown

    model_config = {"from_attributes": True}


class RecalculateRequest(BaseModel):
    """
    Optional custom weights for POST /api/priority/recalculate.
    All weights must sum to 1.0 (±0.01 tolerance).
    """
    weights: Optional[Dict[str, float]] = None
    thresholds: Optional[Dict[str, float]] = None

    @field_validator("weights")
    @classmethod
    def weights_must_sum_to_one(cls, v):
        if v is None:
            return v
        total = sum(v.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0; got {total:.3f}")
        required = {"severity", "recurrence", "pending_time", "public_impact"}
        missing = required - set(v.keys())
        if missing:
            raise ValueError(f"Missing weight keys: {missing}")
        return v


class RecalculateResponse(BaseModel):
    message:          str
    updated_count:    int
    calculated_at:    datetime
    weights_used:     Dict[str, float]
    thresholds_used:  Dict[str, float]


class AssetHistoryOut(BaseModel):
    """Returned by GET /api/assets/{asset_id}/history."""
    asset_id:          str
    asset_type:        str
    area_name:         str
    condition:         str
    total_complaints:  int
    open_complaints:   int
    resolved_complaints: int
    recurrence_flag:   bool           # True if > 1 complaint on this asset
    complaints:        List[ComplaintSummary]


class DashboardStatsV3(BaseModel):
    """Extended dashboard stats including AI fields."""
    total_assets:        int
    total_complaints:    int
    open_complaints:     int
    in_progress:         int
    resolved:            int
    high_priority:       int
    medium_priority:     int
    low_priority:        int
    recurring_assets:    int           # assets with > 1 open complaint
    last_calculated_at:  Optional[datetime]
    top_priority_assets: List[Dict[str, Any]]  # top 3 by AI score


# ─────────────────────────── Phase 4 — Repair Lifecycle Schemas ───────────────

class LifecycleTransitionRequest(BaseModel):
    """Request body for POST /api/complaints/{id}/transition."""
    target_status: str
    actor:         str
    notes:         Optional[str] = None


class AssignmentRequest(BaseModel):
    """Request body for POST /api/complaints/{id}/assign."""
    assigned_team:    str
    assigned_by:      str
    assignment_notes: Optional[str] = None


class RepairSubmitRequest(BaseModel):
    """Request body for POST /api/complaints/{id}/repair — text fields only.
       Image upload is handled as a separate multipart form field."""
    repair_notes: str
    actor:        str


class VerificationRequest(BaseModel):
    """Request body for POST /api/complaints/{id}/verify."""
    result:    str   # "approved" or "rejected"
    reviewer:  str
    notes:     Optional[str] = None

    @field_validator("result")
    @classmethod
    def result_must_be_valid(cls, v: str) -> str:
        if v not in {"approved", "rejected"}:
            raise ValueError("result must be 'approved' or 'rejected'")
        return v


class ReopenRequest(BaseModel):
    """Request body for POST /api/complaints/{id}/reopen."""
    actor: str
    notes: str


class AuditLogOut(BaseModel):
    log_id:       int
    complaint_id: int
    action:       str
    prev_status:  Optional[str]
    new_status:   Optional[str]
    actor:        str
    timestamp:    datetime
    notes:        Optional[str]

    model_config = {"from_attributes": True}


class ComplaintDetailOut(BaseModel):
    """
    Full complaint detail including lifecycle, assignment,
    verification, repair records, and audit trail.
    Returned by GET /api/complaints/{id}/detail
    """
    complaint_id:       int
    asset_id:           str
    asset_type:         Optional[str] = None
    area_name:          Optional[str] = None
    latitude:           Optional[float] = None
    longitude:          Optional[float] = None
    issue_description:  str
    severity:           str
    priority_score:     int
    priority_level:     str
    status:             str
    lifecycle_status:   str
    reported_at:        datetime

    # Assignment
    assigned_team:      Optional[str] = None
    assigned_at:        Optional[datetime] = None
    assigned_by:        Optional[str] = None
    assignment_notes:   Optional[str] = None

    # Verification
    verified_by:          Optional[str] = None
    verified_at:          Optional[datetime] = None
    verification_result:  Optional[str] = None
    verification_notes:   Optional[str] = None

    # Reopen tracking
    reopened_count:       int = 0

    # Related records
    repair_records:  List["RepairRecordOut4"] = []
    audit_logs:      List[AuditLogOut] = []

    model_config = {"from_attributes": True}


class RepairRecordOut4(BaseModel):
    """Extended repair record including verification flag."""
    repair_id:                    int
    complaint_id:                 int
    assigned_team:                Optional[str]
    repair_notes:                 Optional[str]
    evidence_image_path:          Optional[str]
    repaired_at:                  Optional[datetime]
    verified_at:                  Optional[datetime]
    submitted_for_verification:   bool

    model_config = {"from_attributes": True}


# Forward ref resolution
ComplaintDetailOut.model_rebuild()
