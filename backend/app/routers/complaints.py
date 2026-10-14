"""Complaint management endpoints."""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, desc
from app.database import get_session
from app.models.complaint import Complaint, ComplaintTimeline, VALID_STATUS_TRANSITIONS
from app.models.repair import RepairRecord
from app.models.audit import AuditLog
from app.schemas.complaint import (
    ComplaintSchema,
    ComplaintCreateSchema,
    ComplaintPatchSchema,
    ComplaintStatusUpdateSchema,
    ComplaintTimelineSchema,
    AuditLogSchema,
)
from app.schemas.repair import RepairRecordSchema
from app.schemas.common import PaginatedResponse
from app.services.id_generator import generate_complaint_id

router = APIRouter(prefix="/api/complaints", tags=["complaints"])

# ==================== Core Complaint Endpoints ====================

@router.get("")
async def list_complaints(
    session: Session = Depends(get_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=10000),
):
    """List all complaints."""
    try:
        complaints = session.exec(select(Complaint).offset(skip).limit(limit)).all()
        total = session.exec(select(Complaint)).all()
        return {
            "items": complaints,
            "total": len(total),
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        raise


@router.get("/{complaint_id}", response_model=ComplaintSchema)
async def get_complaint(complaint_id: str, session: Session = Depends(get_session)):
    """Get a specific complaint by ID with all details."""
    complaint = session.exec(select(Complaint).where(Complaint.id == complaint_id)).first()
    if not complaint:
        raise HTTPException(status_code=404, detail=f"Complaint {complaint_id} not found")
    return complaint


@router.post("", response_model=ComplaintSchema, status_code=201)
async def create_complaint(
    complaint_data: ComplaintCreateSchema,
    session: Session = Depends(get_session)
):
    """
    Create a new complaint.
    
    **Fields:**
    - **title**: Short title of the issue (required)
    - **description**: Detailed problem description (required)
    - **category**: Issue category (required)
    - **location_text**: Human-readable location (required)
    - **latitude/longitude**: Optional geographic coordinates (validated: lat -90 to 90, lng -180 to 180)
    - **ward**: Optional ward identifier
    - **asset_id**: Optional related asset ID
    - **image_reference**: Optional image URL or reference
    
    **Response:** Complaint object with auto-generated ID and initial status "Reported"
    """
    # Generate unique complaint ID
    complaint_id = generate_complaint_id()
    
    # Create complaint with initial status
    complaint = Complaint(
        id=complaint_id,
        status="Reported",  # Always start as Reported
        **complaint_data.model_dump()
    )
    
    # Create initial timeline entry
    timeline_entry = ComplaintTimeline(
        complaint_id=complaint_id,
        status="Reported",
        note="Complaint received",
        timestamp=datetime.utcnow()
    )
    
    # Add audit log
    audit = AuditLog(
        complaint_id=complaint_id,
        action="create",
        actor=None,
        source="api",
        new_value="Reported",
        details="Complaint created via API"
    )
    
    session.add(complaint)
    session.add(timeline_entry)
    session.add(audit)
    session.commit()
    session.refresh(complaint)
    return complaint


# ==================== PATCH Endpoints ====================

@router.patch("/{complaint_id}", response_model=ComplaintSchema)
async def patch_complaint(
    complaint_id: str,
    complaint_data: ComplaintPatchSchema,
    session: Session = Depends(get_session)
):
    """
    Update allowed complaint fields (priority, assigned team, etc).
    Does NOT change status - use /complaints/{id}/status endpoint for status updates.
    
    **Allowed fields to update:**
    - **title**: Issue title
    - **description**: Issue description  
    - **priority**: Low, Medium, High, or Critical
    - **priority_score**: 0-100 numeric priority
    - **assigned_team**: Team name handling the complaint
    - **repeat_complaint_count**: Number of repeats
    
    **Returns:** Updated complaint object
    """
    complaint = session.exec(select(Complaint).where(Complaint.id == complaint_id)).first()
    if not complaint:
        raise HTTPException(status_code=404, detail=f"Complaint {complaint_id} not found")
    
    update_data = complaint_data.model_dump(exclude_unset=True)
    updated_fields = []
    
    # Track old values for audit
    for key, value in update_data.items():
        old_value = getattr(complaint, key, None)
        if old_value != value:
            setattr(complaint, key, value)
            updated_fields.append(f"{key}: {old_value} → {value}")
    
    if updated_fields:
        complaint.updated_at = datetime.utcnow()
        
        # Add audit log
        audit = AuditLog(
            complaint_id=complaint_id,
            action="update",
            actor=None,
            source="api",
            details="; ".join(updated_fields)
        )
        session.add(audit)
    
    session.add(complaint)
    session.commit()
    session.refresh(complaint)
    return complaint


@router.patch("/{complaint_id}/status", response_model=ComplaintSchema)
async def update_complaint_status(
    complaint_id: str,
    status_update: ComplaintStatusUpdateSchema,
    session: Session = Depends(get_session)
):
    """
    Update complaint status with validation.
    
    **Valid status transitions:**
    - Reported → Under Review, Assigned
    - Under Review → Assigned, Reported
    - Assigned → In Progress, Under Review
    - In Progress → Awaiting Verification, Assigned
    - Awaiting Verification → Resolved, In Progress
    - Resolved → Under Review (for re-opening)
    
    **Parameters:**
    - **status**: New status (required)
    - **note**: Optional note for timeline entry
    
    **Returns:** Updated complaint with new timeline entry and audit log
    """
    complaint = session.exec(select(Complaint).where(Complaint.id == complaint_id)).first()
    if not complaint:
        raise HTTPException(status_code=404, detail=f"Complaint {complaint_id} not found")
    
    new_status = status_update.status
    
    # Validate status value
    valid_statuses = {"Reported", "Under Review", "Assigned", "In Progress", "Awaiting Verification", "Resolved"}
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status '{new_status}'. Must be one of {valid_statuses}"
        )
    
    # Validate transition
    if not complaint.can_transition_to(new_status):
        allowed = VALID_STATUS_TRANSITIONS.get(complaint.status, set())
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status transition: {complaint.status} → {new_status}. Allowed: {allowed}"
        )
    
    old_status = complaint.status
    complaint.status = new_status
    complaint.updated_at = datetime.utcnow()
    
    # Create timeline entry
    timeline_entry = ComplaintTimeline(
        complaint_id=complaint_id,
        status=new_status,
        note=status_update.note or "Status updated",
        timestamp=datetime.utcnow()
    )
    
    # Add audit log
    audit = AuditLog(
        complaint_id=complaint_id,
        action="status_change",
        actor=None,
        source="api",
        old_value=old_status,
        new_value=new_status,
        details=status_update.note or "Status updated"
    )
    
    session.add(complaint)
    session.add(timeline_entry)
    session.add(audit)
    session.commit()
    session.refresh(complaint)
    return complaint


