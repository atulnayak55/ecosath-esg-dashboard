"""Clean messy ESG datasets and output normalized tables.

Supports local paths and Google Cloud Storage URIs (gs://bucket/prefix).
Each dataset is converted back to a tidy daily/monthly time series with
consistent units and derived fields recomputed where appropriate.
"""

from __future__ import annotations

import argparse
import io
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterable, Tuple

import numpy as np
import pandas as pd
from google.cloud import storage


@dataclass
class DatasetHandler:
    input_name: str
    output_name: str
    frequency: str
    cleaner: Callable[[pd.DataFrame], pd.DataFrame]


def parse_uri(uri: str) -> Tuple[str, str]:
    if uri.startswith('gs://'):
        without_scheme = uri[5:]
        if '/' in without_scheme:
            bucket, prefix = without_scheme.split('/', 1)
        else:
            bucket, prefix = without_scheme, ''
        return bucket, prefix.rstrip('/')
    return '', uri


NUMERIC_RE = re.compile(r"[-+]?\d*\.?\d+")


def _extract_number(text: str) -> float:
    match = NUMERIC_RE.search(text.replace(',', ''))
    return float(match.group()) if match else np.nan


def parse_numeric(series: pd.Series, unit_map: Dict[str, float] | None = None, percent: bool = False) -> pd.Series:
    def convert(value) -> float:
        if pd.isna(value):
            return np.nan
        text = str(value)
        factor = 1.0
        if unit_map:
            text_lower = text.lower()
            for key, multiplier in unit_map.items():
                if key in text_lower:
                    factor = multiplier
                    break
        num = _extract_number(text)
        if np.isnan(num):
            return np.nan
        if percent:
            return num / 100.0
        return num * factor

    return series.apply(convert)


def finalize_time_series(df: pd.DataFrame, frequency: str, integer_cols: Iterable[str] = ()) -> pd.DataFrame:
    df = df.sort_values('date').drop_duplicates(subset='date', keep='last').set_index('date')
    full_index = pd.date_range(df.index.min(), df.index.max(), freq=frequency)
    df = df.reindex(full_index)
    df.index.name = 'date'
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_cols:
        df[numeric_cols] = df[numeric_cols].interpolate(limit_direction='both')
        df[numeric_cols] = df[numeric_cols].bfill().ffill()
    non_numeric_cols = [col for col in df.columns if col not in numeric_cols]
    for col in non_numeric_cols:
        df[col] = df[col].ffill().bfill()
    for col in integer_cols:
        if col in df.columns:
            df[col] = np.round(df[col]).astype(int)
    return df.reset_index()


def clean_travel(df: pd.DataFrame) -> pd.DataFrame:
    df['date'] = pd.to_datetime(df['date'])
    default = pd.Series(np.nan, index=df.index)
    df['flights'] = parse_numeric(df.get('flights', default), percent=False).round()
    df['road_trips'] = parse_numeric(df.get('road_trips', default), percent=False).round()
    df['total_distance_km'] = parse_numeric(df.get('total_distance_km', default))
    df['travel_tco2e'] = parse_numeric(df.get('travel_tco2e', default), unit_map={'tco2e': 1.0})
    df['data_quality_score'] = pd.to_numeric(df.get('data_quality_score', default), errors='coerce').clip(0, 1)
    df['source_tag'] = 'synthetic_travel_v1_cleaned'
    df = finalize_time_series(df[['date', 'flights', 'road_trips', 'total_distance_km', 'travel_tco2e', 'data_quality_score', 'source_tag']], 'D', integer_cols=['flights', 'road_trips'])
    return df


def clean_production(df: pd.DataFrame) -> pd.DataFrame:
    df['date'] = pd.to_datetime(df['date'])
    default = pd.Series(np.nan, index=df.index)
    units = parse_numeric(df.get('production_units', default))
    intensity = parse_numeric(df.get('emission_intensity_tco2e_per_unit', default))
    emissions = parse_numeric(df.get('production_tco2e', default))
    emissions = emissions.where(~emissions.isna(), units * intensity)
    df_clean = pd.DataFrame({
        'date': df['date'],
        'production_units': units,
        'emission_intensity_tco2e_per_unit': intensity,
        'production_tco2e': emissions,
    'data_quality_score': pd.to_numeric(df.get('data_quality_score', default), errors='coerce').clip(0, 1),
        'source_tag': 'synthetic_production_v1_cleaned'
    })
    df_clean = finalize_time_series(df_clean, 'D', integer_cols=['production_units'])
    df_clean['production_tco2e'] = df_clean['production_units'] * df_clean['emission_intensity_tco2e_per_unit']
    return df_clean


