from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from app.snapshot.patient_snapshot import get_patient_snapshot
from app.pipeline.diagnosis_pipeline import DiagnosisPipeline
from app.rag.retrieval.build_index import build_knowledge_base, is_knowledge_base_ready
from app.rag.retrieval.qdrant_service import QdrantService

app = FastAPI(
    title="Digital Twin AI API",
    description="Evidence-based clinical decision support system RAG API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PatientDiagnosisRequest(BaseModel):
    patient_id: int = Field(..., example=1, description="Patient ID to analyze")


class DiagnosisResponse(BaseModel):
    patient_id: int
    snapshot: Dict[str, Any]
    query: str
    evidence: List[Dict[str, Any]]
    diagnosis: Any


@app.get("/")
def read_root():
    qdrant_count = 0
    try:
        qdrant = QdrantService()
        qdrant_count = qdrant.get_count()
    except Exception:
        pass

    return {
        "status": "online",
        "system": "Digital Twin AI Support System",
        "knowledge_base": {
            "ready": is_knowledge_base_ready(),
            "indexed_chunks": qdrant_count,
        },
    }


@app.get("/api/v1/patients/{patient_id}")
def get_patient_info(patient_id: int):
    try:
        snapshot = get_patient_snapshot(patient_id)
        return snapshot
    except Exception as e:
        raise HTTPException(
            status_code=404, detail=f"Patient ID {patient_id} not found: {str(e)}"
        )


@app.post("/api/v1/diagnosis/run", response_model=DiagnosisResponse)
def run_diagnosis(request: PatientDiagnosisRequest):
    try:
        pipeline = DiagnosisPipeline()
        result = pipeline.run(request.patient_id)
        return DiagnosisResponse(
            patient_id=result["patient_id"],
            snapshot=result["snapshot"],
            query=result["query"],
            evidence=result["evidence"],
            diagnosis=result["diagnosis"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Pipeline failure for patient {request.patient_id}: {str(e)}"
        )


@app.post("/api/v1/knowledge/sync")
def sync_knowledge_base(background_tasks: BackgroundTasks):
    background_tasks.add_task(build_knowledge_base, force=True)
    return {
        "status": "triggered",
        "message": "Knowledge base rebuild initiated in background.",
    }
