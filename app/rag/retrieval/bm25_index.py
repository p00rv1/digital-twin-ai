from pathlib import Path
import json
import pickle

import nltk
nltk.download('punkt_tab')
from rank_bm25 import BM25Okapi


class BM25Indexer:

    def __init__(self):

        root = Path(__file__).resolve().parents[3]

        self.embedding_dir = root / "knowledge" / "embeddings"

        self.index_dir = root / "knowledge" / "indexes"

        self.index_dir.mkdir(
            parents=True,
            exist_ok=True
        )

    def tokenize(self, text):

        return nltk.word_tokenize(
            text.lower()
        )

    def load_chunks(self):

        with open(

            self.embedding_dir /
            "metadata_by_id.json",

            encoding="utf-8"

        ) as f:

            return json.load(f)
    def build(self):

        metadata = self.load_chunks()

        corpus = []

        lookup = []

        for chunk_id, chunk in metadata.items():

            corpus.append(

                self.tokenize(
                    chunk["text"]
                )

            )

            lookup.append(
                chunk_id
            )

        bm25 = BM25Okapi(corpus)

        with open(

            self.index_dir /
            "bm25.pkl",

            "wb"

        ) as f:

            pickle.dump(
                bm25,
                f
            )

        with open(

            self.index_dir /
            "bm25_lookup.json",

            "w",
            encoding="utf-8"

        ) as f:

            json.dump(
                lookup,
                f,
                indent=4
            )

        print(
            f"Indexed {len(corpus)} chunks"
        )
