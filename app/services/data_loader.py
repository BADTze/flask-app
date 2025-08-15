import datetime
import requests
import pandas as pd
import numpy as np
from scipy.stats import zscore
from app import cache
from flask import current_app

# Rentang waktu untuk ambil dan proses data
def get_date_range():
    now = datetime.datetime.now()
    current_year = now.year
    start_year = current_year - 3     
    end_year = current_year          
    process_until = current_year - 1  
    return start_year, end_year, process_until

# Bangun URL API
def build_api_url():
    start_year, end_year, _ = get_date_range()
    return (
        f"http://10.10.2.70:3008/api/energy-emission/energy"
        f"?start_year={start_year}&end_year={end_year}"
        f"&start_month=01&end_month=12&is_emission=false"
    )

# Ambil data mentah dari API
@cache.memoize(timeout=3600)
def fetch_api_data():
    url = build_api_url()
    try:
        response = requests.get(url, timeout=90)
        response.raise_for_status()
        data = response.json()
        trend_data = data.get("data", {}).get("trendData", [])
        all_data = next((item for item in trend_data if item.get("line") == "All"), None)
        return all_data.get("data", []) if all_data else []
    
    except requests.exceptions.Timeout:
        current_app.logger.error("[❌] Failed fetching data from API: Read timed out after 60 seconds.")
        return None
    except Exception as e:
        current_app.logger.error(f"[❌] Failed fetching data from API: {e}")
        return None

# Proses data menjadi DataFrame
def process_raw_data(column_name: str = "indexEnergy", z_threshold: float = 3.0) -> pd.DataFrame:
    raw_data = fetch_api_data()
    if not raw_data:
        current_app.logger.warning("[⚠️] No raw data returned from API.")
        return pd.DataFrame()

    _, _, process_until = get_date_range()
    last_valid_date = datetime.datetime(process_until, 12, 31)

    clean_data = []
    for item in raw_data:
        try:
            year = int(item.get("year"))
            month = int(item.get("month"))
            val = item.get("values", {}).get(column_name)

            if val is None:
                continue

            date_obj = datetime.datetime(year=year, month=month, day=1)
            if date_obj > last_valid_date:
                continue

            clean_data.append({"ds": date_obj, "y": float(val)})
        except Exception as e:
            current_app.logger.warning(f"[⚠️] Skipping invalid entry: {e}")
            continue

    df = pd.DataFrame(clean_data)

    if df.empty:
        current_app.logger.warning(f"[⚠️] No valid data found for '{column_name}'")
        return df

    df = df.sort_values('ds').reset_index(drop=True)
    df['y'] = df['y'].replace(0, np.nan)

    # Hitung Z-score (pastikan hanya untuk nilai non-NaN)
    z_scores = pd.Series(zscore(df['y'].dropna()), index=df['y'].dropna().index)

    outlier_mask = pd.Series(False, index=df.index)
    outlier_mask[z_scores.index] = z_scores.abs() > z_threshold

    if outlier_mask.any():
        current_app.logger.warning(
            f"[⚠️] Detected {outlier_mask.sum()} outlier(s) in '{column_name}' using Z-score > {z_threshold}."
        )
        df.loc[outlier_mask, 'y'] = np.nan

    # Interpolasi nilai hilang
    df['y'] = df['y'].interpolate(method='linear').fillna(method='bfill').fillna(method='ffill')

    if len(df) < 6:
        current_app.logger.warning(f"[⚠️] Too little data to forecast: '{column_name}'")
        return pd.DataFrame()

    return df

def load_actual_data(category: str) -> pd.DataFrame:
    return process_raw_data(column_name=category)
