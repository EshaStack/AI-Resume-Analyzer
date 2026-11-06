import re

EMAIL_PATTERN = r"[\w.+-]+@[\w-]+\.[\w.-]+"
PHONE_PATTERN = r"\+?\d[\d\s\-()]{8,}\d"
NUMBER_PATTERN = r"\d+\s?%|\$\s?\d+|\b\d+\+?\s?(?:users|customers|clients|projects|members|students|records|requests|people|departments|developers)\b"

ACTION_VERBS = {
    "developed", "built", "designed", "implemented", "led", "managed", "created",
    "improved", "optimized", "analyzed", "deployed", "automated", "collaborated",
    "delivered", "launched", "reduced", "increased", "achieved", "engineered",
    "maintained", "tested", "trained", "organized", "coordinated", "presented",
}

# Words we look for in short lines (headings) of the resume
SECTION_KEYWORDS = {
    "Summary": ["summary", "objective", "profile", "about me"],
    "Education": ["education", "academic"],
    "Experience": ["experience", "internship", "employment", "work history"],
    "Skills": ["skills", "technologies"],
    "Projects": ["projects"],
}


def find_sections(raw_text: str) -> list:
    """Detects resume headings such as 'Education' or 'Skills'."""
    found = []
    for line in raw_text.split("\n"):
        line = line.strip().lower()
        if 0 < len(line) < 40:  # headings are short lines
            for section, words in SECTION_KEYWORDS.items():
                if section not in found and any(w in line for w in words):
                    found.append(section)
    return found


def calculate_ats_score(raw_text: str, cleaned_text: str, resume_skills: dict) -> dict:
    """
    Gives the resume a score from 0 to 100.

    Scoring (total = 100):
      Contact info   10   (email 5 + phone 5)
      Online links   10   (LinkedIn 5 + GitHub 5)
      Sections       25   (5 sections x 5 points)
      Skills         20   (12 or more skills = full points)
      Action verbs   15   (10 or more different verbs = full points)
      Numbers        10   (3 or more measurable results = full points)
      Length         10   (300-900 words is ideal)
    """
    text_lower = raw_text.lower()

    # --- Contact info ---
    has_email = bool(re.search(EMAIL_PATTERN, raw_text))
    has_phone = bool(re.search(PHONE_PATTERN, raw_text))
    contact_points = (5 if has_email else 0) + (5 if has_phone else 0)

    # --- Links ---
    has_linkedin = "linkedin.com" in text_lower
    has_github = "github.com" in text_lower
    link_points = (5 if has_linkedin else 0) + (5 if has_github else 0)

    # --- Sections ---
    sections_found = find_sections(raw_text)
    missing_sections = [s for s in SECTION_KEYWORDS if s not in sections_found]
    section_points = len(sections_found) * 5

    # --- Skills ---
    total_skills = len(resume_skills["technical"]) + len(resume_skills["soft"])
    skills_points = round(min(total_skills, 12) / 12 * 20)

    # --- Action verbs ---
    words = set(re.findall(r"[a-z]+", cleaned_text))
    verbs_found = sorted(words & ACTION_VERBS)
    verb_points = round(min(len(verbs_found), 10) / 10 * 15)

    # --- Numbers / achievements ---
    numbers_found = len(re.findall(NUMBER_PATTERN, text_lower))
    number_points = round(min(numbers_found, 3) / 3 * 10)

    # --- Length ---
    word_count = len(raw_text.split())
    if 300 <= word_count <= 900:
        length_points = 10
    elif 150 <= word_count < 300 or 900 < word_count <= 1200:
        length_points = 5
    else:
        length_points = 0

    breakdown = [
        ("Contact Info", contact_points, 10),
        ("Online Links", link_points, 10),
        ("Resume Sections", section_points, 25),
        ("Skills", skills_points, 20),
        ("Action Verbs", verb_points, 15),
        ("Measurable Results", number_points, 10),
        ("Resume Length", length_points, 10),
    ]

    return {
        "score": sum(points for _, points, _ in breakdown),
        "breakdown": breakdown,
        "has_email": has_email,
        "has_phone": has_phone,
        "has_links": has_linkedin or has_github,
        "missing_sections": missing_sections,
        "action_verbs": verbs_found,
        "numbers_found": numbers_found,
        "word_count": word_count,
    }