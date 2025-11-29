import requests
from urllib.parse import quote_plus
from setting.constants import GEOAPIFY_KEY

def get_place_id(city):
    url = (
        f"https://api.geoapify.com/v1/geocode/search?"
        f"text={quote_plus(city)}&type=city&limit=1&apiKey={GEOAPIFY_KEY}"
    )
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()
    if len(data["features"]) == 0:
        raise ValueError("City not found")

    props = data["features"][0]["properties"]
    coords = data["features"][0]["geometry"]["coordinates"][::-1]  # lat, lon

    return props["place_id"], coords


def get_zones(place_id):
    url = (
        f"https://api.geoapify.com/v1/boundaries/consists-of?"
        f"id={place_id}&boundary=administrative&geometry=geometry_1000"
        f"&apiKey={GEOAPIFY_KEY}"
    )
    r = requests.get(url)
    r.raise_for_status()
    return r.json()
