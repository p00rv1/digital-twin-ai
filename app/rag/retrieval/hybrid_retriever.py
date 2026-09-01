from app.rag.retrieval.retriever import MedicalRetriever
from app.rag.retrieval.bm25_retriever import BM25Retriever
from app.rag.retrieval.qdrant_service import QdrantService
from app.rag.retrieval.build_index import build_knowledge_base, is_knowledge_base_ready


class HybridRetriever:

    def __init__(self):
        if not is_knowledge_base_ready():
            try:
                build_knowledge_base()
            except Exception as e:
                print(f"Warning: Could not build knowledge base automatically: {e}")

        try:
            self.qdrant = QdrantService()
        except Exception as e:
            print(f"Qdrant init warning: {e}")
            self.qdrant = None

        try:
            self.faiss = MedicalRetriever()
            self.bm25 = BM25Retriever()
        except Exception as e:
            print(f"Retriever initialization warning: {e}")
            self.faiss = None
            self.bm25 = None

        self.k_rrf = 60


    def reciprocal_rank_fusion(
        self,
        dense_results,
        sparse_results
    ):
        scores = {}
        documents = {}

        for rank, doc in enumerate(dense_results):
            chunk = doc.get("chunk_id", str(rank))
            documents[chunk] = doc
            scores.setdefault(chunk, 0)
            scores[chunk] += 1 / (self.k_rrf + rank + 1)

        for rank, doc in enumerate(sparse_results):
            chunk = doc.get("chunk_id", str(rank))
            documents[chunk] = doc
            scores.setdefault(chunk, 0)
            scores[chunk] += 1 / (self.k_rrf + rank + 1)

        ranked = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [documents[c] for c, _ in ranked]

    def retrieve(
        self,
        query,
        k=10
    ):
        dense = []
        if self.qdrant and self.qdrant.is_indexed() and self.faiss:
            try:
                query_vector = self.faiss.embed_query(query)[0]
                dense = self.qdrant.search(query_vector, k=20)
            except Exception as e:
                print(f"Qdrant query failed ({e}), falling back to FAISS.")

        if not dense and self.faiss:
            dense = self.faiss.retrieve(query, k=20)

        sparse = []
        if self.bm25:
            sparse = self.bm25.retrieve(query, k=20)

        if not dense and not sparse:
            return []

        results = self.reciprocal_rank_fusion(dense, sparse)
        return results[:k]