"""
End-to-End Workflow Tests

Tests complete workflows from complaint creation through resolution,
including all components: complaints, assets, repairs, verification,
priority evaluation, and dashboard metrics.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models.complaint import Complaint
from app.models.asset import Asset


class TestCompleteComplaintWorkflow:
    """Test complete complaint lifecycle from creation to resolution."""
    
    def test_full_complaint_workflow_e2e(self, client: TestClient, session: Session):
        """Test complete workflow: create → prioritize → repair → verify → resolve."""
        
        # 1. Create an asset
        asset_data = {
            "id": "SL-W12-001",
            "asset_type": "Streetlight",
            "name": "Main Junction Light",
            "ward": "Ward 12",
            "latitude": 22.3152,
            "longitude": 73.1856,
        }
        response = client.post("/api/assets", json=asset_data)
        assert response.status_code == 201
        assert response.json()["id"] == "SL-W12-001"
        
        # 2. Create a complaint
        complaint_data = {
            "title": "Broken streetlight",
            "description": "The streetlight at main junction has been broken for 2 weeks and needs urgent repair",
            "category": "Streetlight",
            "location_text": "Main Junction, Ward 12",
            "latitude": 22.3152,
            "longitude": 73.1856,
            "ward": "Ward 12",
            "asset_id": "SL-W12-001",
        }
        response = client.post("/api/complaints", json=complaint_data)
        assert response.status_code == 201
        complaint = response.json()
        complaint_id = complaint["id"]
        assert complaint["status"] == "Reported"
        
        # 3. Evaluate priority
        response = client.post(f"/api/complaints/{complaint_id}/priority/evaluate")
        assert response.status_code == 200
        priority_eval = response.json()
        assert "priority_score" in priority_eval
        assert priority_eval["model_version"] == "development-mock-v1"
        
        # 4. Update priority based on evaluation (PATCH endpoint)
        update_data = {
            "priority": priority_eval["priority_category"],
            "priority_score": priority_eval["priority_score"] or 75,
            "assigned_team": "Maintenance Team A"
        }
        response = client.patch(f"/api/complaints/{complaint_id}", json=update_data)
        assert response.status_code == 200
        
        # 5. Update status to Assigned
        status_update = {"status": "Assigned", "note": "Assigned to Maintenance Team A"}
        response = client.patch(f"/api/complaints/{complaint_id}/status", json=status_update)
        assert response.status_code == 200
        assert response.json()["status"] == "Assigned"
        
        # 6. Update status to In Progress
        status_update = {"status": "In Progress", "note": "Work started"}
        response = client.patch(f"/api/complaints/{complaint_id}/status", json=status_update)
        assert response.status_code == 200
        assert response.json()["status"] == "In Progress"
        
        # 7. Create repair record
        repair_data = {
            "description": "Replaced broken LED bulb with new energy-efficient bulb",
            "assigned_team": "Maintenance Team A",
        }
        response = client.post(f"/api/complaints/{complaint_id}/repairs", json=repair_data)
        assert response.status_code == 201
        repair = response.json()
        repair_id = repair["id"]
        assert repair["verification_status"] == "Pending"
        
        # 8. Update repair with completion details
        progress_data = {
            "description": "Replaced broken LED bulb with new energy-efficient bulb. Tested and working.",
            "repair_date": "2026-01-15T14:30:00"
        }
        response = client.patch(
            f"/api/complaints/{complaint_id}/repairs/{repair_id}/progress",
            json=progress_data
        )
        assert response.status_code == 200
        assert response.json()["repair_date"] is not None
        
        # 9. Verify repair completion
        verify_data = {
            "verification_status": "Verified",
            "evidence_reference": "https://s3.example.com/photos/repair-001.jpg",
            "verified_by": "Inspector A"
        }
        response = client.patch(
            f"/api/complaints/{complaint_id}/repairs/{repair_id}/verify",
            json=verify_data
        )
        assert response.status_code == 200
        assert response.json()["verification_status"] == "Verified"
        
        # 10. Update status to Awaiting Verification
        status_update = {"status": "Awaiting Verification", "note": "Repair verified"}
        response = client.patch(f"/api/complaints/{complaint_id}/status", json=status_update)
        assert response.status_code == 200
        
        # 11. Resolve complaint
        status_update = {"status": "Resolved", "note": "Issue resolved and verified"}
        response = client.patch(f"/api/complaints/{complaint_id}/status", json=status_update)
        assert response.status_code == 200
        assert response.json()["status"] == "Resolved"
        
        # 12. Get full complaint details
        response = client.get(f"/api/complaints/{complaint_id}")
        assert response.status_code == 200
        final_complaint = response.json()
        assert final_complaint["status"] == "Resolved"
        
        # 13. Retrieve timeline
        response = client.get(f"/api/complaints/{complaint_id}/timeline")
        assert response.status_code == 200
        timeline = response.json()
        assert len(timeline) >= 5  # At least: Reported, Assigned, In Progress, Awaiting Verification, Resolved
        
        # 14. Retrieve audit history
        response = client.get(f"/api/complaints/{complaint_id}/history")
        assert response.status_code == 200
        history = response.json()
        assert history["total"] >= 5  # Multiple audit entries (create, status changes, repair, verification)
        
        # Verify audit trail contains expected actions
        actions = [entry["action"] for entry in history["items"]]
        assert "create" in actions
        assert "status_change" in actions
        assert "repair_start" in actions
        assert "verification" in actions
    
    def test_complaint_with_multiple_repairs_e2e(self, client: TestClient, session: Session):
        """Test complaint with multiple repair attempts."""
        
        # Create complaint
        complaint_data = {
            "title": "Recurring drainage issue",
            "description": "Drainage pipe blocked multiple times in same location",
            "category": "Drainage",
            "location_text": "Main Street intersection",
            "ward": "Ward 5",
            "repeat_complaint_count": 2,
        }
        response = client.post("/api/complaints", json=complaint_data)
        complaint_id = response.json()["id"]
        
        # Assign to team
        update_data = {"assigned_team": "Infrastructure Team B"}
        client.patch(f"/api/complaints/{complaint_id}", json=update_data)
        
        # Update to In Progress
        client.patch(f"/api/complaints/{complaint_id}/status", 
                    json={"status": "Under Review"})
        client.patch(f"/api/complaints/{complaint_id}/status", 
                    json={"status": "Assigned"})
        client.patch(f"/api/complaints/{complaint_id}/status", 
                    json={"status": "In Progress"})
        
        # First repair attempt
        repair1_data = {
            "description": "Cleared drain pipe",
            "assigned_team": "Infrastructure Team B",
        }
        response = client.post(f"/api/complaints/{complaint_id}/repairs", json=repair1_data)
        repair1_id = response.json()["id"]
        
        # Verify first repair failed
        client.patch(f"/api/complaints/{complaint_id}/repairs/{repair1_id}/verify",
                    json={"verification_status": "Failed", "verified_by": "Inspector"})
        
        # Continue complaint
        client.patch(f"/api/complaints/{complaint_id}/status", 
                    json={"status": "In Progress"})
        
        # Second repair attempt
        repair2_data = {
            "description": "Replaced section of drain pipe with new material",
            "assigned_team": "Infrastructure Team B",
        }
        response = client.post(f"/api/complaints/{complaint_id}/repairs", json=repair2_data)
        repair2_id = response.json()["id"]
        
        # Verify second repair succeeded
        client.patch(f"/api/complaints/{complaint_id}/repairs/{repair2_id}/verify",
                    json={"verification_status": "Verified", "verified_by": "Inspector"})
        
        # Resolve
        client.patch(f"/api/complaints/{complaint_id}/status",
                    json={"status": "Awaiting Verification"})
        client.patch(f"/api/complaints/{complaint_id}/status",
                    json={"status": "Resolved"})
        
        # Verify both repairs are in history
        response = client.get(f"/api/complaints/{complaint_id}/repairs")
        assert response.status_code == 200
        repairs = response.json()
        assert len(repairs) == 2


class TestMapAndDashboardE2E:
    """Test map and dashboard with real data."""
    
    def test_map_data_with_mixed_items_e2e(self, client: TestClient, session: Session):
        """Test map data endpoint with complaints and assets."""
        
        # Create assets
        for i in range(2):
            asset_data = {
                "id": f"SL-W12-{100+i:03d}",
                "asset_type": "Streetlight",
                "name": f"Light {i}",
                "ward": "Ward 12",
                "latitude": 22.3152 + i * 0.001,
                "longitude": 73.1856 + i * 0.001,
            }
            resp = client.post("/api/assets", json=asset_data)
            assert resp.status_code == 201
        
        # Create complaints
        for i in range(2):
            complaint_data = {
                "title": f"Issue {i}",
                "description": f"Test issue {i}",
                "category": "Streetlight",
                "location_text": f"Location {i}",
                "latitude": 22.3152 + i * 0.001,
                "longitude": 73.1856 + i * 0.001,
            }
            resp = client.post("/api/complaints", json=complaint_data)
            assert resp.status_code == 201
        
        # Get map data
        response = client.get("/api/dashboard/map-data")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["complaints"]) == 2
        assert len(data["assets"]) == 2
        assert data["total_markers"] == 4
    
    def test_dashboard_stats_reflect_workflow_e2e(self, client: TestClient, session: Session):
        """Test that dashboard stats update correctly through workflow."""
        
        # Create initial complaints
        for i in range(5):
            complaint_data = {
                "title": f"Issue {i}",
                "description": "Test issue",
                "category": "Streetlight",
                "location_text": f"Location {i}",
            }
            response = client.post("/api/complaints", json=complaint_data)
            complaint_id = response.json()["id"]
            
            # Move some through workflow
            if i < 2:  # Resolve first 2 through proper transitions
                # Reported -> Under Review -> Assigned -> In Progress -> Awaiting Verification -> Resolved
                client.patch(f"/api/complaints/{complaint_id}/status",
                           json={"status": "Under Review"})
                client.patch(f"/api/complaints/{complaint_id}/status",
                           json={"status": "Assigned"})
                client.patch(f"/api/complaints/{complaint_id}/status",
                           json={"status": "In Progress"})
                client.patch(f"/api/complaints/{complaint_id}/status",
                           json={"status": "Awaiting Verification"})
                client.patch(f"/api/complaints/{complaint_id}/status",
                           json={"status": "Resolved"})
        
        # Check dashboard stats
        response = client.get("/api/dashboard/stats")
        assert response.status_code == 200
        stats = response.json()
        
        assert stats["complaints"]["total"] == 5
        assert stats["complaints"]["resolved"] == 2
        assert stats["complaints"]["open"] == 3
    
    def test_priority_summary_with_real_distribution_e2e(self, client: TestClient, session: Session):
        """Test priority summary reflects actual priority distribution."""
        
        # Create complaints with different priorities
        priorities = ["Low", "Medium", "High", "Critical"]
        counts = [1, 2, 3, 1]  # Different count for each priority
        
        for priority, count in zip(priorities, counts):
            for i in range(count):
                complaint_data = {
                    "title": f"{priority} issue {i}",
                    "description": f"Issue with {priority} priority",
                    "category": "Streetlight",
                    "location_text": "Test",
                    "priority": priority,
                }
                resp = client.post("/api/complaints", json=complaint_data)
                assert resp.status_code == 201
        
        # Get priority summary
        response = client.get("/api/dashboard/priority-summary")
        assert response.status_code == 200
        data = response.json()
        
        # Verify total count
        assert data["total_complaints"] == 7  # 1+2+3+1
        
        # Verify distributions exist
        assert "by_priority" in data
        assert "distribution_percentage" in data
        
        # Verify percentages sum to ~100
        if data["distribution_percentage"]:
            total_pct = sum(data["distribution_percentage"].values())
            assert abs(total_pct - 100.0) < 0.1
