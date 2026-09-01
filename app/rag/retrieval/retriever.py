from pathlib import Path

import json

import numpy as np

from app.rag.embeddings.embedder import MedicalEmbedder
from .faiss_index import FAISSIndex


class MedicalRetriever:

    def __init__(self):

        root = Path(__file__).resolve().parents[3]

        embedding_dir = root / "knowledge" / "embeddings"

        self.lookup = json.load(
            open(
                embedding_dir / "chunk_lookup.json",
                encoding="utf-8"
            )
        )

        self.metadata = json.load(
            open(
                embedding_dir / "metadata_by_id.json",
                encoding="utf-8"
            )
        )

        self.embedder = MedicalEmbedder()
        self.index = FAISSIndex().load()

    def embed_query(
        self,
        query
    ):
        vector = self.embedder.embed(query)

        return np.array(
            [vector],
            dtype=np.float32
        )
    def search(

        self,

        query,

        k=10

    ):

        vector = self.embed_query(

            query

        )

        scores, indices = self.index.search(

            vector,

            k

        )

        return scores[0], indices[0]
    def retrieve(

        self,

        query,

        k=10

    ):

        scores, indices = self.search(

            query,

            k

        )

        results = []

        for score, idx in zip(

            scores,

            indices

        ):

            if idx == -1:

                continue

            chunk_id = self.lookup[

                str(idx)

            ]

            chunk = self.metadata[

                chunk_id

            ]

            results.append(

                {

                    "score": float(score),

                    **chunk

                }

            )

        return results
