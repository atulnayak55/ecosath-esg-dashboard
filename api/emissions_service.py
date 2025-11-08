"""
Emissions Service API
Real-time REST API for all 7 emissions metrics
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
import asyncio
from datetime import datetime

app = FastAPI(title="Emissions Service API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data directories
REALTIME_DIR = Path("dataset_realtime/emissions")
HISTORICAL_DIR = Path("dataset_clean")

# Cache for datasets
_dataset_cache: Dict[str, pd.DataFrame] = {}
_last_refresh = None

# Metric definitions with mapping to both historical and real-time files
EMISSIONS_METRICS = {
    "travel": {
        "realtime_file": "company_travel_emissions_daily.csv",
        "historical_file": "company_travel_emissions_daily_clean.csv",
        "name": "Travel Emissions",
        "unit": "kg CO₂e",
        "description": "Company travel emissions from air and ground transport",
        "date_field": "date",
        "value_field": "travel_tco2e"
    },
    "production": {
        "realtime_file": "production_emissions_daily.csv",
        "historical_file": "company_production_emissions_daily_clean.csv",
        "name": "Production Emissions",
        "unit": "kg CO₂e",
        "description": "Direct and indirect emissions from production activities",
        "date_field": "date",
        "value_field": "total_emissions_kg"
    },
    "energy": {
        "realtime_file": "energy_consumption_daily.csv",
        "historical_file": "company_energy_consumption_daily_clean.csv",
        "name": "Energy Consumption",
        "unit": "kWh",
        "description": "Daily energy consumption across all sources",
        "date_field": "date",
        "value_field": "total_kwh"
    },
    "water": {
        "realtime_file": "water_usage_daily.csv",
        "historical_file": "company_water_usage_daily_clean.csv",
        "name": "Water Usage",
        "unit": "liters",
        "description": "Total water consumption and recycling metrics",
        "date_field": "date",
        "value_field": "total_consumption_liters"
    },
    "air_quality": {
        "realtime_file": "air_quality_monitoring_daily.csv",
        "historical_file": "factory_air_quality_daily_clean.csv",
        "name": "Air Quality",
        "unit": "AQI",
        "description": "Air quality monitoring including PM2.5, PM10, and other pollutants",
        "date_field": "date",
        "value_field": "aqi_score"
    },
    "energy_mix": {
        "realtime_file": "energy_mix_monthly.csv",
        "historical_file": "company_energy_mix_monthly_clean.csv",
        "name": "Energy Mix",
        "unit": "%",
        "description": "Breakdown of renewable vs fossil fuel energy sources",
        "date_field": "month",
        "value_field": "renewable_total_percent"
    },
    "waste": {
        "realtime_file": "waste_management_monthly.csv",
        "historical_file": "company_waste_monthly_clean.csv",
        "name": "Waste Management",
        "unit": "kg",
        "description": "Waste generation, recycling, and disposal metrics",
        "date_field": "month",
        "value_field": "recycling_rate_percent"
    }
}

def load_metric(metric_key: str) -> Optional[pd.DataFrame]:
    """Load a specific metric from both historical and real-time CSV files"""
    try:
        metric_info = EMISSIONS_METRICS.get(metric_key)
        if not metric_info:
            return None
        
        dfs = []
        
        # Load historical data
        historical_path = HISTORICAL_DIR / metric_info["historical_file"]
        if historical_path.exists():
            df_historical = pd.read_csv(historical_path)
            dfs.append(df_historical)
            print(f"  📊 Loaded {len(df_historical)} historical rows for {metric_key}")
        
        # Load real-time data
        realtime_path = REALTIME_DIR / metric_info["realtime_file"]
        if realtime_path.exists():
            df_realtime = pd.read_csv(realtime_path)
            dfs.append(df_realtime)
            print(f"  ⚡ Loaded {len(df_realtime)} real-time rows for {metric_key}")
        
        if not dfs:
            return None
        
        # Combine dataframes
        df = pd.concat(dfs, ignore_index=True)
        
        # Sort by date field
        date_field = metric_info["date_field"]
        if date_field in df.columns:
            df = df.sort_values(date_field)
            # Remove duplicates, keeping the latest (real-time data)
            df = df.drop_duplicates(subset=[date_field], keep='last')
        
        # Replace NaN values with None for JSON serialization
        df = df.fillna(0)  # Replace NaN with 0 for numeric columns
        
        print(f"  ✅ Total {len(df)} rows for {metric_key}")
        return df
        
    except Exception as e:
        print(f"❌ Error loading {metric_key}: {e}")
        return None

def refresh_cache():
    """Refresh all metric data from files"""
    global _last_refresh
    
    for metric_key in EMISSIONS_METRICS.keys():
        df = load_metric(metric_key)
        if df is not None:
            _dataset_cache[metric_key] = df
    
    _last_refresh = datetime.now()
    print(f"✅ Cache refreshed at {_last_refresh.isoformat()} - {len(_dataset_cache)} metrics loaded")

async def _refresh_loop():
    """Background task to refresh data every 30 seconds"""
    while True:
        await asyncio.sleep(30)
        refresh_cache()

@app.on_event("startup")
async def startup_event():
    """Initialize cache and start background refresh"""
    refresh_cache()
    asyncio.create_task(_refresh_loop())

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "emissions-service",
        "metrics_loaded": len(_dataset_cache),
        "last_refresh": _last_refresh.isoformat() if _last_refresh else None
    }

@app.get("/api/emissions/metrics")
async def list_metrics():
    """List all available emissions metrics"""
    return {
        "metrics": [
            {
                "key": key,
                "name": info["name"],
                "unit": info["unit"],
                "description": info["description"],
                "rows": len(_dataset_cache.get(key, [])),
                "available": key in _dataset_cache
            }
            for key, info in EMISSIONS_METRICS.items()
        ],
        "last_refresh": _last_refresh.isoformat() if _last_refresh else None
    }

@app.get("/api/emissions/{metric_key}")
async def get_metric(metric_key: str, limit: Optional[int] = None):
    """Get data for a specific metric"""
    if metric_key not in EMISSIONS_METRICS:
        raise HTTPException(status_code=404, detail=f"Metric '{metric_key}' not found")
    
    if metric_key not in _dataset_cache:
        raise HTTPException(status_code=503, detail=f"Metric '{metric_key}' not yet available")
    
    df = _dataset_cache[metric_key].copy()
    
    if limit:
        df = df.tail(limit)
    
    return {
        "metric": metric_key,
        "name": EMISSIONS_METRICS[metric_key]["name"],
        "unit": EMISSIONS_METRICS[metric_key]["unit"],
        "rows": len(df),
        "data": df.to_dict(orient="records"),
        "timestamp": _last_refresh.isoformat() if _last_refresh else None
    }

@app.get("/api/emissions/summary/latest")
async def get_latest_summary():
    """Get latest values for all metrics"""
    summary = {}
    
    for key, info in EMISSIONS_METRICS.items():
        if key in _dataset_cache:
            df = _dataset_cache[key]
            if len(df) > 0:
                latest_row = df.iloc[-1].to_dict()
                summary[key] = {
                    "name": info["name"],
                    "unit": info["unit"],
                    "latest": latest_row
                }
    
    return {
        "summary": summary,
        "timestamp": _last_refresh.isoformat() if _last_refresh else None
    }

@app.post("/api/emissions/refresh")
async def manual_refresh():
    """Manually trigger cache refresh"""
    refresh_cache()
    return {
        "status": "refreshed",
        "metrics_loaded": len(_dataset_cache),
        "timestamp": _last_refresh.isoformat() if _last_refresh else None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
