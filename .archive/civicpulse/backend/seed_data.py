"""
seed_data.py — Populate the database with sample records.

All records are DEMO DATA only. They do not represent real
infrastructure locations or actual complaints in Coimbatore.

Run once:
    python seed_data.py
"""

from datetime import datetime
from database import engine, SessionLocal, Base
import models

# Create tables if they don't exist yet
Base.metadata.create_all(bind=engine)

# ── Sample assets ─────────────────────────────────────────────────────────────
SAMPLE_ASSETS = [
    {"asset_id": "SL-CBE-001", "asset_type": "Streetlight", "latitude": 11.0168, "longitude": 76.9558,
     "area_name": "RS Puram",        "installation_date": "2019-03-15", "condition": "poor"},
    {"asset_id": "SL-CBE-002", "asset_type": "Streetlight", "latitude": 11.0200, "longitude": 76.9620,
     "area_name": "Peelamedu",       "installation_date": "2020-06-20", "condition": "fair"},
    {"asset_id": "SL-CBE-003", "asset_type": "Streetlight", "latitude": 11.0135, "longitude": 76.9490,
     "area_name": "Gandhipuram",     "installation_date": "2018-11-10", "condition": "fair"},
    {"asset_id": "SL-CBE-004", "asset_type": "Streetlight", "latitude": 11.0250, "longitude": 76.9700,
     "area_name": "Saibaba Colony",  "installation_date": "2021-01-05", "condition": "good"},
    {"asset_id": "SL-CBE-005", "asset_type": "Streetlight", "latitude": 11.0095, "longitude": 76.9600,
     "area_name": "Singanallur",     "installation_date": "2017-08-22", "condition": "poor"},
    {"asset_id": "SL-CBE-006", "asset_type": "Streetlight", "latitude": 11.0310, "longitude": 76.9540,
     "area_name": "Ganapathy",       "installation_date": "2020-03-30", "condition": "fair"},
    {"asset_id": "SL-CBE-007", "asset_type": "Streetlight", "latitude": 11.0060, "longitude": 76.9670,
     "area_name": "Ukkadam",         "installation_date": "2019-07-14", "condition": "fair"},
    {"asset_id": "SL-CBE-008", "asset_type": "Streetlight", "latitude": 11.0190, "longitude": 76.9750,
     "area_name": "Vadavalli",       "installation_date": "2021-09-01", "condition": "good"},
    {"asset_id": "SL-CBE-009", "asset_type": "Streetlight", "latitude": 11.0360, "longitude": 76.9610,
     "area_name": "Uppilipalayam",   "installation_date": "2018-04-18", "condition": "poor"},
    {"asset_id": "SL-CBE-010", "asset_type": "Streetlight", "latitude": 11.0120, "longitude": 76.9820,
     "area_name": "Ramanathapuram",  "installation_date": "2020-12-10", "condition": "fair"},
    {"asset_id": "SL-CBE-011", "asset_type": "Streetlight", "latitude": 11.0290, "longitude": 76.9460,
     "area_name": "Kuniyamuthur",    "installation_date": "2019-05-25", "condition": "fair"},
    {"asset_id": "SL-CBE-012", "asset_type": "Streetlight", "latitude": 11.0450, "longitude": 76.9690,
     "area_name": "Kovaipudur",      "installation_date": "2022-02-14", "condition": "good"},
]

