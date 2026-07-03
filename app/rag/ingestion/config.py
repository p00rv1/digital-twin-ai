from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

CONFIG_DIR = ROOT / "configs"

KNOWLEDGE_DIR = ROOT / "knowledge"

RAW_DIR = KNOWLEDGE_DIR / "raw"

METADATA_DIR = KNOWLEDGE_DIR / "metadata"

MANIFEST_DIR = KNOWLEDGE_DIR / "manifests"

EUROPE_PMC_URL = (
    "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
)

PAGE_SIZE = 25

TIMEOUT = 30
for directory in [

    KNOWLEDGE_DIR,

    RAW_DIR,

    METADATA_DIR,

    MANIFEST_DIR

]:

    directory.mkdir(
        parents=True,
        exist_ok=True
    )