import folium
from shapely.geometry import shape
from services.waqi_service import get_aqi
from services.weather_service import get_weather
from utils.color_utils import aqi_color

def create_map(selected_feature=None, all_features=None, default_city_coords=None):
    """
    Creates a folium map.
    - selected_feature: GeoJSON of selected zone (optional)
    - all_features: list of GeoJSON zones (optional)
    - default_city_coords: tuple(lat, lon) to center the map if no zone selected
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

    if all_features:
        for feature in all_features:
            name = feature["properties"].get("name", "Zone")
            geom = feature["geometry"]
            poly = shape(geom)
            cent = poly.centroid
            lat, lon = cent.y, cent.x

            # Highlight selected feature
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
                color = "#ADD8E6"  # light blue for other zones
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

    return m
