from pathlib import Path

import pandas as pd
import streamlit as st

from utils.pdf_reader import extract_text_from_pdf
from utils.text_cleaner import clean_text
from utils.skills_detector import find_skills, flatten_skills
from utils.ats_scorer import calculate_ats_score
from utils.jd_matcher import match_resume_to_jd
from utils.suggestions import generate_suggestions

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
MAX_FILE_MB = 10

st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")


# ------------------------------------------------------------------
# Helper functions that build small pieces of HTML for the dashboard
# ------------------------------------------------------------------
def load_css():
    css = (BASE_DIR / "assets" / "style.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def load_sample_jd():
    """Button callback: puts the sample job description into the text box."""
    st.session_state["jd_text"] = (DATA_DIR / "sample_job_description.txt").read_text(encoding="utf-8")


def score_label(score):
    if score >= 80:
        return "Excellent"
    if score >= 60:
        return "Good - a few improvements needed"
    if score >= 40:
        return "Average - needs work"
    return "Weak - needs major improvements"


def progress_bar(value):
    return f'<div class="bar-bg"><div class="bar-fill" style="width:{value}%"></div></div>'


def score_card(title, value, subtitle):
    return (f'<div class="card"><h3>{title}</h3>'
            f'<div class="big-number">{value}<span> / 100</span></div>'
            f'{progress_bar(value)}<p class="muted">{subtitle}</p></div>')


def info_card(title, big_text, subtitle):
    return (f'<div class="card"><h3>{title}</h3>'
            f'<div class="big-number">{big_text}</div>'
            f'<p class="muted">{subtitle}</p></div>')


def chips(skills, css_class):
    if not skills:
        return '<span class="muted">Nothing found</span>'
    return "".join(f'<span class="chip {css_class}">{s}</span>' for s in skills)


def skills_card(title, skills, css_class):
    return f'<div class="card"><h3>{title}</h3>{chips(skills, css_class)}</div>'


# ------------------------------------------------------------------
# Page header and sidebar
# ------------------------------------------------------------------
load_css()

st.markdown(
    '<div class="hero"><h1>📄 AI Resume Analyzer</h1>'
    '<p>Smart ATS Resume Checker - upload your resume, compare it with a job, and improve it.</p></div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("How to use")
    st.markdown(
        "1. Upload your resume (PDF)\n"
        "2. Paste a job description *(optional)*\n"
        "3. Click **Analyze Resume**\n"
        "4. Read your dashboard and tips"
    )
    st.info("🔒 Your resume is processed on your own computer. Nothing is sent online.")

# ------------------------------------------------------------------
# Inputs
# ------------------------------------------------------------------
left, right = st.columns(2)

with left:
    st.subheader("1. Upload Resume")
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

with right:
    st.subheader("2. Job Description (optional)")
    jd_text = st.text_area(
        "Paste the job description here",
        key="jd_text",
        height=200,
        placeholder="Paste the full job description to see matched and missing skills...",
    )
    st.button("Use sample job description", on_click=load_sample_jd)

analyze = st.button("🔍 Analyze Resume", type="primary", use_container_width=True)

# ------------------------------------------------------------------
# Analysis
# ------------------------------------------------------------------
if analyze:
    # ---- Check the upload ----
    if uploaded_file is None:
        st.error("Please upload your resume as a PDF file first.")
        st.stop()
    if uploaded_file.size > MAX_FILE_MB * 1024 * 1024:
        st.error(f"The file is too large. Please upload a PDF smaller than {MAX_FILE_MB} MB.")
        st.stop()

    # ---- Step 1: read the PDF ----
    try:
        with st.spinner("Reading your resume..."):
            raw_text = extract_text_from_pdf(uploaded_file.getvalue())
    except ValueError as error:
        st.error(str(error))
        st.stop()

    # ---- Step 2: analyze the resume ----
    resume_clean = clean_text(raw_text)
    resume_skills = find_skills(resume_clean)
    ats = calculate_ats_score(raw_text, resume_clean, resume_skills)
    total_skills = len(flatten_skills(resume_skills))

    # ---- Step 3: compare with job description (only if one was given) ----
    match = None
    jd_text = jd_text.strip()
    if not jd_text:
        st.info("ℹ️ No job description entered, so job matching was skipped. "
                "Paste one above to see matched and missing skills.")
    elif len(jd_text.split()) < 20:
        st.warning("⚠️ The job description is too short to compare. Please paste the full description.")
    else:
        jd_clean = clean_text(jd_text)
        jd_skills = find_skills(jd_clean)
        match = match_resume_to_jd(resume_clean, jd_clean, resume_skills, jd_skills)
        if not match["jd_skills"]:
            st.warning("No known skills were found in the job description. "
                       "The match score uses text similarity only.")

    suggestions = generate_suggestions(ats, resume_skills, match)

    # ==============================================================
    # DASHBOARD
    # ==============================================================
    st.markdown("## 📊 Analysis Dashboard")

    # ---- Row 1: three score cards ----
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(score_card("ATS Score", ats["score"], score_label(ats["score"])),
                    unsafe_allow_html=True)
    with c2:
        if match:
            skill_part = "n/a" if match["skill_score"] is None else f'{match["skill_score"]}%'
            st.markdown(score_card("Job Match", match["overall"],
                                   f'Skills: {skill_part} • Keywords: {match["text_score"]}%'),
                        unsafe_allow_html=True)
        else:
            st.markdown(info_card("Job Match", "—", "Add a job description to see this score"),
                        unsafe_allow_html=True)
    with c3:
        st.markdown(info_card("Skills Detected", total_skills,
                              f'{len(resume_skills["technical"])} technical • '
                              f'{len(resume_skills["soft"])} soft'),
                    unsafe_allow_html=True)

    # ---- Row 2: skill cards ----
    a, b = st.columns(2)
    if match:
        with a:
            st.markdown(skills_card("✅ Matched Skills", match["matched"], "chip-ok"),
                        unsafe_allow_html=True)
        with b:
            st.markdown(skills_card("❌ Missing Skills", match["missing"], "chip-miss"),
                        unsafe_allow_html=True)
    else:
        with a:
            st.markdown(skills_card("💻 Technical Skills", resume_skills["technical"], "chip-tech"),
                        unsafe_allow_html=True)
        with b:
            st.markdown(skills_card("🤝 Soft Skills", resume_skills["soft"], "chip-soft"),
                        unsafe_allow_html=True)

    # ---- Row 3: score breakdown + suggestions ----
    d, e = st.columns(2)
    with d:
        rows_html = ""
        for name, points, maximum in ats["breakdown"]:
            percent = round(points / maximum * 100)
            rows_html += (f'<div class="bar-row"><span>{name}</span><span>{points} / {maximum}</span></div>'
                          f'{progress_bar(percent)}')
        st.markdown(f'<div class="card"><h3>📈 ATS Score Breakdown</h3>{rows_html}</div>',
                    unsafe_allow_html=True)
    with e:
        tips_html = "".join(f"<li>{tip}</li>" for tip in suggestions)
        st.markdown(f'<div class="card"><h3>💡 Improvement Suggestions</h3>'
                    f'<ul class="tips">{tips_html}</ul></div>',
                    unsafe_allow_html=True)

    # ---- Extra details in expanders ----
    with st.expander("🧾 Extracted resume text"):
        st.text_area("Text found in your PDF", raw_text, height=300, disabled=True)

    with st.expander("🗂️ All detected skills (table)"):
        rows = []
        for category in ("technical", "soft"):
            for skill in resume_skills[category]:
                row = {"Skill": skill, "Type": category.title()}
                if match:
                    row["Required in Job?"] = "Yes" if skill in match["jd_skills"] else "No"
                rows.append(row)
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("No known skills were detected in this resume.")

    with st.expander("📉 Score chart"):
        chart_df = pd.DataFrame(ats["breakdown"], columns=["Category", "Score", "Max"])
        chart_df["Percent"] = (chart_df["Score"] / chart_df["Max"] * 100).round()
        st.bar_chart(chart_df.set_index("Category")["Percent"], color="#1E3A8A")