import re
from pathlib import Path
import pandas as pd

SKILLS_FILE = Path(__file__).resolve().parent.parent / "data" / "skills_database.csv"


def load_skills_database() -> pd.DataFrame:
    """Loads the CSV with all known skills."""
    return pd.read_csv(SKILLS_FILE)


def find_skills(cleaned_text: str) -> dict:
    """
    Looks for every skill from the CSV inside the text.
    Returns: {"technical": [...], "soft": [...]}
    """
    skills_df = load_skills_database()
    found = {"technical": [], "soft": []}

    for _, row in skills_df.iterrows():
        skill = row["skill"]
        # The pattern makes sure "java" does NOT match inside "javascript",
        # and "sql" does NOT match inside "mysql".
        pattern = r"(?<![a-z0-9+#])" + re.escape(skill) + r"(?![a-z0-9+#])"
        if re.search(pattern, cleaned_text):
            found[row["category"]].append(skill)

    found["technical"].sort()
    found["soft"].sort()
    return found


def flatten_skills(skills: dict) -> set:
    """Combines technical + soft skills into one set."""
    return set(skills["technical"]) | set(skills["soft"])