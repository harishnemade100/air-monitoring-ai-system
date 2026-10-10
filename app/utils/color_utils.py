"""
AQI colours and labels.

Two AQI scales are used:
- US EPA AQI (what WAQI and Open-Meteo report): Good, Moderate, ... Hazardous
- India National AQI (CPCB NAQI): Good, Satisfactory, Moderate, Poor, Very Poor, Severe
"""


def to_int(value):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


# ---------------- US EPA AQI ----------------
def aqi_color(aqi):
    aqi = to_int(aqi)
    if aqi is None:
        return "#808080"
    if aqi <= 50: return "#00e400"
    if aqi <= 100: return "#ffff00"
    if aqi <= 150: return "#ff7e00"
    if aqi <= 200: return "#ff0000"
    if aqi <= 300: return "#8f3f97"
    return "#7e0023"


def aqi_health_label(aqi):
    aqi = to_int(aqi)
    if aqi is None:
        return "Not available"
    if aqi <= 50: return "Good"
    if aqi <= 100: return "Moderate"
    if aqi <= 150: return "Unhealthy for Sensitive Groups"
    if aqi <= 200: return "Unhealthy"
    if aqi <= 300: return "Very Unhealthy"
    return "Hazardous"


# ---------------- INDIA NATIONAL AQI (CPCB) ----------------
# (concentration low, concentration high, index low, index high) for 24-hour averages in µg/m³
_NAQI_BREAKPOINTS = {
    "pm2_5": [(0, 30, 0, 50), (30, 60, 50, 100), (60, 90, 100, 200),
              (90, 120, 200, 300), (120, 250, 300, 400), (250, 380, 400, 500)],
    "pm10": [(0, 50, 0, 50), (50, 100, 50, 100), (100, 250, 100, 200),
             (250, 350, 200, 300), (350, 430, 300, 400), (430, 510, 400, 500)],
}

NAQI_CATEGORIES = [  # (upper index, label, colour)
    (50, "Good", "#00b050"),
    (100, "Satisfactory", "#92d050"),
    (200, "Moderate", "#ffd700"),
    (300, "Poor", "#ff9900"),
    (400, "Very Poor", "#ff0000"),
    (500, "Severe", "#c00000"),
]


def naqi_sub_index(pollutant: str, concentration):
    """Convert a PM2.5 or PM10 concentration into India's AQI sub-index (0–500)."""
    if concentration is None:
        return None
    try:
        c = max(float(concentration), 0.0)
    except (TypeError, ValueError):
        return None
    if c != c:  # NaN
        return None
    for c_lo, c_hi, i_lo, i_hi in _NAQI_BREAKPOINTS[pollutant]:
        if c <= c_hi:
            return round(i_lo + (c - c_lo) * (i_hi - i_lo) / (c_hi - c_lo))
    return 500


def india_aqi(pm2_5, pm10):
    """India NAQI from PM2.5 and PM10 (the highest sub-index wins). Returns (value, dominant pollutant)."""
    subs = {"PM2.5": naqi_sub_index("pm2_5", pm2_5), "PM10": naqi_sub_index("pm10", pm10)}
    subs = {k: v for k, v in subs.items() if v is not None}
    if not subs:
        return None, None
    dominant = max(subs, key=subs.get)
    return subs[dominant], dominant


def naqi_category(index):
    index = to_int(index)
    if index is None:
        return "Not available", "#808080"
    for upper, label, colour in NAQI_CATEGORIES:
        if index <= upper:
            return label, colour
    return NAQI_CATEGORIES[-1][1], NAQI_CATEGORIES[-1][2]
