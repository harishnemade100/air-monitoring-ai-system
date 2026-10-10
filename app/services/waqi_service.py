"""WAQI (aqicn.org): live AQI from official monitoring stations."""
import streamlit as st

from setting.constants import CACHE_LIVE, WAQI_TOKEN
from utils.color_utils import to_int
from utils.http import get_json

BASE_URL = "https://api.waqi.info"


@st.cache_data(ttl=CACHE_LIVE, show_spinner=False)
def get_aqi_details(lat: float, lon: float) -> dict:
    """Nearest station's live AQI. Returns {} when unavailable."""
    data = get_json(f"{BASE_URL}/feed/geo:{lat};{lon}/", {"token": WAQI_TOKEN})
    if not data or data.get("status") != "ok":
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


def get_aqi(lat: float, lon: float):
    """Just the AQI number (or None)."""
    return get_aqi_details(lat, lon).get("aqi")


@st.cache_data(ttl=CACHE_LIVE, show_spinner=False)
def get_aqi_towers(city_name: str) -> list[dict]:
    """All monitoring stations matching the city name, as simple dicts."""
    data = get_json(f"{BASE_URL}/search/", {"token": WAQI_TOKEN, "keyword": city_name})
    if not data or data.get("status") != "ok":
        return []
    towers = []
    for t in data.get("data", []):
        geo = (t.get("station") or {}).get("geo") or []
        if len(geo) != 2:
            continue
        towers.append({
            "Station": t["station"].get("name", "Station"),
            "AQI": to_int(t.get("aqi")),
            "Latitude": geo[0],
            "Longitude": geo[1],
            "Updated": ((t.get("time") or {}).get("stime")) or "",
        })
    return towers
