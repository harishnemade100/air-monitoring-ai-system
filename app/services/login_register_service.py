"""Login and registration screen."""
import streamlit as st

from services.user_service import login_user, register_user
from setting.constants import APP_TITLE


def _do_login():
    user = login_user(st.session_state.get("login_user", ""), st.session_state.get("login_pass", ""))
    if user:
        st.session_state.update(logged_in=True, user=user, auth_message=None)
    else:
        st.session_state.auth_message = ("error", "Invalid username/email or password.")


def _do_register():
    if st.session_state.get("reg_pass") != st.session_state.get("reg_confirm"):
        st.session_state.auth_message = ("error", "Passwords don't match.")
        return
    ok, message = register_user(st.session_state.get("reg_user", ""), st.session_state.get("reg_email", ""),
                                st.session_state.get("reg_pass", ""))
    if ok:
        user = login_user(st.session_state["reg_user"], st.session_state["reg_pass"])
        st.session_state.update(logged_in=True, user=user, auth_message=None)
    else:
        st.session_state.auth_message = ("error", message)


def login_register_page():
    st.title(f"🌍 {APP_TITLE}")
    st.caption("Live air quality, forecasts and personalised health advice for Indian cities.")

    login_tab, register_tab = st.tabs(["🔐 Log in", "📝 Create account"])
    with login_tab:
        with st.form("login_form"):
            st.text_input("Username or email", key="login_user")
            st.text_input("Password", type="password", key="login_pass")
            st.form_submit_button("Log in", type="primary", on_click=_do_login)
    with register_tab:
        with st.form("register_form"):
            st.text_input("Username", key="reg_user", help="3–30 characters: letters, numbers or _")
            st.text_input("Email", key="reg_email")
            st.text_input("Password", type="password", key="reg_pass", help="At least 6 characters")
            st.text_input("Confirm password", type="password", key="reg_confirm")
            st.form_submit_button("Create account", type="primary", on_click=_do_register)

    if st.session_state.get("auth_message"):
        kind, text = st.session_state.auth_message
        getattr(st, kind)(text)
