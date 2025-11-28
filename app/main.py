import streamlit as st
from streamlit_folium import st_folium

from services.geoapify_service import get_place_id, get_zones
from services.map_service import create_map
from services.waqi_service import get_aqi
from services.weather_service import get_weather


# ------------------------------------------------------------
# STREAMLIT PAGE SETTINGS
# ------------------------------------------------------------
st.set_page_config(page_title="Live AQI Zone Map", layout="wide")

st.sidebar.title("🌍 City & Zone Selector")


# ------------------------------------------------------------
# 1) CITY INPUT
# ------------------------------------------------------------
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


# ------------------------------------------------------------
# 2) SHOW UI ONLY IF CITY LOADED
# ------------------------------------------------------------
if "zones" in st.session_state:

    zones = st.session_state["zones"]
    zone_names = [z["properties"]["name"] for z in zones]

    selected_zone = st.sidebar.selectbox("Select Zone", zone_names)

    # find selected zone feature
    selected_feature = next(
        (x for x in zones if x["properties"]["name"] == selected_zone),
        zones[0]
    )

    # Extract coordinates for selected zone (centroid)
    geom = selected_feature["geometry"]
    lon, lat = geom["coordinates"][0][0] if geom["type"] == "Polygon" else (st.session_state["city_coords"])

    # ------------------------------------------------------------
    # FETCH AQI + WEATHER FOR SELECTED ZONE
    # ------------------------------------------------------------
    zone_aqi = get_aqi(lat, lon)
    zone_weather = get_weather(lat, lon)


    # ------------------------------------------------------------
    # BIG BOLD AQI SUMMARY (TOP)
    # ------------------------------------------------------------
    st.subheader(f"Zone Summary – {selected_zone}")

    st.markdown("""
        <style>
        .big-line {
            font-size: 26px;
            font-weight: 800;
            line-height: 1.6;
            white-space: nowrap;
            padding-top: 10px;
            padding-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="big-line">
            AQI: {zone_aqi} | Temp: {zone_weather['temp']} °C |
            Wind: {zone_weather['wind']} m/s | Humidity: {zone_weather['humidity']}%
        </div>
        """,
        unsafe_allow_html=True
    )

    # ------------------------------------------------------------
    # FORCE MAP BELOW AQI LINE
    # ------------------------------------------------------------
    st.markdown("<hr>", unsafe_allow_html=True)

    # ------------------------------------------------------------
    # MAP SECTION (FULL WIDTH BELOW)
    # ------------------------------------------------------------
    st.subheader("Interactive Zone Map")

    st.markdown("""
        <style>
        .map-container {
            border-radius: 12px;
            overflow: hidden;
            margin-top: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

    m = create_map(selected_feature, zones)

    st.markdown('<div class="map-container">', unsafe_allow_html=True)
    st_folium(m, width=1100, height=600)
    st.markdown('</div>', unsafe_allow_html=True)
