import streamlit as st
from services.login_register_service import login_register_page
from main_dashboard import show_dashboard  # your existing AQI dashboard code

# Initialize session
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login_register_page()
else:
    show_dashboard()
