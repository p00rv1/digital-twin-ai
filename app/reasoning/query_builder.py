class QueryBuilder:

    def __init__(self):
        pass

    def build(self, snapshot):
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

    def build_expanded_queries(self, snapshot):
        """
        Generates 3 specialized sub-queries for Corrective RAG (CRAG) query expansion:
        1. Hepatocellular / Enzymatic Injury (ALT, AST, ALP)
        2. Synthetic Function & Biliary Staging (Albumin, Bilirubin, A/G ratio)
        3. Risk Stratification & Etiology (De Ritis Ratio, FIB-4 risk tier, differential diagnosis)
        """
        biomarkers = snapshot.get("biomarkers", {})
        clinical_scores = snapshot.get("clinical_scores", {})

        alt_val = biomarkers.get("alt", {}).get("analytics", {}).get("latest", "normal")
        ast_val = biomarkers.get("ast", {}).get("analytics", {}).get("latest", "normal")
        alp_val = biomarkers.get("alp", {}).get("analytics", {}).get("latest", "normal")
        tbil_val = biomarkers.get("tbil", {}).get("analytics", {}).get("latest", "normal")
        alb_val = biomarkers.get("albumin", {}).get("analytics", {}).get("latest", "normal")

        q1 = (
            f"Alanine aminotransferase (ALT: {alt_val}) and aspartate aminotransferase (AST: {ast_val}) "
            f"elevation alkaline phosphatase (ALP: {alp_val}) acute liver injury hepatocellular pattern etiology diagnosis."
        )

        q2 = (
            f"Serum albumin ({alb_val} g/dL) and total bilirubin ({tbil_val} mg/dL) "
            f"hepatic synthetic dysfunction cirrhosis staging prognosis clinical outcomes."
        )

        de_ritis = clinical_scores.get("de_ritis_ratio", "N/A")
        fib4 = clinical_scores.get("fib4_index", "N/A")

        q3 = (
            f"AST ALT ratio De Ritis ({de_ritis}) and FIB-4 index ({fib4}) "
            f"non-alcoholic fatty liver disease alcoholic hepatitis cirrhosis fibrosis risk stratification literature review."
        )

        return [q1, q2, q3]