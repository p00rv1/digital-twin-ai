import unittest
from app.snapshot.patient_snapshot import get_patient_snapshot
from app.services.analytics_service import compute_clinical_scores, predict_biomarker_trajectory
from app.rag.retrieval.evaluator import RelevanceEvaluator
from app.pipeline.diagnosis_pipeline import DiagnosisPipeline


class TestDigitalTwinRAGPipeline(unittest.TestCase):

    def test_patient_snapshot_and_scores(self):
        snapshot = get_patient_snapshot(1)
        self.assertIsNotNone(snapshot)
        self.assertIn("patient_id", snapshot)
        self.assertIn("clinical_scores", snapshot)
        self.assertIn("biomarkers", snapshot)

        scores = snapshot["clinical_scores"]
        self.assertIn("de_ritis_ratio", scores)
        self.assertIn("fib4_index", scores)

    def test_relevance_evaluator(self):
        evaluator = RelevanceEvaluator(high_threshold=0.55, low_threshold=0.35)
        high_evidence = [{"rerank_score": 0.85}, {"rerank_score": 0.72}]
        quality, avg = evaluator.evaluate(high_evidence)
        self.assertEqual(quality, "HIGH")
        self.assertGreaterEqual(avg, 0.55)

        low_evidence = [{"rerank_score": 0.15}, {"rerank_score": 0.20}]
        quality_low, avg_low = evaluator.evaluate(low_evidence)
        self.assertEqual(quality_low, "LOW")

    def test_trajectory_forecasting(self):
        from datetime import date
        dummy_history = [
            (date(2025, 1, 1), 25.0),
            (date(2025, 6, 1), 30.0),
            (date(2025, 12, 1), 35.0),
        ]
        forecast = predict_biomarker_trajectory(dummy_history)
        self.assertIsNotNone(forecast)
        self.assertIn("projected_90d", forecast)
        self.assertIn("projected_180d", forecast)
        self.assertGreater(forecast["projected_90d"], 30.0)

    def test_diagnosis_pipeline_structure(self):
        pipeline = DiagnosisPipeline()
        res = pipeline.run(1)
        self.assertIn("patient_id", res)
        self.assertIn("snapshot", res)
        self.assertIn("evidence", res)
        self.assertIn("diagnosis", res)
        self.assertIn("retrieval_quality", res)
        self.assertIsInstance(res["diagnosis"], dict)


if __name__ == "__main__":
    unittest.main()
