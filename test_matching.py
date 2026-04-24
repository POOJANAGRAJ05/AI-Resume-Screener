#!/usr/bin/env python3
"""
Test script to verify simplified skill matching logic.
"""

from utils.skills import extract_skills, SKILL_KEYWORDS, match_skills_to_job
from utils.similarity import compute_weighted_ats_score

# Sample resume text
sample_resume = """
John Doe
Software Engineer

Skills: Python, JavaScript, React, Node.js, SQL, Git, Docker, AWS

Experience:
- Developed web applications using Python and Django
- Built frontend components with React and JavaScript
- Worked with databases using SQL
- Deployed applications on AWS using Docker
"""

# Sample job description
sample_job = """
Senior Python Developer

Requirements:
- Python programming (3+ years)
- JavaScript and React experience
- SQL database knowledge
- Git version control
- Docker containerization
- AWS cloud services
- Machine Learning experience preferred
"""

def test_skill_extraction():
    print("=== Testing Skill Extraction ===")

    # Extract skills from resume
    resume_skills = extract_skills(sample_resume, SKILL_KEYWORDS)
    print(f"Resume skills: {resume_skills}")

    # Extract skills from job description
    jd_skills = extract_skills(sample_job, SKILL_KEYWORDS)
    print(f"JD skills: {jd_skills}")

    # Test matching
    matched, missing, ratio = match_skills_to_job(resume_skills, jd_skills)
    print(f"Matched: {matched}")
    print(f"Missing: {missing}")
    print(f"Match ratio: {ratio:.2f}")

def test_weighted_scoring():
    print("\n=== Testing Weighted ATS Scoring ===")

    score, skill_score, similarity_score, matched, missing = compute_weighted_ats_score(
        sample_resume, sample_job, SKILL_KEYWORDS
    )

    print(f"Final ATS Score: {score}")
    print(f"Skill score: {skill_score}%")
    print(f"Similarity score: {similarity_score}%")
    print(f"Matched Skills: {matched}")
    print(f"Missing Skills: {missing}")

if __name__ == "__main__":
    test_skill_extraction()
    test_weighted_scoring()