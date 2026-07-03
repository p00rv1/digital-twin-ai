from app.rag.retrieval.retriever import MedicalRetriever
from app.rag.retrieval.bm25_retriever import BM25Retriever
class HybridRetriever:

    def __init__(self):

        self.faiss = MedicalRetriever()

        self.bm25 = BM25Retriever()

        self.k_rrf = 60
    def reciprocal_rank_fusion(
        self,
        faiss_results,
        bm25_results
    ):

        scores = {}

        documents = {}

        for rank, doc in enumerate(faiss_results):

            chunk = doc["chunk_id"]

            documents[chunk] = doc

            scores.setdefault(chunk, 0)

            scores[chunk] += 1 / (
                self.k_rrf + rank + 1
            )

        for rank, doc in enumerate(bm25_results):

            chunk = doc["chunk_id"]

            documents[chunk] = doc

            scores.setdefault(chunk, 0)

            scores[chunk] += 1 / (
                self.k_rrf + rank + 1
            )

        ranked = sorted(

            scores.items(),

            key=lambda x: x[1],

            reverse=True

        )

        return [

            documents[c]

            for c, _ in ranked

        ]
    def retrieve(
        self,
        query,
        k=10
    ):

        dense = self.faiss.retrieve(
            query,
            k=20
        )

        sparse = self.bm25.retrieve(
            query,
            k=20
        )

        results = self.reciprocal_rank_fusion(
            dense,
            sparse
        )

        return results[:k]