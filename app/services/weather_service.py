import requests

def get_weather(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=relativehumidity_2m"
        r = requests.get(url, timeout=10)
        data = r.json()

        current = data.get("current_weather", {})
        humidity = data.get("hourly", {}).get("relativehumidity_2m", ["N/A"])[0]

        return {
            "temp": current.get("temperature", "N/A"),
            "wind": current.get("windspeed", "N/A"),
            "humidity": humidity,
        }
    except:
        return {"temp": "N/A", "wind": "N/A", "humidity": "N/A"}
