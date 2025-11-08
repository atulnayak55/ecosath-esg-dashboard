"""
Real-time Governance Data Generator
Generates governance and compliance metrics continuously
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import os
from pathlib import Path
import json

# Output directory
OUTPUT_DIR = Path("dataset_realtime/governance")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def generate_board_diversity():
    """Generate quarterly board diversity metrics"""
    today = datetime.now()
    quarter = f"{today.year}-Q{(today.month-1)//3 + 1}"
    
    data = {
        "quarter": [quarter],
        "total_board_members": [np.random.randint(7, 12)],
        "independent_directors_count": [np.random.randint(4, 8)],
        "female_directors_count": [np.random.randint(3, 6)],
        "minority_directors_count": [np.random.randint(2, 5)],
        "average_tenure_years": [np.random.uniform(3.5, 6.5)],
        "board_meetings_held": [np.random.randint(4, 8)]
    }
    
    df = pd.DataFrame(data)
    output_file = OUTPUT_DIR / "board_diversity_quarterly.csv"
    
    if output_file.exists():
        existing = pd.read_csv(output_file)
        if quarter in existing['quarter'].values:
            existing = existing[existing['quarter'] != quarter]
        df = pd.concat([existing, df], ignore_index=True)
        df = df.tail(8)
    
    df.to_csv(output_file, index=False)
    return len(df)

def generate_ethics_compliance():
    """Generate monthly ethics and compliance metrics"""
    today = datetime.now()
    month = today.strftime("%Y-%m")
    
    data = {
        "month": [month],
        "ethics_training_completion_percent": [np.random.uniform(95, 100)],
        "policy_violations_reported": [np.random.randint(0, 3)],
        "whistleblower_reports": [np.random.randint(0, 2)],
        "compliance_audits_completed": [np.random.randint(2, 6)],
        "corrective_actions_taken": [np.random.randint(0, 4)],
        "supplier_audits_completed": [np.random.randint(3, 10)]
    }
    
    df = pd.DataFrame(data)
    output_file = OUTPUT_DIR / "ethics_compliance_monthly.csv"
    
    if output_file.exists():
        existing = pd.read_csv(output_file)
        if month in existing['month'].values:
            existing = existing[existing['month'] != month]
        df = pd.concat([existing, df], ignore_index=True)
        df = df.tail(12)
    
    df.to_csv(output_file, index=False)
    return len(df)

def generate_risk_management():
    """Generate quarterly risk assessment metrics"""
    today = datetime.now()
    quarter = f"{today.year}-Q{(today.month-1)//3 + 1}"
    
    data = {
        "quarter": [quarter],
        "total_risks_identified": [np.random.randint(15, 30)],
        "high_priority_risks": [np.random.randint(2, 6)],
        "medium_priority_risks": [np.random.randint(5, 12)],
        "risks_mitigated": [np.random.randint(8, 15)],
        "risk_assessment_score": [np.random.uniform(7.0, 9.0)],
        "cybersecurity_incidents": [np.random.randint(0, 3)]
    }
    
    df = pd.DataFrame(data)
    output_file = OUTPUT_DIR / "risk_management_quarterly.csv"
    
    if output_file.exists():
        existing = pd.read_csv(output_file)
        if quarter in existing['quarter'].values:
            existing = existing[existing['quarter'] != quarter]
        df = pd.concat([existing, df], ignore_index=True)
        df = df.tail(8)
    
    df.to_csv(output_file, index=False)
    return len(df)

def generate_shareholder_engagement():
    """Generate quarterly shareholder engagement metrics"""
    today = datetime.now()
    quarter = f"{today.year}-Q{(today.month-1)//3 + 1}"
    
    data = {
        "quarter": [quarter],
        "shareholder_meetings_held": [np.random.randint(1, 3)],
        "shareholder_resolutions": [np.random.randint(0, 5)],
        "voting_participation_percent": [np.random.uniform(75, 92)],
        "investor_inquiries_received": [np.random.randint(50, 150)],
        "esg_rating_score": [np.random.uniform(75, 90)],
        "transparency_index_score": [np.random.uniform(80, 95)]
    }
    
    df = pd.DataFrame(data)
    output_file = OUTPUT_DIR / "shareholder_engagement_quarterly.csv"
    
    if output_file.exists():
        existing = pd.read_csv(output_file)
        if quarter in existing['quarter'].values:
            existing = existing[existing['quarter'] != quarter]
        df = pd.concat([existing, df], ignore_index=True)
        df = df.tail(8)
    
    df.to_csv(output_file, index=False)
    return len(df)

def generate_data_privacy():
    """Generate monthly data privacy and security metrics"""
    today = datetime.now()
    month = today.strftime("%Y-%m")
    
    data = {
        "month": [month],
        "data_breach_incidents": [np.random.randint(0, 1)],
        "privacy_training_completion_percent": [np.random.uniform(95, 100)],
        "data_subject_requests": [np.random.randint(5, 20)],
        "requests_resolved_within_sla": [np.random.randint(5, 20)],
        "gdpr_compliance_score": [np.random.uniform(90, 100)],
        "security_patches_applied": [np.random.randint(20, 50)]
    }
    
    df = pd.DataFrame(data)
    output_file = OUTPUT_DIR / "data_privacy_monthly.csv"
    
    if output_file.exists():
        existing = pd.read_csv(output_file)
        if month in existing['month'].values:
            existing = existing[existing['month'] != month]
        df = pd.concat([existing, df], ignore_index=True)
        df = df.tail(12)
    
    df.to_csv(output_file, index=False)
    return len(df)

def generate_all_governance():
    """Generate all governance metrics"""
    metrics = {
        "board_diversity": generate_board_diversity(),
        "ethics_compliance": generate_ethics_compliance(),
        "risk_management": generate_risk_management(),
        "shareholder_engagement": generate_shareholder_engagement(),
        "data_privacy": generate_data_privacy()
    }
    
    timestamp = datetime.now().isoformat()
    print(f"[{timestamp}] Generated governance metrics: {json.dumps(metrics, indent=2)}")
    
    return metrics

def main():
    """Main loop - generate data every 60 seconds"""
    print("🏛️ Governance Real-time Generator Started")
    print(f"📁 Output directory: {OUTPUT_DIR.absolute()}")
    print("⏱️  Refresh interval: 60 seconds")
    print("-" * 60)
    
    iteration = 0
    while True:
        iteration += 1
        print(f"\n🔄 Iteration #{iteration}")
        
        try:
            metrics = generate_all_governance()
            print(f"✅ Successfully generated {sum(metrics.values())} total rows across 5 metrics")
        except Exception as e:
            print(f"❌ Error generating data: {e}")
        
        print(f"⏳ Sleeping for 60 seconds...")
        time.sleep(60)

if __name__ == "__main__":
    main()
