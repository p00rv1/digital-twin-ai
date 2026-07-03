from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PaperMetadata:
    """
    Represents one paper discovered from Europe PMC.
    """

    title: str
    abstract: str

    authors: List[str]

    journal: str

    year: int

    pmcid: Optional[str]
    pmid: Optional[str]
    doi: Optional[str]

    source: str

    biomarker: str
    organ: str

    publication_type: Optional[str] = None

    keywords: Optional[List[str]] = None

    has_full_text: bool = False

    download_status: str = "DISCOVERED"

    version: int = 1

    @property
    def document_id(self):

        if self.pmcid:
            return f"PMC_{self.pmcid}"

        if self.pmid:
            return f"PMID_{self.pmid}"

        if self.doi:
            return self.doi.replace("/", "_")

        return self.title.replace(" ", "_")