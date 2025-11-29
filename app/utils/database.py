import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from setting.constants import USER_NAME, PASSWORD, HOST, PORT, DATABASE_NAME

# Encode password for URL
password = urllib.parse.quote_plus(PASSWORD)

DATABASE_URL = f"postgresql+psycopg2://{USER_NAME}:{password}@{HOST}:{PORT}/{DATABASE_NAME}"

# SQLAlchemy engine and session
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
