import json

from dataclasses import asdict


def load_document(path):

    with open(

        path,

        encoding="utf-8"

    ) as f:

        return json.load(f)


def save_chunks(

    chunks,

    path

):

    with open(

        path,

        "w",

        encoding="utf-8"

    ) as f:

        json.dump(

            [

                asdict(c)

                for c in chunks

            ],

            f,

            indent=4,

            ensure_ascii=False

        )