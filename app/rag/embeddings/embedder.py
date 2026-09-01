import re
import gc

ABBREVIATION_MAP = {
    r"\btbil\b": "total bilirubin",
    r"\bdbil\b": "direct bilirubin",
    r"\balp\b": "alkaline phosphatase",
    r"\balt\b": "alanine aminotransferase",
    r"\bast\b": "aspartate aminotransferase",
    r"\btotal_proteins\b": "total proteins",
    r"\balbumin\b": "albumin",
    r"\bag_ratio\b": "albumin globulin ratio",
}


def normalize_clinical_text(text: str) -> str:
    """Expands clinical abbreviations to improve biomedical semantic embedding matching."""
    text_lower = text.lower()
    for pattern, replacement in ABBREVIATION_MAP.items():
        text_lower = re.sub(pattern, replacement, text_lower)
    return text_lower


class MedicalEmbedder:

    def __init__(self):
        self.model_name = "NeuML/pubmedbert-base-embeddings"
        self._model = None

    @property
    def model(self):
        """Lazy load SentenceTransformer model only when embedding generation is required."""
        if self._model is None:
            try:
                import torch
                torch.set_num_threads(1)
            except Exception:
                pass
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def normalize(self, text: str) -> str:
        return normalize_clinical_text(text)

    def embed(self, text: str):
        normalized = self.normalize(text)
        vector = self.model.encode(
            normalized,
            normalize_embeddings=True
        )
        gc.collect()
        return vector

    def embed_batch(self, texts: list[str], batch_size: int = 32):
        normalized_texts = [self.normalize(t) for t in texts]
        vectors = self.model.encode(
            normalized_texts,
            batch_size=batch_size,
            show_progress_bar=True,
            normalize_embeddings=True
        )
        gc.collect()
        return vectors

