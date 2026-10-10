"""WAQI (aqicn.org): live AQI from official monitoring stations."""
import math
from concurrent.futures import ThreadPoolExecutor

import streamlit as st

from setting.constants import CACHE_LIVE, WAQI_TOKEN
from utils.color_utils import to_int
from utils.http import get_json

BASE_URL = "https://api.waqi.info"
MAX_DISTANCE_KM = 60   # ignore stations farther than this from the city centre


def distance_km(lat1, lon1, lat2, lon2) -> float:
    """Great-circle distance between two points (haversine)."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(a))


def _parse_feed(data) -> dict:
    if not data or data.get("status") != "ok" or not isinstance(data.get("data"), dict):
        return {}
    d = data["data"]
    pollutants = {k: v.get("v") for k, v in (d.get("iaqi") or {}).items()
                  if k in ("pm25", "pm10", "no2", "o3", "so2", "co")}
    return {
        "aqi": to_int(d.get("aqi")),
        "dominant": (d.get("dominentpol") or "").upper() or None,
        "station": (d.get("city") or {}).get("name"),
        "time": (d.get("time") or {}).get("s"),
        "pollutants": pollutants,
    }


@st.cache_data(ttl=CACHE_LIVE, show_spinner=False)
def get_aqi_details(lat: float, lon: float) -> dict:
    """Nearest station's live AQI. Returns {} when unavailable."""
    return _parse_feed(get_json(f"{BASE_URL}/feed/geo:{lat};{lon}/", {"token": WAQI_TOKEN}))


def get_aqi(lat: float, lon: float):
    """Just the AQI number (or None)."""
    return get_aqi_details(lat, lon).get("aqi")


@st.cache_data(ttl=CACHE_LIVE, show_spinner=False)
def get_station_aqi(uid: int):
    """Live AQI of one station by its WAQI id (used when search results show '-')."""
    return _parse_feed(get_json(f"{BASE_URL}/feed/@{uid}/", {"token": WAQI_TOKEN})).get("aqi")


@st.cache_data(ttl=CACHE_LIVE, show_spinner=False)
def get_aqi_towers(city_name: str, city_lat: float, city_lon: float) -> list[dict]:
    """Monitoring stations near the city.

    1. Search WAQI by city name, keep only stations within MAX_DISTANCE_KM of the city
       (the name search also matches far-away places, e.g. 'Pune' -> 'Punteras, Chile').
    2. Stations whose search result has no AQI ('-') are looked up individually.
    """
    data = get_json(f"{BASE_URL}/search/", {"token": WAQI_TOKEN, "keyword": city_name})
    if not data or data.get("status") != "ok":
        return []

    towers = []
    for t in data.get("data", []):
        geo = (t.get("station") or {}).get("geo") or []
        if len(geo) != 2:
            continue
        lat, lon = float(geo[0]), float(geo[1])
        km = distance_km(city_lat, city_lon, lat, lon)
        if km > MAX_DISTANCE_KM:
            continue
        towers.append({
            "Station": t["station"].get("name", "Station"),
            "AQI": to_int(t.get("aqi")),
            "Source": "Station",
            "Distance (km)": round(km, 1),
            "Latitude": lat,
            "Longitude": lon,
            "Updated": ((t.get("time") or {}).get("stime")) or "",
            "uid": t.get("uid"),
        })

    # Fill missing values from each station's own live feed (in parallel)
    missing = [t for t in towers if t["AQI"] is None and t["uid"] is not None]
    if missing:
        with ThreadPoolExecutor(max_workers=8) as pool:
            for tower, aqi in zip(missing, pool.map(lambda t: get_station_aqi(t["uid"]), missing)):
                tower["AQI"] = aqi
    return towers
