"""
App settings.

API keys and the database URL are NOT stored in code. They are read from Streamlit
secrets (Settings -> Secrets on Streamlit Cloud, or .streamlit/secrets.toml locally),
with environment variables as a fallback.
"""
import os

import streamlit as st


def _secret(name: str, default: str = "") -> str:
    try:
        value = st.secrets.get(name)
        if value:
            return str(value)
    except Exception:  # no secrets file configured
        pass
    return os.getenv(name, default)


# ---------------- API KEYS (from secrets) ----------------
WAQI_TOKEN = _secret("WAQI_TOKEN")              # https://aqicn.org/data-platform/token/
OPENWEATHER_KEY = _secret("OPENWEATHER_KEY")    # https://openweathermap.org/api
GEOAPIFY_KEY = _secret("GEOAPIFY_KEY")          # https://www.geoapify.com/
GROQ_API_KEY = _secret("GROQ_API_KEY")          # optional, https://console.groq.com
LLM_MODEL = _secret("LLM_MODEL", "openai/gpt-oss-120b")
DATABASE_URL = _secret("DATABASE_URL")          # Neon / Supabase PostgreSQL URL

REQUIRED_SECRETS = {
    "WAQI_TOKEN": WAQI_TOKEN,
    "OPENWEATHER_KEY": OPENWEATHER_KEY,
    "GEOAPIFY_KEY": GEOAPIFY_KEY,
    "DATABASE_URL": DATABASE_URL,
}

# ---------------- DEFAULTS ----------------
APP_TITLE = "Air Monitoring AI System"
DEFAULT_CITY = "Pune"
DEFAULT_COORDS = (18.5204, 73.8567)  # Pune city
REQUEST_TIMEOUT = 15                 # seconds for every API call

# Cache times (seconds): how long API results are reused before fetching again
CACHE_LIVE = 10 * 60        # live AQI / weather
CACHE_FORECAST = 30 * 60    # forecasts
CACHE_STATIC = 24 * 60 * 60 # city boundaries, geocoding

# Major Indian cities for the "Compare cities" tab (lat, lon)
INDIAN_CITIES = {
    "Delhi": (28.6139, 77.2090),
    "Mumbai": (19.0760, 72.8777),
    "Kolkata": (22.5726, 88.3639),
    "Chennai": (13.0827, 80.2707),
    "Bengaluru": (12.9716, 77.5946),
    "Hyderabad": (17.3850, 78.4867),
    "Pune": (18.5204, 73.8567),
    "Ahmedabad": (23.0225, 72.5714),
    "Jaipur": (26.9124, 75.7873),
    "Lucknow": (26.8467, 80.9462),
    "Kanpur": (26.4499, 80.3319),
    "Nagpur": (21.1458, 79.0882),
    "Patna": (25.5941, 85.1376),
    "Chandigarh": (30.7333, 76.7794),
    "Bhopal": (23.2599, 77.4126),
    "Guwahati": (26.1445, 91.7362),
}

# Health profiles used for personalised advice
HEALTH_PROFILES = [
    "General public",
    "Children",
    "Elderly (60+)",
    "Asthma / lung condition",
    "Heart condition",
    "Pregnant",
    "Outdoor worker / athlete",
]
