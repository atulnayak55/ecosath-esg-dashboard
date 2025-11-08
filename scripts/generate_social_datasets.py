"""
Social Impact Data Generator
Generates realistic social metrics for a year-old renewable energy company
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

# Output directory
OUTPUT_DIR = Path("social_dataset")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Company started on Nov 9, 2024 (1 year old)
START_DATE = datetime(2024, 11, 9)
END_DATE = datetime(2025, 11, 8)

def generate_employee_wellbeing():
    """
    Generate monthly employee wellbeing metrics
    Metrics: satisfaction score (1-10), training hours per employee
    """
    print("📊 Generating Employee Wellbeing data...")
    
    dates = []
    current_date = START_DATE
    
    # Generate monthly data for 12 months
    while current_date <= END_DATE:
        dates.append(current_date.strftime("%Y-%m"))
        current_date += timedelta(days=30)
    
    data = []
    base_satisfaction = 7.8
    base_training = 12
    
    for i, month in enumerate(dates):
        # Gradual improvement over time with some variance
        satisfaction_trend = 0.05 * i  # Improves over time
        satisfaction = base_satisfaction + satisfaction_trend + np.random.uniform(-0.3, 0.3)
        satisfaction = min(10, max(6, satisfaction))  # Keep between 6-10
        
        # Training hours vary by quarter (more training in Q1, Q3)
        quarter_boost = 5 if i % 3 == 0 else 0
        training_hours = base_training + quarter_boost + np.random.uniform(-3, 5)
        training_hours = max(5, training_hours)
        
        # Employee count grows over time
        employee_count = 450 + i * 5 + np.random.randint(-5, 10)
        
        data.append({
            "month": month,
            "satisfaction_score": round(satisfaction, 2),
            "training_hours_per_employee": round(training_hours, 1),
            "total_employees": employee_count,
            "response_rate_percent": round(np.random.uniform(78, 95), 1)
        })
    
    df = pd.DataFrame(data)
    output_file = OUTPUT_DIR / "employee_wellbeing_monthly.csv"
    df.to_csv(output_file, index=False)
    print(f"  ✅ Saved {len(df)} rows to {output_file}")
    return df

def generate_diversity_inclusion():
    """
    Generate quarterly diversity & inclusion metrics
    Metrics: % female employees, age diversity distribution
    """
    print("📊 Generating Diversity & Inclusion data...")
    
    # Generate quarterly data (4 quarters)
    quarters = [
        "2024-Q4",
        "2025-Q1", 
        "2025-Q2",
        "2025-Q3",
        "2025-Q4"
    ]
    
    data = []
    base_female_percent = 42
    
    for i, quarter in enumerate(quarters):
        # Gradual improvement in diversity
        female_percent = base_female_percent + i * 1.2 + np.random.uniform(-1, 2)
        female_percent = min(52, max(40, female_percent))
        
        # Age distribution (should sum to 100%)
        age_under_30 = np.random.uniform(25, 32)
        age_30_40 = np.random.uniform(35, 42)
        age_40_50 = np.random.uniform(18, 25)
        age_over_50 = 100 - (age_under_30 + age_30_40 + age_40_50)
        
        # Leadership diversity
        female_leadership = female_percent * 0.85 + np.random.uniform(-2, 3)
        female_leadership = min(50, max(35, female_leadership))
        
        minority_employees = np.random.uniform(30, 40)
        
        data.append({
            "quarter": quarter,
            "female_employees_percent": round(female_percent, 1),
            "female_leadership_percent": round(female_leadership, 1),
            "minority_employees_percent": round(minority_employees, 1),
            "age_under_30_percent": round(age_under_30, 1),
            "age_30_40_percent": round(age_30_40, 1),
            "age_40_50_percent": round(age_40_50, 1),
            "age_over_50_percent": round(age_over_50, 1),
            "pay_equity_ratio": round(np.random.uniform(0.94, 0.99), 3)
        })
    
    df = pd.DataFrame(data)
    output_file = OUTPUT_DIR / "diversity_inclusion_quarterly.csv"
    df.to_csv(output_file, index=False)
    print(f"  ✅ Saved {len(df)} rows to {output_file}")
    return df

def generate_community_impact():
    """
    Generate quarterly community impact metrics
    Metrics: volunteer hours, donations (USD)
    """
    print("📊 Generating Community Impact data...")
    
    quarters = [
        "2024-Q4",
        "2025-Q1",
        "2025-Q2",
        "2025-Q3",
        "2025-Q4"
    ]
    
    data = []
    
    for i, quarter in enumerate(quarters):
        # Growing community engagement over time
        base_volunteer = 800
        volunteer_hours = base_volunteer + i * 150 + np.random.uniform(-100, 200)
        volunteer_hours = max(600, volunteer_hours)
        
        # Donations increase over time as company grows
        base_donation = 75000
        total_donations = base_donation + i * 15000 + np.random.uniform(-10000, 20000)
        total_donations = max(50000, total_donations)
        
        # Break down donation categories
        education = total_donations * np.random.uniform(0.35, 0.45)
        environment = total_donations * np.random.uniform(0.30, 0.40)
        local_business = total_donations - education - environment
        
        # Number of employees participating in volunteering
        employee_participation = np.random.uniform(55, 75)
        
        # Community programs supported
        programs_supported = np.random.randint(8, 15)
        
        # Beneficiaries reached
        beneficiaries = int(volunteer_hours * np.random.uniform(2, 4))
        
        data.append({
            "quarter": quarter,
            "volunteer_hours": round(volunteer_hours, 0),
            "employee_participation_percent": round(employee_participation, 1),
            "total_donations_usd": round(total_donations, 2),
            "education_donations_usd": round(education, 2),
            "environmental_donations_usd": round(environment, 2),
            "local_business_support_usd": round(local_business, 2),
            "programs_supported": programs_supported,
            "beneficiaries_reached": beneficiaries
        })
    
    df = pd.DataFrame(data)
    output_file = OUTPUT_DIR / "community_impact_quarterly.csv"
    df.to_csv(output_file, index=False)
    print(f"  ✅ Saved {len(df)} rows to {output_file}")
    return df

def generate_health_safety():
    """
    Generate monthly health & safety metrics
    Metrics: incidents per 1,000 hours worked, safety training completion
    """
    print("📊 Generating Health & Safety data...")
    
    dates = []
    current_date = START_DATE
    
    # Generate monthly data for 12 months
    while current_date <= END_DATE:
        dates.append(current_date.strftime("%Y-%m"))
        current_date += timedelta(days=30)
    
    data = []
    
    for i, month in enumerate(dates):
        # Total hours worked increases as company grows
        employees = 450 + i * 5
        hours_per_employee = 160  # ~40 hours/week * 4 weeks
        total_hours_worked = employees * hours_per_employee
        
        # Incident rate improves over time (better safety culture)
        base_incident_rate = 2.5  # incidents per 1000 hours
        improvement = i * 0.15
        incident_rate = max(0.5, base_incident_rate - improvement + np.random.uniform(-0.3, 0.5))
        
        # Calculate actual incidents
        total_incidents = int((incident_rate * total_hours_worked) / 1000)
        total_incidents = max(0, total_incidents)
        
        # Lost time incidents (more serious)
        lost_time_incidents = max(0, int(total_incidents * np.random.uniform(0.1, 0.3)))
        
        # Near misses (higher as safety culture improves - more reporting)
        near_misses = int(total_incidents * np.random.uniform(3, 8))
        
        # Safety training completion improves over time
        training_completion = min(100, 85 + i * 1.2 + np.random.uniform(-2, 3))
        
        # Days without incident (varies)
        days_without_incident = np.random.randint(20, 90)
        
        # First aid cases
        first_aid_cases = int(total_incidents * np.random.uniform(1.5, 3))
        
        data.append({
            "month": month,
            "total_hours_worked": total_hours_worked,
            "total_incidents": total_incidents,
            "incident_rate_per_1000_hours": round(incident_rate, 2),
            "lost_time_incidents": lost_time_incidents,
            "near_misses_reported": near_misses,
            "first_aid_cases": first_aid_cases,
            "safety_training_completion_percent": round(training_completion, 1),
            "days_without_major_incident": days_without_incident
        })
    
    df = pd.DataFrame(data)
    output_file = OUTPUT_DIR / "health_safety_monthly.csv"
    df.to_csv(output_file, index=False)
    print(f"  ✅ Saved {len(df)} rows to {output_file}")
    return df

def generate_summary_report():
    """Generate a summary report of all social metrics"""
    print("\n📋 Generating Summary Report...")
    
    summary = {
        "report_date": END_DATE.strftime("%Y-%m-%d"),
        "company_age_months": 12,
        "metrics_generated": 4,
        "files_created": [
            "employee_wellbeing_monthly.csv (13 rows)",
            "diversity_inclusion_quarterly.csv (5 rows)",
            "community_impact_quarterly.csv (5 rows)",
            "health_safety_monthly.csv (13 rows)"
        ]
    }
    
    output_file = OUTPUT_DIR / "summary_report.txt"
    with open(output_file, 'w') as f:
        f.write("=" * 60 + "\n")
        f.write("AURORA RENEWABLES - SOCIAL IMPACT METRICS\n")
        f.write("Year 1 Dataset Summary\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Report Generated: {summary['report_date']}\n")
        f.write(f"Company Age: {summary['company_age_months']} months\n")
        f.write(f"Metrics Categories: {summary['metrics_generated']}\n\n")
        f.write("Files Created:\n")
        for file in summary['files_created']:
            f.write(f"  - {file}\n")
        f.write("\n" + "=" * 60 + "\n")
    
    print(f"  ✅ Summary saved to {output_file}")

def main():
    """Generate all social metrics"""
    print("🤝 Social Impact Data Generator - Aurora Renewables")
    print("=" * 60)
    print(f"📅 Period: {START_DATE.strftime('%Y-%m-%d')} to {END_DATE.strftime('%Y-%m-%d')}")
    print(f"📁 Output Directory: {OUTPUT_DIR.absolute()}")
    print("=" * 60 + "\n")
    
    # Generate all datasets
    df_wellbeing = generate_employee_wellbeing()
    df_diversity = generate_diversity_inclusion()
    df_community = generate_community_impact()
    df_safety = generate_health_safety()
    
    # Generate summary
    generate_summary_report()
    
    print("\n" + "=" * 60)
    print("✅ All social metrics generated successfully!")
    print(f"📂 Check the '{OUTPUT_DIR}' folder for all CSV files")
    print("=" * 60)

if __name__ == "__main__":
    main()
