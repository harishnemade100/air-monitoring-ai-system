def get_aqi_suggestion(aqi, temp, humidity):
    if aqi <= 50:
        aqi_msg = "Air quality is good. Enjoy outdoor activities."
    elif aqi <= 100:
        aqi_msg = "Air quality is moderate. Sensitive people should be cautious."
    elif aqi <= 150:
        aqi_msg = "Unhealthy for sensitive groups. Limit prolonged outdoor exertion."
    elif aqi <= 200:
        aqi_msg = "Air quality is unhealthy. Minimize outdoor activities."
    elif aqi <= 300:
        aqi_msg = "Very unhealthy. Avoid outdoor activities and use masks."
    else:
        aqi_msg = "Hazardous! Stay indoors and use air purifiers."

    weather_msg = ""
    if temp < 10:
        weather_msg = "It's cold outside, wear warm clothes."
    elif temp > 35:
        weather_msg = "It's hot outside, stay hydrated and avoid direct sun."

    if humidity > 80:
        weather_msg += " High humidity may cause discomfort."

    return f"{aqi_msg} {weather_msg}"
