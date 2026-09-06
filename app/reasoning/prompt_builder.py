from typing import List


class PromptBuilder:

    def __init__(self):
        pass

    def build(self, snapshot, evidence):

        prompt = []

        prompt.append(
            "You are an evidence-based clinical decision support assistant."
        )

        prompt.append(
            "Use ONLY the supplied research evidence."
        )

        prompt.append(
            "If evidence is insufficient, explicitly say so."
        )

        prompt.append("\n")

        prompt.append("=" * 60)

        prompt.append("PATIENT SUMMARY")

        prompt.append("=" * 60)

        prompt.append("\n")

        prompt.append(
            f"Patient ID: {snapshot['patient_id']}"
        )

        prompt.append("\n")

        prompt.append("Biomarker Summary:\n")

        for biomarker, info in snapshot.get("biomarkers", {}).items():
            analytics = info.get("analytics")
            if analytics is None:
                continue

            latest_val = analytics.get("latest", "N/A")
            first_val = analytics.get("first", latest_val)
            min_val = analytics.get("min", "N/A")
            max_val = analytics.get("max", "N/A")
            mean_val = analytics.get("mean", "N/A")
            change_val = analytics.get("percent_change", 0)

            prompt.append(
                f"""
Biomarker : {biomarker}
Latest    : {latest_val}
First     : {first_val}
Minimum   : {min_val}
Maximum   : {max_val}
Mean      : {mean_val}
Change    : {change_val}%
"""
            )

        prompt.append("\n")

        prompt.append("=" * 60)

        prompt.append("RESEARCH EVIDENCE")

        prompt.append("=" * 60)

        prompt.append("\n")

        for i, paper in enumerate(evidence, start=1):

            prompt.append(f"Paper {i}")

            prompt.append(
                f"Title: {paper.get('title','')}"
            )

            prompt.append(
                f"Journal: {paper.get('journal','')}"
            )

            prompt.append(
                f"PMCID: {paper.get('pmcid','')}"
            )

            prompt.append(
                f"Text:\n{paper.get('text','')[:1000]}"
            )

            prompt.append("\n")

        prompt.append("=" * 60)

        prompt.append("TASK")

        prompt.append("=" * 60)

        prompt.append(
"""
Using ONLY the supplied evidence:

1. Identify the most likely diagnosis.

2. Explain why.

3. Mention which biomarkers support it.

4. Mention conflicting evidence if any.

5. Suggest follow-up tests.

6. Give a confidence score from 0 to 100.

Return JSON only.

Format:

{
    "diagnosis": "",
    "confidence": 0,
    "reasoning": "",
    "supporting_biomarkers": [],
    "recommended_tests": [],
    "supporting_papers": []
}
"""
        )

        return "\n".join(prompt)