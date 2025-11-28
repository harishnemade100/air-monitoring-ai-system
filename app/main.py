# main.py
import streamlit as st
from streamlit_folium import st_folium
from datetime import datetime
from services.geoapify_service import get_place_id, get_zones
from services.map_service import create_map
from services.waqi_service import get_aqi
from utils.color_utils import aqi_health_label
from services.weather_service import get_weather
from services.forecast_service import get_aqi_forecast, plot_aqi_forecast, get_weather_forecast, plot_weather_forecast

# ---------------- STREAMLIT SETTINGS ----------------
st.set_page_config(page_title="Live AQI & Weather Dashboard", layout="wide")
st.sidebar.title("🌍 City & Zone Selector")

# ---------------- CITY INPUT ----------------
city = st.sidebar.text_input("Enter City", "Pune")

if st.sidebar.button("Load City"):
    try:
        place_id, (lat, lon) = get_place_id(city)
        zones = get_zones(place_id)["features"]

        st.session_state["zones"] = zones
        st.session_state["city_coords"] = (lat, lon)
        st.session_state["city"] = city

    except Exception as e:
        st.error(f"Error: {e}")

if "zones" in st.session_state:

    zones = st.session_state["zones"]
    zone_names = [z["properties"]["name"] for z in zones]
    selected_zone = st.sidebar.selectbox("Select Zone", zone_names)

    selected_feature = next(
        (x for x in zones if x["properties"]["name"] == selected_zone),
        zones[0]
    )

    geom = selected_feature["geometry"]
    lon, lat = geom["coordinates"][0][0] if geom["type"] == "Polygon" else st.session_state["city_coords"]

    # ---------------- FETCH LIVE AQI & WEATHER ----------------
    zone_aqi = get_aqi(lat, lon)
    zone_weather = get_weather(lat, lon)
    aqi_status = aqi_health_label(zone_aqi)

    # ---------------- TOP: FULL WIDTH SUMMARY ----------------
    st.markdown("""
        <style>
        .zone-summary {
            font-size: 24px;
            font-weight: 800;
            padding: 10px 0;
        }
        .live-label {
            color: red;
            font-weight: 900;
            animation: blink 1s infinite;
        }
        @keyframes blink {
            0% { opacity: 1; }
            50% { opacity: 0; }
            100% { opacity: 1; }
        }
        .status-good {color: green;}
        .status-moderate {color: orange;}
        .status-unhealthy {color: red;}
        </style>
    """, unsafe_allow_html=True)

    # Determine color class for AQI status
    status_class = (
        "status-good" if aqi_status=="Good" else
        "status-moderate" if aqi_status=="Moderate" else
        "status-unhealthy"
    )

    # Top line: Zone + Status + LIVE blinking
    st.markdown(f"""
        <div class="zone-summary">
            Zone Summary – {selected_zone} (<span class="{status_class}">Status: {aqi_status}</span>) 
            <span class="live-label">.LIVE</span>
        </div>
    """, unsafe_allow_html=True)

    # Below line: AQI, Temp, Wind, Humidity
    st.markdown(f"""
        <div class="zone-summary">
            | AQI: {zone_aqi} | Temp: {zone_weather['temp']} °C | Wind: {zone_weather['wind']} m/s | Humidity: {zone_weather['humidity']}%
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ---------------- BELOW: SPLIT LAYOUT ----------------
    left_col, right_col = st.columns([1.5, 1])

    # ---------------- LEFT: MAP ----------------
    with left_col:
        st.subheader("Interactive Zone Map")
        m = create_map(selected_feature, zones)
        st_folium(m, width=700, height=500)

    # ---------------- RIGHT: FORECAST CHARTS ----------------
    with right_col:
        st.subheader("📈 AQI Forecast (Past 12h + Next 12h)")
        aqi_df = get_aqi_forecast(lat, lon, zone_aqi)
        fig_aqi = plot_aqi_forecast(aqi_df)
        st.plotly_chart(fig_aqi, use_container_width=True)

        st.markdown("---")

        st.subheader("🌡 Weather Forecast (Next 24h)")
        OPENWEATHER_KEY = "be0eee25ce9b61255d720e187b17bf61"
        weather_df = get_weather_forecast(lat, lon, OPENWEATHER_KEY)
        fig_weather = plot_weather_forecast(weather_df)
        st.plotly_chart(fig_weather, use_container_width=True)
