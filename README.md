# Aurora Renewables - ESG Dashboard

**Team 12 - NOI Hackathon 2025**

## 🌱 Project Overview

Real-time Environmental, Social, and Governance (ESG) monitoring dashboard for Aurora Renewables, a year-old renewable energy company. The system simulates and tracks ESG metrics across three pillars: Emissions, Social Impact, and Governance.

## 🎯 Features

### Emissions Monitoring (Live Demo)
- **Real-time Data Generation**: 7 emissions metrics updated every 60 seconds
- **Historical Data**: Full year (365 days) of historical tracking
- **Interactive Dashboard**: Beautiful dark-themed UI with Plotly charts
- **Time Filters**: 1D, 7D, 1M, 6M, 1Y, All views
- **7 Key Metrics**:
  - ✈️ Travel Emissions (flights + ground transport)
  - 🏭 Production Emissions (direct + indirect)
  - ⚡ Energy Consumption (total kWh)
  - 💧 Water Usage (consumption + recycling)
  - 🌫️ Air Quality (AQI monitoring)
  - 🔋 Energy Mix (renewable vs fossil fuel %)
  - ♻️ Waste Management (recycling rates)

### Social Impact (Ready to Deploy)
- Employee satisfaction tracking
- Diversity & inclusion metrics
- Training & development hours
- Community investment
- Workplace safety incidents

### Governance (Ready to Deploy)
- Board diversity metrics
- Ethics & compliance tracking
- Risk management
- Shareholder engagement
- Data privacy & security

## 🏗️ Architecture

### Backend Services
- **FastAPI Microservices**: Separate services for each ESG pillar
- **Real-time Generators**: Python scripts generating live data
- **Data Pipeline**: Historical + real-time data merging
- **Auto-refresh**: 30-second cache updates

### Frontend
- **Vanilla JavaScript**: No framework dependencies
- **Plotly.js**: Interactive, responsive charts
- **Modern CSS**: Dark theme with gradients and animations
- **Responsive Design**: Mobile-friendly layouts

### Deployment (Ready)
- **Docker Containers**: Dockerfile for each service
- **Google Cloud**: Cloud Run Jobs + Artifact Registry
- **Cloud Storage**: GCS buckets for data persistence

## 📁 Project Structure

```
Infolabs/
├── api/
│   ├── emissions_service.py      # Emissions API (FastAPI)
│   └── main.py                    # Legacy unified API
├── scripts/
│   ├── emissions_realtime_generator.py
│   ├── social_realtime_generator.py
│   ├── governance_realtime_generator.py
│   ├── generate_messy_datasets.py
│   └── clean_datasets.py
├── emissions.html                 # Interactive emissions dashboard
├── Dockerfile.emissions           # Container for emissions service
├── requirements.txt               # Python dependencies
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Virtual environment
- Port 8001 (API) and 5500 (frontend) available

### Installation

1. **Clone the repository**
```bash
git clone https://repos.hackathon.bz.it/2025-sfscon/team-12.git
cd team-12
```

2. **Set up Python environment**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

### Running Locally

1. **Start the real-time data generator** (Terminal 1)
```bash
python scripts/emissions_realtime_generator.py
```

2. **Start the emissions API** (Terminal 2)
```bash
python api/emissions_service.py
# Runs on http://127.0.0.1:8001
```

3. **Start the web server** (Terminal 3)
```bash
python -m http.server 5500
```

4. **Open the dashboard**
```
http://127.0.0.1:5500/emissions.html
```

## 📊 API Endpoints

### Emissions Service (Port 8001)

- `GET /health` - Health check
- `GET /api/emissions/metrics` - List all metrics
- `GET /api/emissions/{metric_key}` - Get specific metric data
  - `metric_key`: travel, production, energy, water, air_quality, energy_mix, waste
  - Query params: `?limit=N` to limit rows
- `GET /api/emissions/summary/latest` - Latest values for all metrics
- `POST /api/emissions/refresh` - Manual cache refresh

## 🐳 Docker Deployment

Build the emissions service container:
```bash
docker build -f Dockerfile.emissions -t emissions-service:latest .
docker run -p 8001:8001 emissions-service
```

## 📈 Data Flow

1. **Real-time Generator** → Generates fresh data every 60 seconds
2. **CSV Storage** → Saves to `dataset_realtime/emissions/`
3. **API Service** → Merges historical + real-time data
4. **Cache Refresh** → Updates every 30 seconds
5. **Frontend** → Fetches via REST API, auto-refreshes every 30 seconds
6. **Interactive Charts** → Plotly renders with time filters

## 🎨 Design Highlights

- **Modern Dark Theme**: Easy on eyes, professional look
- **Gradient Accents**: Green theme matching sustainability focus
- **Smooth Animations**: Hover effects and transitions
- **Status Indicators**: Live pulse, error banners
- **Responsive Cards**: Click-to-explore metrics
- **Time Series Charts**: Spline curves with area fills

## 🔧 Technology Stack

**Backend:**
- Python 3.13
- FastAPI 0.115
- Pandas 2.2
- Uvicorn (ASGI server)

**Frontend:**
- HTML5 / CSS3
- Vanilla JavaScript
- Plotly.js 2.27

**Infrastructure:**
- Docker
- Google Cloud Platform
- Cloud Run Jobs
- Artifact Registry
- Cloud Storage

## 📝 License

Hackathon Project - NOI Techpark 2025

## 👥 Team 12

Aurora Renewables ESG Monitoring System
