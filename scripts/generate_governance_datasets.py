"""
Generate Governance datasets for Aurora Renewables ESG Dashboard
Creates static and quarterly governance metrics including:
1. Board Composition (static with quarterly updates)
2. Compliance Metrics (quarterly)
3. ESG Ratings (quarterly)
4. Transparency & Disclosure (quarterly)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Create output directory
OUTPUT_DIR = 'governance_dataset'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_board_composition():
    """
    Generate board composition data - quarterly snapshots for 1 year
    Tracks board diversity and independence
    """
    
    # Starting from 1 year ago
    start_date = datetime.now() - timedelta(days=365)
    
    # Generate quarterly data (5 quarters to show full year)
    quarters = []
    for i in range(5):
        quarter_date = start_date + timedelta(days=90*i)
        quarter_label = f"Q{((quarter_date.month-1)//3)+1} {quarter_date.year}"
        
        # Progressive improvement in diversity
        data = {
            'quarter': quarter_label,
            'total_directors': 7,
            'independent_directors': 4 + (i // 2),  # Gradually increasing
            'female_directors': 2 + (i // 3),  # Gradually increasing
            'independent_percent': round((4 + (i // 2)) / 7 * 100, 1),
            'female_percent': round((2 + (i // 3)) / 7 * 100, 1),
            'average_tenure_years': round(3.5 + (i * 0.2), 1),
            'board_meetings_held': 4,
            'average_attendance_percent': round(92 + np.random.uniform(-2, 5), 1)
        }
        quarters.append(data)
    
    df = pd.DataFrame(quarters)
    
    # Save to CSV
    output_path = os.path.join(OUTPUT_DIR, 'board_composition_quarterly.csv')
    df.to_csv(output_path, index=False)
    print(f"✅ Generated: {output_path}")
    print(f"   - {len(df)} quarters of board composition data")
    print(f"   - Independent directors: {df['independent_percent'].iloc[-1]}%")
    print(f"   - Female directors: {df['female_percent'].iloc[-1]}%\n")
    
    return df

def generate_compliance_metrics():
    """
    Generate compliance and audit metrics - quarterly for 1 year
    Tracks ESG audit performance and regulatory compliance
    """
    
    start_date = datetime.now() - timedelta(days=365)
    
    quarters = []
    for i in range(5):
        quarter_date = start_date + timedelta(days=90*i)
        quarter_label = f"Q{((quarter_date.month-1)//3)+1} {quarter_date.year}"
        
        # Progressive improvement in compliance
        data = {
            'quarter': quarter_label,
            'esg_audits_conducted': np.random.randint(2, 4),
            'audits_passed': 2 + (i // 2),  # Improving over time
            'compliance_rate_percent': round(75 + (i * 4) + np.random.uniform(-2, 2), 1),
            'regulatory_violations': max(0, 3 - i),  # Decreasing over time
            'corrective_actions_completed': np.random.randint(4, 8),
            'policy_updates': np.random.randint(2, 5),
            'employee_ethics_training_percent': round(85 + (i * 2) + np.random.uniform(-1, 2), 1),
            'whistleblower_reports': np.random.randint(0, 2)
        }
        
        # Ensure compliance rate doesn't exceed 100%
        data['compliance_rate_percent'] = min(98.5, data['compliance_rate_percent'])
        
        quarters.append(data)
    
    df = pd.DataFrame(quarters)
    
    output_path = os.path.join(OUTPUT_DIR, 'compliance_metrics_quarterly.csv')
    df.to_csv(output_path, index=False)
    print(f"✅ Generated: {output_path}")
    print(f"   - {len(df)} quarters of compliance data")
    print(f"   - Latest compliance rate: {df['compliance_rate_percent'].iloc[-1]}%")
    print(f"   - Ethics training coverage: {df['employee_ethics_training_percent'].iloc[-1]}%\n")
    
    return df

def generate_esg_ratings():
    """
    Generate ESG ratings and scores - quarterly for 1 year
    Simulates ratings from major ESG rating agencies
    """
    
    start_date = datetime.now() - timedelta(days=365)
    
    quarters = []
    for i in range(5):
        quarter_date = start_date + timedelta(days=90*i)
        quarter_label = f"Q{((quarter_date.month-1)//3)+1} {quarter_date.year}"
        
        # Progressive improvement in ratings
        base_score = 65 + (i * 3)
        
        data = {
            'quarter': quarter_label,
            # Overall ESG Score (0-100)
            'overall_esg_score': round(base_score + np.random.uniform(-2, 3), 1),
            # Letter grade (A, B, C, etc.)
            'esg_grade': 'B' if base_score < 70 else ('B+' if base_score < 75 else 'A-'),
            # Component scores
            'environmental_score': round(base_score + np.random.uniform(-3, 5), 1),
            'social_score': round(base_score + np.random.uniform(-5, 2), 1),
            'governance_score': round(base_score + np.random.uniform(-2, 4), 1),
            # Risk rating (Low, Medium, High)
            'esg_risk_rating': 'Medium' if base_score < 70 else 'Low',
            # Percentile rank vs peers
            'industry_percentile_rank': round(50 + (i * 5) + np.random.uniform(-3, 5), 1),
            # Carbon disclosure score (CDP-style A to D)
            'carbon_disclosure_score': 'B' if i < 2 else ('B+' if i < 4 else 'A-')
        }
        
        quarters.append(data)
    
    df = pd.DataFrame(quarters)
    
    output_path = os.path.join(OUTPUT_DIR, 'esg_ratings_quarterly.csv')
    df.to_csv(output_path, index=False)
    print(f"✅ Generated: {output_path}")
    print(f"   - {len(df)} quarters of ESG ratings")
    print(f"   - Latest ESG Score: {df['overall_esg_score'].iloc[-1]} (Grade: {df['esg_grade'].iloc[-1]})")
    print(f"   - Industry Rank: Top {100 - df['industry_percentile_rank'].iloc[-1]:.0f}%\n")
    
    return df

def generate_transparency_disclosure():
    """
    Generate transparency and disclosure metrics - quarterly for 1 year
    Tracks data disclosure completeness and verification status
    """
    
    start_date = datetime.now() - timedelta(days=365)
    
    quarters = []
    for i in range(5):
        quarter_date = start_date + timedelta(days=90*i)
        quarter_label = f"Q{((quarter_date.month-1)//3)+1} {quarter_date.year}"
        
        # Progressive improvement in transparency
        data = {
            'quarter': quarter_label,
            'data_disclosure_completeness_percent': round(75 + (i * 4) + np.random.uniform(-1, 3), 1),
            'esg_report_published': 'Yes' if i >= 2 else 'In Progress',
            'third_party_verified_metrics': 8 + i,  # Increasing verification
            'total_reportable_metrics': 15,
            'verification_percent': round((8 + i) / 15 * 100, 1),
            'public_commitments_tracked': 5 + i,
            'commitments_on_track_percent': round(80 + (i * 3) + np.random.uniform(-2, 4), 1),
            'stakeholder_engagement_events': np.random.randint(3, 7),
            'sustainability_website_updates': np.random.randint(4, 9),
            'regulatory_filings_submitted': np.random.randint(3, 6)
        }
        
        # Ensure percentages don't exceed 100%
        data['data_disclosure_completeness_percent'] = min(95.0, data['data_disclosure_completeness_percent'])
        data['commitments_on_track_percent'] = min(98.0, data['commitments_on_track_percent'])
        
        quarters.append(data)
    
    df = pd.DataFrame(quarters)
    
    output_path = os.path.join(OUTPUT_DIR, 'transparency_disclosure_quarterly.csv')
    df.to_csv(output_path, index=False)
    print(f"✅ Generated: {output_path}")
    print(f"   - {len(df)} quarters of transparency data")
    print(f"   - Data disclosure: {df['data_disclosure_completeness_percent'].iloc[-1]}%")
    print(f"   - Verified metrics: {df['verification_percent'].iloc[-1]}%\n")
    
    return df

def generate_summary_report(board_df, compliance_df, ratings_df, transparency_df):
    """
    Generate a summary report of all governance metrics
    """
    
    summary = f"""
