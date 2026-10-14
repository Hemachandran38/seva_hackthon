"""
Seed script for loading demonstration data.

This script creates demo assets and complaints for testing.
Only use in development - NOT for production databases.
"""

import logging
from datetime import datetime, timedelta
from sqlmodel import Session, select
from app.database import engine, SessionLocal
from app.models.asset import Asset
from app.models.complaint import Complaint, ComplaintTimeline
from app.models.repair import RepairRecord
from app.models.audit import AuditLog
from sqlmodel import SQLModel

logger = logging.getLogger(__name__)

# Demo data
DEMO_ASSETS = [
    {
        "id": "SL-W12-001",
        "asset_type": "Streetlight",
        "name": "Main Ring Road Pole 45",
        "ward": "Ward 12",
        "latitude": 22.3152,
        "longitude": 73.1856,
        "installation_date": datetime(2020, 1, 15),
        "condition": "Poor",
    },
    {
        "id": "RD-W13-002",
        "asset_type": "Road & pavement",
        "name": "Jagannath Road Segment A",
        "ward": "Ward 13",
        "latitude": 22.3234,
        "longitude": 73.1923,
        "installation_date": datetime(2018, 6, 20),
        "condition": "Fair",
    },
    {
        "id": "DR-W12-003",
        "asset_type": "Drainage",
        "name": "Rajendra Nagar Channel",
        "ward": "Ward 12",
        "latitude": 22.3102,
        "longitude": 73.1789,
        "installation_date": datetime(2015, 3, 10),
        "condition": "Critical",
    },
    {
        "id": "EL-W11-004",
        "asset_type": "Electrical Hazard",
        "name": "Ganesh Nagar Utility Pole",
        "ward": "Ward 11",
        "latitude": 22.3289,
        "longitude": 73.1654,
        "installation_date": datetime(2019, 8, 5),
        "condition": "Good",
    },
    {
        "id": "PS-W12-005",
        "asset_type": "Public space",
        "name": "Govind Nagar Park",
        "ward": "Ward 12",
        "latitude": 22.3076,
        "longitude": 73.1945,
        "installation_date": datetime(2021, 12, 1),
        "condition": "Fair",
    },
]

DEMO_COMPLAINTS = [
    {
        "id": "CP-2026-0101",
        "title": "Streetlight blackout near main ring road",
        "description": "Streetlight completely non-functional; dark stretch creates safety hazard at night.",
        "category": "Streetlight",
        "location_text": "Main Ring Road, Sector 4, Ward 12",
        "latitude": 22.3152,
        "longitude": 73.1856,
        "ward": "Ward 12",
        "priority": "High",
        "priority_score": 86,
        "status": "In Progress",
        "repeat_complaint_count": 2,
        "asset_id": "SL-W12-001",
        "assigned_team": "Municipal Crew Alpha",
        "reported_at": datetime.utcnow() - timedelta(days=10),
    },
    {
        "id": "CP-2026-0102",
        "title": "Pothole on Jagannath Road",
        "description": "Large pothole causing traffic hazard and vehicle damage.",
        "category": "Road & pavement",
        "location_text": "Jagannath Road, Ward 13",
        "latitude": 22.3234,
        "longitude": 73.1923,
        "ward": "Ward 13",
        "priority": "Medium",
        "priority_score": 65,
        "status": "Resolved",
        "repeat_complaint_count": 1,
        "asset_id": "RD-W13-002",
        "assigned_team": "Road Maintenance Team",
        "reported_at": datetime.utcnow() - timedelta(days=15),
    },
    {
        "id": "CP-2026-0103",
        "title": "Clogged drainage causing stagnation",
        "description": "Drainage completely blocked, causing water stagnation and mosquito breeding.",
        "category": "Drainage",
        "location_text": "Rajendra Nagar, Ward 12",
        "latitude": 22.3102,
        "longitude": 73.1789,
        "ward": "Ward 12",
        "priority": "Critical",
        "priority_score": 92,
        "status": "Reported",
        "repeat_complaint_count": 3,
        "asset_id": "DR-W12-003",
        "reported_at": datetime.utcnow() - timedelta(days=2),
    },
    {
        "id": "CP-2026-0104",
        "title": "Electrical hazard at utility pole",
        "description": "Exposed live wires hanging dangerously low near pedestrian walkway.",
        "category": "Electrical Hazard",
        "location_text": "Ganesh Nagar Crossing, Ward 11",
        "latitude": 22.3289,
        "longitude": 73.1654,
        "ward": "Ward 11",
        "priority": "Critical",
        "priority_score": 95,
        "status": "Awaiting Verification",
        "repeat_complaint_count": 0,
        "asset_id": "EL-W11-004",
        "assigned_team": "Electrical Safety Team",
        "reported_at": datetime.utcnow() - timedelta(days=5),
    },
    {
        "id": "CP-2026-0105",
        "title": "Broken streetlight glass",
        "description": "Streetlight globe shattered, creating safety and vandalism risk.",
        "category": "Streetlight",
        "location_text": "Govind Nagar Park, Ward 12",
        "latitude": 22.3076,
        "longitude": 73.1945,
        "ward": "Ward 12",
        "priority": "Medium",
        "priority_score": 54,
        "status": "Reported",
        "repeat_complaint_count": 0,
        "asset_id": "PS-W12-005",
        "reported_at": datetime.utcnow() - timedelta(days=7),
    },
]

