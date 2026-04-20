import re 
from typing import Dict 


ALLOWED_QUERY_PATTERN = re.compile(r"^[a-zA-Z0-9\s?@#\-_.,'""()]+$")
STOP_WORDS = {"the", "is", "and", "or", "for", "a", "an", "to"}
SYNONYMS = {
    "buy": "purchase",
    "find": "search",
    "latest": "recent",
}


def validate_query(query: str) -> bool:
    if not query or len(query.strip()) < 3:
        raise ValueError("Query must be at least 3 characters long.")
    if not ALLOWED_QUERY_PATTERN.match(query):
        raise ValueError("Query contains invalid characters.")
    return True


def transform_query(query: str) -> Dict[str, str]:
    normalized = query.strip().lower()
    normalized = re.sub(r"\s+", " ", normalized)

    tokens = normalized.split()
    tokens = [SYNONYMS.get(token, token) for token in tokens if token not in STOP_WORDS]
    cleaned_query = " ".join(tokens)

    query_signature = cleaned_query.replace(" ", "_")

    return {
        "original": query,
        "normalized": normalized,
        "cleaned": cleaned_query,
        "signature": query_signature,
    }


def handle_query(query: str) -> Dict[str, str]:
    validate_query(query)
    return transform_query(query)