GOVERNANCE DATASET SUMMARY REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Company: Aurora Renewables (1-year-old company)
Period: Last 5 quarters (1 year + current quarter)

================================
1. BOARD COMPOSITION
================================
Latest Quarter Metrics:
- Total Directors: {board_df['total_directors'].iloc[-1]}
- Independent Directors: {board_df['independent_percent'].iloc[-1]}%
- Female Directors: {board_df['female_percent'].iloc[-1]}%
- Average Board Attendance: {board_df['average_attendance_percent'].iloc[-1]}%

Trend: Steadily improving diversity and independence

================================
2. COMPLIANCE METRICS
================================
Latest Quarter Metrics:
- Compliance Rate: {compliance_df['compliance_rate_percent'].iloc[-1]}%
- Regulatory Violations: {compliance_df['regulatory_violations'].iloc[-1]}
- Ethics Training Coverage: {compliance_df['employee_ethics_training_percent'].iloc[-1]}%

Trend: Strong improvement in compliance, violations decreasing

================================
3. ESG RATINGS
================================
Latest Quarter Metrics:
- Overall ESG Score: {ratings_df['overall_esg_score'].iloc[-1]}/100
- ESG Grade: {ratings_df['esg_grade'].iloc[-1]}
- Environmental Score: {ratings_df['environmental_score'].iloc[-1]}
- Social Score: {ratings_df['social_score'].iloc[-1]}
- Governance Score: {ratings_df['governance_score'].iloc[-1]}
- Industry Percentile: {ratings_df['industry_percentile_rank'].iloc[-1]} (Top {100 - ratings_df['industry_percentile_rank'].iloc[-1]:.0f}%)
- ESG Risk: {ratings_df['esg_risk_rating'].iloc[-1]}
- Carbon Disclosure: {ratings_df['carbon_disclosure_score'].iloc[-1]}

