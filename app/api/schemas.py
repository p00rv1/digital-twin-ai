from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(example="healthy")
    database: str = Field(example="connected")
    timestamp: str = Field(example="2026-09-01 15:30:00")


class PatientSnapshotResponse(BaseModel):
    patient_id: int = Field(example=1)
    age: int = Field(example=65)
    gender: str = Field(example="Female")
    biomarkers: Dict[str, Any]
    clinical_scores: Dict[str, Any]


class DiagnosisResponse(BaseModel):
    patient_id: int = Field(example=1)
    snapshot: Dict[str, Any]
    query: str = Field(example="Patient liver biomarkers ALT latest 16.5...")
    evidence: List[Dict[str, Any]]
    diagnosis: Dict[str, Any]
    retrieval_quality: str = Field(example="HIGH")
    avg_relevance_score: float = Field(example=0.553)
    crag_triggered: bool = Field(example=False)
    expanded_queries: List[str] = Field(default_factory=list)
