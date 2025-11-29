# Picmica-Pollution-Zones


# 🌆 Live AQI & Weather Dashboard

[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)  
[![Streamlit](https://img.shields.io/badge/Streamlit-App-green)](https://streamlit.io/)  
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

A **real-time Air Quality Index (AQI) & Weather Dashboard** built with **Streamlit**, displaying live air pollution data, weather, and humidity for Indian cities. The dashboard includes **city-level and zone-level analysis** with interactive maps and forecasts.  

---

## 🔹 Table of Contents

- [Overview](#overview)  
- [Features](#features)  
- [Technologies & Tools](#technologies--tools)  
- [APIs Used](#apis-used)  
- [Project Structure](#project-structure)  
- [Installation](#installation)  
- [Usage](#usage)  
- [Screenshots](#screenshots)  
- [Future Enhancements](#future-enhancements)  
- [License](#license)  

---

## 🌟 Overview

Air pollution is a growing concern affecting health worldwide. This project provides a **live monitoring system** for AQI and weather conditions. Key highlights:

- City-level average AQI  
- Zone-wise AQI with color-coded indicators  
- Weather info: temperature, humidity, etc.  
- Interactive map showing AQI measurement points  
- Forecasting of AQI and weather  

Designed for **hackathons, research, or educational purposes**.  

---

## ✅ Features

- **City Selection:** Choose a city to view live AQI and weather.  
- **City Summary:** Average AQI, temperature, humidity, and air quality category.  
- **Zone-Level Data:** Color-coded AQI for all zones.  
- **Interactive Map:** Left-side map with pollution markers.  
- **Forecasting:** Simple AQI and weather forecasts.  
- **Scalable Architecture:** Modular structure for easy maintenance.  

---

## 🛠 Technologies & Tools

- **Python 3.10+**  
- **Streamlit** – Web dashboard  
- **Folium & Matplotlib** – Mapping & visualization  
- **Pandas & NumPy** – Data handling  
- **Requests** – API interaction  

---

## 🌐 APIs Used

| API | Purpose | Notes |
|-----|--------|-------|
| **WAQI API** | Live AQI data for cities/zones | Free API key required |
| **OpenWeatherMap API** | Weather forecasts (temperature, humidity) | Free tier available |
| **Geoapify API** | Geocoding & zone boundaries | Free trial available |

> **Tip:** Add your API keys in `services/waqi_service.py`, `services/weather_service.py`, and `services/geoapify_service.py`.  

---

---

## ⚡ Installation

1. **Clone the repository:**

```bash
git clone https://github.com/<your-username>/Air-Pollution-Dashboard.git
cd Air-Pollution-Dashboard

Install dependencies (pip):

pip install -r requirements.txt


Or using pipenv:

pipenv install
pipenv shell


Add your API keys in the respective service files:

WAQI_TOKEN = "your_waqi_api_token"
OPENWEATHER_KEY = "your_openweather_api_key"
GEOAPIFY_KEY = "your_geoapify_api_key"


Run the Streamlit app:

streamlit run app/app.py


Open the URL provided in the terminal (usually http://localhost:8501).

🎯 Usage

Select a city from the dropdown menu.

Left panel: Interactive map with AQI zones.

Right panel: City summary with average AQI, weather, and humidity.

Scroll for zone-wise AQI details and forecast plots.

🖼 Screenshots

(Add images after running the app)

City-level AQI summary

Zone-wise AQI map

Weather forecast panel

🚀 Future Enhancements

Traffic/vehicle monitoring integration

Predictive AQI using machine learning

Multi-city comparison

Historical data visualization

📜 License

This project is open-source under the MIT License. Free to use for educational and hackathon purposes.


---

If you want, I can also **create a GitHub-ready version with colored AQI badges and weather icons** so your repo looks professional and interactive.  

Do you want me to make that enhanced version?
