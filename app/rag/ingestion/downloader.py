from pathlib import Path
import requests

from .repository import DocumentRepository
class EuropePMCDownloader:

    BASE_URL = (
         "https://www.ebi.ac.uk/europepmc/webservices/rest"
    )

    def __init__(self):

        self.repo = DocumentRepository()

        self.raw_dir = (
            Path(__file__)
            .resolve()
            .parents[3]
            / "knowledge"
            / "raw"
        )

        self.raw_dir.mkdir(
            parents=True,
            exist_ok=True
        )
    def build_url(self, pmcid):

        return (
            f"{self.BASE_URL}/"
            f"{pmcid}"
            "/fullTextXML"
        )
    def file_path(self, document):

        return (
            self.raw_dir /
            f"{document.document_id}.xml"
        )
    def download_document(self, document):
        
        if document.pmcid is None:

            self.repo.log_failure(
                document.document_id,
                "Missing PMCID"
            )

            return False

        url = self.build_url(document.pmcid)
        print(url)
        response = requests.get(
            url,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"HTTP Error: {response.status_code}")

            self.repo.log_failure(
                document.document_id,
                f"HTTP {response.status_code}"
            )

            print("Failure logged")

            return False

        path = self.file_path(document)

        path.write_text(
            response.text,
            encoding="utf-8"
        )

        self.repo.mark_downloaded(
            document.document_id
        )
        
        return True
    def run(self):

        papers = self.repo.get_discovered_documents()

        downloaded = 0

        failed = 0

        for paper in papers:

            success = self.download_document(
                paper
            )

            if success:

                downloaded += 1

            else:

                failed += 1

        print()

        print(f"Downloaded : {downloaded}")

        print(f"Failed     : {failed}")