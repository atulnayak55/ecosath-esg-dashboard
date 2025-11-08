"""
Verify all three SQLite databases exist and have proper structure
"""
import sqlite3
from pathlib import Path

def verify_database(db_name):
    """Verify database structure"""
    db_path = Path(db_name)
    
    print(f"\n{'='*80}")
    print(f"DATABASE: {db_name}")
    print(f"{'='*80}")
    
    if not db_path.exists():
        print(f"❌ {db_name} does NOT exist!")
        return False
    
    print(f"✅ File exists: {db_path.stat().st_size:,} bytes")
    
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        if not tables:
            print(f"⚠️  No tables found in {db_name}")
            conn.close()
            return False
        
        print(f"\nTables ({len(tables)}):")
        
        for table_name, in tables:
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            
            # Get column info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            print(f"\n  📊 {table_name}")
            print(f"     Rows: {row_count:,}")
            print(f"     Columns ({len(column_names)}): {', '.join(column_names)}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error reading {db_name}: {e}")
        return False

if __name__ == "__main__":
    print("\n🔍 VERIFYING ALL DATABASES")
    print("="*80)
    
    databases = [
        "emissions_data.db",
        "social_metrics.db",
        "governance_metrics.db"
    ]
    
    results = {}
    
    for db in databases:
        results[db] = verify_database(db)
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    for db, success in results.items():
        status = "✅ VERIFIED" if success else "❌ MISSING/INVALID"
        print(f"{status}: {db}")
    
    all_good = all(results.values())
    
    if all_good:
        print("\n✅ All three databases are present and have data!")
    else:
        print("\n⚠️  Some databases are missing or empty!")
