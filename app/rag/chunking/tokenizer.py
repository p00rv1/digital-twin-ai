from transformers import AutoTokenizer

MODEL = "BAAI/bge-small-en-v1.5"

try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
except Exception:
    tokenizer = None

try:
    import spacy
    try:
        nlp = spacy.load(
            "en_core_web_sm",
            disable=["ner", "tagger", "lemmatizer"]
        )
    except Exception:
        nlp = None
except ImportError:
    nlp = None


def count_tokens(text):
    if tokenizer:
        return len(
            tokenizer.encode(
                text,
                add_special_tokens=False
            )
        )
    return len(text.split())


def split_sentences(text):
    if nlp:
        doc = nlp(text)
        return [
            sent.text.strip()
            for sent in doc.sents
            if sent.text.strip()
        ]
    try:
        import nltk
        return nltk.sent_tokenize(text)
    except Exception:
        return [s.strip() for s in text.split('.') if s.strip()]
