"""
Air Monitoring AI System — entry point.
Run locally:   streamlit run app/app.py
"""
import streamlit as st

st.set_page_config(page_title="Air Monitoring AI System", page_icon="🌍", layout="wide")

from setting.constants import REQUIRED_SECRETS  # noqa: E402

missing = [name for name, value in REQUIRED_SECRETS.items() if not value]
if missing:
    st.error(f"Missing secrets: {', '.join(missing)}. On Streamlit Cloud open Settings → Secrets and add them.")
    st.stop()

from main_dashboard import show_dashboard  # noqa: E402
from services.login_register_service import login_register_page  # noqa: E402
from utils.database import get_engine  # noqa: E402

try:
    get_engine()
except Exception as e:
    st.error(f"Couldn't connect to the database. Check DATABASE_URL in your secrets.\n\nDetails: {e}")
    st.stop()

if not st.session_state.get("logged_in"):
    login_register_page()
else:
    show_dashboard()
