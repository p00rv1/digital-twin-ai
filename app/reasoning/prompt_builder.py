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

        for biomarker, info in snapshot["biomarkers"].items():

            analytics = info["analytics"]

            if analytics is None:
                continue

            prompt.append(
                f"""
Biomarker : {biomarker}
Latest    : {analytics['latest']}
First     : {analytics['first']}
Minimum   : {analytics['min']}
Maximum   : {analytics['max']}
Mean      : {analytics['mean']}
Change    : {analytics['percent_change']}%
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