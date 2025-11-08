"""
Create emissions_data.db with 7 tables from CSV files
Each CSV file becomes a separate table
"""
import sqlite3
import pandas as pd
from pathlib import Path

# Database configuration
DB_NAME = "emissions_data.db"
DATASET_FOLDER = "dataset"

# CSV files and their corresponding table names
CSV_FILES = {
    "company_energy_consumption_daily.csv": "energy_consumption",
    "company_energy_mix_monthly.csv": "energy_mix",
    "company_production_emissions_daily.csv": "production_emissions",
    "company_travel_emissions_daily.csv": "travel_emissions",
    "company_waste_monthly.csv": "waste",
    "company_water_usage_daily.csv": "water_usage",
    "factory_air_quality_daily.csv": "air_quality"
}

def create_emissions_database():
    """Create emissions database from CSV files"""
    
    print(f"🗄️  Creating {DB_NAME} with 7 tables...")
    print("="*80)
    
    # Create database connection
    conn = sqlite3.connect(DB_NAME)
    
    # Load each CSV file into a table
    for csv_file, table_name in CSV_FILES.items():
        csv_path = Path(DATASET_FOLDER) / csv_file
        
        if not csv_path.exists():
            print(f"⚠️  Warning: {csv_file} not found, skipping...")
            continue
        
        print(f"\n📊 Loading {csv_file} → {table_name}")
        
        # Read CSV file
        df = pd.read_csv(csv_path)
        
        print(f"   Rows: {len(df):,}")
        print(f"   Columns: {', '.join(df.columns.tolist())}")
        
        # Write to SQLite table
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        
        print(f"   ✅ Table '{table_name}' created successfully")
    
    # Verify all tables
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    print("\n" + "="*80)
    print(f"✅ Database created successfully!")
    print(f"Total tables: {len(tables)}")
    print("\nTables in database:")
    
    for table_name, in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        print(f"  - {table_name}: {row_count:,} rows")
    
    conn.close()
    print("\n" + "="*80)

if __name__ == "__main__":
    create_emissions_database()
