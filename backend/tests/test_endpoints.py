"""Tests for API endpoints."""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models.asset import Asset
from app.models.complaint import Complaint, ComplaintTimeline
from app.models.repair import RepairRecord

# ==================== Health & Root Tests ====================

def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data

def test_root(client: TestClient):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "docs" in data

# ==================== Asset Tests ====================

def test_create_asset(client: TestClient):
    """Test creating an asset."""
    asset_data = {
        "id": "SL-W12-001",
        "asset_type": "Streetlight",
        "name": "Test Light",
        "ward": "Ward 12",
        "latitude": 22.3152,
        "longitude": 73.1856,
    }
    response = client.post("/api/assets", json=asset_data)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == "SL-W12-001"
    assert data["asset_type"] == "Streetlight"

def test_get_asset(client: TestClient, session: Session):
    """Test getting an asset."""
    # Create asset in database
    asset = Asset(
        id="SL-W12-001",
        asset_type="Streetlight",
        name="Test Light",
        ward="Ward 12",
    )
    session.add(asset)
    session.commit()
    
    response = client.get("/api/assets/SL-W12-001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "SL-W12-001"

def test_get_nonexistent_asset(client: TestClient):
    """Test getting a non-existent asset."""
    response = client.get("/api/assets/NONEXISTENT")
    assert response.status_code == 404

def test_list_assets(client: TestClient, session: Session):
    """Test listing assets with pagination."""
    # Create test assets
    for i in range(5):
        asset = Asset(
            id=f"SL-W12-{i:03d}",
            asset_type="Streetlight",
            name=f"Light {i}",
            ward="Ward 12",
        )
        session.add(asset)
    session.commit()
    
    response = client.get("/api/assets?skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 5

def test_list_assets_with_ward_filter(client: TestClient, session: Session):
    """Test listing assets with ward filter."""
    # Create assets in different wards
    for ward_num in [11, 12, 13]:
        asset = Asset(
            id=f"SL-W{ward_num}-001",
            asset_type="Streetlight",
            name=f"Light {ward_num}",
            ward=f"Ward {ward_num}",
        )
        session.add(asset)
    session.commit()
    
    response = client.get("/api/assets?ward=Ward%2012")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["ward"] == "Ward 12"

def test_create_complaint(client: TestClient):
    """Test creating a complaint."""
    complaint_data = {
        "title": "Streetlight broken",
        "description": "Light is not working",
        "category": "Streetlight",
        "location_text": "Main Road",
        "latitude": 22.3152,
        "longitude": 73.1856,
        "ward": "Ward 12",
    }
    response = client.post("/api/complaints", json=complaint_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Streetlight broken"
    assert data["status"] == "Reported"
    assert "id" in data  # Should have generated ID

def test_get_complaint(client: TestClient, session: Session):
    """Test getting a complaint."""
    # Create complaint
    complaint = Complaint(
        id="CP-2026-0101",
        title="Test Issue",
        description="Test",
        category="Streetlight",
        location_text="Test",
    )
    session.add(complaint)
    session.commit()
    
    response = client.get("/api/complaints/CP-2026-0101")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "CP-2026-0101"

def test_get_nonexistent_complaint(client: TestClient):
    """Test getting a non-existent complaint."""
    response = client.get("/api/complaints/NONEXISTENT")
    assert response.status_code == 404

def test_list_complaints(client: TestClient, session: Session):
    """Test listing complaints with pagination."""
    # Create test complaints
    for i in range(5):
        complaint = Complaint(
            id=f"CP-2026-010{i}",
            title=f"Issue {i}",
            description="Test",
            category="Streetlight",
            location_text="Test",
        )
        session.add(complaint)
    session.commit()
    
    response = client.get("/api/complaints?skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5

def test_list_complaints_with_priority_filter(client: TestClient, session: Session):
    """Test listing complaints with priority filter."""
    # Create complaints with different priorities
    for priority in ["Low", "Medium", "High", "Critical"]:
        complaint = Complaint(
            id=f"CP-2026-{priority[:2].upper()}-01",
            title=f"{priority} Issue",
            description="Test",
            category="Streetlight",
            location_text="Test",
            priority=priority,
        )
        session.add(complaint)
    session.commit()
    
    response = client.get("/api/complaints?priority=High")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["priority"] == "High"

def test_pagination(client: TestClient, session: Session):
    """Test pagination parameters."""
    # Create 25 complaints
    for i in range(25):
        complaint = Complaint(
            id=f"CP-2026-{i:04d}",
            title=f"Issue {i}",
            description="Test",
            category="Streetlight",
            location_text="Test",
        )
        session.add(complaint)
    session.commit()
    
    # Test first page
    response = client.get("/api/complaints?skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 10
    assert data["total"] == 25
    assert data["skip"] == 0
    assert data["limit"] == 10
    
    # Test second page
    response = client.get("/api/complaints?skip=10&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 10
    assert data["skip"] == 10

def test_invalid_limit_pagination(client: TestClient):
    """Test that invalid pagination limits are rejected."""
    # Limit > 100 should be capped
    response = client.get("/api/complaints?limit=200")
    assert response.status_code == 422  # Validation error
    
    # Limit < 1 should be rejected
    response = client.get("/api/complaints?limit=0")
    assert response.status_code == 422

def test_list_assets_with_ward_filter(client: TestClient, session: Session):
    """Test listing assets with ward filter."""
    # Create assets in different wards
    for i, ward in enumerate(["Ward 1", "Ward 2", "Ward 1"]):
        asset = Asset(
            id=f"SL-W-{i:03d}",
            asset_type="Streetlight",
            name=f"Light {i}",
            ward=ward,
        )
        session.add(asset)
    session.commit()
    
    response = client.get("/api/assets?ward=Ward%201")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2

def test_patch_asset(client: TestClient, session: Session):
    """Test patching an asset."""
    asset = Asset(
        id="SL-W12-001",
        asset_type="Streetlight",
        name="Old Name",
        ward="Ward 12",
        condition="Good",
    )
    session.add(asset)
    session.commit()
    
    patch_data = {"name": "New Name", "condition": "Poor"}
    response = client.patch("/api/assets/SL-W12-001", json=patch_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name"
    assert data["condition"] == "Poor"

# ==================== Complaint Tests ====================

def test_create_complaint(client: TestClient):
    """Test creating a complaint."""
    complaint_data = {
        "title": "Broken streetlight",
        "description": "Streetlight is not working at main junction",
        "category": "Streetlight",
        "location_text": "Main Junction, Ward 12",
        "latitude": 22.3152,
        "longitude": 73.1856,
        "ward": "Ward 12",
    }
    response = client.post("/api/complaints", json=complaint_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Broken streetlight"
    assert data["status"] == "Reported"
    assert "CP-" in data["id"]  # Should have auto-generated ID

def test_get_complaint(client: TestClient, session: Session):
    """Test getting a complaint."""
    complaint = Complaint(
        id="CP-2026-0001",
        title="Test Issue",
        description="Test description",
        category="Streetlight",
        location_text="Test Location",
    )
    session.add(complaint)
    session.commit()
    
    response = client.get("/api/complaints/CP-2026-0001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "CP-2026-0001"
    assert data["title"] == "Test Issue"

def test_get_nonexistent_complaint(client: TestClient):
    """Test getting a non-existent complaint."""
    response = client.get("/api/complaints/NONEXISTENT")
    assert response.status_code == 404

def test_list_complaints(client: TestClient, session: Session):
    """Test listing complaints."""
    for i in range(3):
        complaint = Complaint(
            id=f"CP-2026-000{i}",
            title=f"Issue {i}",
            description="Test description",
            category="Streetlight",
            location_text="Test Location",
        )
        session.add(complaint)
    session.commit()
    
    response = client.get("/api/complaints?skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3

def test_list_complaints_with_priority_filter(client: TestClient, session: Session):
    """Test filtering complaints by priority."""
    for priority in ["Low", "Medium", "High"]:
        complaint = Complaint(
            id=f"CP-2026-{priority}",
            title=f"{priority} Issue",
            description="Test",
            category="Streetlight",
            location_text="Test",
            priority=priority,
        )
        session.add(complaint)
    session.commit()
    
    response = client.get("/api/complaints?priority=High")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1

def test_patch_complaint(client: TestClient, session: Session):
    """Test patching complaint fields."""
    complaint = Complaint(
        id="CP-2026-0001",
        title="Original Title",
        description="Original description that is long enough",
        category="Streetlight",
        location_text="Test",
        priority="Low",
    )
    session.add(complaint)
    session.commit()
    
    patch_data = {"priority": "High", "assigned_team": "Team A"}
    response = client.patch("/api/complaints/CP-2026-0001", json=patch_data)
    assert response.status_code == 200
    data = response.json()
    assert data["priority"] == "High"
    assert data["assigned_team"] == "Team A"

def test_update_complaint_status_valid_transition(client: TestClient, session: Session):
    """Test valid status transition."""
    complaint = Complaint(
        id="CP-2026-0001",
        title="Test",
        description="Test description",
        category="Streetlight",
        location_text="Test",
        status="Reported",
    )
    session.add(complaint)
    session.commit()
    
    status_data = {"status": "Under Review", "note": "Now reviewing"}
    response = client.patch("/api/complaints/CP-2026-0001/status", json=status_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Under Review"

def test_update_complaint_status_invalid_transition(client: TestClient, session: Session):
    """Test invalid status transition."""
    complaint = Complaint(
        id="CP-2026-0001",
        title="Test",
        description="Test description",
        category="Streetlight",
        location_text="Test",
        status="Reported",
    )
    session.add(complaint)
    session.commit()
    
    # Try invalid transition: Reported -> In Progress (should go through Under Review/Assigned first)
    status_data = {"status": "In Progress"}
    response = client.patch("/api/complaints/CP-2026-0001/status", json=status_data)
    assert response.status_code == 400

# ==================== Repair Tests ====================

def test_create_repair_record(client: TestClient, session: Session):
    """Test creating a repair record."""
    complaint = Complaint(
        id="CP-2026-0001",
        title="Test",
        description="Test description",
        category="Streetlight",
        location_text="Test",
    )
    session.add(complaint)
    session.commit()
    
    repair_data = {
        "description": "Replaced broken bulb with new LED",
        "assigned_team": "Maintenance Team A",
    }
    response = client.post("/api/complaints/CP-2026-0001/repairs", json=repair_data)
    assert response.status_code == 201
    data = response.json()
    assert "RP-" in data["id"]
    assert data["complaint_id"] == "CP-2026-0001"
    assert data["verification_status"] == "Pending"

def test_get_complaint_repairs(client: TestClient, session: Session):
    """Test getting all repairs for a complaint."""
    complaint = Complaint(
        id="CP-2026-0001",
        title="Test",
        description="Test description",
        category="Streetlight",
        location_text="Test",
    )
    session.add(complaint)
    session.commit()
    
    for i in range(2):
        repair = RepairRecord(
            id=f"RP-20260115-000{i}",
            complaint_id="CP-2026-0001",
            description=f"Repair work {i}",
        )
        session.add(repair)
    session.commit()
    
    response = client.get("/api/complaints/CP-2026-0001/repairs")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

def test_verify_repair_completion(client: TestClient, session: Session):
    """Test verifying repair completion."""
    complaint = Complaint(
        id="CP-2026-0001",
        title="Test",
        description="Test description",
        category="Streetlight",
        location_text="Test",
    )
    session.add(complaint)
    session.commit()
    
    repair = RepairRecord(
        id="RP-20260115-0001",
        complaint_id="CP-2026-0001",
        description="Repair work done",
    )
    session.add(repair)
    session.commit()
    
    verify_data = {
        "verification_status": "Verified",
        "evidence_reference": "https://example.com/photo.jpg",
        "verified_by": "Inspector A",
    }
    response = client.patch(
        "/api/complaints/CP-2026-0001/repairs/RP-20260115-0001/verify",
        json=verify_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["verification_status"] == "Verified"
    assert data["verified_by"] == "Inspector A"

def test_verify_repair_invalid_status(client: TestClient, session: Session):
    """Test verifying repair with invalid status."""
    complaint = Complaint(
        id="CP-2026-0001",
        title="Test",
        description="Test description",
        category="Streetlight",
        location_text="Test",
    )
    session.add(complaint)
    session.commit()
    
    repair = RepairRecord(
        id="RP-20260115-0001",
        complaint_id="CP-2026-0001",
        description="Repair work",
    )
    session.add(repair)
    session.commit()
    
    verify_data = {
        "verification_status": "InvalidStatus",
    }
    response = client.patch(
        "/api/complaints/CP-2026-0001/repairs/RP-20260115-0001/verify",
        json=verify_data
    )
    assert response.status_code == 400

# ==================== Audit & History Tests ====================

def test_get_complaint_timeline(client: TestClient, session: Session):
    """Test getting complaint status timeline."""
    complaint = Complaint(
        id="CP-2026-0001",
        title="Test",
        description="Test description",
        category="Streetlight",
        location_text="Test",
    )
    session.add(complaint)
    
    # Add timeline entries
    for i, status in enumerate(["Reported", "Under Review"]):
        timeline = ComplaintTimeline(
            complaint_id="CP-2026-0001",
            status=status,
            note=f"Status {i}",
        )
        session.add(timeline)
    session.commit()
    
    response = client.get("/api/complaints/CP-2026-0001/timeline")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["status"] == "Reported"

def test_get_complaint_history(client: TestClient, session: Session):
    """Test getting complete complaint audit history."""
    complaint = Complaint(
        id="CP-2026-0001",
        title="Test",
        description="Test description",
        category="Streetlight",
        location_text="Test",
    )
    session.add(complaint)
    session.commit()
    
    response = client.get("/api/complaints/CP-2026-0001/history?skip=0&limit=100")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data

# ==================== Edge Cases & Validation ====================

def test_pagination(client: TestClient, session: Session):
    """Test pagination works correctly."""
    for i in range(15):
        complaint = Complaint(
            id=f"CP-2026-{i:04d}",
            title=f"Issue {i}",
            description="Test",
            category="Streetlight",
            location_text="Test",
        )
        session.add(complaint)
    session.commit()
    
    # Get first page
    response = client.get("/api/complaints?skip=0&limit=5")
    data = response.json()
    assert len(data["items"]) == 5
    assert data["total"] == 15
    
    # Get second page
    response = client.get("/api/complaints?skip=5&limit=5")
    data = response.json()
    assert len(data["items"]) == 5

def test_invalid_limit_pagination(client: TestClient):
    """Test pagination with invalid limit."""
    response = client.get("/api/complaints?limit=200")
    assert response.status_code == 422  # Validation error

def test_create_complaint_with_missing_required_field(client: TestClient):
    """Test creating complaint without required field."""
    complaint_data = {
        "title": "Broken streetlight",
        # missing description - required field
        "category": "Streetlight",
        "location_text": "Main Junction",
    }
    response = client.post("/api/complaints", json=complaint_data)
    assert response.status_code == 422

def test_status_complete_workflow(client: TestClient, session: Session):
    """Test complete complaint workflow through statuses."""
    complaint_data = {
        "title": "Issue",
        "description": "Detailed issue description",
        "category": "Streetlight",
        "location_text": "Location",
    }
    response = client.post("/api/complaints", json=complaint_data)
    assert response.status_code == 201
    complaint_id = response.json()["id"]
    
    # Reported -> Under Review
    response = client.patch(
        f"/api/complaints/{complaint_id}/status",
        json={"status": "Under Review"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "Under Review"
    
    # Under Review -> Assigned
    response = client.patch(
        f"/api/complaints/{complaint_id}/status",
        json={"status": "Assigned"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "Assigned"
    
    # Assigned -> In Progress
    response = client.patch(
        f"/api/complaints/{complaint_id}/status",
        json={"status": "In Progress"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "In Progress"
    
    # In Progress -> Awaiting Verification
    response = client.patch(
        f"/api/complaints/{complaint_id}/status",
        json={"status": "Awaiting Verification"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "Awaiting Verification"
    
    # Awaiting Verification -> Resolved
    response = client.patch(
        f"/api/complaints/{complaint_id}/status",
        json={"status": "Resolved"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "Resolved"