# ==================== Repair Endpoints ====================

@router.post("/{complaint_id}/repairs", response_model=RepairRecordSchema, status_code=201)
async def create_repair_record(
    complaint_id: str,
    repair_data: dict,  # Accept flexible input
    session: Session = Depends(get_session)
):
    """
    Create a repair record for a complaint.
    
    **Parameters:**
    - **assigned_team**: Optional team name
    - **description**: Description of repair work (required, min 10 chars)
    - **repair_date**: Optional date when repair was completed
    
    **Returns:** New repair record
    """
    # Verify complaint exists
    complaint = session.exec(select(Complaint).where(Complaint.id == complaint_id)).first()
    if not complaint:
        raise HTTPException(status_code=404, detail=f"Complaint {complaint_id} not found")
    
    # Generate repair ID
    from app.services.id_generator import generate_repair_id
    repair_id = generate_repair_id()
    
    # Validate required fields
    if not repair_data.get("description") or len(repair_data.get("description", "")) < 10:
        raise HTTPException(status_code=400, detail="Description is required and must be at least 10 characters")
    
    # Create repair record
    repair = RepairRecord(
        id=repair_id,
        complaint_id=complaint_id,
        assigned_team=repair_data.get("assigned_team"),
        description=repair_data.get("description"),
        repair_date=repair_data.get("repair_date"),
    )
    
    # Add audit log
    audit = AuditLog(
        complaint_id=complaint_id,
        repair_id=repair_id,
        action="repair_start",
        actor=None,
        source="api",
        new_value=repair_id,
        details=f"Repair record created: {repair_data.get('description')[:100]}"
    )
    
    session.add(repair)
    session.add(audit)
    session.commit()
    session.refresh(repair)
    return repair


@router.get("/{complaint_id}/repairs", response_model=List[RepairRecordSchema])
async def get_complaint_repairs(
    complaint_id: str,
    session: Session = Depends(get_session)
):
    """
    Get all repair records for a complaint.
    
    **Returns:** List of repair records ordered by creation date
    """
    # Verify complaint exists
    complaint = session.exec(select(Complaint).where(Complaint.id == complaint_id)).first()
    if not complaint:
        raise HTTPException(status_code=404, detail=f"Complaint {complaint_id} not found")
    
    repairs = session.exec(
        select(RepairRecord)
        .where(RepairRecord.complaint_id == complaint_id)
        .order_by(desc(RepairRecord.created_at))
    ).all()
    
    return repairs


