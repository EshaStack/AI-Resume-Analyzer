from utils.skills_detector import flatten_skills


def generate_suggestions(ats: dict, resume_skills: dict, match: dict = None) -> list:
    """Creates a list of simple, practical improvement tips."""
    tips = []

    if not ats["has_email"]:
        tips.append("Add a professional email address at the top of your resume.")
    if not ats["has_phone"]:
        tips.append("Add your phone number so recruiters can contact you.")
    if not ats["has_links"]:
        tips.append("Add your LinkedIn and/or GitHub profile links.")

    if ats["missing_sections"]:
        names = ", ".join(ats["missing_sections"])
        tips.append(f"Add clear section headings for: {names}. ATS software looks for standard headings.")

    if len(flatten_skills(resume_skills)) < 8:
        tips.append("List more relevant skills. Aim for at least 8-12 clearly named skills.")
    if not resume_skills["soft"]:
        tips.append("Show soft skills (teamwork, communication, leadership) inside your experience bullets.")

    if len(ats["action_verbs"]) < 6:
        tips.append("Start bullet points with strong action verbs such as developed, built, optimized, led.")
    if ats["numbers_found"] < 3:
        tips.append("Add numbers to show your impact, for example: 'reduced load time by 30%'.")

    if ats["word_count"] < 300:
        tips.append("Your resume is quite short. Add more details about projects and achievements.")
    elif ats["word_count"] > 900:
        tips.append("Your resume is long. Try to keep it to 1-2 pages with only the most relevant points.")

    if match:
        if match["missing"]:
            top_missing = ", ".join(match["missing"][:8])
            tips.append(f"The job asks for skills not found in your resume: {top_missing}. "
                        "Add them only if you genuinely have them.")
        if match["overall"] < 50:
            tips.append("Tailor your resume to this job: reuse important words from the job description.")

    if not tips:
        tips.append("Great job! Your resume looks strong. Keep it updated and tailor it for each job.")

    return tips