from dataclasses import dataclass, field
from typing import List


@dataclass
class Paragraph:

    text: str


@dataclass
class Table:

    caption: str

    rows: List[List[str]] = field(default_factory=list)


@dataclass
class Figure:

    caption: str


@dataclass
class Section:

    heading: str

    paragraphs: List[Paragraph] = field(default_factory=list)

    tables: List[Table] = field(default_factory=list)

    figures: List[Figure] = field(default_factory=list)

    children: List["Section"] = field(default_factory=list)


@dataclass
class ParsedDocument:

    document_id: str

    title: str

    abstract: List[Paragraph]

    journal: str

    year: int

    biomarker: str

    organ: str

    sections: List[Section]