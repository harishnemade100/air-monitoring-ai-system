"""
Open-Meteo Air Quality API (free, no API key needed).

Gives REAL hourly pollution history and forecast (replaces the old simulated AQI forecast),
pollutant concentrations, and current AQI for many cities in one request.
Docs: https://open-meteo.com/en/docs/air-quality-api
"""
import pandas as pd
import streamlit as st

from setting.constants import CACHE_FORECAST, CACHE_LIVE
from utils.color_utils import india_aqi
from utils.http import get_json

BASE_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
POLLUTANTS = {
    "pm2_5": "PM2.5", "pm10": "PM10", "nitrogen_dioxide": "NO₂",
    "ozone": "O₃", "sulphur_dioxide": "SO₂", "carbon_monoxide": "CO",
}


@st.cache_data(ttl=CACHE_FORECAST, show_spinner=False)
def get_hourly_air_quality(lat: float, lon: float, past_days: int = 2, forecast_days: int = 4) -> pd.DataFrame:
    """Hourly US AQI, pollutants and India NAQI (24-hour rolling average, as CPCB defines it)."""
    data = get_json(BASE_URL, {
        "latitude": lat, "longitude": lon,
        "hourly": ",".join(["us_aqi", *POLLUTANTS]),
        "past_days": past_days, "forecast_days": forecast_days, "timezone": "auto",
    })
    if not data or "hourly" not in data:
        return pd.DataFrame()

    df = pd.DataFrame(data["hourly"]).rename(columns={"time": "datetime", "us_aqi": "US AQI", **POLLUTANTS})
    df["datetime"] = pd.to_datetime(df["datetime"])
    pm25_24h = df["PM2.5"].rolling(24, min_periods=12).mean()
    pm10_24h = df["PM10"].rolling(24, min_periods=12).mean()
    df["India AQI"] = [india_aqi(a, b)[0] for a, b in zip(pm25_24h, pm10_24h)]
    df.attrs["now"] = pd.Timestamp.now(tz=data.get("timezone") or "UTC").tz_localize(None).floor("h")
    return df


@st.cache_data(ttl=CACHE_LIVE, show_spinner=False)
def get_current_for_cities(cities: dict) -> pd.DataFrame:
    """Current US AQI, PM2.5 and PM10 for many cities (one request)."""
    names = list(cities)
    data = get_json(BASE_URL, {
        "latitude": ",".join(str(cities[n][0]) for n in names),
        "longitude": ",".join(str(cities[n][1]) for n in names),
        "current": "us_aqi,pm2_5,pm10", "timezone": "auto",
    })
    if data is None:
        return pd.DataFrame()
    results = data if isinstance(data, list) else [data]

    rows = []
    for name, item in zip(names, results):
        current = (item or {}).get("current") or {}
        pm25, pm10 = current.get("pm2_5"), current.get("pm10")
        rows.append({
            "City": name,
            "US AQI": current.get("us_aqi"),
            "India AQI (est.)": india_aqi(pm25, pm10)[0],
            "PM2.5": pm25,
            "PM10": pm10,
            "Latitude": cities[name][0],
            "Longitude": cities[name][1],
        })
    return pd.DataFrame(rows).dropna(subset=["US AQI"]).sort_values("US AQI").reset_index(drop=True)


@st.cache_data(ttl=CACHE_LIVE, show_spinner=False)
def get_current_us_aqi_at(points: tuple) -> list:
    """Current modelled US AQI at each (lat, lon) point, in the same order (None if unavailable).
    Used to fill monitoring stations that have no live reading."""
    if not points:
        return []
    data = get_json(BASE_URL, {
        "latitude": ",".join(str(round(p[0], 4)) for p in points),
        "longitude": ",".join(str(round(p[1], 4)) for p in points),
        "current": "us_aqi", "timezone": "auto",
    })
    if data is None:
        return [None] * len(points)
    results = data if isinstance(data, list) else [data]
    values = [((item or {}).get("current") or {}).get("us_aqi") for item in results]
    return (values + [None] * len(points))[: len(points)]
