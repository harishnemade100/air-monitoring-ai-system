import requests
import pandas as pd
from setting.constants import WAQI_TOKEN


def get_aqi(lat, lon):
    url = f"https://api.waqi.info/feed/geo:{lat};{lon}/?token={WAQI_TOKEN}"
    r = requests.get(url)
    data = r.json()
    if data["status"] != "ok":
        return None
    return data["data"]["aqi"]

def get_aqi_forecast(lat, lon):
    url = f"https://api.waqi.info/feed/geo:{lat};{lon}/?token={WAQI_TOKEN}"
    r = requests.get(url)
    data = r.json()
    if data["status"] != "ok":
        return pd.DataFrame()
    
    forecast_data = data["data"].get("forecast", {}).get("daily", {}).get("pm25", [])
    df = pd.DataFrame(forecast_data)
    df['date'] = pd.to_datetime(df['day'])
    df = df.melt(id_vars=['date'], value_name='AQI', var_name='Metric')
    return df


def get_aqi_towers(city_name):
    """
    Returns all AQI towers (stations) in the given city.
    """
    url = f"https://api.waqi.info/search/?token={WAQI_TOKEN}&keyword={city_name}"
    response = requests.get(url)
    data = response.json()
    if data["status"] == "ok":
        return data["data"]
    return []