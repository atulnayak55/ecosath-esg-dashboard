"""Generate intentionally messy ESG datasets for simulation.

This script takes the clean baseline CSV files generated earlier and injects
realistic data quality issues: missing days, duplicates, unit mix-ups,
outliers, and string-formatted numbers. The messy outputs can be used to
demonstrate automated cleaning pipelines prior to analytics.

Usage:
    python generate_messy_datasets.py \
        --input-dir dataset \
        --output-dir dataset_raw \
        --seed 123
"""

from __future__ import annotations

import argparse
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd
from google.cloud import storage


def sample_indices(length: int, fraction: float, rng: random.Random) -> List[int]:
    """Return unique indices based on a fraction of total length."""

    count = max(1, int(length * fraction))
    return rng.sample(range(length), count)


def insert_duplicates(df: pd.DataFrame, how_many: int, rng: random.Random) -> pd.DataFrame:
    """Append a handful of duplicate rows (with slight timestamp jitter)."""

    dup_rows = df.sample(n=min(how_many, len(df)), replace=False, random_state=rng.randint(0, 1_000_000))
    dup_rows = dup_rows.copy()
    date_cols = [c for c in dup_rows.columns if dup_rows[c].dtype == 'datetime64[ns]']
    for col in date_cols:
        jitter_days = rng.choices([-1, 0, 1], k=len(dup_rows))
        dup_rows[col] = dup_rows[col] + pd.to_timedelta(jitter_days, unit='D')
    dup_rows['data_issue_flag'] = 'duplicate_injected'
    return pd.concat([df, dup_rows], ignore_index=True)


def apply_missing_values(df: pd.DataFrame, columns: Iterable[str], fraction: float, rng: random.Random) -> None:
    """Set a fraction of values in each column to NaN."""

    for col in columns:
        if col not in df.columns:
            continue
        n_missing = max(1, int(len(df) * fraction))
        missing_idx = rng.sample(range(len(df)), n_missing)
        df.loc[missing_idx, col] = np.nan


def convert_to_strings(df: pd.DataFrame, column: str, formatter, fraction: float, rng: random.Random) -> None:
    """Convert a fraction of column values to formatted strings."""

    if column not in df:
        return
    # Ensure column can hold string representations.
    df[column] = df[column].astype(object)
    idx = sample_indices(len(df), fraction, rng)
    df.loc[idx, column] = df.loc[idx, column].apply(formatter)


def parse_gcs_uri(uri: str) -> Tuple[str, str]:
    if not uri.startswith('gs://'):
        raise ValueError(f"Expected GCS URI beginning with gs://, received: {uri}")
    without_scheme = uri[5:]
    if '/' in without_scheme:
        bucket, prefix = without_scheme.split('/', 1)
    else:
        bucket, prefix = without_scheme, ''
    return bucket, prefix.rstrip('/')


def add_numeric_spikes(df: pd.DataFrame, column: str, fraction: float, factor_range: tuple[float, float], rng: random.Random) -> None:
    """Multiply some values by a spike factor to mimic anomalies."""

    if column not in df:
        return
    idx = sample_indices(len(df), fraction, rng)
    factors = np.array([rng.uniform(*factor_range) for _ in idx])
    df.loc[idx, column] = df.loc[idx, column] * factors


def random_case(text: str, rng: random.Random) -> str:
    return ''.join(rng.choice([ch.lower(), ch.upper()]) for ch in text)


@dataclass
class DatasetSpec:
    filename: str
    kind: str


def make_travel_messy(df: pd.DataFrame, rng: random.Random) -> pd.DataFrame:
    df = df.copy()
    drop_idx = sample_indices(len(df), fraction=0.03, rng=rng)
    df = df.drop(index=drop_idx).reset_index(drop=True)

    apply_missing_values(df, ['flights', 'road_trips'], 0.04, rng)
    convert_to_strings(df, 'total_distance_km', lambda v: f"{v:,.0f} km", 0.08, rng)
    convert_to_strings(df, 'travel_tco2e', lambda v: f"{v:.3f} tCO2e", 0.07, rng)

    add_numeric_spikes(df, 'travel_tco2e', 0.015, (1.4, 1.9), rng)
    df['source_tag'] = df['source_tag'].apply(lambda s: random_case(s, rng))
    df = insert_duplicates(df, how_many=8, rng=rng)
    return df


def make_production_messy(df: pd.DataFrame, rng: random.Random) -> pd.DataFrame:
    df = df.copy()
    apply_missing_values(df, ['production_units'], 0.03, rng)
    convert_to_strings(df, 'emission_intensity_tco2e_per_unit', lambda v: f"{v:.3f} /unit", 0.1, rng)
    add_numeric_spikes(df, 'production_tco2e', 0.02, (0.5, 2.3), rng)
    df = insert_duplicates(df, how_many=5, rng=rng)
    return df


def make_energy_daily_messy(df: pd.DataFrame, rng: random.Random) -> pd.DataFrame:
    df = df.copy()
    apply_missing_values(df, ['electricity_kwh'], 0.05, rng)
    convert_to_strings(df, 'electricity_kwh', lambda v: f"{v/1000:.2f} MWh", 0.07, rng)
    convert_to_strings(df, 'natural_gas_mwh', lambda v: f"{v:.1f} MWh", 0.06, rng)
    add_numeric_spikes(df, 'peak_demand_kw', 0.02, (1.3, 2.1), rng)
    df = insert_duplicates(df, how_many=6, rng=rng)
    return df


