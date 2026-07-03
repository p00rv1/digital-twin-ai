from app.snapshot.patient_snapshot import get_patient_snapshot

class QueryBuilder:

    def __init__(self):
        pass

    def build(self, patient_id):

        snapshot = get_patient_snapshot(patient_id)

        parts = []

        for biomarker, info in snapshot["biomarkers"].items():

            analytics = info["analytics"]

            if analytics is None:
                continue

            latest = analytics["latest"]

            change = analytics["percent_change"]

            parts.append(
                f"{biomarker} latest {latest}"
            )

            if abs(change) > 5:

                if change > 0:

                    parts.append(
                        f"{biomarker} increased by {change}%"
                    )

                else:

                    parts.append(
                        f"{biomarker} decreased by {abs(change)}%"
                    )

        query = (
            "Patient liver biomarkers. "
            + ". ".join(parts)
            + ". Find peer reviewed literature discussing diagnosis, prognosis, biomarker interpretation and treatment."
        )

        return query