from sqlalchemy.orm import Session

from .etl_db import (
    SessionLocal,
    Document,
    Failure,
    PipelineRun,
    create_tables
)

class DocumentRepository:

    def __init__(self):

        create_tables()

        self.db: Session = SessionLocal()

    def add_document(self, paper):

        if self.exists(paper.document_id):
            return

        doc = Document(

            document_id=paper.document_id,

            pmcid=paper.pmcid,

            pmid=paper.pmid,

            doi=paper.doi,

            title=paper.title,

            journal=paper.journal,

            year=paper.year,

            biomarker=paper.biomarker,

            organ=paper.organ,

            status="DISCOVERED",

            downloaded=False,

            version=1
        )

        self.db.add(doc)

        self.db.commit()

    def exists(self, document_id):

        return (

            self.db.query(Document)

            .filter(
                Document.document_id == document_id
            )

            .first()

            is not None
        )
    def get_document(self, document_id):

        return (

            self.db.query(Document)

            .filter(
                Document.document_id == document_id
            )

            .first()
        )
    def get_discovered_documents(self):

        return (

            self.db.query(Document)

            .filter(
                Document.status == "DISCOVERED"
            )

            .all()
        )
    def mark_downloaded(self, document_id):

        doc = self.get_document(document_id)

        if doc is None:
            return

        doc.status = "DOWNLOADED"

        doc.downloaded = True

        self.db.commit()
        
    def get_downloaded_documents(self):

        return (

            self.db.query(Document)

            .filter(Document.status == "DOWNLOADED")

            .all()

        )
    def mark_parsed(self, document_id):

        doc = self.get_document(document_id)

        if doc:

            doc.status = "PARSED"

            self.db.commit()
    def mark_chunked(self, document_id):

        doc = self.get_document(document_id)

        if doc:

            doc.status = "CHUNKED"

            self.db.commit()
    def mark_embedded(self, document_id):

        doc = self.get_document(document_id)

        if doc:

            doc.status = "EMBEDDED"

            self.db.commit()

    def log_failure(self, document_id, reason):

        failure = Failure(

            document_id=document_id,

            reason=reason
        )

        self.db.add(failure)

        self.db.commit()
    def create_pipeline_run(self):

        run = PipelineRun()

        self.db.add(run)

        self.db.commit()

        return run.id