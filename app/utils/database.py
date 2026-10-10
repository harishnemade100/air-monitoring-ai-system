"""Database connection (cloud PostgreSQL such as Neon or Supabase)."""
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from setting.constants import DATABASE_URL

Base = declarative_base()


def _normalize_url(url: str) -> str:
    """Neon/Supabase URLs start with postgresql:// or postgres://.
    Tell SQLAlchemy to use the psycopg (v3) driver."""
    url = url.strip()
    for prefix in ("postgres://", "postgresql://", "postgresql+psycopg2://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix):]
    return url


@st.cache_resource(show_spinner="Connecting to the database…")
def get_engine():
    """One shared connection pool; creates tables on first run."""
    import models.users  # noqa: F401  (registers the tables on Base)

    engine = create_engine(_normalize_url(DATABASE_URL), pool_pre_ping=True, pool_size=5, max_overflow=5)
    Base.metadata.create_all(bind=engine)
    return engine


def get_session():
    """Open a database session. Use with `with get_session() as db:`."""
    return sessionmaker(bind=get_engine(), autoflush=False, expire_on_commit=False)()
