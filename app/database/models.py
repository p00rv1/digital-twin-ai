from sqlalchemy import *
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True)

    age = Column(Integer)

    gender = Column(String)
class Biomarker(Base):
    __tablename__ = "biomarkers"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    category = Column(String)


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer)
    report_date = Column(Date)


class Measurement(Base):
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True)

    report_id = Column(Integer)

    biomarker_id = Column(Integer)

    value = Column(Float)