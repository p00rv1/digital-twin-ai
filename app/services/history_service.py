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