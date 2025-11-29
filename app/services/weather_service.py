import requests
import pandas as pd

OPENWEATHER_KEY = "be0eee25ce9b61255d720e187b17bf61"

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