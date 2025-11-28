def aqi_color(aqi):
    try:
        aqi = int(aqi)
    except:
        return "#808080"   # grey

    if aqi <= 50: return "#00e400"
    if aqi <= 100: return "#ffff00"
    if aqi <= 150: return "#ff7e00"
    if aqi <= 200: return "#ff0000"
    if aqi <= 300: return "#8f3f97"
    return "#7e0023"