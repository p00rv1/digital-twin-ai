
from app.services.analytics_service import (
    get_biomarker_analytics)
LIVER_MARKERS = [
    "tbil",
    "dbil",
    "alp",
    "alt",
    "ast",
    "albumin",
    "ag_ratio"
]
def get_patient_snapshot(
    patient_id
):

    snapshot = {}

    for marker in LIVER_MARKERS:

        snapshot[marker] = (
            get_biomarker_analytics(
                patient_id,
                marker
            )
        )

    return snapshot