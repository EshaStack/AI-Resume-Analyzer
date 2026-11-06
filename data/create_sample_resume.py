"""
Run this file once to create a sample PDF resume for testing:
    python create_sample_resume.py
It creates:  data/sample_resume.pdf
"""
from pathlib import Path
import fitz  # PyMuPDF

RESUME_TEXT = """SAMPLE CANDIDATE
Email: sample.candidate@example.com | Phone: +92 300 1234567
LinkedIn: linkedin.com/in/sample-candidate | GitHub: github.com/sample-candidate

SUMMARY
Computer Science graduate with a passion for data and Python. Built several projects using
machine learning and data analysis. Strong teamwork and communication skills.

EDUCATION
Bachelor of Science in Computer Science, Sample University, 2021 - 2025

EXPERIENCE
Data Analyst Intern, Example Tech Pvt Ltd (June 2024 - August 2024)
- Developed Python scripts with pandas and numpy to clean sales data for 5 departments.
- Built weekly Excel and matplotlib reports that reduced manual work by 40%.
- Collaborated with a team of 6 developers and presented results to managers.
- Used Git and GitHub for version control.

PROJECTS
House Price Predictor
- Created a machine learning model with scikit-learn that reached 85% accuracy.
- Designed a simple web interface using Flask, HTML and CSS.

Student Database System
- Implemented a SQL database with MySQL for managing 500+ student records.

SKILLS
Python, SQL, MySQL, pandas, numpy, scikit-learn, matplotlib, Flask, HTML, CSS, Git, Excel
Teamwork, Communication, Problem solving, Time management
"""

def main():
    output_file = Path(__file__).parent / "data" / "sample_resume.pdf"
    doc = fitz.open()
    page = doc.new_page()                              # A4 page
    box = fitz.Rect(50, 50, 545, 790)                  # Text area with margins
    result = page.insert_textbox(box, RESUME_TEXT, fontsize=9.5, fontname="helv")
    if result < 0:
        print("Warning: some text did not fit on the page.")
    doc.save(str(output_file))
    doc.close()
    print(f"Sample resume created: {output_file}")

if __name__ == "__main__":
    main()