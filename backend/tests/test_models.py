"""Tests for database models."""

import pytest
from datetime import datetime
from sqlmodel import Session
from app.models.asset import Asset
from app.models.complaint import Complaint, ComplaintTimeline
from app.models.repair import RepairRecord
from app.models.audit import AuditLog

def test_asset_creation(session: Session):
    """Test creating an asset."""
    asset = Asset(
        id="SL-W12-001",
        asset_type="Streetlight",
        name="Test Light",
        ward="Ward 12",
        latitude=22.3152,
        longitude=73.1856,
    )
    session.add(asset)
    session.commit()
    
    assert asset.id == "SL-W12-001"
    assert asset.asset_type == "Streetlight"

def test_asset_coordinate_validation():
    """Test coordinate validation for assets."""
    # Valid coordinates
    asset = Asset(
        id="SL-W12-001",
        asset_type="Streetlight",
        name="Test",
        ward="Ward 12",
        latitude=0.0,
        longitude=0.0,
    )
    assert asset.latitude == 0.0
    
    # Invalid latitude
    with pytest.raises(ValueError):
        Asset(
            id="SL-W12-002",
            asset_type="Streetlight",
            name="Test",
            ward="Ward 12",
            latitude=91.0,  # Out of range
            longitude=0.0,
        )

def test_complaint_creation(session: Session):
    """Test creating a complaint."""
    complaint = Complaint(
        id="CP-2026-0101",
        title="Test Issue",
        description="Test description",
        category="Streetlight",
        location_text="Test Location",
        priority="High",
        priority_score=85,
    )
    session.add(complaint)
    session.commit()
    
    assert complaint.id == "CP-2026-0101"
    assert complaint.priority == "High"
    assert complaint.status == "Reported"

def test_complaint_priority_validation():
    """Test priority validation."""
    # Valid priority
    complaint = Complaint(
        id="CP-2026-0101",
        title="Test",
        description="Test",
        category="Streetlight",
        location_text="Test",
        priority="Critical",
    )
    assert complaint.priority == "Critical"
    
    # Invalid priority
    with pytest.raises(ValueError):
        Complaint(
            id="CP-2026-0102",
            title="Test",
            description="Test",
            category="Streetlight",
            location_text="Test",
            priority="Urgent",  # Invalid
        )

def test_complaint_status_validation():
    """Test status validation."""
    complaint = Complaint(
        id="CP-2026-0101",
        title="Test",
        description="Test",
        category="Streetlight",
        location_text="Test",
        status="Resolved",
    )
    assert complaint.status == "Resolved"
    
    # Invalid status
    with pytest.raises(ValueError):
        Complaint(
            id="CP-2026-0102",
            title="Test",
            description="Test",
            category="Streetlight",
            location_text="Test",
            status="Closed",  # Invalid
        )

def test_complaint_priority_score_validation():
    """Test priority score validation."""
    # Valid score
    complaint = Complaint(
        id="CP-2026-0101",
        title="Test",
        description="Test",
        category="Streetlight",
        location_text="Test",
        priority_score=75,
    )
    assert complaint.priority_score == 75
    
    # Invalid score
    with pytest.raises(ValueError):
        Complaint(
            id="CP-2026-0102",
            title="Test",
            description="Test",
            category="Streetlight",
            location_text="Test",
            priority_score=101,  # Out of range
        )

def test_complaint_timeline_entry(session: Session):
    """Test creating complaint timeline entries."""
    complaint = Complaint(
        id="CP-2026-0101",
        title="Test",
        description="Test",
        category="Streetlight",
        location_text="Test",
    )
    session.add(complaint)
    
    timeline = ComplaintTimeline(
        complaint_id="CP-2026-0101",
        status="In Progress",
        note="Work started",
    )
    session.add(timeline)
    session.commit()
    
    assert timeline.status == "In Progress"
    assert timeline.complaint_id == "CP-2026-0101"

def test_repair_record(session: Session):
    """Test creating a repair record."""
    complaint = Complaint(
        id="CP-2026-0101",
        title="Test",
        description="Test",
        category="Streetlight",
        location_text="Test",
    )
    session.add(complaint)
    session.commit()
    
    repair = RepairRecord(
        id="RP-20260115-0001",
        complaint_id="CP-2026-0101",
        assigned_team="Team A",
        description="Fixed issue",
    )
    session.add(repair)
    session.commit()
    
    assert repair.complaint_id == "CP-2026-0101"
    assert repair.verification_status == "Pending"

def test_audit_log(session: Session):
    """Test creating audit log."""
    log = AuditLog(
        complaint_id="CP-2026-0101",
        action="create",
        actor="system",
        source="api",
    )
    session.add(log)
    session.commit()
    
    assert log.action == "create"
    assert log.source == "api"

def test_coordinate_range_validation():
    """Test coordinate range validation."""
    # Latitude range: -90 to 90
    # Longitude range: -180 to 180
    
    valid_asset = Asset(
        id="SL-W12-001",
        asset_type="Streetlight",
        name="Test",
        ward="Ward 12",
        latitude=-90.0,
        longitude=-180.0,
    )
    assert valid_asset.latitude == -90.0
    assert valid_asset.longitude == -180.0
    
    valid_asset2 = Asset(
        id="SL-W12-002",
        asset_type="Streetlight",
        name="Test",
        ward="Ward 12",
        latitude=90.0,
        longitude=180.0,
    )
    assert valid_asset2.latitude == 90.0
    assert valid_asset2.longitude == 180.0
