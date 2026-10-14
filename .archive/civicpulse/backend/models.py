"""
models.py — SQLAlchemy ORM table definitions.

Tables:
  - assets          : physical infrastructure items
  - complaints      : fault reports (Phase 2)
  - repair_records  : work evidence per complaint (Phase 2, extended Phase 4)
  - audit_log       : immutable event trail (Phase 4)
"""

from sqlalchemy import (
    Column, Integer, String, Float, DateTime,
    ForeignKey, Text, Boolean
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


# ─────────────────────────────────────────────────────────────────
# PHASE 2 — ASSETS
# ─────────────────────────────────────────────────────────────────
class Asset(Base):
    __tablename__ = "assets"

    asset_id          = Column(String, primary_key=True, index=True)
    asset_type        = Column(String, nullable=False)
    latitude          = Column(Float,  nullable=False)
    longitude         = Column(Float,  nullable=False)
    area_name         = Column(String, nullable=False)
    installation_date = Column(String, nullable=True)
    condition         = Column(String, default="good")   # good / fair / poor

    complaints = relationship("Complaint", back_populates="asset",
                              cascade="all, delete-orphan")


# ─────────────────────────────────────────────────────────────────
# PHASE 2 + 4 — COMPLAINTS
# New Phase 4 columns: lifecycle_status, assigned_team, assigned_at,
#   assigned_by, assignment_notes, verified_by, verified_at,
#   verification_result, verification_notes, reopened_count
# ─────────────────────────────────────────────────────────────────
class Complaint(Base):
    __tablename__ = "complaints"

    complaint_id      = Column(Integer, primary_key=True, autoincrement=True, index=True)
    asset_id          = Column(String, ForeignKey("assets.asset_id"), nullable=False)
    issue_description = Column(Text, nullable=False)
    severity          = Column(String, default="medium")       # low / medium / high
    priority_score    = Column(Integer, default=50)            # 0–100
    priority_level    = Column(String, default="medium")       # low / medium / high / resolved
    reported_at       = Column(DateTime(timezone=True), server_default=func.now())

    # ── Phase 4: lifecycle ──────────────────────────────────────
    # Allowed values:
    #   reported → under_inspection → assigned → in_progress →
    #   awaiting_verification → resolved | reopened
    lifecycle_status  = Column(String, default="reported")

    # For backwards compat the old "status" column is kept but
    # mirrors lifecycle_status via a property-style approach.
    # We store it separately so Phase 2/3 queries still work.
    status            = Column(String, default="open")         # open / in-progress / resolved

    # Assignment fields
    assigned_team     = Column(String, nullable=True)
    assigned_at       = Column(DateTime(timezone=True), nullable=True)
    assigned_by       = Column(String, nullable=True)          # actor username
    assignment_notes  = Column(Text, nullable=True)

    # Verification fields
    verified_by       = Column(String, nullable=True)
    verified_at       = Column(DateTime(timezone=True), nullable=True)
    verification_result = Column(String, nullable=True)        # approved / rejected
    verification_notes  = Column(Text, nullable=True)

    # Reopen tracking
    reopened_count    = Column(Integer, default=0)

    # Relationships
    asset          = relationship("Asset", back_populates="complaints")
    repair_records = relationship("RepairRecord", back_populates="complaint",
                                  cascade="all, delete-orphan")
    audit_logs     = relationship("AuditLog", back_populates="complaint",
                                  cascade="all, delete-orphan",
                                  order_by="AuditLog.timestamp")


# ─────────────────────────────────────────────────────────────────
# PHASE 2 + 4 — REPAIR RECORDS
# New Phase 4 column: submitted_for_verification
# ─────────────────────────────────────────────────────────────────
class RepairRecord(Base):
    __tablename__ = "repair_records"

    repair_id           = Column(Integer, primary_key=True, autoincrement=True, index=True)
    complaint_id        = Column(Integer, ForeignKey("complaints.complaint_id"), nullable=False)
    assigned_team       = Column(String, nullable=True)
    repair_notes        = Column(Text,   nullable=True)
    evidence_image_path = Column(String, nullable=True)   # relative path only, never abs
    repaired_at         = Column(DateTime(timezone=True), nullable=True)
    verified_at         = Column(DateTime(timezone=True), nullable=True)

    # Phase 4
    submitted_for_verification = Column(Boolean, default=False)

    complaint = relationship("Complaint", back_populates="repair_records")


# ─────────────────────────────────────────────────────────────────
# PHASE 4 — AUDIT LOG
# Immutable at the application layer (no UPDATE/DELETE endpoints).
# ─────────────────────────────────────────────────────────────────
class AuditLog(Base):
    __tablename__ = "audit_log"

    log_id        = Column(Integer, primary_key=True, autoincrement=True, index=True)
    complaint_id  = Column(Integer, ForeignKey("complaints.complaint_id"), nullable=False)
    action        = Column(String, nullable=False)    # e.g. "complaint_created"
    prev_status   = Column(String, nullable=True)
    new_status    = Column(String, nullable=True)
    actor         = Column(String, nullable=False)    # username or "system"
    timestamp     = Column(DateTime(timezone=True), server_default=func.now())
    notes         = Column(Text, nullable=True)

    complaint = relationship("Complaint", back_populates="audit_logs")
