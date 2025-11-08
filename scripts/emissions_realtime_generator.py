"""
Real-time Emissions Data Generator
Generates all 7 emissions-related metrics continuously
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import os
from pathlib import Path
import json

# Output directory
OUTPUT_DIR = Path("dataset_realtime/emissions")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def generate_travel_emissions():
    """Generate daily company travel emissions"""
    today = datetime.now()
    date = today.strftime("%Y-%m-%d")
    
    data = {
        "date": [date],
        "air_travel_km": [np.random.uniform(5000, 15000)],
        "ground_transport_km": [np.random.uniform(2000, 8000)],
        "air_emissions_kg": [np.random.uniform(800, 2400)],
        "ground_emissions_kg": [np.random.uniform(150, 600)]
    }
    
    df = pd.DataFrame(data)
    output_file = OUTPUT_DIR / "company_travel_emissions_daily.csv"
    
    # Append if file exists, otherwise create new
    if output_file.exists():
        existing = pd.read_csv(output_file)
        df = pd.concat([existing, df], ignore_index=True)
        # Keep only last 30 days
        df = df.tail(30)
    
    df.to_csv(output_file, index=False)
    return len(df)

def generate_production_emissions():
    """Generate daily production emissions"""
    today = datetime.now()
    date = today.strftime("%Y-%m-%d")
    
    data = {
        "date": [date],
        "production_volume_units": [np.random.uniform(8000, 12000)],
        "direct_emissions_kg": [np.random.uniform(3000, 5000)],
        "indirect_emissions_kg": [np.random.uniform(1500, 2500)],
        "total_emissions_kg": [np.random.uniform(4500, 7500)]
    }
    
    df = pd.DataFrame(data)
    output_file = OUTPUT_DIR / "production_emissions_daily.csv"
    
    if output_file.exists():
        existing = pd.read_csv(output_file)
        df = pd.concat([existing, df], ignore_index=True)
        df = df.tail(30)
    
    df.to_csv(output_file, index=False)
    return len(df)

def generate_energy_consumption():
    """Generate daily energy consumption"""
    today = datetime.now()
    date = today.strftime("%Y-%m-%d")
    
    data = {
        "date": [date],
        "electricity_kwh": [np.random.uniform(15000, 25000)],
        "natural_gas_kwh": [np.random.uniform(8000, 12000)],
        "renewable_kwh": [np.random.uniform(5000, 10000)],
        "total_kwh": [np.random.uniform(28000, 47000)]
    }
    
    df = pd.DataFrame(data)
    output_file = OUTPUT_DIR / "energy_consumption_daily.csv"
    
    if output_file.exists():
        existing = pd.read_csv(output_file)
        df = pd.concat([existing, df], ignore_index=True)
        df = df.tail(30)
    
    df.to_csv(output_file, index=False)
    return len(df)

def generate_water_usage():
    """Generate daily water usage"""
    today = datetime.now()
    date = today.strftime("%Y-%m-%d")
    
    data = {
        "date": [date],
        "process_water_liters": [np.random.uniform(50000, 80000)],
        "cooling_water_liters": [np.random.uniform(30000, 50000)],
        "domestic_water_liters": [np.random.uniform(5000, 10000)],
        "recycled_water_liters": [np.random.uniform(20000, 35000)],
        "total_consumption_liters": [np.random.uniform(85000, 140000)]
    }
    
    df = pd.DataFrame(data)
    output_file = OUTPUT_DIR / "water_usage_daily.csv"
    
    if output_file.exists():
        existing = pd.read_csv(output_file)
        df = pd.concat([existing, df], ignore_index=True)
        df = df.tail(30)
    
    df.to_csv(output_file, index=False)
    return len(df)

def generate_air_quality():
    """Generate daily air quality monitoring"""
    today = datetime.now()
    date = today.strftime("%Y-%m-%d")
    
    data = {
        "date": [date],
        "pm25_ug_m3": [np.random.uniform(10, 50)],
        "pm10_ug_m3": [np.random.uniform(20, 80)],
        "no2_ppb": [np.random.uniform(15, 45)],
        "so2_ppb": [np.random.uniform(5, 20)],
        "co_ppm": [np.random.uniform(0.5, 2.0)],
        "aqi_score": [np.random.uniform(30, 90)]
    }
    
    df = pd.DataFrame(data)
    output_file = OUTPUT_DIR / "air_quality_monitoring_daily.csv"
    
    if output_file.exists():
        existing = pd.read_csv(output_file)
        df = pd.concat([existing, df], ignore_index=True)
        df = df.tail(30)
    
    df.to_csv(output_file, index=False)
    return len(df)

def generate_energy_mix():
    """Generate monthly energy mix"""
    today = datetime.now()
    month = today.strftime("%Y-%m")
    
    # Generate mix that sums to 100%
    solar = np.random.uniform(25, 35)
    wind = np.random.uniform(20, 30)
    hydro = np.random.uniform(10, 15)
    fossil = 100 - solar - wind - hydro
    
    data = {
        "month": [month],
        "solar_percent": [solar],
        "wind_percent": [wind],
        "hydro_percent": [hydro],
        "fossil_percent": [fossil],
        "renewable_total_percent": [solar + wind + hydro]
    }
    
    df = pd.DataFrame(data)
    output_file = OUTPUT_DIR / "energy_mix_monthly.csv"
    
    if output_file.exists():
        existing = pd.read_csv(output_file)
        # Check if this month already exists
        if month in existing['month'].values:
            existing = existing[existing['month'] != month]
        df = pd.concat([existing, df], ignore_index=True)
        df = df.tail(12)  # Keep last 12 months
    
    df.to_csv(output_file, index=False)
    return len(df)

def generate_waste_management():
    """Generate monthly waste management"""
    today = datetime.now()
    month = today.strftime("%Y-%m")
    
    recycled = np.random.uniform(15000, 25000)
    composted = np.random.uniform(5000, 10000)
    landfill = np.random.uniform(8000, 15000)
    hazardous = np.random.uniform(500, 2000)
    total = recycled + composted + landfill + hazardous
    
    data = {
        "month": [month],
        "recycled_kg": [recycled],
        "composted_kg": [composted],
        "landfill_kg": [landfill],
        "hazardous_waste_kg": [hazardous],
        "total_waste_kg": [total],
        "recycling_rate_percent": [(recycled / total) * 100]
    }
    
    df = pd.DataFrame(data)
    output_file = OUTPUT_DIR / "waste_management_monthly.csv"
    
    if output_file.exists():
        existing = pd.read_csv(output_file)
        if month in existing['month'].values:
            existing = existing[existing['month'] != month]
        df = pd.concat([existing, df], ignore_index=True)
        df = df.tail(12)
    
    df.to_csv(output_file, index=False)
    return len(df)

def generate_all_emissions():
    """Generate all 7 emissions metrics"""
    metrics = {
        "travel_emissions": generate_travel_emissions(),
        "production_emissions": generate_production_emissions(),
        "energy_consumption": generate_energy_consumption(),
        "water_usage": generate_water_usage(),
        "air_quality": generate_air_quality(),
        "energy_mix": generate_energy_mix(),
        "waste_management": generate_waste_management()
    }
    
    timestamp = datetime.now().isoformat()
    print(f"[{timestamp}] Generated emissions metrics: {json.dumps(metrics, indent=2)}")
    
    return metrics

def main():
    """Main loop - generate data every 60 seconds"""
    print("🌱 Emissions Real-time Generator Started")
    print(f"📁 Output directory: {OUTPUT_DIR.absolute()}")
    print("⏱️  Refresh interval: 60 seconds")
    print("-" * 60)
    
    iteration = 0
    while True:
        iteration += 1
        print(f"\n🔄 Iteration #{iteration}")
        
        try:
            metrics = generate_all_emissions()
            print(f"✅ Successfully generated {sum(metrics.values())} total rows across 7 metrics")
        except Exception as e:
            print(f"❌ Error generating data: {e}")
        
        print(f"⏳ Sleeping for 60 seconds...")
        time.sleep(60)

if __name__ == "__main__":
    main()
