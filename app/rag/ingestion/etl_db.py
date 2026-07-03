from pathlib import Path
from datetime import datetime

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
)

from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

ROOT = Path(__file__).resolve().parents[3]

DB_PATH = ROOT / "knowledge" / "etl.db"

DB_PATH.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    echo=False
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

Base = declarative_base()


class Document(Base):

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)

    document_id = Column(String, unique=True, nullable=False)

    pmcid = Column(String)

    pmid = Column(String)

    doi = Column(String)

    title = Column(String)

    journal = Column(String)

    year = Column(Integer)

    biomarker = Column(String)

    organ = Column(String)

    status = Column(String)

    version = Column(Integer, default=1)

    downloaded = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)


class PipelineRun(Base):

    __tablename__ = "pipeline_runs"

    id = Column(Integer, primary_key=True)

    start_time = Column(DateTime, default=datetime.utcnow)

    end_time = Column(DateTime)

    downloaded = Column(Integer, default=0)

    skipped = Column(Integer, default=0)

    failed = Column(Integer, default=0)


class Failure(Base):

    __tablename__ = "failures"

    id = Column(Integer, primary_key=True)

    document_id = Column(String)

    reason = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)


def create_tables():

    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":

    create_tables()

    print("ETL database created.")