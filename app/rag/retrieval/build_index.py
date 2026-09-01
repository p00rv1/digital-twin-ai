from pathlib import Path
from app.rag.ingestion.etl_db import create_tables
from app.rag.ingestion.client import EuropePMCClient
from app.rag.ingestion.search_jobs import load_search_jobs
from app.rag.ingestion.repository import DocumentRepository
from app.rag.ingestion.downloader import EuropePMCDownloader
from app.rag.parser.parser import MedicalParser
from app.rag.chunking.chunker import MedicalChunker
from app.rag.embeddings.embed_all import EmbeddingPipeline
from app.rag.retrieval.faiss_index import FAISSIndex
from app.rag.retrieval.bm25_index import BM25Indexer


def is_knowledge_base_ready() -> bool:
    root = Path(__file__).resolve().parents[3]
    required_files = [
        root / "knowledge" / "indexes" / "faiss.index",
        root / "knowledge" / "indexes" / "bm25.pkl",
        root / "knowledge" / "indexes" / "bm25_lookup.json",
        root / "knowledge" / "embeddings" / "chunk_lookup.json",
        root / "knowledge" / "embeddings" / "metadata_by_id.json",
    ]
    return all(f.exists() and f.stat().st_size > 0 for f in required_files)



def build_knowledge_base(force: bool = False) -> bool:
    if not force and is_knowledge_base_ready():
        print("Knowledge base index is cached and ready for retrieval.")
        return True

    print("Building / updating knowledge base...")
    create_tables()
    root = Path(__file__).resolve().parents[3]
    raw_dir = root / "knowledge" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    repo = DocumentRepository()
    downloaded_docs = repo.get_downloaded_documents()
    raw_xml_files = list(raw_dir.glob("*.xml"))

    if not downloaded_docs and not raw_xml_files:
        print("No cached documents found. Fetching medical papers from Europe PMC...")
        client = EuropePMCClient()
        jobs = load_search_jobs()
        for job in jobs:
            biomarker = job["name"]
            organ = job["organ"]
            query = job["query"]
            print(f"Searching for {biomarker} ({organ})...")
            try:
                response = client.search(query)
                papers = client.parse_response(response, biomarker, organ)
                print(f"Found {len(papers)} papers for {biomarker}")
                for paper in papers:
                    repo.add_document(paper)
            except Exception as e:
                print(f"Error fetching papers for {biomarker}: {e}")

        downloader = EuropePMCDownloader()
        downloader.run()

    print("Parsing XML documents...")
    parser = MedicalParser()
    parser.run()

    print("Chunking parsed documents...")
    chunker = MedicalChunker()
    chunker.run()

    print("Generating embeddings...")
    embedder = EmbeddingPipeline()
    embedder.build_embeddings()

    print("Building FAISS index...")
    FAISSIndex().build()

    print("Building BM25 index...")
    BM25Indexer().build()

    print("Knowledge base built and ready for retrieval!")
    return True


if __name__ == "__main__":
    build_knowledge_base()
