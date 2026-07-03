from pathlib import Path
import uuid

from .models import MedicalChunk

from .utils import (
    load_document,
    save_chunks
)

from .tokenizer import (
    count_tokens
)


class MedicalChunker:

    TARGET = 300

    MAX = 450

    MIN = 150


    def __init__(self):

        root = Path(__file__).resolve().parents[3]

        self.parsed = root / "knowledge" / "parsed"

        self.output = root / "knowledge" / "chunks"

        self.output.mkdir(

            parents=True,

            exist_ok=True

        )
    def flatten_sections(

        self,

        sections,

        parent=""

    ):

        flat = []

        for sec in sections:

            heading = sec["heading"]

            if parent:

                path = parent + " > " + heading

            else:

                path = heading

            flat.append(

                (

                    path,

                    sec

                )

            )

            flat.extend(

                self.flatten_sections(

                    sec["children"],

                    path

                )

            )

        return flat

    def build_chunks(

        self,

        document

    ):

        chunks = []

        sections = self.flatten_sections(

            document["sections"]

        )

        for heading, sec in sections:

            text = ""

            for p in sec["paragraphs"]:

                paragraph = p["text"].strip()

                if not paragraph:

                    continue

                if count_tokens(

                    text + paragraph

                ) < self.TARGET:

                    text += "\n\n" + paragraph

                else:

                   

                    chunks.append(

                        MedicalChunk(

                            chunk_id=str(uuid.uuid4()),

                            paper_id=document["document_id"],

                            paper_title=document["title"],

                            chunk_type="section",

                            heading_path=heading,

                            text=text.strip(),

                            journal=document["journal"],

                            year=document["year"],

                            organ=document["organ"],

                            biomarker=document["biomarker"],

                            token_count=count_tokens(
                                text
                            )

                        )

                    )

            if text:


                    chunks.append(

                        MedicalChunk(

                            chunk_id=str(uuid.uuid4()),

                            paper_id=document["document_id"],

                            paper_title=document["title"],

                            chunk_type="section",

                            heading_path=heading,

                            text=text.strip(),

                            journal=document["journal"],

                            year=document["year"],

                            organ=document["organ"],

                            biomarker=document["biomarker"],

                            token_count=count_tokens(
                                text
                            )

                        )

                    )
        return chunks

    def run(self):

        files = sorted(
            self.parsed.glob("*.json")
        )

        print(f"Found {len(files)} parsed papers")

        for file in files:

            print(f"\nProcessing {file.name}")

            document = load_document(file)

            chunks = self.build_chunks(document)

            print(f"Created {len(chunks)} initial chunks")

            output = (
                self.output /
                file.name
            )

            save_chunks(
                chunks,
                output
            )

        print("\nFinished!")