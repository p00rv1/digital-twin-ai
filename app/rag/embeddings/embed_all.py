from pathlib import Path

import json

import numpy as np

from .embedder import MedicalEmbedder


class EmbeddingPipeline:

    def __init__(self):

        root = Path(__file__).resolve().parents[3]

        self.chunk_dir = root / "knowledge" / "chunks"

        self.embedding_dir = root / "knowledge" / "embeddings"

        self.embedding_dir.mkdir(

            parents=True,

            exist_ok=True

        )

        self.embedder = MedicalEmbedder()
    def load_chunks(self):

        chunks = []

        for file in self.chunk_dir.glob("*.json"):

            with open(

                file,

                encoding="utf-8"

            ) as f:

                chunks.extend(

                    json.load(f)

                )

        return chunks
    def build_embeddings(self):

        chunks = self.load_chunks()

        texts = [chunk["text"] for chunk in chunks]
        metadata = list(chunks)
        lookup = [chunk["chunk_id"] for chunk in chunks]

        print(f"Generating embeddings for {len(chunks)} chunks using {self.embedder.model_name}...")
        vectors = self.embedder.embed_batch(texts, batch_size=128)

        vectors = np.array(
            vectors,
            dtype=np.float32
        )

        np.save(

            self.embedding_dir /

            "chunk_vectors.npy",

            vectors

        )

        with open(

            self.embedding_dir /

            "metadata.json",

            "w",

            encoding="utf-8"

        ) as f:

            json.dump(

                metadata,

                f,

                indent=4
            )
        lookup_dict = {

        str(i): chunk_id

        for i, chunk_id

        in enumerate(lookup)

    }
        with open(

        self.embedding_dir /

        "chunk_lookup.json",

        "w",

        encoding="utf-8"

    ) as f:

            json.dump(

                lookup_dict,

                f,

                indent=4

            )
        
        metadata_lookup = {}

        for chunk in metadata:

            metadata_lookup[
                chunk["chunk_id"]
            ] = chunk
        with open(

            self.embedding_dir /

            "metadata_by_id.json",

            "w",

            encoding="utf-8"

        ) as f:

            json.dump(

                metadata_lookup,

                f,

                indent=4

            )
        print(

            f"Embedded {len(chunks)} chunks"
        )