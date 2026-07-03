from app.rag.ingestion.client import EuropePMCClient

from app.rag.ingestion.search_jobs import load_search_jobs

from app.rag.ingestion.repository import DocumentRepository


client = EuropePMCClient()

repo = DocumentRepository()


jobs = load_search_jobs()


for job in jobs:

    biomarker = job["name"]

    organ = job["organ"]

    query = job["query"]

    print(f"\nSearching {biomarker}...")

    response = client.search(query)

    papers = client.parse_response(
        response,
        biomarker,
        organ
    )

    print(f"Found {len(papers)} papers")

    for paper in papers:

        repo.add_document(paper)

print("\nFinished!")