def clean_energy_daily(df: pd.DataFrame) -> pd.DataFrame:
    df['date'] = pd.to_datetime(df['date'])
    default = pd.Series(np.nan, index=df.index)
    electricity = parse_numeric(df.get('electricity_kwh', default), unit_map={'mwh': 1000.0, 'kwh': 1.0})
    gas = parse_numeric(df.get('natural_gas_mwh', default), unit_map={'mwh': 1.0})
    renewables = parse_numeric(df.get('renewables_onsite_kwh', default), unit_map={'mwh': 1000.0, 'kwh': 1.0})
    peak_kw = parse_numeric(df.get('peak_demand_kw', default), unit_map={'mw': 1000.0, 'kw': 1.0})
    df_clean = pd.DataFrame({
        'date': df['date'],
        'electricity_kwh': electricity,
        'natural_gas_mwh': gas,
        'renewables_onsite_kwh': renewables,
        'peak_demand_kw': peak_kw,
    'data_quality_score': pd.to_numeric(df.get('data_quality_score', default), errors='coerce').clip(0, 1),
        'source_tag': 'synthetic_energy_v1_cleaned'
    })
    df_clean = finalize_time_series(df_clean, 'D')
    return df_clean


def clean_energy_mix(df: pd.DataFrame) -> pd.DataFrame:
    df['date'] = pd.to_datetime(df['date'])
    default = pd.Series(np.nan, index=df.index)
    renewable = parse_numeric(df.get('renewable_share', default), percent=True)
    non_renewable = parse_numeric(df.get('non_renewable_share', default), percent=True)
    df_clean = pd.DataFrame({
        'date': df['date'],
        'renewable_share': renewable,
        'non_renewable_share': non_renewable,
        'source_tag': 'synthetic_energy_mix_v1_cleaned'
    })
    df_clean = finalize_time_series(df_clean, 'MS')
    df_clean['non_renewable_share'] = 1 - df_clean['renewable_share']
    df_clean[['renewable_share', 'non_renewable_share']] = df_clean[['renewable_share', 'non_renewable_share']].clip(0, 1)
    return df_clean


def clean_water(df: pd.DataFrame) -> pd.DataFrame:
    df['date'] = pd.to_datetime(df['date'])
    default = pd.Series(np.nan, index=df.index)
    withdrawn = parse_numeric(df.get('water_withdrawn_m3', default), unit_map={'l': 1 / 1000.0})
    recycled = parse_numeric(df.get('water_recycled_m3', default), unit_map={'l': 1 / 1000.0})
    discharge = parse_numeric(df.get('water_discharge_m3', default), unit_map={'l': 1 / 1000.0})
    df_clean = pd.DataFrame({
        'date': df['date'],
        'water_withdrawn_m3': withdrawn,
        'water_recycled_m3': recycled,
        'water_discharge_m3': discharge,
        'data_quality_score': pd.to_numeric(df.get('data_quality_score', default), errors='coerce').clip(0, 1),
        'source_tag': 'synthetic_water_v1_cleaned'
    })
    df_clean = finalize_time_series(df_clean, 'D')
    df_clean['water_recycled_rate'] = (df_clean['water_recycled_m3'] / df_clean['water_withdrawn_m3']).replace([np.inf, -np.inf], np.nan)
    df_clean['water_recycled_rate'] = df_clean['water_recycled_rate'].clip(0, 1).fillna(0)
    return df_clean


def clean_waste(df: pd.DataFrame) -> pd.DataFrame:
    df['date'] = pd.to_datetime(df['date'])
    default = pd.Series(np.nan, index=df.index)
    hazardous = parse_numeric(df.get('hazardous_waste_tons', default), unit_map={'kg': 1 / 1000.0, 't': 1.0})
    non_hazardous = parse_numeric(df.get('non_hazardous_waste_tons', default), unit_map={'kg': 1 / 1000.0, 't': 1.0})
    recycled_fraction = parse_numeric(df.get('recycled_fraction', default), percent=True)
    df_clean = pd.DataFrame({
        'date': df['date'],
        'hazardous_waste_tons': hazardous,
        'non_hazardous_waste_tons': non_hazardous,
        'recycled_fraction': recycled_fraction,
        'source_tag': 'synthetic_waste_v1_cleaned'
    })
    df_clean = finalize_time_series(df_clean, 'MS')
    df_clean['recycled_tons'] = df_clean['non_hazardous_waste_tons'] * df_clean['recycled_fraction']
    df_clean['landfill_tons'] = df_clean['non_hazardous_waste_tons'] - df_clean['recycled_tons']
    return df_clean


