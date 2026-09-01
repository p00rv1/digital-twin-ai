import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DEFAULT_DB_URL = "postgresql://postgres:poorvi@localhost:5434/health_twin"
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    try:
        import streamlit as st
        if "DATABASE_URL" in st.secrets:
            DATABASE_URL = st.secrets["DATABASE_URL"]
    except Exception:
        pass

if not DATABASE_URL:
    DATABASE_URL = DEFAULT_DB_URL

# Enable connect_timeout=5 to fail fast instead of hanging on unreachable database URLs
connect_args = {}
if "postgresql" in DATABASE_URL:
    connect_args["connect_timeout"] = 5

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args=connect_args
)


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