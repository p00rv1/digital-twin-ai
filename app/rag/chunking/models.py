from dataclasses import dataclass
from dataclasses import field
from dataclasses import asdict

from typing import List


@dataclass
class MedicalChunk:

    chunk_id: str

    paper_id: str

    paper_title: str

    chunk_type: str

    heading_path: str

    text: str

    journal: str

    year: int

    organ: str

    biomarker: str

    token_count: int

    keywords: List[str] = field(default_factory=list)


    def to_dict(self):

        return asdict(self)