from app.services.history_service import get_history
from app.services.analytics_service import get_biomarker_analytics

from app.config.biomarkers import LIVER_MARKERS


def get_patient_snapshot(patient_id):

    snapshot = {

        "patient_id": patient_id,

        "biomarkers": {}

    }

    for biomarker in LIVER_MARKERS:

        history = get_history(

            patient_id,

            biomarker

        )

        analytics = get_biomarker_analytics(

            patient_id,

            biomarker

        )

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

    return snapshot