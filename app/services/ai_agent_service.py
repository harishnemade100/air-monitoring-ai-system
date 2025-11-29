import requests
from setting.constants import DEEPAI_API_KEY, NEWSAPI_KEY


# ---------------- DEEPAI AI ADVISORY ----------------
def get_ai_suggestion_deepai(city, zone, aqi, temp, humidity):
    """
    Generate short news-style advisory based on AQI, temperature, humidity, and zone.
    """
    prompt = f"""
    You are an environmental assistant.
    The user is in {zone}, {city}.
    Current conditions:
    AQI: {aqi}
    Temperature: {temp}°C
    Humidity: {humidity}%
    Provide a short, actionable news-style advisory for residents.
    """
    try:
        response = requests.post(
            "https://api.deepai.org/api/text-generator",
            data={'text': prompt},
            headers={'api-key': DEEPAI_API_KEY}
        )
        result = response.json()
        return result.get('output', "No AI advisory available at the moment.")
    except Exception as e:
        return f"No AI advisory available. Error: {str(e)}"

# ---------------- NEWSAPI POLLUTION NEWS ----------------
def get_local_pollution_news(city):
    """
    Fetch latest pollution/environment news for the city.
    Uses multiple queries to ensure at least 1 article.
    """
    queries = [f"air pollution {city}", f"pollution {city}", f"environment {city}"]
    for q in queries:
        url = f"https://newsapi.org/v2/everything?q={q}&apiKey={NEWSAPI_KEY}&language=en&pageSize=1"
        try:
            res = requests.get(url).json()
            articles = res.get("articles", [])
            if articles:
                article = articles[0]
                return f"{article['title']} - {article['source']['name']}"
        except:
            continue
    return "No recent pollution news available."

# ---------------- COMBINED ADVISORY ----------------
def get_combined_advisory(city, zone, aqi, temp, humidity):
    """
    Combine AI advisory and latest news for dashboard display.
    """
    ai_advice = get_ai_suggestion_deepai(city, zone, aqi, temp, humidity)
    news = get_local_pollution_news(city)

    combined = f"{ai_advice}\n\n📰 Latest Pollution News: {news}"
    return combined
