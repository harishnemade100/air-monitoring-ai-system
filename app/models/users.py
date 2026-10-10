"""Database tables. Names use an `aqi_` prefix so they never clash with other projects in the same database."""
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint

from utils.database import Base


def _now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "aqi_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)          # hashed, never plain text
    role = Column(String, default="user")
    health_profile = Column(String, default="General public")
    alert_threshold = Column(Integer, default=150)          # warn when AQI goes above this
    created_at = Column(DateTime(timezone=True), default=_now)
    last_login = Column(DateTime(timezone=True), default=_now)


class SavedCity(Base):
    __tablename__ = "aqi_saved_cities"
    __table_args__ = (UniqueConstraint("user_id", "city_name"),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("aqi_users.id", ondelete="CASCADE"), nullable=False)
    city_name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_now)
