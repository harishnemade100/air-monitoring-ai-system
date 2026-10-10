"""
Personalised health advice and "best time to go outside".

Sensitive groups (children, elderly, asthma, heart, pregnancy) are treated one risk level
more strictly than the general public, in line with standard AQI health guidance.
"""
import pandas as pd

from utils.color_utils import to_int

SENSITIVE = {"Children", "Elderly (60+)", "Asthma / lung condition", "Heart condition", "Pregnant"}

# risk level -> (headline, outdoor advice, mask advice, indoor advice)
_LEVELS = [
    ("Low risk", "Great day to be outside. Enjoy outdoor activities.",
     "No mask needed.", "Open windows to let fresh air in."),
    ("Moderate risk", "Outdoor activity is fine. Unusually sensitive people should take it easier.",
     "Mask not usually needed.", "Ventilating your home is fine."),
    ("High risk", "Reduce long or intense outdoor activity. Take more breaks.",
     "Consider an N95/FFP2 mask if you're outside for long.", "Keep windows closed at peak hours."),
    ("Very high risk", "Avoid long or intense outdoor activity. Move exercise indoors.",
     "Wear an N95/FFP2 mask outdoors.", "Keep windows closed; use an air purifier if you have one."),
    ("Severe risk", "Avoid all outdoor activity. Stay indoors as much as possible.",
     "Wear an N95/FFP2 mask if you must go out.", "Keep windows closed and run an air purifier."),
]

_PROFILE_TIPS = {
    "Children": "Children breathe faster and are more affected: keep outdoor play short on poor-air days.",
    "Elderly (60+)": "Older adults should avoid exertion outdoors when AQI is high and watch for breathlessness.",
    "Asthma / lung condition": "Keep your reliever inhaler with you and follow your asthma action plan.",
    "Heart condition": "Avoid strenuous activity outdoors; seek help for chest pain or palpitations.",
    "Pregnant": "Limit time in polluted air; prefer indoor walks on poor-air days.",
    "Outdoor worker / athlete": "Schedule hard work or training for the cleanest hours shown below.",
    "General public": "Check the best-time windows below to plan outdoor activities.",
}


def risk_level(us_aqi, profile: str):
    """0 (low) to 4 (severe), or None when there's no AQI data."""
    aqi = to_int(us_aqi)
    if aqi is None:
        return None
    level = 0 if aqi <= 50 else 1 if aqi <= 100 else 2 if aqi <= 150 else 3 if aqi <= 200 else 4
    if profile in SENSITIVE and aqi > 50:
        level = min(level + 1, 4)
    return level


def health_advice(us_aqi, profile: str) -> dict:
    level = risk_level(us_aqi, profile)
    if level is None:
        return {"level": None, "headline": "Air quality data unavailable",
                "outdoor": "Live air quality data isn't available right now. Check again before long outdoor activity.",
                "mask": "Check again when data is available.", "indoor": "No change needed.",
                "profile_tip": _PROFILE_TIPS.get(profile, "")}
    headline, outdoor, mask, indoor = _LEVELS[level]
    return {
        "level": level, "headline": headline, "outdoor": outdoor,
        "mask": mask, "indoor": indoor, "profile_tip": _PROFILE_TIPS.get(profile, ""),
    }


def outdoor_score(us_aqi, temp=None, humidity=None):
    """0–100 score combining air quality and comfort (higher is better); None without AQI data."""
    aqi = to_int(us_aqi)
    if aqi is None:
        return None
    score = max(0, 100 - aqi * 0.5)            # AQI 0 -> 100, AQI 200 -> 0
    if temp is not None:
        if temp > 35: score -= min(25, (temp - 35) * 4)
        elif temp < 10: score -= min(20, (10 - temp) * 3)
    if humidity is not None and humidity > 80:
        score -= 10
    return int(max(0, min(100, score)))


def best_time_windows(hourly: pd.DataFrame, hours_ahead: int = 24, window: int = 2, top: int = 3,
                      day_start: int = 6, day_end: int = 21) -> list[dict]:
    """Cleanest daytime windows in the next `hours_ahead` hours (non-overlapping)."""
    if hourly.empty or "US AQI" not in hourly:
        return []
    now = hourly.attrs.get("now", hourly["datetime"].min())
    upcoming = hourly[(hourly["datetime"] >= now) &
                      (hourly["datetime"] < now + pd.Timedelta(hours=hours_ahead))].dropna(subset=["US AQI"])
    upcoming = upcoming.reset_index(drop=True)
    candidates = []
    for i in range(len(upcoming) - window + 1):
        block = upcoming.iloc[i:i + window]
        start = block["datetime"].iloc[0]
        if start.hour < day_start or start.hour + window > day_end + 1:
            continue
        candidates.append((block["US AQI"].mean(), start))

    chosen = []
    for avg, start in sorted(candidates):
        if all(abs((start - c["start"]).total_seconds()) >= window * 3600 for c in chosen):
            chosen.append({"start": start, "end": start + pd.Timedelta(hours=window), "avg_aqi": round(avg)})
        if len(chosen) == top:
            break
    return sorted(chosen, key=lambda c: c["start"])


def daily_outlook(hourly: pd.DataFrame) -> pd.DataFrame:
    """Average and worst AQI for today and the coming days."""
    if hourly.empty:
        return pd.DataFrame()
    now = hourly.attrs.get("now", hourly["datetime"].min())
    future = hourly[hourly["datetime"] >= now.normalize()].copy()
    future["Date"] = future["datetime"].dt.date
    out = future.groupby("Date").agg(
        **{"Average US AQI": ("US AQI", "mean"), "Worst US AQI": ("US AQI", "max"),
           "Average PM2.5": ("PM2.5", "mean"), "India AQI (24h)": ("India AQI", "max")}
    ).round(0).reset_index()
    return out
