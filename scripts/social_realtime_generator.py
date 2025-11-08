"""
Real-time Social Impact Data Generator
Generates social and community metrics continuously
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import os
from pathlib import Path
import json

# Output directory
OUTPUT_DIR = Path("dataset_realtime/social")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def generate_employee_satisfaction():
    """Generate monthly employee satisfaction scores"""
    today = datetime.now()
    month = today.strftime("%Y-%m")
    
    data = {
        "month": [month],
        "overall_satisfaction_score": [np.random.uniform(7.5, 9.0)],
        "work_life_balance_score": [np.random.uniform(7.0, 8.5)],
        "career_growth_score": [np.random.uniform(7.2, 8.8)],
        "management_score": [np.random.uniform(7.5, 8.9)],
        "response_rate_percent": [np.random.uniform(75, 95)]
    }
    
    df = pd.DataFrame(data)
    output_file = OUTPUT_DIR / "employee_satisfaction_monthly.csv"
    
    if output_file.exists():
        existing = pd.read_csv(output_file)
        if month in existing['month'].values:
            existing = existing[existing['month'] != month]
        df = pd.concat([existing, df], ignore_index=True)
        df = df.tail(12)
    
    df.to_csv(output_file, index=False)
    return len(df)

def generate_diversity_metrics():
    """Generate quarterly diversity and inclusion metrics"""
    today = datetime.now()
    quarter = f"{today.year}-Q{(today.month-1)//3 + 1}"
    
    data = {
        "quarter": [quarter],
        "female_employees_percent": [np.random.uniform(42, 52)],
        "minority_employees_percent": [np.random.uniform(35, 45)],
        "women_leadership_percent": [np.random.uniform(38, 48)],
        "pay_equity_ratio": [np.random.uniform(0.95, 1.00)],
        "total_employees": [np.random.randint(450, 550)]
    }
    
    df = pd.DataFrame(data)
    output_file = OUTPUT_DIR / "diversity_metrics_quarterly.csv"
    
    if output_file.exists():
        existing = pd.read_csv(output_file)
        if quarter in existing['quarter'].values:
            existing = existing[existing['quarter'] != quarter]
        df = pd.concat([existing, df], ignore_index=True)
        df = df.tail(8)  # Keep last 2 years
    
    df.to_csv(output_file, index=False)
    return len(df)

def generate_training_hours():
    """Generate monthly training and development hours"""
    today = datetime.now()
    month = today.strftime("%Y-%m")
    
    data = {
        "month": [month],
        "total_training_hours": [np.random.uniform(800, 1500)],
        "hours_per_employee": [np.random.uniform(1.5, 3.0)],
        "technical_training_hours": [np.random.uniform(400, 800)],
        "leadership_training_hours": [np.random.uniform(200, 400)],
        "safety_training_hours": [np.random.uniform(200, 300)],
        "employees_trained": [np.random.randint(400, 500)]
    }
    
    df = pd.DataFrame(data)
    output_file = OUTPUT_DIR / "training_hours_monthly.csv"
    
    if output_file.exists():
        existing = pd.read_csv(output_file)
        if month in existing['month'].values:
            existing = existing[existing['month'] != month]
        df = pd.concat([existing, df], ignore_index=True)
        df = df.tail(12)
    
    df.to_csv(output_file, index=False)
    return len(df)

def generate_community_investment():
    """Generate quarterly community investment"""
    today = datetime.now()
    quarter = f"{today.year}-Q{(today.month-1)//3 + 1}"
    
    data = {
        "quarter": [quarter],
        "total_investment_usd": [np.random.uniform(50000, 150000)],
        "education_programs_usd": [np.random.uniform(20000, 60000)],
        "environmental_initiatives_usd": [np.random.uniform(15000, 50000)],
        "local_business_support_usd": [np.random.uniform(10000, 40000)],
        "volunteer_hours": [np.random.uniform(500, 1200)],
        "beneficiaries_count": [np.random.randint(1000, 3000)]
    }
    
    df = pd.DataFrame(data)
    output_file = OUTPUT_DIR / "community_investment_quarterly.csv"
    
    if output_file.exists():
        existing = pd.read_csv(output_file)
        if quarter in existing['quarter'].values:
            existing = existing[existing['quarter'] != quarter]
        df = pd.concat([existing, df], ignore_index=True)
        df = df.tail(8)
    
    df.to_csv(output_file, index=False)
    return len(df)

def generate_safety_incidents():
    """Generate monthly workplace safety incidents"""
    today = datetime.now()
    month = today.strftime("%Y-%m")
    
    data = {
        "month": [month],
        "total_incidents": [np.random.randint(0, 5)],
        "lost_time_incidents": [np.random.randint(0, 2)],
        "near_misses_reported": [np.random.randint(5, 20)],
        "safety_training_completion_percent": [np.random.uniform(92, 100)],
        "days_without_incident": [np.random.randint(15, 90)]
    }
    
    df = pd.DataFrame(data)
    output_file = OUTPUT_DIR / "safety_incidents_monthly.csv"
    
    if output_file.exists():
        existing = pd.read_csv(output_file)
        if month in existing['month'].values:
            existing = existing[existing['month'] != month]
        df = pd.concat([existing, df], ignore_index=True)
        df = df.tail(12)
    
    df.to_csv(output_file, index=False)
    return len(df)

def generate_all_social():
    """Generate all social metrics"""
    metrics = {
        "employee_satisfaction": generate_employee_satisfaction(),
        "diversity_metrics": generate_diversity_metrics(),
        "training_hours": generate_training_hours(),
        "community_investment": generate_community_investment(),
        "safety_incidents": generate_safety_incidents()
    }
    
    timestamp = datetime.now().isoformat()
    print(f"[{timestamp}] Generated social metrics: {json.dumps(metrics, indent=2)}")
    
    return metrics

def main():
    """Main loop - generate data every 60 seconds"""
    print("🤝 Social Impact Real-time Generator Started")
    print(f"📁 Output directory: {OUTPUT_DIR.absolute()}")
    print("⏱️  Refresh interval: 60 seconds")
    print("-" * 60)
    
    iteration = 0
    while True:
        iteration += 1
        print(f"\n🔄 Iteration #{iteration}")
        
        try:
            metrics = generate_all_social()
            print(f"✅ Successfully generated {sum(metrics.values())} total rows across 5 metrics")
        except Exception as e:
            print(f"❌ Error generating data: {e}")
        
        print(f"⏳ Sleeping for 60 seconds...")
        time.sleep(60)

if __name__ == "__main__":
    main()
