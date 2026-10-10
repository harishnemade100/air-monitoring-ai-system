"""Main dashboard (shown after login)."""
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from services.ai_agent_service import get_ai_advisory, get_pollution_news
from services.air_quality_service import POLLUTANTS, get_current_for_cities, get_hourly_air_quality
from services.forecast_service import (plot_aqi_trend, plot_city_comparison, plot_pollutants,
                                       plot_station_bars, plot_weather_forecast)
from services.geoapify_service import get_place_id, get_zones
from services.health_service import best_time_windows, daily_outlook, health_advice, outdoor_score
from services.map_service import create_comparison_map, create_map
from services.user_service import list_saved_cities, remove_city, save_city, update_preferences
from services.waqi_service import get_aqi_details, get_aqi_towers
from services.weather_service import get_weather, get_weather_forecast
from setting.constants import APP_TITLE, DEFAULT_CITY, DEFAULT_COORDS, HEALTH_PROFILES, INDIAN_CITIES
from utils.color_utils import aqi_color, aqi_health_label, naqi_category, to_int


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _fmt(value, unit="", digits=None):
    if value is None or (isinstance(value, float) and value != value):
        return "n/a"
    if digits is not None:
        value = round(float(value), digits)
    return f"{value}{unit}"


def _badge(text, colour):
    return (f"<span style='background:{colour};color:#111;padding:2px 10px;border-radius:12px;"
            f"font-weight:600;font-size:0.9em'>{text}</span>")


def _load_city(city: str):
    """Geocode a city and load its zones into the session."""
    try:
        place_id, coords = get_place_id(city)
        zones = get_zones(place_id).get("features", [])
        st.session_state.update(city=city.strip().title(), city_coords=tuple(coords), zones=zones)
        st.session_state.pop("zone_select", None)
        st.session_state.city_error = None
    except Exception as e:
        st.session_state.city_error = f"Couldn't load '{city}': {e}"


def _logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.logged_in = False


