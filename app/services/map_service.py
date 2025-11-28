import folium
from shapely.geometry import shape
from services.waqi_service import get_aqi
from services.weather_service import get_weather
from utils.color_utils import aqi_color

def create_map(selected_feature, all_features):
    geom = selected_feature["geometry"]
    poly = shape(geom)
    centroid = poly.centroid
    m = folium.Map(location=[centroid.y, centroid.x], zoom_start=12)

    for feature in all_features:
        name = feature["properties"].get("name", "Zone")
        geom = feature["geometry"]
        poly = shape(geom)
        cent = poly.centroid
        lat, lon = cent.y, cent.x

        # Highlight selected zone
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

    return m
