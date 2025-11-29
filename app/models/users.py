from sqlalchemy import Column, Integer, String, DateTime
from utils.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)  # Store hashed passwords in production!
    email = Column(String, unique=True, nullable=False)
    role = Column(String, default="user")
    last_login = Column(DateTime, default=datetime.utcnow)