"""
Social Impact Service API
REST API serving social metrics from SQLite database
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

app = FastAPI(title="Social Impact Service API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database path
DB_PATH = Path("social_metrics.db")

# Metric definitions
SOCIAL_METRICS = {
    "employee_wellbeing": {
        "name": "Employee Wellbeing",
        "table": "employee_wellbeing",
        "description": "Monthly satisfaction scores and training hours",
        "frequency": "monthly"
    },
    "diversity_inclusion": {
        "name": "Diversity & Inclusion",
        "table": "diversity_inclusion",
        "description": "Quarterly diversity metrics and pay equity",
        "frequency": "quarterly"
    },
    "community_impact": {
        "name": "Community Impact",
        "table": "community_impact",
        "description": "Quarterly volunteer hours and donations",
        "frequency": "quarterly"
    },
    "health_safety": {
        "name": "Health & Safety",
        "table": "health_safety",
        "description": "Monthly incident rates and safety metrics",
        "frequency": "monthly"
    }
}

def get_db_connection():
    """Get database connection"""
    if not DB_PATH.exists():
        raise HTTPException(status_code=503, detail="Database not found. Run create_social_db.py first.")
    return sqlite3.connect(DB_PATH)

def dict_factory(cursor, row):
    """Convert database row to dictionary"""
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_exists = DB_PATH.exists()
    return {
        "status": "healthy" if db_exists else "database_missing",
        "service": "social-service",
        "database": str(DB_PATH),
        "database_exists": db_exists
    }

@app.get("/api/social/metrics")
async def list_metrics():
    """List all available social metrics"""
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    metrics_info = []
    for key, info in SOCIAL_METRICS.items():
        try:
            cursor.execute(f"SELECT COUNT(*) as count FROM {info['table']}")
            result = cursor.fetchone()
            count = result['count'] if result else 0
            
            metrics_info.append({
                "key": key,
                "name": info["name"],
                "description": info["description"],
                "frequency": info["frequency"],
                "rows": count,
                "available": True
            })
        except Exception as e:
            metrics_info.append({
                "key": key,
                "name": info["name"],
                "description": info["description"],
                "frequency": info["frequency"],
                "rows": 0,
                "available": False,
                "error": str(e)
            })
    
    conn.close()
    
    return {
        "metrics": metrics_info,
        "total_metrics": len(metrics_info)
    }

@app.get("/api/social/{metric_key}")
async def get_metric(metric_key: str, limit: Optional[int] = None):
    """Get data for a specific metric"""
    if metric_key not in SOCIAL_METRICS:
        raise HTTPException(status_code=404, detail=f"Metric '{metric_key}' not found")
    
    metric_info = SOCIAL_METRICS[metric_key]
    table_name = metric_info["table"]
    
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    try:
        if limit:
            query = f"SELECT * FROM {table_name} ORDER BY ROWID DESC LIMIT {limit}"
        else:
            query = f"SELECT * FROM {table_name}"
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Reverse if limited to maintain chronological order
        if limit:
            rows = list(reversed(rows))
        
        conn.close()
        
        return {
            "metric": metric_key,
            "name": metric_info["name"],
            "description": metric_info["description"],
            "frequency": metric_info["frequency"],
            "rows": len(rows),
            "data": rows
        }
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/social/summary/latest")
async def get_latest_summary():
    """Get latest values for all metrics"""
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    summary = {}
    
    for key, info in SOCIAL_METRICS.items():
        try:
            cursor.execute(f"SELECT * FROM {info['table']} ORDER BY ROWID DESC LIMIT 1")
            latest = cursor.fetchone()
            
            if latest:
                summary[key] = {
                    "name": info["name"],
                    "frequency": info["frequency"],
                    "latest": latest
                }
        except Exception as e:
            summary[key] = {
                "name": info["name"],
                "error": str(e)
            }
    
    conn.close()
    
    return {
        "summary": summary,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/social/stats")
async def get_statistics():
    """Get aggregated statistics across all metrics"""
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    stats = {}
    
    try:
        # Employee wellbeing stats
        cursor.execute("""
            SELECT 
                AVG(satisfaction_score) as avg_satisfaction,
                MAX(satisfaction_score) as max_satisfaction,
                AVG(training_hours_per_employee) as avg_training_hours,
                MAX(total_employees) as current_employees
            FROM employee_wellbeing
        """)
        stats["wellbeing"] = cursor.fetchone()
        
        # Diversity stats
        cursor.execute("""
            SELECT 
                AVG(female_employees_percent) as avg_female_percent,
                AVG(pay_equity_ratio) as avg_pay_equity
            FROM diversity_inclusion
        """)
        stats["diversity"] = cursor.fetchone()
        
        # Community impact stats
        cursor.execute("""
            SELECT 
                SUM(volunteer_hours) as total_volunteer_hours,
                SUM(total_donations_usd) as total_donations,
                SUM(beneficiaries_reached) as total_beneficiaries
            FROM community_impact
        """)
        stats["community"] = cursor.fetchone()
        
        # Safety stats
        cursor.execute("""
            SELECT 
                AVG(incident_rate_per_1000_hours) as avg_incident_rate,
                SUM(total_incidents) as total_incidents,
                AVG(safety_training_completion_percent) as avg_training_completion
            FROM health_safety
        """)
        stats["safety"] = cursor.fetchone()
        
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))
    
    conn.close()
    
    return {
        "statistics": stats,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
