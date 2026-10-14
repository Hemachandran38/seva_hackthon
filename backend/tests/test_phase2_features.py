"""
Phase 2 Feature Tests: AI Priority, Dashboard, and Map Integration

Tests for:
- Priority evaluation endpoint
- Dashboard statistics
- Map data retrieval
- Filter functionality
- Empty database handling
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models.asset import Asset
from app.models.complaint import Complaint, ComplaintTimeline
from app.models.repair import RepairRecord


class TestPriorityEvaluation:
    """Test AI priority evaluation endpoints."""
    
    def test_evaluate_complaint_priority_mock(self, client: TestClient, session: Session):
        """Test priority evaluation with mock engine."""
        # Create a test complaint
        complaint = Complaint(
            id="CP-2026-0001",
            title="Broken streetlight",
            description="The streetlight at main junction has been broken for 2 weeks",
            category="Streetlight",
            location_text="Main Junction, Ward 12",
            priority="Medium",
            priority_score=50,
        )
        session.add(complaint)
        session.commit()
        
        # Evaluate priority
        response = client.post("/api/complaints/CP-2026-0001/priority/evaluate")
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert data["complaint_id"] == "CP-2026-0001"
        assert "priority_category" in data
        assert "priority_score" in data
        assert "explanation" in data
        assert "model_version" in data
        assert data["model_version"] == "development-mock-v1"
        
        # Verify disclaimer is in explanation
        assert "development" in data["explanation"].lower() or "mock" in data["explanation"].lower()
    
    def test_get_complaint_priority_mock(self, client: TestClient, session: Session):
        """Test GET priority endpoint with mock engine."""
        complaint = Complaint(
            id="CP-2026-0002",
            title="Broken road",
            description="Pothole at Station Road causing safety issues",
            category="Road & pavement",
            location_text="Station Road, Ward 5",
            repeat_complaint_count=3,  # Multiple complaints
        )
        session.add(complaint)
        session.commit()
        
        response = client.get("/api/complaints/CP-2026-0002/priority")
        assert response.status_code == 200
        data = response.json()
        
        assert data["complaint_id"] == "CP-2026-0002"
        assert "priority_score" in data
        # With repeat_complaint_count=3, score should be higher than 50
        assert data["priority_score"] >= 55
    
    def test_evaluate_nonexistent_complaint_priority(self, client: TestClient):
        """Test priority evaluation for nonexistent complaint."""
        response = client.post("/api/complaints/CP-9999-9999/priority/evaluate")
        assert response.status_code == 404
    
    def test_priority_with_coordinates(self, client: TestClient, session: Session):
        """Test that coordinates boost priority score."""
        # Complaint with coordinates
        complaint1 = Complaint(
            id="CP-2026-COORD1",
            title="Issue with coordinates",
            description="This issue has precise location information",
            category="Streetlight",
            location_text="Main St",
            latitude=22.3152,
            longitude=73.1856,
        )
        session.add(complaint1)
        session.commit()
        
        response1 = client.post("/api/complaints/CP-2026-COORD1/priority/evaluate")
        data1 = response1.json()
        score_with_coords = data1["priority_score"]
        
        # Complaint without coordinates
        complaint2 = Complaint(
            id="CP-2026-NOCOORD",
            title="Issue without coordinates",
            description="This issue has no precise location information",
            category="Streetlight",
            location_text="Somewhere in Ward 12",
        )
        session.add(complaint2)
        session.commit()
        
        response2 = client.post("/api/complaints/CP-2026-NOCOORD/priority/evaluate")
        data2 = response2.json()
        score_without_coords = data2["priority_score"]
        
        # Score with coordinates should be higher or equal
        assert score_with_coords >= score_without_coords
    
    def test_priority_safety_category_boost(self, client: TestClient, session: Session):
        """Test that electrical hazard gets priority boost."""
        # Electrical hazard (critical category)
        complaint1 = Complaint(
            id="CP-2026-ELEC",
            title="Electrical hazard",
            description="Exposed wires near playground",
            category="Electrical Hazard",
            location_text="Near Park",
        )
        session.add(complaint1)
        session.commit()
        
        response1 = client.post("/api/complaints/CP-2026-ELEC/priority/evaluate")
        data1 = response1.json()
        elec_score = data1["priority_score"]
        
        # Non-critical category
        complaint2 = Complaint(
            id="CP-2026-BENCH",
            title="Broken bench",
            description="Park bench is broken",
            category="Public space",
            location_text="Near Park",
        )
        session.add(complaint2)
        session.commit()
        
        response2 = client.post("/api/complaints/CP-2026-BENCH/priority/evaluate")
        data2 = response2.json()
        bench_score = data2["priority_score"]
        
        # Electrical hazard should score higher
        assert elec_score > bench_score


class TestDashboardStats:
    """Test dashboard statistics endpoints."""
    
    def test_dashboard_stats_empty_database(self, client: TestClient, session: Session):
        """Test stats endpoint with empty database."""
        response = client.get("/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        
        assert data["complaints"]["total"] == 0
        assert data["complaints"]["open"] == 0
        assert data["complaints"]["resolved"] == 0
    
    def test_dashboard_stats_with_data(self, client: TestClient, session: Session):
        """Test stats endpoint with complaint data."""
        # Create various complaints
        for i in range(5):
            status = "Resolved" if i < 2 else "In Progress"
            complaint = Complaint(
                id=f"CP-2026-{i:04d}",
                title=f"Issue {i}",
                description=f"Test issue {i}",
                category="Streetlight",
                location_text=f"Location {i}",
                status=status,
                priority="High" if i % 2 == 0 else "Low",
                repeat_complaint_count=i % 3,
            )
            session.add(complaint)
        session.commit()
        
        response = client.get("/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        
        assert data["complaints"]["total"] == 5
        assert data["complaints"]["open"] == 3
        assert data["complaints"]["resolved"] == 2
        assert "In Progress" in data["status_distribution"]
        assert "Resolved" in data["status_distribution"]
    
    def test_dashboard_stats_recent_period(self, client: TestClient, session: Session):
        """Test stats with different time periods."""
        # Create a complaint
        complaint = Complaint(
            id="CP-2026-0001",
            title="Recent issue",
            description="Recent issue",
            category="Streetlight",
            location_text="Test",
        )
        session.add(complaint)
        session.commit()
        
        # Test with 7 days
        response = client.get("/api/dashboard/stats?days=7")
        assert response.status_code == 200
        data = response.json()
        assert data["period_days"] == 7
        assert data["complaints"]["recent"] == 1
    
    def test_priority_summary(self, client: TestClient, session: Session):
        """Test priority summary endpoint."""
        # Create complaints with different priorities
        priorities = ["Low", "Medium", "High", "Critical"]
        for i, priority in enumerate(priorities):
            for j in range(i + 1):  # 1, 2, 3, 4 complaints for each
                complaint = Complaint(
                    id=f"CP-2026-{priority[:1]}-{j:02d}",
                    title=f"{priority} issue {j}",
                    description="Test",
                    category="Streetlight",
                    location_text="Test",
                    priority=priority,
                    assigned_team=None if j == 0 else "Team A",  # Some unassigned
                )
                session.add(complaint)
        session.commit()
        
        response = client.get("/api/dashboard/priority-summary")
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_complaints"] == 10  # 1+2+3+4
        assert data["by_priority"]["Low"] == 1
        assert data["by_priority"]["Medium"] == 2
        assert data["by_priority"]["High"] == 3
        assert data["by_priority"]["Critical"] == 4
        assert sum(data["distribution_percentage"].values()) == pytest.approx(100, abs=0.1)
    
    def test_asset_summary(self, client: TestClient, session: Session):
        """Test asset summary endpoint."""
        # Create various assets
        for i in range(3):
            asset = Asset(
                id=f"SL-W12-{i:03d}",
                asset_type="Streetlight",
                name=f"Light {i}",
                ward="Ward 12",
                condition="Good" if i == 0 else "Poor",
                latitude=22.3152 if i < 2 else None,
                longitude=73.1856 if i < 2 else None,
            )
            session.add(asset)
        
        # Add a road asset
        asset = Asset(
            id="RD-W12-001",
            asset_type="Road & pavement",
            name="Main Road",
            ward="Ward 12",
            condition="Fair",
        )
        session.add(asset)
        session.commit()
        
        response = client.get("/api/dashboard/asset-summary")
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_assets"] == 4
        assert data["by_type"]["Streetlight"] == 3
        assert data["by_type"]["Road & pavement"] == 1
        assert data["with_valid_coordinates"] == 2  # Only first 2 have coordinates


class TestMapIntegration:
    """Test map data endpoints."""
    
    def test_map_data_empty(self, client: TestClient, session: Session):
        """Test map data with empty database."""
        response = client.get("/api/dashboard/map-data")
        assert response.status_code == 200
        data = response.json()
        
        assert data["complaints"] == []
        assert data["assets"] == []
        assert data["total_markers"] == 0
    
    def test_map_data_with_complaints(self, client: TestClient, session: Session):
        """Test map data includes complaints."""
        complaint = Complaint(
            id="CP-2026-0001",
            title="Broken streetlight",
            description="Not working",
            category="Streetlight",
            location_text="Main Junction",
            latitude=22.3152,
            longitude=73.1856,
            status="In Progress",
            priority="High",
        )
        session.add(complaint)
        session.commit()
        
        response = client.get("/api/dashboard/map-data?include_complaints=true&include_assets=false")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["complaints"]) == 1
        assert data["complaints"][0]["id"] == "CP-2026-0001"
        assert data["complaints"][0]["type"] == "complaint"
        assert data["complaints"][0]["latitude"] == 22.3152
    
    def test_map_data_with_assets(self, client: TestClient, session: Session):
        """Test map data includes assets."""
        asset = Asset(
            id="SL-W12-001",
            asset_type="Streetlight",
            name="Main Junction Light",
            ward="Ward 12",
            latitude=22.3152,
            longitude=73.1856,
            condition="Good",
        )
        session.add(asset)
        session.commit()
        
        response = client.get("/api/dashboard/map-data?include_complaints=false&include_assets=true")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["assets"]) == 1
        assert data["assets"][0]["id"] == "SL-W12-001"
        assert data["assets"][0]["type"] == "asset"
    
    def test_map_data_coordinates_only_filter(self, client: TestClient, session: Session):
        """Test that coordinates_only filter works."""
        # With coordinates
        complaint1 = Complaint(
            id="CP-2026-0001",
            title="Issue with coords",
            description="Has coordinates",
            category="Streetlight",
            location_text="Location",
            latitude=22.3152,
            longitude=73.1856,
        )
        session.add(complaint1)
        
        # Without coordinates
        complaint2 = Complaint(
            id="CP-2026-0002",
            title="Issue without coords",
            description="No coordinates",
            category="Streetlight",
            location_text="Somewhere",
        )
        session.add(complaint2)
        session.commit()
        
        # Get all complaints
        response = client.get("/api/dashboard/map-data?coordinates_only=false")
        assert response.status_code == 200
        data = response.json()
        assert len(data["complaints"]) == 2
        
        # Get only complaints with coordinates
        response = client.get("/api/dashboard/map-data?coordinates_only=true")
        assert response.status_code == 200
        data = response.json()
        assert len(data["complaints"]) == 1
        assert data["complaints"][0]["id"] == "CP-2026-0001"
    
    def test_map_data_filters_priority(self, client: TestClient, session: Session):
        """Test map data filters by priority."""
        for priority in ["Low", "High", "Critical"]:
            complaint = Complaint(
                id=f"CP-2026-{priority[:1]}",
                title=f"{priority} issue",
                description="Test",
                category="Streetlight",
                location_text="Test",
                latitude=22.3 + float(ord(priority[0])) * 0.001,
                longitude=73.1,
                priority=priority,
            )
            session.add(complaint)
        session.commit()
        
        response = client.get("/api/dashboard/map-data?priority_filter=High")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["complaints"]) == 1
        assert data["complaints"][0]["priority"] == "High"
    
    def test_map_data_filters_status(self, client: TestClient, session: Session):
        """Test map data filters by status."""
        for status in ["Reported", "In Progress", "Resolved"]:
            complaint = Complaint(
                id=f"CP-2026-{status[:3]}",
                title=f"{status}",
                description="Test",
                category="Streetlight",
                location_text="Test",
                latitude=22.3,
                longitude=73.1,
                status=status,
            )
            session.add(complaint)
        session.commit()
        
        response = client.get("/api/dashboard/map-data?status_filter=Resolved")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["complaints"]) == 1
        assert data["complaints"][0]["status"] == "Resolved"
