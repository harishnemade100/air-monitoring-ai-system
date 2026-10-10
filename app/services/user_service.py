"""Accounts, saved cities and user preferences."""
import re
from datetime import datetime, timezone

from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from models.users import SavedCity, User
from utils.database import get_session

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
USERNAME_RE = re.compile(r"^[a-z0-9_]{3,30}$")


def _user_dict(user: User) -> dict:
    return {"id": user.id, "username": user.username, "email": user.email,
            "health_profile": user.health_profile or "General public",
            "alert_threshold": user.alert_threshold or 150}


def register_user(username: str, email: str, password: str) -> tuple[bool, str]:
    username, email = username.strip().lower(), email.strip().lower()
    if not USERNAME_RE.match(username):
        return False, "Username must be 3–30 characters: letters, numbers or _."
    if not EMAIL_RE.match(email):
        return False, "Enter a valid email address."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    with get_session() as db:
        db.add(User(username=username, email=email, password_hash=generate_password_hash(password)))
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            return False, "That username or email is already registered."
    return True, "Account created."


def login_user(username_or_email: str, password: str) -> dict | None:
    key = username_or_email.strip().lower()
    with get_session() as db:
        user = db.query(User).filter(or_(func.lower(User.username) == key, func.lower(User.email) == key)).first()
        if not user or not check_password_hash(user.password_hash, password):
            return None
        user.last_login = datetime.now(timezone.utc)
        db.commit()
        return _user_dict(user)


def update_preferences(user_id: int, health_profile: str, alert_threshold: int) -> None:
    with get_session() as db:
        user = db.get(User, user_id)
        if user:
            user.health_profile, user.alert_threshold = health_profile, int(alert_threshold)
            db.commit()


def list_saved_cities(user_id: int) -> list[dict]:
    with get_session() as db:
        rows = db.query(SavedCity).filter(SavedCity.user_id == user_id).order_by(SavedCity.city_name).all()
        return [{"city": r.city_name, "coords": (r.latitude, r.longitude)} for r in rows]


def save_city(user_id: int, city: str, coords: tuple[float, float]) -> bool:
    with get_session() as db:
        db.add(SavedCity(user_id=user_id, city_name=city.strip().title(), latitude=coords[0], longitude=coords[1]))
        try:
            db.commit()
            return True
        except IntegrityError:
            db.rollback()
            return False


def remove_city(user_id: int, city: str) -> None:
    with get_session() as db:
        db.query(SavedCity).filter(SavedCity.user_id == user_id, SavedCity.city_name == city).delete()
        db.commit()
