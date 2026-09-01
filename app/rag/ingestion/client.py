import requests
    
from .models import PaperMetadata


from .config import (
    EUROPE_PMC_URL,
    PAGE_SIZE,
    TIMEOUT
)
class EuropePMCClient:

    def __init__(self):

        self.base_url = EUROPE_PMC_URL
    def search(
        self,
        query,
        page=1
    ):

        params = {

            "query":
                f"{query} OPEN_ACCESS:y",

            "format":
                "json",

            "page":
                page,

            "pageSize":
                PAGE_SIZE
        }

        response = requests.get(

            self.base_url,

            params=params,

            timeout=TIMEOUT
        )

        response.raise_for_status()

        return response.json()
    def parse_response(
        self,
        data,
        biomarker,
        organ
    ):

        papers = []

        results = data.get(
            "resultList",
            {}
        ).get(
            "result",
            []
        )

        for item in results:

            authors = []

            if item.get("authorString"):

                authors = [

                    a.strip()

                    for a in item["authorString"].split(",")

                ]

            year = item.get("pubYear")

            try:
                year = int(year)
            except (ValueError, TypeError):
                year = 0

            paper = PaperMetadata(

                title=item.get(
                    "title",
                    ""
                ),

                abstract=item.get(
                    "abstractText",
                    ""
                ),

                authors=authors,

                journal=item.get(
                    "journalTitle",
                    ""
                ),

                year=year,

                pmcid=item.get(
                    "pmcid"
                ),

                pmid=item.get(
                    "pmid"
                ),

                doi=item.get(
                    "doi"
                ),

                source="Europe PMC",

                biomarker=biomarker,

                organ=organ
            )

            papers.append(
                paper
            )

        return papers