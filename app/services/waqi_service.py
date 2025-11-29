import requests
import pandas as pd

WAQI_TOKEN = "b6488c90742fa136de473fa5647d956d91b92f84"

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