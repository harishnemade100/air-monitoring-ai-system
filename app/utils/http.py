"""Small helper so every API call has a timeout and returns None instead of crashing."""
import requests

from setting.constants import REQUEST_TIMEOUT


def get_json(url: str, params: dict | None = None):
    try:
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None
