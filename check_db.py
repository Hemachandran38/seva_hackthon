import sqlite3
import os

os.chdir('c:\\seva_hackthon\\backend')
conn = sqlite3.connect('civicpulse.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"Tables: {[t[0] for t in tables]}")

# Try to get complaints
try:
    cursor.execute('SELECT id, title, latitude, longitude, status, priority FROM complaint LIMIT 5')
    rows = cursor.fetchall()
    print(f"\nComplaints found: {len(rows)}")
    for r in rows:
        print(f"  {r[0]}: {r[1][:30]}... lat={r[2]}, lng={r[3]}, status={r[4]}, priority={r[5]}")
except Exception as e:
    print(f"Error with 'complaint' table: {e}")
    
    # Try alternative table names
    for table in [t[0] for t in tables]:
        print(f"\nTrying table: {table}")
        try:
            cursor.execute(f'SELECT * FROM {table} LIMIT 1')
            row = cursor.fetchone()
            if row:
                print(f"  Columns: {[desc[0] for desc in cursor.description]}")
                print(f"  Sample row: {row}")
        except Exception as e2:
            print(f"  Error: {e2}")
