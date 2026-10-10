"""OpenWeatherMap: current weather and 5-day / 3-hour forecast."""
import pandas as pd
import streamlit as st

from setting.constants import CACHE_FORECAST, CACHE_LIVE, OPENWEATHER_KEY
from utils.http import get_json

BASE_URL = "https://api.openweathermap.org/data/2.5"


@st.cache_data(ttl=CACHE_LIVE, show_spinner=False)
def get_weather(lat: float, lon: float) -> dict:
    data = get_json(f"{BASE_URL}/weather", {"lat": lat, "lon": lon, "units": "metric", "appid": OPENWEATHER_KEY})
    if not data or "main" not in data:
        return {"temp": None, "humidity": None, "wind": None, "description": None, "feels_like": None}
    return {
        "temp": round(data["main"]["temp"], 1),
        "feels_like": round(data["main"].get("feels_like", data["main"]["temp"]), 1),
        "humidity": data["main"]["humidity"],
        "wind": data.get("wind", {}).get("speed"),
        "description": (data.get("weather") or [{}])[0].get("description", "").capitalize() or None,
    }


@st.cache_data(ttl=CACHE_FORECAST, show_spinner=False)
def get_weather_forecast(lat: float, lon: float) -> pd.DataFrame:
    """Next 5 days in 3-hour steps: temperature, humidity, wind, rain chance."""
    data = get_json(f"{BASE_URL}/forecast", {"lat": lat, "lon": lon, "units": "metric", "appid": OPENWEATHER_KEY})
    if not data or "list" not in data:
        return pd.DataFrame()
    offset = pd.Timedelta(seconds=(data.get("city") or {}).get("timezone", 0))
    return pd.DataFrame([{
        "datetime": pd.to_datetime(x["dt"], unit="s") + offset,   # local time of the city
        "Temp": x["main"]["temp"],
        "Humidity": x["main"]["humidity"],
        "Wind": x.get("wind", {}).get("speed"),
        "Rain chance": round(100 * x.get("pop", 0)),
    } for x in data["list"]])
