from dataclasses import dataclass


@dataclass
class EmbeddingRecord:

    chunk_id: str

    vector: list