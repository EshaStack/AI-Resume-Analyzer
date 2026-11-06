import re


def clean_text(text: str) -> str:
    """Makes text lowercase and removes extra symbols so matching is easier."""
    text = text.lower()
    text = text.replace("problem-solving", "problem solving")  # common spelling variant
    # Keep letters, numbers and symbols used in skills like c++, c#, node.js, ci/cd
    text = re.sub(r"[^a-z0-9+#./\-\s]", " ", text)
    text = re.sub(r"\s+", " ", text)  # many spaces/newlines -> one space
    return text.strip()