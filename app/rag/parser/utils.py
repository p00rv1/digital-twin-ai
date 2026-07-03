from dataclasses import asdict
import json


def save_json(document, path):

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            asdict(document),
            f,
            indent=4,
            ensure_ascii=False
        )