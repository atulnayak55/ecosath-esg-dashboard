"""
Create SQLite database from governance CSV files
Converts all governance datasets into a single governance_metrics.db
"""

import sqlite3
import pandas as pd
import os

# Input directory
INPUT_DIR = 'governance_dataset'
OUTPUT_DB = 'governance_metrics.db'

def create_database():
    """
    Create SQLite database from governance CSV files
    """
    
    # Remove existing database if it exists
    if os.path.exists(OUTPUT_DB):
        os.remove(OUTPUT_DB)
        print(f"🗑️  Removed existing {OUTPUT_DB}")
    
    # Connect to SQLite database (creates if doesn't exist)
    conn = sqlite3.connect(OUTPUT_DB)
    print(f"✅ Created new database: {OUTPUT_DB}")
    
    # CSV files to import
    csv_files = {
        'board_composition': 'board_composition_quarterly.csv',
        'compliance_metrics': 'compliance_metrics_quarterly.csv',
        'esg_ratings': 'esg_ratings_quarterly.csv',
        'transparency_disclosure': 'transparency_disclosure_quarterly.csv'
    }
    
    tables_created = []
    
    for table_name, csv_file in csv_files.items():
        csv_path = os.path.join(INPUT_DIR, csv_file)
        
        if not os.path.exists(csv_path):
            print(f"⚠️  Warning: {csv_path} not found, skipping...")
            continue
        
        # Read CSV
        df = pd.read_csv(csv_path)
        
        # Write to SQLite
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        
        print(f"✅ Imported: {csv_file} → {table_name} table ({len(df)} rows)")
        tables_created.append((table_name, len(df)))
    
    # Close connection
    conn.close()
    
    return tables_created

def verify_database(tables_created):
    """
    Verify the database was created correctly
    """
    
    print("\n" + "="*60)
    print("DATABASE VERIFICATION")
    print("="*60)
    
    # Get database size
    db_size = os.path.getsize(OUTPUT_DB) / 1024  # KB
    print(f"Database size: {db_size:.2f} KB")
    
    # Connect and verify tables
    conn = sqlite3.connect(OUTPUT_DB)
    cursor = conn.cursor()
    
    print(f"\nTables created: {len(tables_created)}")
    
    for table_name, expected_rows in tables_created:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        actual_rows = cursor.fetchone()[0]
        
        status = "✅" if actual_rows == expected_rows else "❌"
        print(f"  {status} {table_name}: {actual_rows} rows")
        
        # Show sample data
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
        sample = cursor.fetchone()
        if sample:
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            print(f"     Columns: {', '.join(columns[:5])}{'...' if len(columns) > 5 else ''}")
    
    conn.close()
    
    print("\n" + "="*60)
    print("✅ DATABASE CREATED SUCCESSFULLY!")
    print("="*60)
    print(f"Location: {os.path.abspath(OUTPUT_DB)}")
    print(f"Size: {db_size:.2f} KB")
    print(f"Tables: {len(tables_created)}")
    print(f"Total rows: {sum([rows for _, rows in tables_created])}")

def main():
    print("="*60)
    print("GOVERNANCE DATABASE CREATOR")
    print("Converting CSV files to SQLite database")
    print("="*60)
    print()
    
    # Create database
    tables_created = create_database()
    
    # Verify database
    verify_database(tables_created)

if __name__ == "__main__":
    main()
