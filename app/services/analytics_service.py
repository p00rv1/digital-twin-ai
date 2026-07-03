from statistics import mean

from app.services.history_service import (
    get_history
)
def get_biomarker_analytics(
    patient_id,
    biomarker
):
    history = get_history(
        patient_id,
        biomarker
    )

    if not history:
        return None

    values = [
        float(row[1])
        for row in history
    ]

    first = values[0]
    latest = values[-1]

    change = (
        ((latest-first)/first)*100
        if first != 0
        else 0
    )

    return {
        "biomarker": biomarker,
        "first": first,
        "latest": latest,
        "min": min(values),
        "max": max(values),
        "mean": mean(values),
        "percent_change": round(
            change,
            2
        )
    }
