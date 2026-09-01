from typing import List
from pydantic import BaseModel, Field


class ClinicalDiagnosis(BaseModel):
    diagnosis: str = Field(
        default="Unspecified Hepatic Condition",
        description="Most likely evidence-based clinical diagnosis"
    )
    confidence: int = Field(
        default=50,
        description="Clinical confidence score between 0 and 100"
    )
    reasoning: str = Field(
        default="Evidence analysis completed.",
        description="Step-by-step clinical justification and evidence synthesis"
    )
    supporting_biomarkers: List[str] = Field(
        default_factory=list,
        description="List of patient biomarkers supporting this diagnosis"
    )
    recommended_tests: List[str] = Field(
        default_factory=list,
        description="List of recommended follow-up laboratory tests, imaging, or diagnostic evaluations"
    )
    supporting_papers: List[str] = Field(
        default_factory=list,
        description="List of supporting medical research paper titles or PMCIDs"
    )
