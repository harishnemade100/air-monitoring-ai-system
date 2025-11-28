import requests

WAQI_TOKEN = "b6488c90742fa136de473fa5647d956d91b92f84"

def get_aqi(lat, lon):
    try:
        url = f"https://api.waqi.info/feed/geo:{lat};{lon}/?token={WAQI_TOKEN}"
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return "N/A"

        data = r.json()
        if data.get("status") != "ok":
            return "N/A"

        return data["data"].get("aqi", "N/A")
    except:
        return "N/A"
