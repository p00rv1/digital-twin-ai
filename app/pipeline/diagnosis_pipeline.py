from app.snapshot.patient_snapshot import get_patient_snapshot
from app.reasoning.query_builder import QueryBuilder
from app.reasoning.prompt_builder import PromptBuilder
from app.rag.retrieval.hybrid_retriever import HybridRetriever
from app.rag.retrieval.evaluator import RelevanceEvaluator
from app.rag.reranking.reranker import MedicalReranker
from app.llm.llm_service import LLMService
import time


class DiagnosisPipeline:

    def __init__(self):
        self.query_builder = QueryBuilder()
        self.retriever = HybridRetriever()
        self.evaluator = RelevanceEvaluator()
        self.reranker = MedicalReranker()
        self.prompt_builder = PromptBuilder()
        self.llm = LLMService()

    def run(
        self,
        patient_id
    ):
        # -----------------------
        # Patient Snapshot
        # -----------------------
        snapshot = get_patient_snapshot(
            patient_id
        )

        # -----------------------
        # Primary Clinical Query
        # -----------------------
        query = self.query_builder.build(
            snapshot
        )

        # -----------------------
        # Retrieve Initial Candidate Chunks
        # -----------------------
        retrieved = self.retriever.retrieve(
            query,
            k=20
        )

        # -----------------------
        # Initial Reranking
        # -----------------------
        evidence = self.reranker.rerank(
            query,
            retrieved,
            top_k=5
        )

        # -----------------------
        # Corrective RAG (CRAG) Evaluation
        # -----------------------
        retrieval_quality, avg_score = self.evaluator.evaluate(evidence)
        crag_triggered = False
        expanded_queries = []

        # If evidence quality is LOW (< 0.35 threshold), trigger CRAG Query Expansion Loop
        if retrieval_quality == "LOW" or avg_score < 0.35:
            crag_triggered = True
            expanded_queries = self.query_builder.build_expanded_queries(snapshot)

            all_retrieved = list(retrieved)

            for eq in expanded_queries:
                eq_chunks = self.retriever.retrieve(eq, k=15)
                all_retrieved.extend(eq_chunks)

            # Deduplicate retrieved chunks by chunk_id
            seen_chunks = set()
            unique_chunks = []
            for doc in all_retrieved:
                cid = doc.get("chunk_id")
                if cid and cid not in seen_chunks:
                    seen_chunks.add(cid)
                    unique_chunks.append(doc)

            # Re-score and re-rerank merged candidate pool
            evidence = self.reranker.rerank(
                query,
                unique_chunks,
                top_k=5
            )

            # Re-evaluate evidence quality after expansion
            new_quality, avg_score = self.evaluator.evaluate(evidence)
            retrieval_quality = f"{new_quality} (CRAG Corrected ⚡)"

        # -----------------------
        # Prompt Construction
        # -----------------------
        prompt = self.prompt_builder.build(
            snapshot,
            evidence
        )

        # -----------------------
        # LLM Diagnosis Generation
        # -----------------------
        diagnosis = self.llm.generate(
            prompt
        )

        return {
            "patient_id": patient_id,
            "snapshot": snapshot,
            "query": query,
            "evidence": evidence,
            "prompt": prompt,
            "diagnosis": diagnosis,
            "retrieval_quality": retrieval_quality,
            "avg_relevance_score": avg_score,
            "crag_triggered": crag_triggered,
            "expanded_queries": expanded_queries
        }