@router.patch("/{complaint_id}/repairs/{repair_id}/progress", response_model=RepairRecordSchema)
async def update_repair_progress(
    complaint_id: str,
    repair_id: str,
    progress_data: dict,
    session: Session = Depends(get_session)
):
    """
    Update repair progress (repair date, description).
    
    **Parameters:**
    - **repair_date**: When the repair was completed
    - **description**: Updated work description
    
    **Returns:** Updated repair record
    """
    repair = session.exec(
        select(RepairRecord)
        .where(RepairRecord.id == repair_id)
        .where(RepairRecord.complaint_id == complaint_id)
    ).first()
    
    if not repair:
        raise HTTPException(status_code=404, detail=f"Repair record {repair_id} not found for complaint {complaint_id}")
    
    old_data = f"repair_date={repair.repair_date}, description={repair.description[:50]}"
    
    if "repair_date" in progress_data and progress_data["repair_date"] is not None:
        # Handle both string and datetime objects
        repair_date_val = progress_data["repair_date"]
        if isinstance(repair_date_val, str):
            from datetime import datetime
            repair.repair_date = datetime.fromisoformat(repair_date_val)
        else:
            repair.repair_date = repair_date_val
    
    if "description" in progress_data and progress_data["description"] is not None:
        repair.description = progress_data["description"]
    
    repair.updated_at = datetime.utcnow()
    
    # Add audit log
    audit = AuditLog(
        complaint_id=complaint_id,
        repair_id=repair_id,
        action="repair_update",
        actor=None,
        source="api",
        details=f"Repair progress updated: {old_data}"
    )
    
    session.add(repair)
    session.add(audit)
    session.commit()
    session.refresh(repair)
    return repair


@router.patch("/{complaint_id}/repairs/{repair_id}/verify", response_model=RepairRecordSchema)
async def verify_repair_completion(
    complaint_id: str,
    repair_id: str,
    verification_data: dict,
    session: Session = Depends(get_session)
):
    """
    Verify or reject repair completion.
    Marks repair as verified or failed. Does NOT auto-resolve complaint - that's a separate status update.
    
    **Parameters:**
    - **verification_status**: Verified, Failed, or Rejected
    - **evidence_reference**: URL or reference to verification evidence
    - **verified_by**: Optional person/system verifying
    
    **Returns:** Updated repair record
    
    **Note:** After repair verification, you must separately use PATCH /complaints/{id}/status to update complaint status.
    """
    repair = session.exec(
        select(RepairRecord)
        .where(RepairRecord.id == repair_id)
        .where(RepairRecord.complaint_id == complaint_id)
    ).first()
    
    if not repair:
        raise HTTPException(status_code=404, detail=f"Repair record {repair_id} not found for complaint {complaint_id}")
    
    # Validate verification status
    new_status = verification_data.get("verification_status")
    if new_status not in {"Verified", "Failed", "Rejected"}:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid verification_status. Must be 'Verified', 'Failed', or 'Rejected'"
        )
    
    old_status = repair.verification_status
    repair.verification_status = new_status
    repair.verified_at = datetime.utcnow()
    repair.verified_by = verification_data.get("verified_by")
    repair.evidence_reference = verification_data.get("evidence_reference")
    repair.updated_at = datetime.utcnow()
    
    # Add audit log
    audit = AuditLog(
        complaint_id=complaint_id,
        repair_id=repair_id,
        action="verification",
        actor=verification_data.get("verified_by"),
        source="api",
        old_value=old_status,
        new_value=new_status,
        details=f"Repair verification: {new_status}. Evidence: {verification_data.get('evidence_reference')}"
    )
    
    session.add(repair)
    session.add(audit)
    session.commit()
    session.refresh(repair)
    return repair


# ==================== History & Audit Endpoints ====================

@router.get("/{complaint_id}/history", response_model=PaginatedResponse[AuditLogSchema])
async def get_complaint_history(
    complaint_id: str,
    session: Session = Depends(get_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    """
    Get full audit history for a complaint.
    
    Chronological log of all actions: creation, status changes, assignments, repairs, verifications.
    
    **Returns:** Paginated list of audit log entries (most recent first)
    """
    # Verify complaint exists
    complaint = session.exec(select(Complaint).where(Complaint.id == complaint_id)).first()
    if not complaint:
        raise HTTPException(status_code=404, detail=f"Complaint {complaint_id} not found")
    
    # Get audit entries
    query = select(AuditLog).where(AuditLog.complaint_id == complaint_id)
    total = len(session.exec(query).all())
    
    audit_entries = session.exec(
        query.order_by(desc(AuditLog.timestamp)).offset(skip).limit(limit)
    ).all()
    
    return PaginatedResponse(
        items=audit_entries,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{complaint_id}/timeline", response_model=List[ComplaintTimelineSchema])
async def get_complaint_timeline(
    complaint_id: str,
    session: Session = Depends(get_session)
):
    """
    Get status change timeline for a complaint.
    
    Shows all status transitions with timestamps and notes.
    
    **Returns:** List of timeline entries (chronological order)
    """
    # Verify complaint exists
    complaint = session.exec(select(Complaint).where(Complaint.id == complaint_id)).first()
    if not complaint:
        raise HTTPException(status_code=404, detail=f"Complaint {complaint_id} not found")
    
    timeline = session.exec(
        select(ComplaintTimeline)
        .where(ComplaintTimeline.complaint_id == complaint_id)
        .order_by(ComplaintTimeline.timestamp)
    ).all()
    
    return timeline
