from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class PatientInfo(BaseModel):

    patient_id: int

    name: str

    age: int

    gender: str


class HistoryPoint(BaseModel):

    timestamp: datetime

    biomarker: str

    value: float


class AnalyticsSummary(BaseModel):

    biomarker: str

    first: float

    latest: float

    minimum: float

    maximum: float

    mean: float

    percent_change: float


class PatientSnapshotModel(BaseModel):

    patient: PatientInfo

    biomarker: str

    history: List[HistoryPoint]

    analytics: AnalyticsSummary