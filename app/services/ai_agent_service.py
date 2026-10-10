"""
AI advisory and local pollution news.

- Advisory: Groq LLM when GROQ_API_KEY is set, otherwise a rule-based advisory
  (replaces the old DeepAI text generator).
- News: Google News RSS (free, no API key; replaces NewsAPI, whose free plan
  is limited to development use).
"""
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

import requests
import streamlit as st

from services.health_service import health_advice
from setting.constants import CACHE_FORECAST, GROQ_API_KEY, LLM_MODEL, REQUEST_TIMEOUT
from utils.color_utils import aqi_health_label


def rule_based_advisory(city, zone, aqi, temp, humidity, profile="General public") -> str:
    advice = health_advice(aqi, profile)
    if advice["level"] is None:
        return f"{zone}, {city}: live air quality data isn't available right now. Please check again shortly."
    parts = [f"{zone}, {city}: air quality is {aqi_health_label(aqi).lower()} (US AQI {aqi if aqi is not None else 'n/a'}).",
             advice["outdoor"], advice["mask"]]
    if temp is not None and temp > 35:
        parts.append("It's hot: stay hydrated and avoid the midday sun.")
    elif temp is not None and temp < 10:
        parts.append("It's cold: dress warmly.")
    if humidity is not None and humidity > 80:
        parts.append("High humidity may make it feel heavier outside.")
    return " ".join(parts)


@st.cache_data(ttl=CACHE_FORECAST, show_spinner=False)
def get_ai_advisory(city, zone, aqi, temp, humidity, profile="General public", best_times="") -> tuple[str, str]:
    """Returns (advisory text, source). Falls back to rules if Groq is unavailable."""
    fallback = rule_based_advisory(city, zone, aqi, temp, humidity, profile)
    if not GROQ_API_KEY:
        return fallback, "Rule-based"
    try:
        from groq import Groq

        prompt = (
            f"Location: {zone}, {city}, India. US AQI: {aqi}. Temperature: {temp}°C. Humidity: {humidity}%.\n"
            f"Reader's health profile: {profile}. Cleanest upcoming hours: {best_times or 'unknown'}.\n"
            "Write a short, practical air-quality advisory (3–4 sentences) for this reader: "
            "what to do today, whether to wear a mask, and the best time to go outside. "
            "Be factual and calm. No markdown headings."
        )
        response = Groq(api_key=GROQ_API_KEY, timeout=REQUEST_TIMEOUT).chat.completions.create(
            model=LLM_MODEL, temperature=0.3, max_tokens=2000,
            messages=[{"role": "system", "content": "You are a public-health air quality assistant."},
                      {"role": "user", "content": prompt}],
        )
        text = (response.choices[0].message.content or "").strip()
        return (text, f"AI ({LLM_MODEL})") if text else (fallback, "Rule-based")
    except Exception:
        return fallback, "Rule-based (AI unavailable)"


@st.cache_data(ttl=CACHE_FORECAST, show_spinner=False)
def get_pollution_news(city: str, limit: int = 6) -> list[dict]:
    """Latest air-pollution headlines for the city from Google News (India edition)."""
    try:
        response = requests.get(
            "https://news.google.com/rss/search",
            params={"q": f'"{city}" (AQI OR "air pollution" OR "air quality")', "hl": "en-IN", "gl": "IN", "ceid": "IN:en"},
            timeout=REQUEST_TIMEOUT, headers={"User-Agent": "Mozilla/5.0"},
        )
        response.raise_for_status()
        items = ET.fromstring(response.content).findall("./channel/item")
    except Exception:
        return []

    news = []
    for item in items[:limit]:
        title = item.findtext("title", "")
        source = item.findtext("source", "") or (title.rsplit(" - ", 1)[-1] if " - " in title else "")
        if source and title.endswith(f" - {source}"):
            title = title[: -len(f" - {source}")]
        try:
            published = parsedate_to_datetime(item.findtext("pubDate", "")).strftime("%d %b %Y")
        except Exception:
            published = ""
        news.append({"title": title, "link": item.findtext("link", ""), "source": source, "published": published})
    return news
