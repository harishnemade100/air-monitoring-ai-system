import folium
from shapely.geometry import shape
from services.waqi_service import get_aqi, get_aqi_towers
from services.weather_service import get_weather
from utils.color_utils import aqi_color

def create_map(selected_feature=None, all_features=None, default_city_coords=None, show_towers=False, city_name=None):
    """
    Creates a folium map.
    """
    if selected_feature:
        geom = selected_feature["geometry"]
        poly = shape(geom)
        centroid = poly.centroid
        map_center = (centroid.y, centroid.x)
    elif default_city_coords:
        map_center = default_city_coords
    else:
        map_center = (18.5204, 73.8567)  # fallback Pune

    m = folium.Map(location=map_center, zoom_start=12)

    # Draw zones
    if all_features:
        for feature in all_features:
            name = feature["properties"].get("name", "Zone")
            geom = feature["geometry"]
            poly = shape(geom)
            cent = poly.centroid
            lat, lon = cent.y, cent.x

            if feature == selected_feature:
                aqi = get_aqi(lat, lon)
                weather = get_weather(lat, lon)
                color = aqi_color(aqi)
                popup = (
                    f"<b>Zone:</b> {name}<br>"
                    f"<b>AQI:</b> {aqi}<br>"
                    f"<b>Temp:</b> {weather['temp']} °C<br>"
                    f"<b>Wind:</b> {weather['wind']} m/s<br>"
                    f"<b>Humidity:</b> {weather['humidity']}%"
                )
            else:
                color = "#ADD8E6"
                popup = name

            folium.GeoJson(
                feature,
                style_function=lambda x, c=color: {
                    "fillColor": c,
                    "color": "black",
                    "weight": 2,
                    "fillOpacity": 0.5,
                },
                tooltip=name,
            ).add_to(m)

            folium.Marker([lat, lon], popup=popup).add_to(m)

    # Add AQI towers
    if show_towers and city_name:
        towers = get_aqi_towers(city_name)
        for t in towers:
            tower_name = t['station']['name']
            lat, lon = t['station']['geo']
            aqi = t['aqi'] if t['aqi'] != '-' else 0
            color = aqi_color(aqi)

            folium.CircleMarker(
                location=[lat, lon],
                radius=7,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.8,
                popup=f"<b>{tower_name}</b><br>AQI: {aqi}"
            ).add_to(m)

    return m
