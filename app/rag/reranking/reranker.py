from sentence_transformers import CrossEncoder
class MedicalReranker:

    def __init__(self):

        self.model = CrossEncoder(

            "BAAI/bge-reranker-base"

        )
    def rerank(

        self,

        query,

        documents,

        top_k=5

    ):

        pairs = [

            (

                query,

                doc["text"]

            )

            for doc in documents

        ]

        scores = self.model.predict(

            pairs

        )

        for score, doc in zip(

            scores,

            documents

        ):

            doc["rerank_score"] = float(score)

        documents.sort(

            key=lambda x: x["rerank_score"],

            reverse=True

        )

        return documents[:top_k]