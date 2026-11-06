from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils.skills_detector import flatten_skills


def text_similarity(resume_clean: str, jd_clean: str) -> float:
    """
    Compares two texts with TF-IDF + cosine similarity (scikit-learn).
    Returns a number from 0 to 100. Higher = more similar wording.
    """
    try:
        vectorizer = TfidfVectorizer(stop_words="english")
        matrix = vectorizer.fit_transform([resume_clean, jd_clean])
        score = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
        return float(score) * 100
    except ValueError:  # happens if a text has no usable words
        return 0.0


def match_resume_to_jd(resume_clean, jd_clean, resume_skills, jd_skills) -> dict:
    """Compares resume and job description."""
    resume_set = flatten_skills(resume_skills)
    jd_set = flatten_skills(jd_skills)

    matched = sorted(resume_set & jd_set)   # skills in BOTH
    missing = sorted(jd_set - resume_set)   # in the job, NOT in the resume

    similarity = text_similarity(resume_clean, jd_clean)
    # Raw similarity is usually low (20-40% is already good), so we scale it up
    text_score = min(similarity * 2, 100)

    if jd_set:
        skill_score = len(matched) / len(jd_set) * 100
        overall = 0.7 * skill_score + 0.3 * text_score   # skills matter most
    else:
        skill_score = None
        overall = text_score

    return {
        "overall": round(overall),
        "skill_score": None if skill_score is None else round(skill_score),
        "text_score": round(text_score),
        "matched": matched,
        "missing": missing,
        "jd_skills": jd_set,
    }