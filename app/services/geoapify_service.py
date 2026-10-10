"""Geoapify: find a city and its administrative zones (wards/areas)."""
import streamlit as st

from setting.constants import CACHE_STATIC, GEOAPIFY_KEY
from utils.http import get_json


@st.cache_data(ttl=CACHE_STATIC, show_spinner=False)
def get_place_id(city: str):
    data = get_json("https://api.geoapify.com/v1/geocode/search",
                    {"text": city, "type": "city", "limit": 1, "apiKey": GEOAPIFY_KEY})
    if not data or not data.get("features"):
        raise ValueError(f"City '{city}' not found")
    feature = data["features"][0]
    lon, lat = feature["geometry"]["coordinates"]
    return feature["properties"]["place_id"], (lat, lon)


@st.cache_data(ttl=CACHE_STATIC, show_spinner=False)
def get_zones(place_id: str) -> dict:
    data = get_json("https://api.geoapify.com/v1/boundaries/consists-of",
                    {"id": place_id, "boundary": "administrative", "geometry": "geometry_1000",
                     "apiKey": GEOAPIFY_KEY})
    return data or {"features": []}
