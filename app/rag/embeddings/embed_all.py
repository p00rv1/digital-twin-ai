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
        if not chunks:
            print("No chunks found to embed.")
            return

        texts = [chunk["text"] for chunk in chunks]
        lookup = [chunk["chunk_id"] for chunk in chunks]

        # Batched vector encoding
        print(f"Generating embeddings for {len(chunks)} chunks in batches...")
        vectors = self.embedder.model.encode(
            texts,
            batch_size=64,
            show_progress_bar=True,
            normalize_embeddings=True
        )

        # Upsert into Qdrant Vector DB
        try:
            from app.rag.retrieval.qdrant_service import QdrantService
            qdrant = QdrantService()
            qdrant.upsert_chunks(chunks, vectors)
            print(f"Upserted {len(chunks)} chunks into Qdrant Vector DB.")
        except Exception as e:
            print(f"Warning: Qdrant upsert failed ({e}), falling back to file saves.")

        vectors_np = np.array(vectors, dtype=np.float32)

        np.save(
            self.embedding_dir / "chunk_vectors.npy",
            vectors_np
        )

        with open(
            self.embedding_dir / "metadata.json",
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(chunks, f, indent=4)

        lookup_dict = {
            str(i): chunk_id
            for i, chunk_id in enumerate(lookup)
        }
        with open(
            self.embedding_dir / "chunk_lookup.json",
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(lookup_dict, f, indent=4)

        metadata_lookup = {
            chunk["chunk_id"]: chunk for chunk in chunks
        }
        with open(
            self.embedding_dir / "metadata_by_id.json",
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(metadata_lookup, f, indent=4)

        print(f"Embedded & indexed {len(chunks)} chunks.")