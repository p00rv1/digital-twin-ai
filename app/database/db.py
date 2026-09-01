import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DEFAULT_DB_URL = "postgresql://postgres:poorvi@localhost:5434/health_twin"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300
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