def _save_preferences():
    user = st.session_state.user
    user["health_profile"] = st.session_state.pref_profile
    user["alert_threshold"] = st.session_state.pref_threshold
    update_preferences(user["id"], user["health_profile"], user["alert_threshold"])
    st.toast("Preferences saved.")


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
def _sidebar(user):
    sb = st.sidebar
    sb.markdown(f"### 👋 Hi, {user['username']}")
    sb.button("Log out", on_click=_logout, width="stretch")
    sb.divider()

    sb.subheader("📍 City & zone")
    city_input = sb.text_input("Enter a city", st.session_state.get("city", DEFAULT_CITY))
    if sb.button("Load city", type="primary", width="stretch"):
        _load_city(city_input)
    if st.session_state.get("city_error"):
        sb.error(st.session_state.city_error)

    # Saved cities
    saved = list_saved_cities(user["id"])
    current_city = st.session_state.get("city", DEFAULT_CITY)
    if saved:
        names = [s["city"] for s in saved]
        pick = sb.selectbox("⭐ Saved cities", names, index=None, placeholder="Open a saved city…")
        c1, c2 = sb.columns(2)
        if c1.button("Open", width="stretch", disabled=pick is None):
            _load_city(pick)
        if c2.button("Remove", width="stretch", disabled=pick is None):
            remove_city(user["id"], pick)
            st.rerun()
    if current_city not in [s["city"] for s in saved]:
        if sb.button(f"⭐ Save {current_city}", width="stretch"):
            save_city(user["id"], current_city, st.session_state.get("city_coords", DEFAULT_COORDS))
            st.rerun()

    zones = st.session_state.get("zones", [])
    selected_zone = None
    if zones:
        zone_names = [z["properties"].get("name", "Zone") for z in zones]
        selected_zone = sb.selectbox("Select zone", zone_names, index=None,
                                     placeholder="Whole city", key="zone_select")
    else:
        sb.caption("Click **Load city** to see the city's zones on the map.")

    show_towers = sb.checkbox("Show monitoring stations", value=True)

    sb.divider()
    with sb.expander("⚙️ My health preferences", expanded=False):
        st.selectbox("Health profile", HEALTH_PROFILES, key="pref_profile",
                     index=HEALTH_PROFILES.index(user["health_profile"]) if user["health_profile"] in HEALTH_PROFILES else 0)
        st.slider("Alert me when US AQI is above", 50, 300, int(user["alert_threshold"]), 10, key="pref_threshold")
        st.button("Save preferences", on_click=_save_preferences, width="stretch")

    return selected_zone, show_towers


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
def show_dashboard():
    user = st.session_state.user
    selected_zone, show_towers = _sidebar(user)
    profile, threshold = user["health_profile"], user["alert_threshold"]

    city_name = st.session_state.get("city", DEFAULT_CITY)
    city_lat, city_lon = st.session_state.get("city_coords", DEFAULT_COORDS)
    zones = st.session_state.get("zones", [])

    # ---------------- LIVE DATA ----------------
    with st.spinner(f"Fetching live data for {city_name}…"):
        details = get_aqi_details(city_lat, city_lon)
        weather = get_weather(city_lat, city_lon)
        hourly = get_hourly_air_quality(city_lat, city_lon)

    now_row = None
    if not hourly.empty:
        now = hourly.attrs.get("now")
        past = hourly[hourly["datetime"] <= now] if now is not None else hourly
        now_row = past.iloc[-1] if not past.empty else hourly.iloc[0]

    us_aqi = details.get("aqi")
    aqi_source = f"WAQI station: {details.get('station')}" if us_aqi is not None else None
    if us_aqi is None and now_row is not None:
        us_aqi, aqi_source = to_int(now_row["US AQI"]), "Open-Meteo model estimate"
    india_now = to_int(now_row["India AQI"]) if now_row is not None else None
    india_label, india_colour = naqi_category(india_now)
    status = aqi_health_label(us_aqi)

    # ---------------- HEADER ----------------
    st.markdown(f"## 🌍 {APP_TITLE}")
    st.markdown(f"### {city_name}{' – ' + selected_zone if selected_zone else ''} &nbsp; "
                f"{_badge(status, aqi_color(us_aqi))}", unsafe_allow_html=True)
    caption = [aqi_source or "Live AQI unavailable"]
    if details.get("time"):
        caption.append(f"updated {details['time']}")
    if weather.get("description"):
        caption.append(weather["description"])
    st.caption(" · ".join(caption))

    if us_aqi is not None and us_aqi > threshold:
        st.error(f"⚠️ **Alert:** US AQI is **{us_aqi}**, above your alert level of {threshold}. "
                 f"{health_advice(us_aqi, profile)['outdoor']}")

    # 24h change for the AQI metric
    delta = None
    if now_row is not None:
        day_ago = hourly[hourly["datetime"] == now_row["datetime"] - pd.Timedelta(hours=24)]
        if not day_ago.empty and pd.notna(day_ago["US AQI"].iloc[0]) and pd.notna(now_row["US AQI"]):
            delta = int(now_row["US AQI"] - day_ago["US AQI"].iloc[0])

    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("US AQI", _fmt(us_aqi), None if delta is None else f"{delta:+d} vs 24h ago", delta_color="inverse",
              help="US EPA scale (used by WAQI). Lower is better.")
    m2.metric("India AQI (CPCB)", _fmt(india_now), india_label, delta_color="off",
              help="India's National AQI, calculated from 24-hour average PM2.5 and PM10.")
    m3.metric("Temperature", _fmt(weather["temp"], " °C"),
              f"Feels {_fmt(weather.get('feels_like'), ' °C')}", delta_color="off")
    m4.metric("Humidity", _fmt(weather["humidity"], "%"))
    m5.metric("Wind", _fmt(weather["wind"], " m/s"))
    score = outdoor_score(us_aqi, weather["temp"], weather["humidity"])
    m6.metric("Outdoor score", "n/a" if score is None else f"{score}/100",
              help="Combines air quality, heat/cold and humidity. Higher is better.")

    tabs = st.tabs(["🗺️ Live map", "📈 Forecast & trends", "🩺 Health planner",
                    "🏙️ Compare cities", "🤖 AI advisory & news"])

    # ---------------- TAB 1: MAP ----------------
    with tabs[0]:
        towers = get_aqi_towers(city_name) if show_towers else []
        df_towers = pd.DataFrame(towers)
        left, right = st.columns([2, 1])
        with left:
            selected_feature = next((z for z in zones if z["properties"].get("name") == selected_zone), None)
            fmap = create_map(selected_feature, zones, (city_lat, city_lon), towers)
            st_folium(fmap, height=560, use_container_width=True, returned_objects=[],
                      key=f"map_{city_name}_{selected_zone}_{show_towers}")
        with right:
            st.subheader("Monitoring stations")
            valid = df_towers.dropna(subset=["AQI"]) if not df_towers.empty else df_towers
            if not valid.empty:
                c1, c2 = st.columns(2)
                c1.metric("Stations", len(valid))
                c2.metric("Average AQI", int(valid["AQI"].mean()))
                best, worst = valid.loc[valid["AQI"].idxmin()], valid.loc[valid["AQI"].idxmax()]
                st.markdown(f"🟢 Cleanest: **{best['Station']}** ({int(best['AQI'])})  \n"
                            f"🔴 Most polluted: **{worst['Station']}** ({int(worst['AQI'])})")
                st.plotly_chart(plot_station_bars(valid), width="stretch")
                st.download_button("⬇️ Download station data (CSV)", valid.to_csv(index=False),
                                   f"{city_name}_stations.csv", "text/csv", width="stretch")
            elif show_towers:
                st.info("No monitoring station data found for this city.")
            else:
                st.info("Turn on **Show monitoring stations** in the sidebar.")

            if details.get("pollutants"):
                st.markdown("**Nearest station pollutants (sub-index)**")
                st.dataframe(pd.DataFrame([details["pollutants"]]).rename(columns=str.upper),
                             hide_index=True, width="stretch")

    # ---------------- TAB 2: FORECAST ----------------
    with tabs[1]:
        if hourly.empty:
            st.warning("Air quality forecast is unavailable right now. Try again in a few minutes.")
        else:
            st.subheader("AQI: last 2 days + next 4 days")
            show_india = st.toggle("Show India AQI (CPCB)", value=True)
            st.plotly_chart(plot_aqi_trend(hourly, show_india), width="stretch")
            st.caption("Hourly data from Open-Meteo (CAMS model). Model values can differ from station readings.")

            st.subheader("Pollutant breakdown")
            chosen = st.multiselect("Pollutants", list(POLLUTANTS.values()), default=["PM2.5", "PM10", "NO₂", "O₃"])
            if chosen:
                st.plotly_chart(plot_pollutants(hourly, chosen), width="stretch")
            st.download_button("⬇️ Download hourly air quality (CSV)", hourly.to_csv(index=False),
                               f"{city_name}_air_quality.csv", "text/csv")

        st.subheader("🌡️ Weather forecast (next 5 days)")
        weather_df = get_weather_forecast(city_lat, city_lon)
        if weather_df.empty:
            st.warning("Weather forecast is unavailable right now.")
        else:
            st.plotly_chart(plot_weather_forecast(weather_df), width="stretch")

    # ---------------- TAB 3: HEALTH ----------------
    with tabs[2]:
        advice = health_advice(us_aqi, profile)
        st.subheader(f"Advice for: {profile}")
        st.caption("Change your profile in the sidebar under ⚙️ My health preferences.")
        level_box = st.info if advice["level"] is None else [st.success, st.info, st.warning, st.error, st.error][advice["level"]]
        level_box(f"**{advice['headline']}** (US AQI {_fmt(us_aqi)})")
        a1, a2, a3 = st.columns(3)
        a1.markdown(f"**🏃 Outdoors**  \n{advice['outdoor']}")
        a2.markdown(f"**😷 Mask**  \n{advice['mask']}")
        a3.markdown(f"**🏠 At home**  \n{advice['indoor']}")
        if advice["profile_tip"]:
            st.info(advice["profile_tip"])

        st.subheader("⏰ Best time to go outside (next 24 hours)")
        windows = best_time_windows(hourly)
        if windows:
            cols = st.columns(len(windows))
            for col, w in zip(cols, windows):
                col.metric(f"{w['start']:%a %H:%M} – {w['end']:%H:%M}", f"AQI ~{w['avg_aqi']}",
                           aqi_health_label(w["avg_aqi"]), delta_color="off")
        else:
            st.info("Not enough forecast data to suggest times.")

        st.subheader("📅 Daily outlook")
        outlook = daily_outlook(hourly)
        if not outlook.empty:
            outlook["Expected air"] = outlook["Worst US AQI"].apply(aqi_health_label)
            st.dataframe(outlook, hide_index=True, width="stretch")
        st.caption("This is general guidance, not medical advice. Follow your doctor's advice for any health condition.")

    # ---------------- TAB 4: COMPARE ----------------
    with tabs[3]:
        cities = dict(INDIAN_CITIES)
        if city_name not in cities:
            cities[city_name] = (city_lat, city_lon)
        compare = get_current_for_cities(cities)
        if compare.empty:
            st.warning("City comparison is unavailable right now.")
        else:
            cleanest, worst = compare.iloc[0], compare.iloc[-1]
            rank = compare.index[compare["City"] == city_name]
            c1, c2, c3 = st.columns(3)
            c1.metric("🟢 Cleanest now", cleanest["City"], f"AQI {int(cleanest['US AQI'])}", delta_color="off")
            c2.metric("🔴 Most polluted now", worst["City"], f"AQI {int(worst['US AQI'])}", delta_color="off")
            if len(rank):
                c3.metric(f"📍 {city_name} rank", f"#{rank[0] + 1} of {len(compare)}", "1 = cleanest", delta_color="off")
            left, right = st.columns([1, 1])
            with left:
                st.plotly_chart(plot_city_comparison(compare, city_name), width="stretch")
            with right:
                st_folium(create_comparison_map(compare), height=520, use_container_width=True,
                          returned_objects=[], key="compare_map")
            st.dataframe(compare.drop(columns=["Latitude", "Longitude"]).round(1), hide_index=True,
                         width="stretch")
            st.caption("Current model estimates from Open-Meteo for city centres. India AQI here uses current "
                       "PM values, so it's an estimate of the official 24-hour index.")

    # ---------------- TAB 5: AI + NEWS ----------------
    with tabs[4]:
        st.subheader("🤖 Advisory")
        best_text = ", ".join(f"{w['start']:%H:%M}–{w['end']:%H:%M}" for w in best_time_windows(hourly))
        with st.spinner("Writing advisory…"):
            text, source = get_ai_advisory(city_name, selected_zone or "Entire city", us_aqi,
                                           weather["temp"], weather["humidity"], profile, best_text)
        st.info(text)
        st.caption(f"Source: {source}")

        st.subheader("📰 Latest air-quality news")
        news = get_pollution_news(city_name)
        if news:
            for item in news:
                st.markdown(f"- [{item['title']}]({item['link']})  \n  <small>{item['source']} · {item['published']}</small>",
                            unsafe_allow_html=True)
        else:
            st.info("No recent news found.")
