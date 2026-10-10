"""Folium maps: city zones, monitoring stations, and city comparison."""
import folium
from shapely.geometry import shape

from services.waqi_service import get_aqi
from services.weather_service import get_weather
from utils.color_utils import aqi_color, aqi_health_label

_LEGEND = """
<div style="position: fixed; bottom: 20px; left: 20px; z-index: 9999; background: white; color: black;
     padding: 8px 10px; border-radius: 6px; font-size: 12px; box-shadow: 0 0 4px rgba(0,0,0,.3);">
<b>US AQI</b><br>
<span style="color:#00e400">&#9632;</span> 0–50 Good<br>
<span style="color:#ffff00">&#9632;</span> 51–100 Moderate<br>
<span style="color:#ff7e00">&#9632;</span> 101–150 Sensitive<br>
<span style="color:#ff0000">&#9632;</span> 151–200 Unhealthy<br>
<span style="color:#8f3f97">&#9632;</span> 201–300 Very unhealthy<br>
<span style="color:#7e0023">&#9632;</span> 300+ Hazardous<br>
<span style="color:#808080">&#9632;</span> No data<br>
<span style="opacity:.6">&#9711;</span> Faded, dashed = model estimate
</div>
"""


def _fmt(value, unit=""):
    return f"{value}{unit}" if value is not None else "n/a"


def create_map(selected_feature=None, all_features=None, default_city_coords=None, towers=None):
    """City map with zone boundaries; the selected zone is coloured by its live AQI."""
    if selected_feature:
        centroid = shape(selected_feature["geometry"]).centroid
        center, zoom = (centroid.y, centroid.x), 13
    else:
        center, zoom = (default_city_coords or (18.5204, 73.8567)), 11

    m = folium.Map(location=center, zoom_start=zoom)

    for feature in all_features or []:
        name = feature["properties"].get("name", "Zone")
        centroid = shape(feature["geometry"]).centroid
        is_selected = feature is selected_feature
        if is_selected:
            aqi = get_aqi(centroid.y, centroid.x)
            weather = get_weather(centroid.y, centroid.x)
            color = aqi_color(aqi)
            popup = (f"<b>Zone:</b> {name}<br><b>AQI:</b> {_fmt(aqi)} ({aqi_health_label(aqi)})<br>"
                     f"<b>Temp:</b> {_fmt(weather['temp'], ' °C')}<br><b>Wind:</b> {_fmt(weather['wind'], ' m/s')}<br>"
                     f"<b>Humidity:</b> {_fmt(weather['humidity'], '%')}")
            folium.Marker([centroid.y, centroid.x], popup=folium.Popup(popup, max_width=250),
                          icon=folium.Icon(color="red", icon="info-sign")).add_to(m)
        else:
            color, popup = "#ADD8E6", name

        folium.GeoJson(
            feature,
            style_function=lambda _, c=color, sel=is_selected: {
                "fillColor": c, "color": "black", "weight": 3 if sel else 1, "fillOpacity": 0.5 if sel else 0.25,
            },
            tooltip=name,
        ).add_to(m)

    for t in towers or []:
        color = aqi_color(t["AQI"])
        estimated = t.get("Source") == "Model estimate"
        label = "Model estimate" if estimated else "Live station reading"
        folium.CircleMarker(
            location=[t["Latitude"], t["Longitude"]], radius=8, color=color, weight=2,
            dash_array="4 3" if estimated else None,
            fill=True, fill_color=color, fill_opacity=0.35 if estimated else 0.85,
            popup=folium.Popup(f"<b>{t['Station']}</b><br>AQI: {_fmt(t['AQI'])} ({aqi_health_label(t['AQI'])})"
                               f"<br><i>{label}</i>", max_width=260),
            tooltip=f"{t['Station']}: {_fmt(t['AQI'])}{' (estimate)' if estimated else ''}",
        ).add_to(m)

    m.get_root().html.add_child(folium.Element(_LEGEND))
    return m


def create_comparison_map(df_cities):
    """India map with a coloured circle per city (bigger = worse)."""
    m = folium.Map(location=(22.5, 79.0), zoom_start=5)
    for _, row in df_cities.iterrows():
        color = aqi_color(row["US AQI"])
        folium.CircleMarker(
            location=[row["Latitude"], row["Longitude"]], radius=6 + min(row["US AQI"], 300) / 20,
            color=color, fill=True, fill_color=color, fill_opacity=0.8,
            tooltip=f"{row['City']}: US AQI {int(row['US AQI'])} ({aqi_health_label(row['US AQI'])})",
        ).add_to(m)
    m.get_root().html.add_child(folium.Element(_LEGEND))
    return m
