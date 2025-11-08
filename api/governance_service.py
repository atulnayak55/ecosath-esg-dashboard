"""
FastAPI service for Governance Metrics
Serves governance data from SQLite database on port 8003
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import uvicorn
from typing import List, Dict, Any, Optional

app = FastAPI(
    title="Governance Metrics API",
    description="REST API for Aurora Renewables Governance Metrics",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
DATABASE_PATH = 'governance_metrics.db'

# Metric definitions
GOVERNANCE_METRICS = [
    {
        "key": "board_composition",
        "name": "Board Composition",
        "description": "Board diversity and independence metrics",
        "table": "board_composition",
        "available": True
    },
    {
        "key": "compliance_metrics",
        "name": "Compliance & Audit",
        "description": "ESG audit performance and regulatory compliance",
        "table": "compliance_metrics",
        "available": True
    },
    {
        "key": "esg_ratings",
        "name": "ESG Ratings & Scores",
        "description": "ESG scores from rating agencies",
        "table": "esg_ratings",
        "available": True
    },
    {
        "key": "transparency_disclosure",
        "name": "Transparency & Disclosure",
        "description": "Data disclosure completeness and verification",
        "table": "transparency_disclosure",
        "available": True
    }
]

def get_db_connection():
    """Get database connection with row factory for dict responses"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def dict_from_row(row):
    """Convert sqlite3.Row to dictionary"""
    return dict(zip(row.keys(), row))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "governance-metrics",
        "database": DATABASE_PATH
    }

@app.get("/api/governance/metrics")
async def list_metrics():
    """Get list of all available governance metrics"""
    return {
        "metrics": GOVERNANCE_METRICS,
        "total": len(GOVERNANCE_METRICS)
    }

@app.get("/api/governance/{metric_key}")
async def get_metric_data(metric_key: str, limit: Optional[int] = None):
    """
    Get data for a specific governance metric
    
    Args:
        metric_key: Key of the metric (board_composition, compliance_metrics, etc.)
        limit: Optional limit on number of records to return
    """
    
    # Find metric definition
    metric_def = next((m for m in GOVERNANCE_METRICS if m["key"] == metric_key), None)
    
    if not metric_def:
        raise HTTPException(status_code=404, detail=f"Metric '{metric_key}' not found")
    
    if not metric_def["available"]:
        raise HTTPException(status_code=503, detail=f"Metric '{metric_key}' not available")
    
    # Get data from database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = f"SELECT * FROM {metric_def['table']} ORDER BY quarter"
    if limit:
        query += f" LIMIT {limit}"
    
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    
    # Convert to list of dicts
    data = [dict_from_row(row) for row in rows]
    
    return {
        "metric": metric_def["name"],
        "key": metric_key,
        "description": metric_def["description"],
        "data": data,
        "count": len(data)
    }

@app.get("/api/governance/summary/latest")
async def get_latest_summary():
    """
    Get latest values from all governance metrics
    """
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    summary = {}
    
    # Board composition - latest quarter
    cursor.execute("""
        SELECT * FROM board_composition 
        ORDER BY quarter DESC LIMIT 1
    """)
    board = cursor.fetchone()
    if board:
        summary["board_composition"] = dict_from_row(board)
    
    # Compliance - latest quarter
    cursor.execute("""
        SELECT * FROM compliance_metrics 
        ORDER BY quarter DESC LIMIT 1
    """)
    compliance = cursor.fetchone()
    if compliance:
        summary["compliance_metrics"] = dict_from_row(compliance)
    
    # ESG Ratings - latest quarter
    cursor.execute("""
        SELECT * FROM esg_ratings 
        ORDER BY quarter DESC LIMIT 1
    """)
    esg = cursor.fetchone()
    if esg:
        summary["esg_ratings"] = dict_from_row(esg)
    
    # Transparency - latest quarter
    cursor.execute("""
        SELECT * FROM transparency_disclosure 
        ORDER BY quarter DESC LIMIT 1
    """)
    transparency = cursor.fetchone()
    if transparency:
        summary["transparency_disclosure"] = dict_from_row(transparency)
    
    conn.close()
    
    return {
        "summary": summary,
        "metrics_count": len(summary)
    }

@app.get("/api/governance/stats")
async def get_aggregated_stats():
    """
    Get aggregated statistics across all governance metrics
    """
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    stats = {}
    
    # Board composition stats
    cursor.execute("""
        SELECT 
            AVG(independent_percent) as avg_independent_percent,
            MAX(independent_percent) as max_independent_percent,
            AVG(female_percent) as avg_female_percent,
            MAX(female_percent) as max_female_percent,
            AVG(average_attendance_percent) as avg_attendance
        FROM board_composition
    """)
    board_stats = cursor.fetchone()
    if board_stats:
        stats["board"] = dict_from_row(board_stats)
    
    # Compliance stats
    cursor.execute("""
        SELECT 
            AVG(compliance_rate_percent) as avg_compliance_rate,
            MAX(compliance_rate_percent) as max_compliance_rate,
            SUM(regulatory_violations) as total_violations,
            AVG(employee_ethics_training_percent) as avg_ethics_training
        FROM compliance_metrics
    """)
    compliance_stats = cursor.fetchone()
    if compliance_stats:
        stats["compliance"] = dict_from_row(compliance_stats)
    
    # ESG ratings stats
    cursor.execute("""
        SELECT 
            AVG(overall_esg_score) as avg_esg_score,
            MAX(overall_esg_score) as max_esg_score,
            MIN(overall_esg_score) as min_esg_score,
            AVG(environmental_score) as avg_environmental_score,
            AVG(social_score) as avg_social_score,
            AVG(governance_score) as avg_governance_score
        FROM esg_ratings
    """)
    esg_stats = cursor.fetchone()
    if esg_stats:
        stats["esg_ratings"] = dict_from_row(esg_stats)
    
    # Transparency stats
    cursor.execute("""
        SELECT 
            AVG(data_disclosure_completeness_percent) as avg_disclosure,
            MAX(data_disclosure_completeness_percent) as max_disclosure,
            AVG(verification_percent) as avg_verification,
            SUM(stakeholder_engagement_events) as total_engagement_events
        FROM transparency_disclosure
    """)
    transparency_stats = cursor.fetchone()
    if transparency_stats:
        stats["transparency"] = dict_from_row(transparency_stats)
    
    conn.close()
    
    return {
        "stats": stats,
        "categories": len(stats)
    }

if __name__ == "__main__":
    print("="*60)
    print("Starting Governance Metrics API Service")
    print("="*60)
    print(f"Database: {DATABASE_PATH}")
    print(f"Port: 8003")
    print(f"Metrics: {len(GOVERNANCE_METRICS)}")
    print("="*60)
    
    uvicorn.run(app, host="0.0.0.0", port=8003)
