from pathlib import Path

import faiss
import numpy as np


class FAISSIndex:

    def __init__(self):

        root = Path(__file__).resolve().parents[3]

        self.embedding_dir = (
            root / "knowledge" / "embeddings"
        )

        self.index_dir = (
            root / "knowledge" / "indexes"
        )

        self.index_dir.mkdir(
            parents=True,
            exist_ok=True
        )

    def load_vectors(self):

        return np.load(
            self.embedding_dir /
            "chunk_vectors.npy"
        )
    def build(self):

        vectors = self.load_vectors()

        dimension = vectors.shape[1]

        index = faiss.IndexFlatIP(
            dimension
        )

        index.add(vectors)

        print(
            f"Indexed {index.ntotal} vectors"
        )

        faiss.write_index(

            index,

            str(

                self.index_dir /

                "faiss.index"

            )
        )

    def load(self):

        return faiss.read_index(

            str(

                self.index_dir /

                "faiss.index"

            )

        )