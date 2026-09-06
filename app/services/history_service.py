from app.database.db import SessionLocal
from app.database.models import (
    Report,
    Measurement,
    Biomarker
)

def get_history(
    patient_id,
    biomarker_name
):
    db = SessionLocal()

    rows = (
        db.query(
            Report.report_date,
            Measurement.value
        )

        .join(
            Measurement,
            Report.id ==
            Measurement.report_id
        )

        .join(
            Biomarker,
            Measurement.biomarker_id ==
            Biomarker.id
        )

        .filter(
            Report.patient_id ==
            patient_id
        )

        .filter(
            Biomarker.name ==
            biomarker_name
        )

        .order_by(
            Report.report_date
        )
        .all()
    )
    db.close()
    return rows

def get_all_patient_history(patient_id):
    """
    Fetches all historical biomarker measurements for a patient in a single database query.
    Returns a dict mapping biomarker_name -> list of (report_date, value) tuples.
    """
    db = SessionLocal()
    try:
        rows = (
            db.query(
                Biomarker.name,
                Report.report_date,
                Measurement.value
            )
            .join(Measurement, Report.id == Measurement.report_id)
            .join(Biomarker, Measurement.biomarker_id == Biomarker.id)
            .filter(Report.patient_id == patient_id)
            .order_by(Report.report_date)
            .all()
        )
        history_map = {}
        for bm_name, r_date, val in rows:
            history_map.setdefault(bm_name, []).append((r_date, val))
        return history_map
    except Exception as e:
        print(f"Warning: get_all_patient_history failed ({e})")
        return {}
    finally:
        db.close()