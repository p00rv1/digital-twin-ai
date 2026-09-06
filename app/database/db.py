import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

from app.config.settings import DATABASE_URL, get_secret

# Dynamically re-evaluate DATABASE_URL if st.secrets is populated during Streamlit execution
if not DATABASE_URL or "localhost" in DATABASE_URL:
    resolved = get_secret("DATABASE_URL", DATABASE_URL)
    if resolved:
        DATABASE_URL = resolved

# Enable connect_timeout=15 to allow Neon cloud database instances time to wake up from sleep
connect_args = {}
if "postgresql" in DATABASE_URL:
    connect_args["connect_timeout"] = 15

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args=connect_args
)

def init_db_tables():
    """Helper to ensure database tables are created."""
    try:
        from app.database.models import Base
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Warning: Could not auto-create database tables ({e}).")


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@contextmanager
def get_db():
    """
    Context manager for database sessions that guarantees session closure
    and prevents connection leaks.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()