import requests
import pandas as pd
from setting.constants import OPENWEATHER_KEY 

def get_weather(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={OPENWEATHER_KEY}"
    r = requests.get(url)
    data = r.json()
    return {
        "temp": data['main']['temp'],
        "humidity": data['main']['humidity'],
        "wind": data['wind']['speed']
    }

def get_weather_forecast(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&appid={OPENWEATHER_KEY}"
    r = requests.get(url)
    data = r.json()
    df = pd.DataFrame([{
        "datetime": x["dt_txt"],
        "temp": x["main"]["temp"],
        "humidity": x["main"]["humidity"],
        "wind": x["wind"]["speed"]
    } for x in data['list']])
    df['datetime'] = pd.to_datetime(df['datetime'])
    return df