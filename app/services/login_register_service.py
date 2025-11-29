import streamlit as st
from utils.database import SessionLocal, Base, engine
from models.users import User
from sqlalchemy.exc import IntegrityError
from datetime import datetime

# Create tables if missing
Base.metadata.create_all(bind=engine)

def login_register_page():
    st.title("🔐 Login / Register")

    menu = ["Login", "Register"]
    choice = st.radio("Go to", menu)

    db = SessionLocal()

    if choice == "Login":
        st.subheader("Login Section")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = db.query(User).filter(User.username == username, User.password == password).first()
            if user:
                user.last_login = datetime.utcnow()
                db.commit()
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.success(f"Welcome {username}!")
            else:
                st.error("Invalid username or password")

    elif choice == "Register":
        st.subheader("Create New Account")
        new_username = st.text_input("Username", key="reg_user")
        new_email = st.text_input("Email")
        new_password = st.text_input("Password", type="password", key="reg_pass")

        if st.button("Register"):
            new_user = User(
                username=new_username,
                password=new_password,
                email=new_email
            )
            try:
                db.add(new_user)
                db.commit()
                st.success("Account created successfully! Please login.")
            except IntegrityError:
                db.rollback()
                st.error("Username or email already exists!")
