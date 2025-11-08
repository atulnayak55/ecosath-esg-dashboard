from __future__ import annotations

import asyncio
import logging
import os
from contextlib import suppress
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from scripts.clean_datasets import clean_datasets
from scripts.generate_messy_datasets import generate_messy_datasets

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
)
logger = logging.getLogger("esg-api")

BASE_INPUT_DIR = Path(os.getenv("CLEAN_BASE_DIR", "dataset"))
RAW_DIR = Path(os.getenv("RAW_OUTPUT_DIR", "dataset_raw"))
CLEAN_DIR = Path(os.getenv("CLEAN_OUTPUT_DIR", "dataset_clean"))
REFRESH_INTERVAL_SECONDS = max(30, int(os.getenv("REFRESH_INTERVAL_SECONDS", "300")))
GENERATOR_SEED = int(os.getenv("GENERATOR_SEED", "42"))
UPLOAD_GCS_URI = os.getenv("UPLOAD_GCS_URI")

app = FastAPI(title="ESG Data Simulation API", version="0.1.0")

_raw_origins = os.getenv("API_CORS_ORIGINS", "*")
if _raw_origins == "*":
    _allowed_origins = ["*"]
else:
    _allowed_origins = [origin.strip() for origin in _raw_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

_dataset_cache: Dict[str, List[dict]] = {}
_last_refresh: datetime | None = None
_last_error: str | None = None
_cache_lock = asyncio.Lock()
_pipeline_lock = asyncio.Lock()
_scheduler_task: asyncio.Task[None] | None = None


def _load_clean_outputs() -> Dict[str, List[dict]]:
    datasets: Dict[str, List[dict]] = {}
    if not CLEAN_DIR.exists():
        return datasets
    for csv_path in CLEAN_DIR.glob("*.csv"):
        df = pd.read_csv(csv_path)
        if "date" in df.columns:
            with suppress(Exception):
                df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
        datasets[csv_path.stem] = df.to_dict(orient="records")
    return datasets


async def _refresh_pipeline() -> None:
    global _last_refresh, _last_error
    async with _pipeline_lock:
        try:
            def run_tasks() -> Dict[str, List[dict]]:
                generate_messy_datasets(BASE_INPUT_DIR, RAW_DIR, seed=GENERATOR_SEED, upload_gcs=UPLOAD_GCS_URI)
                clean_datasets(str(RAW_DIR), str(CLEAN_DIR))
                return _load_clean_outputs()

            datasets = await asyncio.to_thread(run_tasks)
            async with _cache_lock:
                _dataset_cache.clear()
                _dataset_cache.update(datasets)
                _last_refresh = datetime.now(timezone.utc)
                _last_error = None
            logger.info("Pipeline refresh completed: %d datasets", len(datasets))
        except Exception as exc:  # noqa: BLE001 - surface pipeline failures
            logger.exception("Pipeline refresh failed")
            async with _cache_lock:
                _last_error = str(exc)


async def _scheduler_loop() -> None:
    while True:
        await asyncio.sleep(REFRESH_INTERVAL_SECONDS)
        await _refresh_pipeline()


@app.on_event("startup")
async def _on_startup() -> None:
    global _scheduler_task
    await _refresh_pipeline()
    _scheduler_task = asyncio.create_task(_scheduler_loop())


@app.on_event("shutdown")
async def _on_shutdown() -> None:
    if _scheduler_task is None:
        return
    _scheduler_task.cancel()
    with suppress(asyncio.CancelledError):
        await _scheduler_task


@app.get("/health")
async def health() -> dict:
    async with _cache_lock:
        last_refresh = _last_refresh.isoformat() if _last_refresh else None
        status = "ok" if _last_error is None else "degraded"
        error = _last_error
    return {"status": status, "last_refresh": last_refresh, "error": error}


@app.get("/api/datasets")
async def list_datasets() -> dict:
    async with _cache_lock:
        summary = [{"name": name, "rows": len(rows)} for name, rows in _dataset_cache.items()]
        last_refresh = _last_refresh.isoformat() if _last_refresh else None
        error = _last_error
    return {"datasets": summary, "last_refresh": last_refresh, "error": error}


@app.get("/api/datasets/{dataset_name}")
async def get_dataset(dataset_name: str, limit: int | None = Query(default=None, ge=1)) -> dict:
    async with _cache_lock:
        data = _dataset_cache.get(dataset_name)
        last_refresh = _last_refresh.isoformat() if _last_refresh else None
    if data is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    result = data if limit is None else data[:limit]
    return {"dataset": dataset_name, "rows": len(result), "last_refresh": last_refresh, "data": result}


@app.post("/api/refresh", status_code=202)
async def trigger_refresh() -> dict:
    asyncio.create_task(_refresh_pipeline())
    return {"status": "scheduled"}
