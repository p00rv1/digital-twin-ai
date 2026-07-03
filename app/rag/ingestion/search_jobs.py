import yaml

from .config import CONFIG_DIR
def load_search_jobs():

    file = CONFIG_DIR / "biomarkers.yaml"

    with open(
        file,
        encoding="utf-8"
    ) as f:

        data = yaml.safe_load(f)

    return data["biomarkers"]