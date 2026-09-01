from typing import List, Dict, Tuple


class RelevanceEvaluator:
    """
    Evaluates document relevance scores produced by the Cross-Encoder Reranker
    to determine if the retrieved evidence is sufficient or if CRAG query expansion is required.
    """

    def __init__(self, high_threshold: float = 0.55, low_threshold: float = 0.35):
        self.high_threshold = high_threshold
        self.low_threshold = low_threshold

    def evaluate(self, evidence: List[Dict]) -> Tuple[str, float]:
        """
        Computes average relevance score of top retrieved papers and returns (quality_label, average_score).
        Quality Labels:
          - "HIGH": average score >= 0.55
          - "MEDIUM": 0.35 <= average score < 0.55
          - "LOW": average score < 0.35
        """
        if not evidence or len(evidence) == 0:
            return "LOW", 0.0

        scores = []
        for paper in evidence:
            score = paper.get("rerank_score") if paper.get("rerank_score") is not None else paper.get("score", 0.0)
            scores.append(float(score))

        avg_score = sum(scores) / len(scores)

        if avg_score >= self.high_threshold:
            quality = "HIGH"
        elif avg_score >= self.low_threshold:
            quality = "MEDIUM"
        else:
            quality = "LOW"

        return quality, round(avg_score, 3)
