from pathlib import Path
from typing import List, Dict, Any, Optional
import uuid

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import (
        VectorParams,
        Distance,
        PointStruct,
        Filter,
        FieldCondition,
        MatchValue,
    )
except ImportError:
    QdrantClient = None


class QdrantService:
    COLLECTION_NAME = "medical_literature"
    VECTOR_SIZE = 384  # BAAI/bge-small-en-v1.5 dimension

    def __init__(self):
        root = Path(__file__).resolve().parents[3]
        self.db_path = root / "knowledge" / "qdrant_db"
        self.db_path.mkdir(parents=True, exist_ok=True)
        self.client = QdrantClient(path=str(self.db_path))
        self.ensure_collection()

    def ensure_collection(self):
        collections = [c.name for c in self.client.get_collections().collections]
        if self.COLLECTION_NAME not in collections:
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=self.VECTOR_SIZE,
                    distance=Distance.COSINE,
                ),
            )

    def is_indexed(self) -> bool:
        return self.get_count() > 0

    def get_existing_paper_ids(self) -> set:
        existing_ids = set()
        try:
            scroll_res = self.client.scroll(
                collection_name=self.COLLECTION_NAME,
                limit=10000,
                with_payload=True,
                with_vectors=False,
            )
            points, _ = scroll_res
            for point in points:
                if point.payload and "paper_id" in point.payload:
                    existing_ids.add(point.payload["paper_id"])
        except Exception:
            pass
        return existing_ids

    def get_count(self) -> int:
        try:
            res = self.client.count(collection_name=self.COLLECTION_NAME)
            return res.count
        except Exception:
            return 0

    def upsert_chunks(self, chunks: List[Dict[str, Any]], vectors: List[List[float]]):
        points = []
        for chunk, vector in zip(chunks, vectors):
            chunk_id = chunk.get("chunk_id", str(uuid.uuid4()))
            # Convert string UUID to standard format for Qdrant point id or use string
            points.append(
                PointStruct(
                    id=chunk_id,
                    vector=vector if isinstance(vector, list) else vector.tolist(),
                    payload=chunk,
                )
            )

        # Batch upsert into Qdrant
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i : i + batch_size]
            self.client.upsert(
                collection_name=self.COLLECTION_NAME,
                points=batch,
            )

    def search(
        self,
        query_vector: List[float],
        k: int = 10,
        biomarker: Optional[str] = None,
        organ: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        query_filter = None
        conditions = []
        if biomarker:
            conditions.append(
                FieldCondition(
                    key="biomarker", match=MatchValue(value=biomarker.lower())
                )
            )
        if organ:
            conditions.append(
                FieldCondition(key="organ", match=MatchValue(value=organ.lower()))
            )
        if conditions:
            query_filter = Filter(must=conditions)

        search_result = self.client.search(
            collection_name=self.COLLECTION_NAME,
            query_vector=query_vector if isinstance(query_vector, list) else query_vector.tolist(),
            limit=k,
            query_filter=query_filter,
        )

        results = []
        for hit in search_result:
            doc = hit.payload or {}
            doc["score"] = float(hit.score)
            results.append(doc)
        return results
