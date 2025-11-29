import folium

def create_map(selected_feature, all_features):
    m = folium.Map(location=selected_feature["center"], zoom_start=13)

    for z in all_features:
        folium.GeoJson(
            z["geojson"],
            name=z["name"],
            style_function=lambda x: {"color": "gray", "weight": 1}
        ).add_to(m)

    folium.GeoJson(
        selected_feature["geojson"],
        style_function=lambda x: {"color": "blue", "weight": 3}
    ).add_to(m)

    return m
