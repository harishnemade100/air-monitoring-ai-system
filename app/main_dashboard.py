# main.py
def show_dashboard():
    import streamlit as st
    from streamlit_folium import st_folium
    from services.geoapify_service import get_place_id, get_zones
    from services.map_service import create_map
    from services.waqi_service import get_aqi
    from services.weather_service import get_weather
    from services.forecast_service import get_aqi_forecast, plot_aqi_forecast, get_weather_forecast, plot_weather_forecast
    from services.ai_agent_service import get_combined_advisory
    from utils.color_utils import aqi_health_label
    from setting.constants import OPENWEATHER_KEY, DEFAULT_COORDS, DEFAULT_CITY

    # -------------------- PAGE SETUP --------------------
    st.set_page_config(page_title="Live AQI & Weather Dashboard", layout="wide")
    st.sidebar.title("🌍 City & Zone Selector")

    # -------------------- SIDEBAR INPUT --------------------
    city = st.sidebar.text_input("Enter City", DEFAULT_CITY)

    if st.sidebar.button("Load City"):
        try:
            place_id, (lat, lon) = get_place_id(city)
            zones = get_zones(place_id)["features"]

            st.session_state["zones"] = zones
            st.session_state["city_coords"] = (lat, lon)
            st.session_state["city"] = city
        except Exception as e:
            st.error(f"Error: {e}")

    # -------------------- COORDINATES --------------------
    if "city_coords" in st.session_state:
        city_lat, city_lon = st.session_state["city_coords"]
        city_name = st.session_state["city"]
        zones = st.session_state.get("zones", [])
    else:
        city_lat, city_lon = DEFAULT_COORDS
        city_name = DEFAULT_CITY
        zones = []

    # -------------------- LIVE DATA --------------------
    city_aqi = get_aqi(city_lat, city_lon)
    city_weather = get_weather(city_lat, city_lon)
    aqi_status = aqi_health_label(city_aqi)
    status_color = "green" if aqi_status=="Good" else "orange" if aqi_status=="Moderate" else "red"

    # -------------------- TOP SUMMARY --------------------
    st.markdown(f"""
        <div style="font-size:22px; font-weight:700;">
            Zone Summary – {city_name} (<span style="color:{status_color}">Status: {aqi_status}</span>) .LIVE
        </div>
        <div style="font-size:18px; font-weight:500; padding-top:5px;">
            | AQI: {city_aqi} | Temp: {city_weather['temp']} °C | Wind: {city_weather['wind']} m/s | Humidity: {city_weather['humidity']}%
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # -------------------- ZONE DROPDOWN --------------------
    selected_zone = None
    if zones:
        zone_names = [z["properties"].get("name", "Zone") for z in zones]
        selected_zone = st.sidebar.selectbox("Select Zone", zone_names)

    # -------------------- MAP --------------------
    st.subheader(f"Interactive Map – {city_name}")
    if selected_zone:
        selected_feature = next((z for z in zones if z["properties"].get("name") == selected_zone), None)
        m = create_map(selected_feature, zones)
    else:
        m = create_map(all_features=zones, default_city_coords=(city_lat, city_lon))

    st_folium(m, width=750, height=400)

    st.markdown("---")

    # -------------------- FORECAST CHARTS --------------------
    left_col, right_col = st.columns(2)
    with left_col:
        st.subheader("🌡 Weather Forecast (Next 24h)")
        weather_df = get_weather_forecast(city_lat, city_lon, OPENWEATHER_KEY)
        fig_weather = plot_weather_forecast(weather_df)
        st.plotly_chart(fig_weather, use_container_width=True)
    with right_col:
        st.subheader("📈 AQI Forecast (Past 12h + Next 12h)")
        aqi_df = get_aqi_forecast(city_lat, city_lon, city_aqi)
        fig_aqi = plot_aqi_forecast(aqi_df)
        st.plotly_chart(fig_aqi, use_container_width=True)

    st.markdown("---")

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
            padding:12px; 
            border-radius:8px; 
            font-weight:600;
            animation: blink 1.5s infinite;">
            🤖 AI + News Advisory: {combined_advice}
        </div>
        <style>
            @keyframes blink {{0% {{opacity:1;}} 50% {{opacity:0.5;}} 100% {{opacity:1;}}}}
        </style>
    """, unsafe_allow_html=True)
