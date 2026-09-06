import os

class MedicalReranker:

    def __init__(self):
        self.model_name = "BAAI/bge-reranker-base"
        self._model = None

    @property
    def model(self):
        """Lazy load CrossEncoder model only when reranking is required."""
        if self._model is None:
            try:
                import torch
                threads = max(1, os.cpu_count() or 4)
                torch.set_num_threads(threads)
            except Exception:
                pass
            from sentence_transformers import CrossEncoder
            self._model = CrossEncoder(self.model_name)
        return self._model

    def rerank(
        self,
        query,
        documents,
        top_k=5
    ):
        if not documents or len(documents) == 0:
            return []

        # Limit candidate reranking pool to top 12 chunks for high speed while maintaining accuracy
        candidate_docs = documents[:12]

        pairs = [
            (query, doc.get("text", ""))
            for doc in candidate_docs
        ]

        scores = self.model.predict(
            pairs,
            batch_size=12
        )

        for score, doc in zip(scores, candidate_docs):
            doc["rerank_score"] = float(score)

        candidate_docs.sort(
            key=lambda x: x["rerank_score"],
            reverse=True
        )

        return candidate_docs[:top_k]