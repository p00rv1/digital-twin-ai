from app.snapshot.patient_snapshot import get_patient_snapshot

from app.reasoning.query_builder import QueryBuilder

from app.reasoning.prompt_builder import PromptBuilder

from app.rag.retrieval.hybrid_retriever import HybridRetriever

from app.rag.reranking.reranker import MedicalReranker

from app.llm.llm_service import LLMService
import time

class DiagnosisPipeline:

    def __init__(self):

        self.query_builder = QueryBuilder()

        self.retriever = HybridRetriever()

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
        # Build Query
        # -----------------------

        query = self.query_builder.build(
            patient_id
        )

        # -----------------------
        # Retrieve Papers
        # -----------------------

        retrieved = self.retriever.retrieve(

            query,

            k=20

        )

        # -----------------------
        # Rerank
        # -----------------------

        evidence = self.reranker.rerank(

            query,

            retrieved,

            top_k=5

        )

        # -----------------------
        # Prompt
        # -----------------------

        prompt = self.prompt_builder.build(

            snapshot,

            evidence

        )

        # -----------------------
        # LLM
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

            "diagnosis": diagnosis

        }