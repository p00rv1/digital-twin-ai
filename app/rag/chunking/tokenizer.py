from transformers import AutoTokenizer

import spacy

MODEL = "BAAI/bge-small-en-v1.5"

tokenizer = AutoTokenizer.from_pretrained(MODEL)

nlp = spacy.load(
    "en_core_web_sm",
    disable=[
        "ner",
        "tagger",
        "lemmatizer"
    ]
)


def count_tokens(text):

    return len(

        tokenizer.encode(

            text,

            add_special_tokens=False

        )

    )


def split_sentences(text):

    doc = nlp(text)

    return [

        sent.text.strip()

        for sent in doc.sents

        if sent.text.strip()

    ]