def clean_air_quality(df: pd.DataFrame) -> pd.DataFrame:
    df['date'] = pd.to_datetime(df['date'])
    default = pd.Series(np.nan, index=df.index)
    aqi = parse_numeric(df.get('aqi', default))
    pm25 = parse_numeric(df.get('pm25_ugm3', default))
    pm10 = parse_numeric(df.get('pm10_ugm3', default))
    no2 = parse_numeric(df.get('no2_ppb', default))
    co = parse_numeric(df.get('co_ppm', default))
    sensor_series = df.get('sensor_id')
    if sensor_series is None:
        sensor_series = pd.Series('factory-monitor-01', index=df.index)
    else:
        sensor_series = sensor_series.fillna('factory-monitor-01')

    df_clean = pd.DataFrame({
        'date': df['date'],
        'aqi': aqi,
        'pm25_ugm3': pm25,
        'pm10_ugm3': pm10,
        'no2_ppb': no2,
        'co_ppm': co,
        'sensor_id': sensor_series.astype(str),
        'data_quality_score': pd.to_numeric(df.get('data_quality_score', default), errors='coerce').clip(0, 1),
        'source_tag': 'synthetic_air_quality_v1_cleaned'
    })
    df_clean = finalize_time_series(df_clean, 'D')
    df_clean[['aqi', 'pm25_ugm3', 'pm10_ugm3', 'no2_ppb', 'co_ppm']] = df_clean[['aqi', 'pm25_ugm3', 'pm10_ugm3', 'no2_ppb', 'co_ppm']].clip(lower=0)
    return df_clean


HANDLERS = [
    DatasetHandler('company_travel_emissions_daily_messy.csv', 'company_travel_emissions_daily_clean.csv', 'D', clean_travel),
    DatasetHandler('company_production_emissions_daily_messy.csv', 'company_production_emissions_daily_clean.csv', 'D', clean_production),
    DatasetHandler('company_energy_consumption_daily_messy.csv', 'company_energy_consumption_daily_clean.csv', 'D', clean_energy_daily),
    DatasetHandler('company_energy_mix_monthly_messy.csv', 'company_energy_mix_monthly_clean.csv', 'MS', clean_energy_mix),
    DatasetHandler('company_water_usage_daily_messy.csv', 'company_water_usage_daily_clean.csv', 'D', clean_water),
    DatasetHandler('company_waste_monthly_messy.csv', 'company_waste_monthly_clean.csv', 'MS', clean_waste),
    DatasetHandler('factory_air_quality_daily_messy.csv', 'factory_air_quality_daily_clean.csv', 'D', clean_air_quality),
]


def download_dataframe(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def download_gcs_dataframe(client: storage.Client, bucket_name: str, blob_name: str) -> pd.DataFrame:
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    data = blob.download_as_bytes()
    return pd.read_csv(io.BytesIO(data))


def upload_dataframe(df: pd.DataFrame, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(destination, index=False)


def upload_gcs_dataframe(client: storage.Client, bucket_name: str, blob_name: str, df: pd.DataFrame) -> None:
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_string(df.to_csv(index=False), content_type='text/csv')


def run_local(input_dir: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for handler in HANDLERS:
        source_path = input_dir / handler.input_name
        if not source_path.exists():
            print(f"[WARN] Missing local file: {source_path}")
            continue
        df = download_dataframe(source_path)
        cleaned = handler.cleaner(df)
        upload_dataframe(cleaned, output_dir / handler.output_name)
        print(f"Wrote cleaned dataset: {output_dir / handler.output_name} ({len(cleaned)} rows)")


def run_gcs(source_uri: str, target_uri: str) -> None:
    src_bucket, src_prefix = parse_uri(source_uri)
    tgt_bucket, tgt_prefix = parse_uri(target_uri)
    client = storage.Client()

    for handler in HANDLERS:
        blob_name = '/'.join(filter(None, [src_prefix, handler.input_name]))
        try:
            df = download_gcs_dataframe(client, src_bucket, blob_name)
        except Exception as exc:
            print(f"[WARN] Failed to download gs://{src_bucket}/{blob_name}: {exc}")
            continue
        cleaned = handler.cleaner(df)
        target_blob = '/'.join(filter(None, [tgt_prefix, handler.output_name]))
        upload_gcs_dataframe(client, tgt_bucket, target_blob, cleaned)
        print(f"Uploaded cleaned dataset: gs://{tgt_bucket}/{target_blob} ({len(cleaned)} rows)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Clean messy ESG datasets and upload normalized outputs.')
    parser.add_argument('--input-uri', required=True, help='Input directory or gs://bucket/prefix containing messy CSV files.')
    parser.add_argument('--output-uri', required=True, help='Output directory or gs://bucket/prefix for cleaned CSV files.')
    return parser.parse_args()


def clean_datasets(input_uri: str, output_uri: str) -> None:
    if input_uri.startswith('gs://') and output_uri.startswith('gs://'):
        run_gcs(input_uri, output_uri)
    else:
        run_local(Path(input_uri), Path(output_uri))


def main() -> None:
    args = parse_args()
    clean_datasets(args.input_uri, args.output_uri)


if __name__ == '__main__':
    main()
