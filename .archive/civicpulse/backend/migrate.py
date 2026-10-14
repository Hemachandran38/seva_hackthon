"""
migrate.py — Apply Phase 4 column additions to the existing SQLite database.
Run once: python migrate.py
"""
import sqlite3

conn = sqlite3.connect("civicpulse.db")
cur  = conn.cursor()

migrations = [
    "ALTER TABLE complaints ADD COLUMN lifecycle_status TEXT DEFAULT 'reported'",
    "ALTER TABLE complaints ADD COLUMN assigned_team TEXT",
    "ALTER TABLE complaints ADD COLUMN assigned_at DATETIME",
    "ALTER TABLE complaints ADD COLUMN assigned_by TEXT",
    "ALTER TABLE complaints ADD COLUMN assignment_notes TEXT",
    "ALTER TABLE complaints ADD COLUMN verified_by TEXT",
    "ALTER TABLE complaints ADD COLUMN verified_at DATETIME",
    "ALTER TABLE complaints ADD COLUMN verification_result TEXT",
    "ALTER TABLE complaints ADD COLUMN verification_notes TEXT",
    "ALTER TABLE complaints ADD COLUMN reopened_count INTEGER DEFAULT 0",
    "ALTER TABLE repair_records ADD COLUMN submitted_for_verification INTEGER DEFAULT 0",
]

for sql in migrations:
    try:
        cur.execute(sql)
        print(f"  OK  : {sql[:60]}")
    except sqlite3.OperationalError as e:
        print(f"  SKIP: {e}")

# Backfill lifecycle_status from existing status values
cur.execute("UPDATE complaints SET lifecycle_status = 'resolved'   WHERE status = 'resolved'")
cur.execute("UPDATE complaints SET lifecycle_status = 'in_progress' WHERE status = 'in-progress'")
cur.execute("UPDATE complaints SET lifecycle_status = 'reported'    WHERE status = 'open'")
print("  OK  : lifecycle_status backfilled")

conn.commit()
conn.close()
print("\nMigration complete.")