def seed_database():
    """Load demo data into database."""
    session = SessionLocal()
    
    try:
        logger.info("Starting database seed...")
        
        # Check if data already exists
        existing_assets = session.exec(select(Asset)).first()
        if existing_assets:
            logger.warning("Database already contains data. Skipping seed.")
            return
        
        # Create assets
        logger.info(f"Creating {len(DEMO_ASSETS)} demo assets...")
        for asset_data in DEMO_ASSETS:
            asset = Asset(**asset_data)
            session.add(asset)
        
        session.commit()
        logger.info(f"Created {len(DEMO_ASSETS)} assets")
        
        # Create complaints and timeline entries
        logger.info(f"Creating {len(DEMO_COMPLAINTS)} demo complaints...")
        for complaint_data in DEMO_COMPLAINTS:
            reported_at = complaint_data.pop("reported_at")
            complaint = Complaint(
                **complaint_data,
                reported_at=reported_at,
                updated_at=reported_at,
            )
            session.add(complaint)
            
            # Add initial timeline entry
            timeline = ComplaintTimeline(
                complaint_id=complaint.id,
                status="Reported",
                note="Complaint received",
                timestamp=reported_at,
            )
            session.add(timeline)
            
            # Add audit log
            audit = AuditLog(
                complaint_id=complaint.id,
                action="create",
                source="seed",
                details="Demo complaint created during seeding",
            )
            session.add(audit)
        
        session.commit()
        logger.info(f"Created {len(DEMO_COMPLAINTS)} complaints with timeline entries")
        
        # Create a sample repair record
        logger.info("Creating demo repair record...")
        repair = RepairRecord(
            id="RP-20260115-0001",
            complaint_id="CP-2026-0102",
            assigned_team="Road Maintenance Team",
            description="Pothole filled with asphalt and compacted",
            repair_date=datetime.utcnow() - timedelta(days=3),
            verification_status="Verified",
            evidence_reference="IMG-20260115-001.jpg",
        )
        session.add(repair)
        
        audit = AuditLog(
            complaint_id="CP-2026-0102",
            action="repair_record_create",
            source="seed",
            details="Demo repair record created during seeding",
        )
        session.add(audit)
        
        session.commit()
        logger.info("Created demo repair record")
        
        logger.info("Database seeding completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during seeding: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("\n⚠️  WARNING: This script loads DEMO DATA into the database.")
    print("Only use this in development environments.\n")
    
    response = input("Continue? (yes/no): ").strip().lower()
    if response == "yes":
        seed_database()
    else:
        print("Seeding cancelled.")