def make_energy_mix_messy(df: pd.DataFrame, rng: random.Random) -> pd.DataFrame:
    df = df.copy()
    convert_to_strings(df, 'renewable_share', lambda v: f"{v*100:.1f}%", 0.3, rng)
    convert_to_strings(df, 'non_renewable_share', lambda v: f"{v*100:.1f}%", 0.3, rng)
    apply_missing_values(df, ['renewable_share'], 0.08, rng)
    df = insert_duplicates(df, how_many=2, rng=rng)
    return df


def make_water_messy(df: pd.DataFrame, rng: random.Random) -> pd.DataFrame:
    df = df.copy()
    drop_idx = sample_indices(len(df), 0.02, rng)
    df = df.drop(index=drop_idx).reset_index(drop=True)
    apply_missing_values(df, ['water_withdrawn_m3', 'water_recycled_m3'], 0.06, rng)
    convert_to_strings(df, 'water_withdrawn_m3', lambda v: f"{v*1000:.0f} L", 0.05, rng)
    convert_to_strings(df, 'water_discharge_m3', lambda v: f"{v:.1f} m3", 0.05, rng)
    df = insert_duplicates(df, how_many=5, rng=rng)
    return df


def make_waste_messy(df: pd.DataFrame, rng: random.Random) -> pd.DataFrame:
    df = df.copy()
    convert_to_strings(df, 'hazardous_waste_tons', lambda v: f"{v*1000:.0f} kg", 0.2, rng)
    convert_to_strings(df, 'non_hazardous_waste_tons', lambda v: f"{v:.2f} t", 0.2, rng)
    apply_missing_values(df, ['recycled_fraction'], 0.1, rng)
    df = insert_duplicates(df, how_many=2, rng=rng)
    return df


def make_air_quality_messy(df: pd.DataFrame, rng: random.Random) -> pd.DataFrame:
    df = df.copy()
    apply_missing_values(df, ['aqi', 'pm25_ugm3', 'pm10_ugm3'], 0.04, rng)
    convert_to_strings(df, 'pm25_ugm3', lambda v: f"{v:.1f} μg/m3", 0.12, rng)
    convert_to_strings(df, 'co_ppm', lambda v: f"{v:.2f} ppm", 0.1, rng)
    df['sensor_id'] = df['sensor_id'].apply(lambda s: random_case(s, rng))
    df = insert_duplicates(df, how_many=7, rng=rng)
    add_numeric_spikes(df, 'aqi', 0.02, (0.4, 1.8), rng)
    return df


CORRUPTION_PIPELINE = {
    'company_travel_emissions_daily.csv': make_travel_messy,
    'company_production_emissions_daily.csv': make_production_messy,
    'company_energy_consumption_daily.csv': make_energy_daily_messy,
    'company_energy_mix_monthly.csv': make_energy_mix_messy,
    'company_water_usage_daily.csv': make_water_messy,
    'company_waste_monthly.csv': make_waste_messy,
    'factory_air_quality_daily.csv': make_air_quality_messy,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Generate messy ESG datasets from clean baselines.')
    parser.add_argument('--input-dir', type=Path, required=True, help='Directory containing clean CSV files.')
    parser.add_argument('--output-dir', type=Path, required=True, help='Destination for messy CSV files.')
    parser.add_argument('--seed', type=int, default=1234, help='Random seed for reproducibility.')
    parser.add_argument('--upload-gcs', type=str, help='Optional gs://bucket/prefix destination for uploading messy files.')
    return parser.parse_args()

def generate_messy_datasets(
    input_dir: Path,
    output_dir: Path,
    seed: int = 1234,
    upload_gcs: Optional[str] = None,
) -> List[Path]:
    rng = random.Random(seed)
    np.random.seed(seed)

    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory '{input_dir}' does not exist")

    output_dir.mkdir(parents=True, exist_ok=True)

    generated_files: List[Path] = []

    for filename, transformer in CORRUPTION_PIPELINE.items():
        source_path = input_dir / filename
        if not source_path.exists():
            print(f"[WARN] Missing source file: {source_path}")
            continue

        df = pd.read_csv(source_path, parse_dates=['date'])
        messy_df = transformer(df, rng)

        messy_path = output_dir / filename.replace('.csv', '_messy.csv')
        messy_df.to_csv(messy_path, index=False)
        generated_files.append(messy_path)
        print(f"Wrote messy dataset: {messy_path} ({len(messy_df)} rows)")

    if upload_gcs and generated_files:
        bucket_name, prefix = parse_gcs_uri(upload_gcs)
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        for path in generated_files:
            destination = f"{prefix}/{path.name}" if prefix else path.name
            blob = bucket.blob(destination)
            blob.upload_from_filename(path)
            print(f"Uploaded to gs://{bucket_name}/{destination}")

    return generated_files


def main() -> None:
    args = parse_args()
    generate_messy_datasets(args.input_dir, args.output_dir, args.seed, args.upload_gcs)


if __name__ == '__main__':
    main()