# ── Sample complaints ─────────────────────────────────────────────────────────
SAMPLE_COMPLAINTS = [
    {"asset_id": "SL-CBE-001", "issue_description": "Streetlight completely non-functional; dark stretch creates safety hazard at night.",
     "severity": "high",   "priority_score": 92, "priority_level": "high",   "status": "open",        "reported_at": datetime(2026, 10, 10)},
    {"asset_id": "SL-CBE-002", "issue_description": "Flickering light — bulb nearing end of life, intermittent failure.",
     "severity": "medium", "priority_score": 65, "priority_level": "medium", "status": "in-progress", "reported_at": datetime(2026, 10, 8)},
    {"asset_id": "SL-CBE-003", "issue_description": "Minor dimming observed; light still operational but below standard lux level.",
     "severity": "low",    "priority_score": 32, "priority_level": "low",    "status": "open",        "reported_at": datetime(2026, 10, 5)},
    {"asset_id": "SL-CBE-004", "issue_description": "Damaged pole after vehicle collision. Pole replaced and light restored.",
     "severity": "high",   "priority_score": 0,  "priority_level": "resolved","status": "resolved",   "reported_at": datetime(2026, 9, 28)},
    {"asset_id": "SL-CBE-005", "issue_description": "Exposed wiring at base of pole — electric shock risk reported by residents.",
     "severity": "high",   "priority_score": 88, "priority_level": "high",   "status": "open",        "reported_at": datetime(2026, 10, 11)},
    {"asset_id": "SL-CBE-006", "issue_description": "Light remains on during daytime due to faulty photosensor.",
     "severity": "medium", "priority_score": 58, "priority_level": "medium", "status": "in-progress", "reported_at": datetime(2026, 10, 7)},
    {"asset_id": "SL-CBE-007", "issue_description": "Overgrown tree branches partially blocking light cone.",
     "severity": "low",    "priority_score": 28, "priority_level": "low",    "status": "open",        "reported_at": datetime(2026, 10, 1)},
    {"asset_id": "SL-CBE-008", "issue_description": "Control panel fault causing group outage. MCB replaced and restored.",
     "severity": "high",   "priority_score": 0,  "priority_level": "resolved","status": "resolved",   "reported_at": datetime(2026, 9, 22)},
    {"asset_id": "SL-CBE-009", "issue_description": "Complete blackout across a 200 m stretch near school zone — urgent.",
     "severity": "high",   "priority_score": 95, "priority_level": "high",   "status": "open",        "reported_at": datetime(2026, 10, 12)},
    {"asset_id": "SL-CBE-010", "issue_description": "Light mounted at incorrect angle after last maintenance; beam misdirected.",
     "severity": "medium", "priority_score": 71, "priority_level": "medium", "status": "in-progress", "reported_at": datetime(2026, 10, 9)},
    {"asset_id": "SL-CBE-011", "issue_description": "Protective casing cracked; no immediate electrical hazard but needs replacement.",
     "severity": "low",    "priority_score": 22, "priority_level": "low",    "status": "open",        "reported_at": datetime(2026, 9, 30)},
    {"asset_id": "SL-CBE-012", "issue_description": "Vandalism — bulb shattered. New vandal-proof fitting installed.",
     "severity": "medium", "priority_score": 0,  "priority_level": "resolved","status": "resolved",   "reported_at": datetime(2026, 9, 18)},
]

# ── Sample repair records ──────────────────────────────────────────────────────
SAMPLE_REPAIRS = [
    {"complaint_id": 4,  "assigned_team": "Team Alpha", "repair_notes": "Replaced damaged pole and rewired fitting.",
     "repaired_at": datetime(2026, 9, 30), "verified_at": datetime(2026, 10, 1)},
    {"complaint_id": 8,  "assigned_team": "Team Beta",  "repair_notes": "Replaced faulty MCB in control panel; tested all lights on circuit.",
     "repaired_at": datetime(2026, 9, 24), "verified_at": datetime(2026, 9, 25)},
    {"complaint_id": 12, "assigned_team": "Team Gamma", "repair_notes": "Installed vandal-proof polycarbonate fitting.",
     "repaired_at": datetime(2026, 9, 20), "verified_at": datetime(2026, 9, 21)},
]


def seed():
    db = SessionLocal()
    try:
        # Skip if data already exists
        if db.query(models.Asset).count() > 0:
            print("Database already seeded. Skipping.")
            return

        # Insert assets
        for a in SAMPLE_ASSETS:
            db.add(models.Asset(**a))
        db.commit()
        print(f"  ✔ Inserted {len(SAMPLE_ASSETS)} assets.")

        # Insert complaints
        for c in SAMPLE_COMPLAINTS:
            db.add(models.Complaint(**c))
        db.commit()
        print(f"  ✔ Inserted {len(SAMPLE_COMPLAINTS)} complaints.")

        # Insert repair records
        for r in SAMPLE_REPAIRS:
            db.add(models.RepairRecord(**r))
        db.commit()
        print(f"  ✔ Inserted {len(SAMPLE_REPAIRS)} repair records.")

        print("\nSeed complete. Run the API with: uvicorn main:app --reload --port 8000")

    except Exception as e:
        db.rollback()
        print(f"Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Seeding CivicPulse AI database with sample data...")
    seed()
