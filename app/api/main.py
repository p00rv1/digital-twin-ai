import time
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.database.db import get_db, SessionLocal
from app.snapshot.patient_snapshot import get_patient_snapshot
from app.pipeline.diagnosis_pipeline import DiagnosisPipeline
from app.api.schemas import HealthResponse, PatientSnapshotResponse, DiagnosisResponse

app = FastAPI(
    title="🧬 Digital Twin AI — Clinical Decision Support API",
    description="Evidence-based liver health decision support system using Hybrid RAG, CRAG, and Groq LLM reasoning.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for external web dashboards, mobile apps, and microservices
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy singleton initialization for pipeline
_pipeline = None


def get_pipeline():
    global _pipeline
    if _pipeline is None:
        _pipeline = DiagnosisPipeline()
    return _pipeline


@app.get("/", tags=["System"])
def root():
    return {
        "title": "🧬 Digital Twin AI CDSS API",
        "status": "running",
        "documentation": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", response_model=HealthResponse, tags=["System"])
def health_check():
    db_status = "disconnected"
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        database=db_status,
        timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
    )


@app.get("/api/v1/patients/{patient_id}/snapshot", response_model=PatientSnapshotResponse, tags=["Patient Analytics"])
def get_snapshot(patient_id: int):
    try:
        snapshot = get_patient_snapshot(patient_id)
        return PatientSnapshotResponse(
            patient_id=snapshot["patient_id"],
            age=snapshot.get("age", 45),
            gender=snapshot.get("gender", "Unknown"),
            biomarkers=snapshot.get("biomarkers", {}),
            clinical_scores=snapshot.get("clinical_scores", {})
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate patient snapshot: {str(e)}"
        )


@app.post("/api/v1/patients/{patient_id}/analyze", response_model=DiagnosisResponse, tags=["Clinical RAG Pipeline"])
def analyze_patient(patient_id: int, pipeline: DiagnosisPipeline = Depends(get_pipeline)):
    try:
        result = pipeline.run(patient_id)
        return DiagnosisResponse(
            patient_id=result["patient_id"],
            snapshot=result["snapshot"],
            query=result["query"],
            evidence=result["evidence"],
            diagnosis=result["diagnosis"] if isinstance(result["diagnosis"], dict) else {"diagnosis": str(result["diagnosis"])},
            retrieval_quality=result.get("retrieval_quality", "HIGH"),
            avg_relevance_score=float(result.get("avg_relevance_score", 0.0)),
            crag_triggered=bool(result.get("crag_triggered", False)),
            expanded_queries=result.get("expanded_queries", [])
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline execution failed: {str(e)}"
        )
