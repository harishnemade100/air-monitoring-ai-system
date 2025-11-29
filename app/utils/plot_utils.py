import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd

def plot_aqi_forecast(df):
    """
    Simple AQI line chart: past + forecast trend
    """
    if df.empty:
        st.info("No AQI data available")
        return

    # Ensure date column is datetime
    if df['date'].dtype == 'O':  # object/string
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    # Drop rows with invalid dates or AQI
    df = df.dropna(subset=['date', 'AQI'])

    # Ensure AQI column is numeric
    df['AQI'] = pd.to_numeric(df['AQI'], errors='coerce')
    df = df.dropna(subset=['AQI'])

    if df.empty:
        st.info("No valid AQI data to plot")
        return

    fig, ax = plt.subplots(figsize=(6,3))
    ax.plot(df['date'], df['AQI'], marker='o', color='red')
    ax.set_title("AQI Trend (Past + Forecast)", fontsize=14)
    ax.set_xlabel("Date/Time")
    ax.set_ylabel("AQI")
    ax.grid(True, linestyle='--', alpha=0.5)
    fig.autofmt_xdate()
    st.pyplot(fig)

def plot_weather_forecast(df):
    """
    Simple temperature line chart
    """
    if df.empty:
        st.info("No weather data available")
        return

    fig, ax = plt.subplots(figsize=(6,3))
    ax.plot(df['datetime'], df['temp'], marker='o', color='orange')
    ax.set_title("Temperature Trend (Next 24h)", fontsize=14)
    ax.set_xlabel("Date/Time")
    ax.set_ylabel("Temp (°C)")
    ax.grid(True, linestyle='--', alpha=0.5)
    st.pyplot(fig)
