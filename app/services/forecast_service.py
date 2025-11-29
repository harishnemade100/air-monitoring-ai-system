import pandas as pd
import requests
from datetime import datetime, timedelta
import plotly.graph_objects as go
from utils.color_utils import aqi_color, aqi_health_label


def get_aqi_forecast(lat, lon, current_aqi):
    """
    Returns simulated past 12h + next 12h AQI forecast DataFrame
    """
    now = datetime.now()
    hours = [now - timedelta(hours=i) for i in reversed(range(12))] + \
            [now + timedelta(hours=i) for i in range(1,13)]
    values = [current_aqi - 5 + i for i in range(12)] + [current_aqi + i for i in range(12)]
    df = pd.DataFrame({"datetime": hours, "AQI": values})
    df['status'] = df['AQI'].apply(aqi_health_label)
    df['color'] = df['AQI'].apply(aqi_color)
    return df

def plot_aqi_forecast(aqi_df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=aqi_df['datetime'],
        y=aqi_df['AQI'],
        mode='lines+markers',
        marker=dict(color=aqi_df['color']),
        line=dict(color='blue'),
        hovertemplate="Time: %{x}<br>AQI: %{y}<br>Status: %{text}",
        text=aqi_df['status'],
        name='AQI'
    ))
    fig.update_layout(
        title="Past + Forecast AQI",
        xaxis_title="Time",
        yaxis_title="AQI",
        hovermode="x unified",
        height=300
    )
    return fig

# ---------------- WEATHER FORECAST ----------------
def get_weather_forecast(lat, lon, api_key):
    """
    Returns next 24h temperature forecast DataFrame
    """
    weather_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    resp = requests.get(weather_url).json()

    df = pd.DataFrame({
        "datetime": [datetime.fromtimestamp(item['dt']) for item in resp['list'][:8]],  # next 24h (3h interval)
        "Temp": [item['main']['temp'] for item in resp['list'][:8]]
    })

    def temp_color(temp):
        if temp < 15:
            return 'blue'
        elif temp > 35:
            return 'red'
        else:
            return 'orange'

    df['color'] = df['Temp'].apply(temp_color)
    return df

def plot_weather_forecast(weather_df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=weather_df['datetime'],
        y=weather_df['Temp'],
        mode='lines+markers',
        line=dict(color='orange'),
        marker=dict(color=weather_df['color']),
        hovertemplate="Time: %{x}<br>Temp: %{y} °C",
        name='Temp'
    ))
    fig.update_layout(
        title="Next 24h Temperature Forecast",
        xaxis_title="Time",
        yaxis_title="Temp (°C)",
        hovermode="x unified",
        height=300
    )
    return fig
