from datetime import date
from random import uniform

from app.database.db import SessionLocal
from app.database.models import *

db = SessionLocal()

patients = db.query(Patient).all()

for patient in patients:

    first_report = (
        db.query(Report)
        .filter(
            Report.patient_id == patient.id
        )
        .first()
    )

    measurements = (
        db.query(Measurement)
        .filter(
            Measurement.report_id ==
            first_report.id
        )
        .all()
    )

    report2 = Report(
        patient_id=patient.id,
        report_date=date(2025,6,1)
    )

    db.add(report2)
    db.commit()
    db.refresh(report2)

    report3 = Report(
        patient_id=patient.id,
        report_date=date(2025,12,1)
    )

    db.add(report3)
    db.commit()
    db.refresh(report3)

    for m in measurements:

        val = float(m.value)

        val2 = val * uniform(0.95,1.10)

        val3 = val2 * uniform(0.95,1.10)

        db.add(
            Measurement(
                report_id=report2.id,
                biomarker_id=m.biomarker_id,
                value=val2
            )
        )

        db.add(
            Measurement(
                report_id=report3.id,
                biomarker_id=m.biomarker_id,
                value=val3
            )
        )
db.commit()
db.close()