Trend: Consistent improvement across all ESG dimensions

================================
4. TRANSPARENCY & DISCLOSURE
================================
Latest Quarter Metrics:
- Data Disclosure Completeness: {transparency_df['data_disclosure_completeness_percent'].iloc[-1]}%
- Verified Metrics: {transparency_df['verification_percent'].iloc[-1]}%
- ESG Report Status: {transparency_df['esg_report_published'].iloc[-1]}
- Public Commitments on Track: {transparency_df['commitments_on_track_percent'].iloc[-1]}%

Trend: Increasing transparency and third-party verification

================================
FILE SUMMARY
================================
Total Files Generated: 4 CSV files + 1 summary report
Total Data Points: {len(board_df) + len(compliance_df) + len(ratings_df) + len(transparency_df)} records

Files:
1. board_composition_quarterly.csv ({len(board_df)} rows)
2. compliance_metrics_quarterly.csv ({len(compliance_df)} rows)
3. esg_ratings_quarterly.csv ({len(ratings_df)} rows)
4. transparency_disclosure_quarterly.csv ({len(transparency_df)} rows)

================================
INSIGHTS FOR 1-YEAR-OLD COMPANY
================================
✅ Strong governance foundation established early
✅ Board diversity improving quarter-over-quarter
✅ Compliance rate trending toward excellence (>95%)
✅ ESG ratings show upward trajectory (B → A-)
✅ Transparency commitments being met
⚠️  Early-stage company still building track record
💡 Positioned well for future ESG leadership

================================
"""
    
    output_path = os.path.join(OUTPUT_DIR, 'summary_report.txt')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"✅ Generated: {output_path}")
    print("\n" + "="*50)
    print("ALL GOVERNANCE DATASETS GENERATED SUCCESSFULLY!")
    print("="*50)

def main():
    print("="*50)
    print("GOVERNANCE DATASET GENERATOR")
    print("Aurora Renewables ESG Dashboard")
    print("="*50)
    print()
    
    # Generate all datasets
    board_df = generate_board_composition()
    compliance_df = generate_compliance_metrics()
    ratings_df = generate_esg_ratings()
    transparency_df = generate_transparency_disclosure()
    
    # Generate summary report
    generate_summary_report(board_df, compliance_df, ratings_df, transparency_df)
    
    print(f"\n📁 All files saved to: {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()
