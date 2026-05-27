import re

def normalize_text(text: str) -> str:
    """
    Normalizes Turkish text by:
    - Converting to lowercase
    - Replacing Turkish characters with their English/normalized equivalents
    - Removing non-alphanumeric characters (punctuation, etc.)
    - Collapsing multiple spaces into a single space
    """
    if not text:
        return ""

    # Pre-replace uppercase Turkish characters to avoid locale-specific lowercasing issues
    text = text.replace("İ", "i").replace("I", "ı")
    text = text.strip().lower()

    replacements = {
        "ç": "c",
        "ğ": "g",
        "ı": "i",
        "ö": "o",
        "ş": "s",
        "ü": "u",
        "â": "a",
        "î": "i",
        "û": "u",
        "i̇": "i",  # handle combining dot if any
    }

    for tr_char, en_char in replacements.items():
        text = text.replace(tr_char, en_char)

    # Replace non-alphanumeric characters with space
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()
