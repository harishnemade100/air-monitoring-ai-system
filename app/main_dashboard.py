# main_dashboard.py
import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px

from services.geoapify_service import get_place_id, get_zones
from services.map_service import create_map
from services.waqi_service import get_aqi, get_aqi_towers
from services.weather_service import get_weather
from services.forecast_service import get_aqi_forecast, plot_aqi_forecast, get_weather_forecast, plot_weather_forecast
from services.ai_agent_service import get_combined_advisory
from utils.color_utils import aqi_health_label
from setting.constants import OPENWEATHER_KEY, DEFAULT_COORDS, DEFAULT_CITY


def show_dashboard():
    # -------------------- PAGE SETUP --------------------
    st.set_page_config(page_title="🌍 Picmica-Pollution-Zones Analyzer", layout="wide")
    st.sidebar.title("City & Zone Selector")

    # -------------------- SIDEBAR INPUT --------------------
    city = st.sidebar.text_input("Enter City", DEFAULT_CITY)
    load_city = st.sidebar.button("Load City")

    if load_city:
        try:
            place_id, (lat, lon) = get_place_id(city)
            zones = get_zones(place_id)["features"]

            st.session_state["zones"] = zones
            st.session_state["city_coords"] = (lat, lon)
            st.session_state["city"] = city
        except Exception as e:
            st.error(f"Error loading city: {e}")

    # -------------------- DEFAULTS --------------------
    city_lat, city_lon = st.session_state.get("city_coords", DEFAULT_COORDS)
    city_name = st.session_state.get("city", DEFAULT_CITY)
    zones = st.session_state.get("zones", [])

    # -------------------- LIVE DATA --------------------
    city_aqi = get_aqi(city_lat, city_lon)
    city_weather = get_weather(city_lat, city_lon)
    aqi_status = aqi_health_label(city_aqi)
    status_color = "green" if aqi_status == "Good" else "orange" if aqi_status == "Moderate" else "red"

    # -------------------- TOP SUMMARY --------------------
    st.markdown(f"""
        <div style="font-size:26px; font-weight:800; text-align:center;">
            Picmica-Pollution-Zones Analyzer
        </div>
        <div style="font-size:22px; font-weight:700; text-align:center; margin-top:5px;">
            {city_name} – <span style="color:{status_color}">AQI Status: {aqi_status}</span>
        </div>
        <div style="font-size:20px; font-weight:500; text-align:center; margin-top:3px;">
            AQI: {city_aqi} | Temp: {city_weather['temp']} °C | Wind: {city_weather['wind']} m/s | Humidity: {city_weather['humidity']}%
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # -------------------- ZONE SELECTION --------------------
    selected_zone = None
    if zones:
        zone_names = [z["properties"].get("name", "Zone") for z in zones]
        selected_zone = st.sidebar.selectbox("Select Zone", zone_names)

    # -------------------- AQI TOWERS --------------------
    show_towers = st.sidebar.checkbox("Show City AQI Towers", value=False)
    towers = get_aqi_towers(city_name) if show_towers else []

    if towers:
        tower_list = []
        aqi_values = []
        for t in towers:
            name = t['station']['name']
            lat, lon = t['station']['geo']
            aqi = t['aqi'] if t['aqi'] != '-' else None
            if aqi:
                aqi_values.append(int(aqi))
            tower_list.append({
                "Station": name,
                "AQI": aqi,
                "Latitude": lat,
                "Longitude": lon
            })
        df_towers = pd.DataFrame(tower_list)
        avg_aqi = int(sum(aqi_values)/len(aqi_values)) if aqi_values else "N/A"
        dominant_pollutant = towers[0]['dominentpol'] if 'dominentpol' in towers[0] else "N/A"
    else:
        df_towers = pd.DataFrame()
        avg_aqi = dominant_pollutant = "N/A"

    # -------------------- LAYOUT --------------------
    left_col, right_col = st.columns([2, 1])

    # -------------------- LEFT: MAP --------------------
    with left_col:
        st.subheader("Interactive Map")
        if selected_zone:
            selected_feature = next((z for z in zones if z["properties"].get("name") == selected_zone), None)
            m = create_map(selected_feature, zones, show_towers=show_towers, city_name=city_name)
        else:
            m = create_map(all_features=zones, default_city_coords=(city_lat, city_lon), show_towers=show_towers, city_name=city_name)
        st_folium(m, width=800, height=600, key=f"map_{city_name}_{selected_zone}")

    # -------------------- RIGHT: SUMMARY --------------------
    with right_col:
        st.subheader("City AQI Tower Summary")
        st.markdown(f"**Average AQI:** {avg_aqi}")
        st.markdown(f"**Dominant Pollutant:** {dominant_pollutant.upper()}")

        if not df_towers.empty:
            pie_df = df_towers[df_towers["AQI"].notnull()]
            pie_df["AQI"] = pie_df["AQI"].astype(int)

            # Big Pie Chart
            fig = px.pie(
                pie_df,
                names="Station",
                values="AQI",
                color_discrete_sequence=px.colors.qualitative.Set3,
                title="Tower-wise AQI Distribution",
                width=700,
                height=700
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No AQI tower data available.")

    st.markdown("---")

    # -------------------- FORECASTS --------------------
    forecast_col1, forecast_col2 = st.columns(2)
    with forecast_col1:
        st.subheader("🌡 Weather Forecast (Next 24h)")
        weather_df = get_weather_forecast(city_lat, city_lon, OPENWEATHER_KEY)
        fig_weather = plot_weather_forecast(weather_df)
        fig_weather.update_layout(width=700, height=400)  # Bigger chart
        st.plotly_chart(fig_weather, use_container_width=True)

    with forecast_col2:
        st.subheader("📈 AQI Forecast (Past 12h + Next 12h)")
        aqi_df = get_aqi_forecast(city_lat, city_lon, city_aqi)
        fig_aqi = plot_aqi_forecast(aqi_df)
        fig_aqi.update_layout(width=700, height=400)  # Bigger chart
        st.plotly_chart(fig_aqi, use_container_width=True)

    # -------------------- AI + NEWS ADVISORY --------------------
    combined_advice = get_combined_advisory(
        city_name,
        selected_zone if selected_zone else "Entire City",
        city_aqi,
        city_weather['temp'],
        city_weather['humidity']
    )

    st.markdown(f"""
        <div style="
            background: linear-gradient(90deg, #a3d5ff, #007bff);
            color:white;
            padding:14px; 
            border-radius:10px; 
            font-weight:700;
            text-align:center;">
            🤖 AI + News Advisory: {combined_advice}
        </div>
    """, unsafe_allow_html=True)
