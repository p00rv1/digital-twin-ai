from pathlib import Path

from bs4 import BeautifulSoup

from .models import (
    ParsedDocument,
    Paragraph,
    Section,
    Table,
    Figure
)

from .utils import save_json

class MedicalParser:

    def __init__(self):

        root = Path(__file__).resolve().parents[3]

        self.raw_dir = root / "knowledge" / "raw"

        self.output_dir = root / "knowledge" / "parsed"

        self.output_dir.mkdir(
            exist_ok=True,
            parents=True
        )
    def read_xml(self, xml_path):

        with open(
            xml_path,
            "r",
            encoding="utf-8"
        ) as f:

            return f.read()
    def load_soup(self, xml_path):

        xml = self.read_xml(xml_path)

        return BeautifulSoup(
            xml,
            "xml"
        )
    def get_title(self, soup):

        tag = soup.find("article-title")

        if tag:

            return tag.get_text(
                " ",
                strip=True
            )

        return ""
    def get_journal(self, soup):

        tag = soup.find("journal-title")

        if tag:

            return tag.get_text(
                " ",
                strip=True
            )

        return ""
    def get_year(self, soup):

        years = soup.find_all("year")

        for y in years:

            try:

                year = int(y.get_text())

                if 1900 <= year <= 2100:

                    return year

            except ValueError:

                pass

        return 0
    def get_abstract(self, soup):

        abstract = soup.find("abstract")

        if abstract is None:

            return []

        paragraphs = []

        for p in abstract.find_all("p"):

            text = p.get_text(
                " ",
                strip=True
            )

            if text:

                paragraphs.append(
                    Paragraph(text=text)
                )

        return paragraphs
    
    def parse_section(self, sec):

        heading = ""

        title = sec.find(
            "title",
            recursive=False
        )

        if title:

            heading = title.get_text(
                " ",
                strip=True
            )

        section = Section(
            heading=heading
        )

        # --------------------------
        # Direct paragraphs only
        # --------------------------

        for p in sec.find_all(
            "p",
            recursive=False
        ):

            text = p.get_text(
                " ",
                strip=True
            )

            if text:

                section.paragraphs.append(
                    Paragraph(text=text)
                )

        # --------------------------
        # Tables
        # --------------------------

        for table in sec.find_all(
            "table-wrap",
            recursive=False
        ):

            caption = ""

            cap = table.find("caption")

            if cap:

                caption = cap.get_text(
                    " ",
                    strip=True
                )

            section.tables.append(
                Table(
                    caption=caption
                )
            )

        # --------------------------
        # Figures
        # --------------------------

        for fig in sec.find_all(
            "fig",
            recursive=False
        ):

            caption = ""

            cap = fig.find("caption")

            if cap:

                caption = cap.get_text(
                    " ",
                    strip=True
                )

            section.figures.append(
                Figure(
                    caption=caption
                )
            )

        # --------------------------
        # Child sections
        # --------------------------

        for child in sec.find_all(
            "sec",
            recursive=False
        ):

            section.children.append(

                self.parse_section(child)

            )

        return section
    def get_sections(self, soup):

        body = soup.find("body")

        if body is None:

            return []

        sections = []

        for sec in body.find_all(
            "sec",
            recursive=False
        ):

            sections.append(

                self.parse_section(sec)

            )

        return sections
    def parse_document(
        self,
        xml_path,
        metadata
    ):

        soup = self.load_soup(
            xml_path
        )

        document = ParsedDocument(

            document_id=metadata.document_id,

            title=self.get_title(soup),

            abstract=self.get_abstract(soup),

            journal=self.get_journal(soup),

            year=self.get_year(soup),

            biomarker=metadata.biomarker,

            organ=metadata.organ,

            sections=self.get_sections(soup)

        )

        output = (

            self.output_dir /

            f"{metadata.document_id}.json"

        )

        save_json(
            document,
            output
        )

        return document

    def run(self):
        from app.rag.ingestion.repository import DocumentRepository
        from app.rag.ingestion.models import PaperMetadata

        repo = DocumentRepository()
        documents = repo.get_downloaded_documents()
        parsed_count = 0

        if documents:
            for doc in documents:
                xml_path = self.raw_dir / f"{doc.document_id}.xml"
                if xml_path.exists():
                    self.parse_document(xml_path, doc)
                    repo.mark_parsed(doc.document_id)
                    parsed_count += 1
        else:
            for xml_path in self.raw_dir.glob("*.xml"):
                doc_id = xml_path.stem
                meta = PaperMetadata(
                    title=doc_id, abstract="", authors=[], journal="",
                    year=2024, pmcid=doc_id.replace("PMC_", ""), pmid=None, doi=None,
                    source="Europe PMC", biomarker="liver", organ="liver"
                )
                self.parse_document(xml_path, meta)
                parsed_count += 1

        print(f"Parsed {parsed_count} documents")