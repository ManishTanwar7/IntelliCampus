"""
IntelliCampus: Live Database Migration Script
Usage:
    python scripts/migrate_live_db.py [DATABASE_URL]
Example:
    python scripts/migrate_live_db.py "mysql://avnadmin:pwd@mysql-28a.aivencloud.com:12345/defaultdb?ssl-mode=REQUIRED"
"""
import sys
import os
import urllib.parse
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from services.database import DatabaseManager

def run_migration(db_url: str = None):
    if db_url:
        os.environ["DATABASE_URL"] = db_url

    print("====================================================")
    print("   IntelliCampus: Live Database Migration Tool     ")
    print("====================================================")
    
    db = DatabaseManager()
    print("[Migration] Connecting to target database...")
    db.init_database()
    
    # Run seed script for 25BCS11666
    from database.seed_student_25bcs11666 import seed_25bcs11666
    seed_25bcs11666()
    
    print("[Migration] SUCCESS! All tables, constraints, indexes, and student 25BCS11666 data migrated successfully.")

if __name__ == "__main__":
    target_url = sys.argv[1] if len(sys.argv) > 1 else None
    run_migration(target_url)
