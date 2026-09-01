import gc


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
                torch.set_num_threads(1)
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

        pairs = [
            (
                query,
                doc["text"]
            )
            for doc in documents
        ]

        scores = self.model.predict(
            pairs
        )

        for score, doc in zip(
            scores,
            documents
        ):
            doc["rerank_score"] = float(score)

        documents.sort(
            key=lambda x: x["rerank_score"],
            reverse=True
        )

        gc.collect()
        return documents[:top_k]