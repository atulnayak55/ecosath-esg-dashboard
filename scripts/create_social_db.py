"""
Convert Social CSV datasets to SQLite database
"""
import pandas as pd
import sqlite3
from pathlib import Path

# Paths
CSV_DIR = Path("social_dataset")
DB_PATH = Path("social_metrics.db")

def create_database():
    """Create SQLite database from CSV files"""
    print("📦 Creating SQLite database for social metrics...")
    print(f"📁 Source: {CSV_DIR.absolute()}")
    print(f"💾 Database: {DB_PATH.absolute()}")
    print("=" * 60)
    
    # Remove old database if exists
    if DB_PATH.exists():
        DB_PATH.unlink()
        print("🗑️  Removed old database")
    
    # Create connection
    conn = sqlite3.connect(DB_PATH)
    
    # Load and store each CSV
    csv_files = {
        "employee_wellbeing": "employee_wellbeing_monthly.csv",
        "diversity_inclusion": "diversity_inclusion_quarterly.csv",
        "community_impact": "community_impact_quarterly.csv",
        "health_safety": "health_safety_monthly.csv"
    }
    
    for table_name, csv_file in csv_files.items():
        csv_path = CSV_DIR / csv_file
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            print(f"✅ {table_name}: {len(df)} rows loaded")
        else:
            print(f"⚠️  {csv_file} not found")
    
    conn.close()
    
    print("=" * 60)
    print(f"✅ Database created successfully!")
    print(f"💾 File size: {DB_PATH.stat().st_size / 1024:.2f} KB")
    
    # Verify database
    verify_database()

def verify_database():
    """Verify database contents"""
    print("\n🔍 Verifying database contents...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print(f"📊 Tables found: {len(tables)}")
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"   - {table_name}: {count} rows")
    
    conn.close()

if __name__ == "__main__":
    create_database()
