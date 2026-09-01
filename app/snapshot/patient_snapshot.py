from app.services.history_service import get_history
from app.services.analytics_service import get_biomarker_analytics, compute_clinical_scores
from app.database.db import SessionLocal
from app.database.models import Patient
from app.config.biomarkers import LIVER_MARKERS


def get_patient_snapshot(patient_id):
    db = SessionLocal()
    patient_record = db.query(Patient).filter(Patient.id == patient_id).first()
    db.close()

    age = patient_record.age if patient_record and patient_record.age else 45
    gender = patient_record.gender if patient_record and patient_record.gender else "Unknown"

    snapshot = {
        "patient_id": patient_id,
        "age": age,
        "gender": gender,
        "biomarkers": {},
        "clinical_scores": {}
    }

    latest_biomarkers = {}

    for biomarker in LIVER_MARKERS:
        history = get_history(
            patient_id,
            biomarker
        )

        analytics = get_biomarker_analytics(
            patient_id,
            biomarker
        )

        if analytics and "latest" in analytics:
            latest_biomarkers[biomarker] = analytics["latest"]

        snapshot["biomarkers"][biomarker] = {
            "history": [
                {
                    "date": row[0],
                    "value": float(row[1])
                }
                for row in history
            ],
            "analytics": analytics
        }

    snapshot["clinical_scores"] = compute_clinical_scores(age, latest_biomarkers)

    return snapshot