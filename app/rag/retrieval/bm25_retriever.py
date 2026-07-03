

from pathlib import Path
import json
import pickle

import nltk


class BM25Retriever:

    def __init__(self):

        root = Path(__file__).resolve().parents[3]

        index_dir = root / "knowledge" / "indexes"

        embedding_dir = root / "knowledge" / "embeddings"

        with open(
            index_dir / "bm25.pkl",
            "rb"
        ) as f:

            self.bm25 = pickle.load(f)

        self.lookup = json.load(

            open(
                index_dir /
                "bm25_lookup.json",
                encoding="utf-8"
            )

        )

        self.metadata = json.load(

            open(
                embedding_dir /
                "metadata_by_id.json",
                encoding="utf-8"
            )

        )


    def retrieve(
        self,
        query,
        k=10
    ):

        query_tokens = nltk.word_tokenize(

            query.lower()

        )

        scores = self.bm25.get_scores(

            query_tokens

        )

        ranked = sorted(

            enumerate(scores),

            key=lambda x: x[1],

            reverse=True

        )[:k]

        results = []

        for idx, score in ranked:

            chunk_id = self.lookup[idx]

            chunk = self.metadata[chunk_id]

            results.append(

                {

                    "score": float(score),

                    **chunk

                }

            )

        return results