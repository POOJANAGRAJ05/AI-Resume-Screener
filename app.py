import csv
import io
import re
from typing import List

import altair as alt
import pandas as pd
import streamlit as st

from utils.parser import extract_text
from utils.skills import extract_skills, SKILL_KEYWORDS
from utils.similarity import (
    compute_similarity,
    compute_weighted_ats_score,
    score_to_percentage,
    rank_candidates,
)


THEME_CSS_LIGHT = """
<style>
/* ===== LIGHT MODE THEME ===== */
:root {
  --bg-primary: #ffffff;
  --bg-secondary: #f8fafc;
  --text-primary: #0f172a;
  --text-secondary: #475569;
  --text-muted: #64748b;
  --border-color: #e2e8f0;
  --accent-primary: #3b82f6;
  --accent-secondary: #38bdf8;
  --card-shadow: rgba(15, 23, 42, 0.08);
  --score-high: #059669;
  --score-medium: #d97706;
  --score-low: #dc2626;
  --badge-text: #ffffff;
}

/* Base Layout */
body {
  background: var(--bg-primary) !important;
  color: var(--text-primary) !important;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-size: 0.95rem;
  line-height: 1.6;
}

main { padding: 2rem 2.5rem !important; }
section.main { padding: 0 !important; }

/* Sidebar */
.stSidebar {
  background: var(--bg-secondary) !important;
  border-right: 1px solid var(--border-color) !important;
}
.stSidebar [data-testid="stSidebarContent"] {
  padding: 1.5rem 1rem !important;
  color: var(--text-primary) !important;
}
.stSidebar [data-testid="stBaseButton"] { width: 100%; }

/* Buttons */
.stButton > button {
  background: var(--accent-primary) !important;
  color: var(--bg-primary) !important;
  border: none !important;
  font-weight: 600;
  transition: all 0.2s;
  border-radius: 6px !important;
}
.stButton > button:hover {
  background: var(--accent-secondary) !important;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

/* Form Elements */
.stCheckbox label {
  color: var(--text-primary) !important;
  font-weight: 500;
}
.stTextInput label, .stTextArea label, .stSelectbox label, .stSlider label, .stMultiSelect label {
  color: var(--text-primary) !important;
  font-weight: 600;
  margin-bottom: 0.5rem;
}
.stTextInput input, .stTextArea textarea, .stSelectbox select {
  background-color: var(--bg-primary) !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--border-color) !important;
  border-radius: 6px !important;
}
.stTextInput input::placeholder, .stTextArea textarea::placeholder {
  color: var(--text-muted) !important;
}

/* Cards */
.card {
  border-radius: 12px;
  background: var(--bg-secondary) !important;
  padding: 1.25rem;
  box-shadow: 0 4px 12px var(--card-shadow);
  border: 1px solid var(--border-color);
  margin-bottom: 1.5rem;
  color: var(--text-primary) !important;
  line-height: 1.6;
}

.metric-card {
  border-radius: 12px;
  background: var(--bg-secondary) !important;
  padding: 1rem 1.25rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid var(--border-color);
  text-align: center;
  color: var(--text-primary) !important;
}
.metric-card .metric-label {
  font-size: 0.9rem;
  color: var(--text-secondary);
  font-weight: 600;
  margin-bottom: 0.75rem;
  letter-spacing: 0.5px;
}
.metric-card .metric-value {
  font-size: 2rem;
  font-weight: 800;
  color: var(--accent-primary);
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.06);
}

.small-card {
  border-radius: 10px;
  background: var(--bg-primary) !important;
  padding: 1rem;
  border: 1px solid var(--border-color);
  margin-bottom: 0.75rem;
  color: var(--text-primary) !important;
  line-height: 1.6;
}

/* Score Highlighting */
.score-high { color: var(--score-high) !important; }
.score-medium { color: var(--score-medium) !important; }
.score-low { color: var(--score-low) !important; }

/* Typography */
.section-title {
  font-size: 1.3rem;
  font-weight: 800;
  color: var(--text-primary) !important;
  margin-bottom: 1rem;
  letter-spacing: 0.3px;
}
.section-desc {
  font-size: 0.95rem;
  color: var(--text-secondary) !important;
  margin-top: 0.5rem;
  font-weight: 500;
}

/* Badges */
.badge {
  display: inline-block;
  border-radius: 6px;
  padding: 0.4rem 0.85rem;
  font-size: 0.85rem;
  color: var(--badge-text) !important;
  font-weight: 600;
  letter-spacing: 0.3px;
}
.badge-neutral { background: #94a3b8; }
.badge-success { background: var(--score-high); }
.badge-warning { background: var(--score-medium); }
.badge-danger { background: var(--score-low); }

/* Header */
.top-header {
  background: var(--bg-secondary) !important;
  padding: 2rem 2.5rem;
  border-bottom: 1px solid var(--border-color);
  margin: -2rem -2.5rem 2rem;
}
.top-header h1 {
  margin: 0;
  font-size: 2rem;
  font-weight: 800;
  color: var(--text-primary) !important;
  letter-spacing: -0.5px;
}
.top-header p {
  margin: 0.75rem 0 0;
  font-size: 1rem;
  color: var(--text-secondary) !important;
  font-weight: 500;
}

/* Alerts */
.stInfo, .stSuccess, .stWarning, .stError {
  border-radius: 8px;
  padding: 1rem;
}
.stInfo {
  background-color: rgba(59, 130, 246, 0.08) !important;
  color: var(--text-primary) !important;
  border: 1px solid rgba(59, 130, 246, 0.2) !important;
}
.stSuccess {
  background-color: rgba(16, 185, 129, 0.08) !important;
  color: var(--text-primary) !important;
  border: 1px solid rgba(16, 185, 129, 0.2) !important;
}
.stWarning {
  background-color: rgba(245, 158, 11, 0.08) !important;
  color: var(--text-primary) !important;
  border: 1px solid rgba(245, 158, 11, 0.2) !important;
}
.stError {
  background-color: rgba(239, 68, 68, 0.08) !important;
  color: var(--text-primary) !important;
  border: 1px solid rgba(239, 68, 68, 0.2) !important;
}

/* Progress Bars */
.stProgressBar > div > div { background: var(--accent-primary) !important; }

/* Headings */
h1, h2, h3, h4, h5, h6 {
  color: var(--text-primary) !important;
  font-weight: 800 !important;
  letter-spacing: -0.3px;
}

/* Spacing */
div[data-testid="stVerticalBlock"] > div:first-child .element-container:first-child {
  margin-bottom: 1.5rem;
}

/* Secondary buttons (sidebar navigation) */
.stButton > button[data-baseweb="button"][kind="secondary"] {
  background: transparent !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--border-color) !important;
}
.stButton > button[data-baseweb="button"][kind="secondary"]:hover {
  background: var(--bg-secondary) !important;
  color: var(--text-primary) !important;
  border-color: var(--accent-primary) !important;
}

/* Primary buttons (active navigation, theme toggle) */
.stButton > button[data-baseweb="button"][kind="primary"] {
  background: var(--accent-primary) !important;
  color: var(--bg-primary) !important;
  border: none !important;
}
.stButton > button[data-baseweb="button"][kind="primary"]:hover {
  background: var(--accent-secondary) !important;
}
</style>
"""

THEME_CSS_DARK = """
<style>
/* ===== DARK MODE THEME ===== */
:root {
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --text-primary: #f1f5f9;
  --text-secondary: #cbd5e1;
  --text-muted: #94a3b8;
  --border-color: #334155;
  --accent-primary: #3b82f6;
  --accent-secondary: #38bdf8;
  --card-shadow: rgba(0, 0, 0, 0.3);
  --score-high: #10b981;
  --score-medium: #f59e0b;
  --score-low: #ef4444;
  --badge-text: #ffffff;
}

/* Base Layout */
body {
  background: var(--bg-primary) !important;
  color: var(--text-primary) !important;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-size: 0.95rem;
  line-height: 1.6;
}

main { padding: 2rem 2.5rem !important; }
section.main { padding: 0 !important; }

/* Sidebar */
.stSidebar {
  background: var(--bg-secondary) !important;
  border-right: 1px solid var(--border-color) !important;
}
.stSidebar [data-testid="stSidebarContent"] {
  padding: 1.5rem 1rem !important;
  color: var(--text-primary) !important;
}
.stSidebar [data-testid="stBaseButton"] { width: 100%; }

/* Buttons */
.stButton > button {
  background: var(--accent-primary) !important;
  color: var(--bg-primary) !important;
  border: none !important;
  font-weight: 600;
  transition: all 0.2s;
  border-radius: 6px !important;
}
.stButton > button:hover {
  background: var(--accent-secondary) !important;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

/* Form Elements */
.stCheckbox label {
  color: var(--text-primary) !important;
  font-weight: 500;
}
.stTextInput label, .stTextArea label, .stSelectbox label, .stSlider label, .stMultiSelect label {
  color: var(--text-primary) !important;
  font-weight: 600;
  margin-bottom: 0.5rem;
}
.stTextInput input, .stTextArea textarea, .stSelectbox select {
  background-color: var(--bg-secondary) !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--border-color) !important;
  border-radius: 6px !important;
}
.stTextInput input::placeholder, .stTextArea textarea::placeholder {
  color: var(--text-muted) !important;
}

/* Cards */
.card {
  border-radius: 12px;
  background: var(--bg-secondary) !important;
  padding: 1.25rem;
  box-shadow: 0 4px 12px var(--card-shadow);
  border: 1px solid var(--border-color);
  margin-bottom: 1.5rem;
  color: var(--text-primary) !important;
  line-height: 1.6;
}

.metric-card {
  border-radius: 12px;
  background: var(--bg-secondary) !important;
  padding: 1rem 1.25rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  border: 1px solid var(--border-color);
  text-align: center;
  color: var(--text-primary) !important;
}
.metric-card .metric-label {
  font-size: 0.9rem;
  color: var(--text-secondary);
  font-weight: 600;
  margin-bottom: 0.75rem;
  letter-spacing: 0.5px;
}
.metric-card .metric-value {
  font-size: 2rem;
  font-weight: 800;
  color: var(--accent-secondary);
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.small-card {
  border-radius: 10px;
  background: var(--bg-primary) !important;
  padding: 1rem;
  border: 1px solid var(--border-color);
  margin-bottom: 0.75rem;
  color: var(--text-primary) !important;
  line-height: 1.6;
}

/* Score Highlighting */
.score-high { color: var(--score-high) !important; }
.score-medium { color: var(--score-medium) !important; }
.score-low { color: var(--score-low) !important; }

/* Typography */
.section-title {
  font-size: 1.3rem;
  font-weight: 800;
  color: var(--text-primary) !important;
  margin-bottom: 1rem;
  letter-spacing: 0.3px;
}
.section-desc {
  font-size: 0.95rem;
  color: var(--text-secondary) !important;
  margin-top: 0.5rem;
  font-weight: 500;
}

/* Badges */
.badge {
  display: inline-block;
  border-radius: 6px;
  padding: 0.4rem 0.85rem;
  font-size: 0.85rem;
  color: var(--badge-text) !important;
  font-weight: 600;
  letter-spacing: 0.3px;
}
.badge-neutral { background: #475569; }
.badge-success { background: var(--score-high); }
.badge-warning { background: var(--score-medium); }
.badge-danger { background: var(--score-low); }

/* Header */
.top-header {
  background: var(--bg-secondary) !important;
  padding: 2rem 2.5rem;
  border-bottom: 1px solid var(--border-color);
  margin: -2rem -2.5rem 2rem;
}
.top-header h1 {
  margin: 0;
  font-size: 2rem;
  font-weight: 800;
  color: var(--text-primary) !important;
  letter-spacing: -0.5px;
}
.top-header p {
  margin: 0.75rem 0 0;
  font-size: 1rem;
  color: var(--text-secondary) !important;
  font-weight: 500;
}

/* Alerts */
.stInfo, .stSuccess, .stWarning, .stError {
  border-radius: 8px;
  padding: 1rem;
}
.stInfo {
  background-color: rgba(59, 130, 246, 0.1) !important;
  color: var(--text-primary) !important;
  border: 1px solid rgba(59, 130, 246, 0.3) !important;
}
.stSuccess {
  background-color: rgba(16, 185, 129, 0.1) !important;
  color: var(--text-primary) !important;
  border: 1px solid rgba(16, 185, 129, 0.3) !important;
}
.stWarning {
  background-color: rgba(245, 158, 11, 0.1) !important;
  color: var(--text-primary) !important;
  border: 1px solid rgba(245, 158, 11, 0.3) !important;
}
.stError {
  background-color: rgba(239, 68, 68, 0.1) !important;
  color: var(--text-primary) !important;
  border: 1px solid rgba(239, 68, 68, 0.3) !important;
}

/* Progress Bars */
.stProgressBar > div > div { background: var(--accent-secondary) !important; }

/* Headings */
h1, h2, h3, h4, h5, h6 {
  color: var(--text-primary) !important;
  font-weight: 800 !important;
  letter-spacing: -0.3px;
}

/* Spacing */
div[data-testid="stVerticalBlock"] > div:first-child .element-container:first-child {
  margin-bottom: 1.5rem;
}

/* Secondary buttons (sidebar navigation) */
.stButton > button[data-baseweb="button"][kind="secondary"] {
  background: transparent !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--border-color) !important;
}
.stButton > button[data-baseweb="button"][kind="secondary"]:hover {
  background: var(--bg-secondary) !important;
  color: var(--text-primary) !important;
  border-color: var(--accent-primary) !important;
}

/* Primary buttons (active navigation, theme toggle) */
.stButton > button[data-baseweb="button"][kind="primary"] {
  background: var(--accent-primary) !important;
  color: var(--bg-primary) !important;
  border: none !important;
}
.stButton > button[data-baseweb="button"][kind="primary"]:hover {
  background: var(--accent-secondary) !important;
}
</style>
"""


def initialize_state() -> None:
    if "results" not in st.session_state:
        st.session_state.results = []
    if "job_description" not in st.session_state:
        st.session_state.job_description = ""
    if "threshold" not in st.session_state:
        st.session_state.threshold = 70
    if "search_query" not in st.session_state:
        st.session_state.search_query = ""
    if "selected_skills" not in st.session_state:
        st.session_state.selected_skills = []
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False
    if "last_sync" not in st.session_state:
        st.session_state.last_sync = "Never"
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Dashboard"
    if "selected_candidate" not in st.session_state:
        st.session_state.selected_candidate = ""


def get_score_color_class(score: int) -> str:
    """Return CSS class for score highlighting."""
    if score >= 75:
        return "score-high"
    elif score >= 50:
        return "score-medium"
    else:
        return "score-low"


def clean_text(text: str) -> str:
    return " ".join(text.split())


def format_candidate(candidate: dict) -> dict:
    return {
        "name": candidate["name"],
        "score": candidate["score"],
        "rank": candidate["rank"],
        "skills": candidate["skills"],
        "text": candidate["text"],
        "shortlisted": candidate.get("shortlisted", False),
    }


def compute_summary(results: List[dict]) -> dict:
    total = len(results)
    average = round(sum(item["score"] for item in results) / total, 1) if total else 0
    highest = max((item["score"] for item in results), default=0)
    shortlisted = sum(1 for item in results if item.get("shortlisted", False))
    return {"total": total, "average": average, "highest": highest, "shortlisted": shortlisted}


def build_score_df(results: List[dict]) -> pd.DataFrame:
    df = pd.DataFrame([{"candidate": item["name"], "score": item["score"]} for item in results])
    return df.sort_values("score", ascending=False)


def build_skill_df(results: List[dict]) -> pd.DataFrame:
    skills = {}
    for candidate in results:
        for skill in candidate.get("skills", []):
            skills[skill] = skills.get(skill, 0) + 1
    data = [{"skill": skill, "count": count} for skill, count in sorted(skills.items(), key=lambda x: x[1], reverse=True)]
    return pd.DataFrame(data[:8])


def build_pie_df(results: List[dict]) -> pd.DataFrame:
    shortlisted = sum(1 for item in results if item.get("shortlisted", False))
    rejected = len(results) - shortlisted
    return pd.DataFrame({"status": ["Shortlisted", "Rejected"], "count": [shortlisted, rejected]})


def compute_skill_gap(results: List[dict], job_skills: List[str]) -> dict:
    total_matched = 0
    total_missing = 0
    all_matched = set()
    all_missing = set()
    for candidate in results:
        matched = set(candidate["skills"]) & set(job_skills)
        missing = set(job_skills) - set(candidate["skills"])
        total_matched += len(matched)
        total_missing += len(missing)
        all_matched.update(matched)
        all_missing.update(missing)
    return {
        "total_matched": total_matched,
        "total_missing": total_missing,
        "unique_matched": sorted(all_matched),
        "unique_missing": sorted(all_missing),
    }


def compute_review(candidate: dict, job_skills: List[str]) -> dict:
    matched = sorted(set(candidate["skills"]) & set(job_skills)) if job_skills else []
    missing = sorted(set(job_skills) - set(candidate["skills"])) if job_skills else []
    years = extract_experience_years(candidate["text"])
    experience_score = min(100, years * 12)
    education_score = extract_education_score(candidate["text"])
    grammar_score = 90 if len(candidate["text"]) < 2500 else 80
    formatting_score = 85 if "-" in candidate["text"] else 70
    fit_score = round((len(matched) * 4 + experience_score * 0.3 + education_score * 0.2 + grammar_score * 0.1) / 5)
    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "skill_match": len(matched) * 10 if job_skills else 0,
        "experience": experience_score,
        "education": education_score,
        "grammar": grammar_score,
        "formatting": formatting_score,
        "fit_score": min(fit_score, 100),
    }


def extract_experience_years(text: str) -> int:
    matches = re.findall(r"(\d+)\+?\s*(?:years|yrs|year)", text.lower())
    if matches:
        return min(15, max(int(value) for value in matches))
    return 2


def extract_education_score(text: str) -> int:
    text_lower = text.lower()
    if "phd" in text_lower or "doctor" in text_lower:
        return 100
    if "master" in text_lower or "mba" in text_lower:
        return 85
    if "bachelor" in text_lower or "ba" in text_lower or "bs" in text_lower:
        return 70
    return 55


def highlight_keywords(text: str, keywords: List[str]) -> str:
    highlighted = text
    for keyword in sorted(keywords, key=len, reverse=True):
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        highlighted = pattern.sub(f"**{keyword}**", highlighted)
    return highlighted


def export_to_csv(results: List[dict]) -> bytes:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Rank",
        "Candidate",
        "Score",
        "Skill Score",
        "Semantic Similarity",
        "Skills",
        "Matched Skills",
        "Missing Skills",
        "Shortlisted",
    ])
    for candidate in results:
        writer.writerow([
            candidate["rank"],
            candidate["name"],
            candidate["score"],
            candidate.get("skill_score", 0),
            candidate.get("similarity_score", 0),
            ", ".join(candidate["skills"]),
            ", ".join(candidate.get("matched_skills", [])),
            ", ".join(candidate.get("missing_skills", [])),
            "Yes" if candidate.get("shortlisted", False) else "No",
        ])
    return output.getvalue().encode("utf-8")


def render_dashboard_page() -> None:
    summary = compute_summary(st.session_state.results)

    # Metrics Row with improved layout
    with st.container():
        st.markdown("<div class='section-title'>Overview</div>", unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

        metric_cols = st.columns(4, gap="medium")
        metrics = [
            ("Total Resumes", summary["total"]),
            ("Average Score", f"{summary['average']}%"),
            ("Highest Score", f"{summary['highest']}%"),
            ("Shortlisted", summary["shortlisted"]),
        ]
        for col, (label, value) in zip(metric_cols, metrics):
            with col:
                st.markdown(
                    f"<div class='metric-card'>"
                    f"<div class='metric-label'>{label}</div>"
                    f"<div class='metric-value'>{value}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

    # Charts Section with improved layout
    if summary["total"] > 0:
        with st.container():
            st.markdown("<div class='section-title'>Analysis Overview</div>", unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

            chart_cols = st.columns(3, gap="large")

            with chart_cols[0]:
                with st.container():
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    st.markdown("<div class='section-title' style='margin: 0; font-size: 1.05rem;'>Candidate Scores</div>", unsafe_allow_html=True)
                    score_df = build_score_df(st.session_state.results)
                    score_chart = alt.Chart(score_df).mark_bar().encode(
                        x=alt.X("candidate:N", title=None, sort=alt.EncodingSortField(field="score", order="descending")),
                        y=alt.Y("score:Q", title="Score (%)", scale=alt.Scale(domain=[0, 100])),
                        tooltip=[alt.Tooltip("candidate:N", title="Candidate"), alt.Tooltip("score:Q", title="Score")]
                    ).properties(height=280)
                    st.altair_chart(score_chart, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)

            with chart_cols[1]:
                with st.container():
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    st.markdown("<div class='section-title' style='margin: 0; font-size: 1.05rem;'>Shortlist Status</div>", unsafe_allow_html=True)
                    pie_df = build_pie_df(st.session_state.results)
                    pie_chart = alt.Chart(pie_df).mark_arc(innerRadius=50).encode(
                        theta=alt.Theta("count:Q"),
                        color=alt.Color("status:N", scale=alt.Scale(domain=["Shortlisted", "Rejected"], range=["#10b981", "#ef4444"])),
                        tooltip=[alt.Tooltip("status:N"), alt.Tooltip("count:Q")]
                    ).properties(height=280)
                    st.altair_chart(pie_chart, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)

            with chart_cols[2]:
                with st.container():
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    st.markdown("<div class='section-title' style='margin: 0; font-size: 1.05rem;'>Top Skills</div>", unsafe_allow_html=True)
                    skill_df = build_skill_df(st.session_state.results)
                    if not skill_df.empty:
                        skill_chart = alt.Chart(skill_df).mark_bar().encode(
                            y=alt.Y("skill:N", sort="-x", title=None),
                            x=alt.X("count:Q", title="Count"),
                            tooltip=[alt.Tooltip("skill:N", title="Skill"), alt.Tooltip("count:Q", title="Count")]
                        ).properties(height=280)
                        st.altair_chart(skill_chart, use_container_width=True)
                    else:
                        st.info("Skills appear after analysis")
                    st.markdown("</div>", unsafe_allow_html=True)

        # Top candidates highlight
        with st.container():
            st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>Top Candidates</div>", unsafe_allow_html=True)
            top_candidates = st.session_state.results[:5]
            if top_candidates:
                top_cols = st.columns(len(top_candidates), gap="large")
                for col, candidate in zip(top_cols, top_candidates):
                    with col:
                        score_class = get_score_color_class(candidate['score'])
                        st.markdown(
                            f"<div class='small-card'><strong>{candidate['name']}</strong>"
                            f"<div style='margin-top:0.5rem; font-size:1.5rem; font-weight:700;' class='{score_class}'>{candidate['score']}%</div>"
                            f"<div style='margin-top:0.5rem; color: var(--text-secondary); font-size:0.85rem;'>Skills {len(candidate.get('matched_skills', []))} / {len(extract_skills(st.session_state.job_description))}</div>"
                            f"</div>",
                            unsafe_allow_html=True,
                        )
            else:
                st.info("No ranked candidates available yet.")

    # Skill Gap Analysis with improved layout
    if st.session_state.results and st.session_state.job_description:
        with st.container():
            st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>Skill Gap Analysis</div>", unsafe_allow_html=True)

            job_skills = extract_skills(st.session_state.job_description)
            gap = compute_skill_gap(st.session_state.results, job_skills)

            gap_cols = st.columns(2, gap="large")
            with gap_cols[0]:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("<div class='section-title' style='margin: 0; font-size: 1.05rem;'>Matched Skills</div>", unsafe_allow_html=True)
                st.write(f"Total matches: {gap['total_matched']}")
                st.write(", ".join(gap['unique_matched']) if gap['unique_matched'] else "None")
                st.markdown("</div>", unsafe_allow_html=True)

            with gap_cols[1]:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("<div class='section-title' style='margin: 0; font-size: 1.05rem;'>Missing Skills</div>", unsafe_allow_html=True)
                st.write(f"Total gaps: {gap['total_missing']}")
                st.write(", ".join(gap['unique_missing']) if gap['unique_missing'] else "None")
                st.markdown("</div>", unsafe_allow_html=True)


def render_upload_page() -> None:
    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Upload & Analyze Resumes</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-desc'>Upload resumes and job descriptions for instant ATS scoring</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Select Resume Files (PDF or DOCX)",
        type=["pdf", "docx"],
        accept_multiple_files=True,
        help="Upload one or more resume files for analysis.",
    )

    if uploaded_files:
        st.markdown("<div class='small-card'>", unsafe_allow_html=True)
        st.write(f"{len(uploaded_files)} file(s) selected")
        for file in uploaded_files:
            st.write(f"  • {file.name}")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

    st.session_state.job_description = st.text_area(
        "Job Description",
        value=st.session_state.job_description,
        height=180,
        placeholder="Paste the job description here...",
    )

    if st.session_state.job_description.strip():
        job_skills = extract_skills(st.session_state.job_description)
        st.markdown("<div class='small-card'>", unsafe_allow_html=True)
        st.markdown("<strong>Extracted Keywords:</strong>")
        st.write(", ".join(job_skills) if job_skills else "No clear keywords detected.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 3])
    with col1:
        analyze_btn = st.button("Analyze", type="primary", use_container_width=True)
    
    if analyze_btn:
        if not uploaded_files:
            st.warning("Please upload at least one resume.")
        elif not st.session_state.job_description.strip():
            st.warning("Please enter a job description.")
        else:
            with st.spinner("Analyzing resumes..."):
                candidates = []
                for resume_file in uploaded_files:
                    try:
                        text = extract_text(resume_file)
                        skills = extract_skills(text)
                        # Use improved weighted ATS scoring
                        score_float, skill_score, similarity_score, matched_skills, missing_skills = compute_weighted_ats_score(
                            text, st.session_state.job_description, SKILL_KEYWORDS
                        )
                        score = int(score_float)
                        candidates.append({
                            "name": resume_file.name,
                            "text": clean_text(text),
                            "skills": skills,
                            "score": score,
                            "skill_score": skill_score,
                            "similarity_score": similarity_score,
                            "rank": 0,
                            "shortlisted": False,
                            "matched_skills": matched_skills,
                            "missing_skills": missing_skills,
                        })
                    except Exception as exc:
                        st.error(f"Failed to parse {resume_file.name}: {exc}")
                st.session_state.results = rank_candidates(candidates)
                st.session_state.last_sync = "Just now"
            st.success("Analysis complete!")

    if st.session_state.results:
        with st.container():
            st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>Analysis Results Preview</div>", unsafe_allow_html=True)

            preview_cols = st.columns(3, gap="large")
            for idx, candidate in enumerate(st.session_state.results[:3]):
                with preview_cols[idx]:
                    score_class = get_score_color_class(candidate['score'])
                    st.markdown(
                        f"<div class='small-card'><strong>{candidate['name']}</strong>"
                        f"<div style='margin-top:0.5rem;'><span style='font-size:1.4rem; font-weight:700;' class='{score_class}'>{candidate['score']}%</span></div>"
                        f"<div style='margin-top:0.5rem; color: var(--text-secondary); font-size:0.9rem;'>Rank #{candidate['rank']}</div>"
                        f"<div style='margin-top:0.75rem; font-size:0.85rem;'>{', '.join(candidate['skills'][:2]) or 'No skills'}</div></div>",
                        unsafe_allow_html=True,
                    )


def render_rankings_page() -> None:
    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Candidate Rankings</div>", unsafe_allow_html=True)

    if not st.session_state.results:
        st.info("No analysis results. Run Upload & Analyze first.")
        return

    # Export button
    csv_data = export_to_csv(st.session_state.results)
    col1, col2 = st.columns([1, 3])
    with col1:
        st.download_button("Export CSV", csv_data, "rankings.csv", "text/csv", type="primary", use_container_width=True)

    # Filters Row
    filter_cols = st.columns([2, 2, 2], gap="medium")
    with filter_cols[0]:
        st.session_state.search_query = st.text_input("Search", value=st.session_state.search_query, placeholder="Name or skill...")
    with filter_cols[1]:
        min_score = st.slider("Min Score", min_value=0, max_value=100, value=0, step=5)
    with filter_cols[2]:
        skill_options = sorted({skill for candidate in st.session_state.results for skill in candidate["skills"]})
        st.session_state.selected_skills = st.multiselect("Skills", skill_options, default=st.session_state.selected_skills)
    
    sort_col = st.columns([1, 1, 1, 1])
    with sort_col[0]:
        sort_option = st.selectbox("Sort", ["Rank", "Score", "Name"], index=0)
    
    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

    # Filter logic
    filtered = [
        candidate
        for candidate in st.session_state.results
        if candidate["score"] >= min_score
        and (
            not st.session_state.search_query
            or st.session_state.search_query.lower() in candidate["name"].lower()
            or any(st.session_state.search_query.lower() in skill.lower() for skill in candidate["skills"])
        )
        and (not st.session_state.selected_skills or set(st.session_state.selected_skills).issubset(candidate["skills"]))
    ]

    if sort_option == "Score":
        filtered.sort(key=lambda item: item["score"], reverse=True)
    elif sort_option == "Name":
        filtered.sort(key=lambda item: item["name"].lower())
    else:
        filtered.sort(key=lambda item: item["rank"])

    if not filtered:
        st.warning("No candidates match filters.")
        return

    # Candidates List
    for candidate in filtered:
        with st.container():
            status_class = "badge-success" if candidate.get("shortlisted") else "badge-neutral"
            score_class = get_score_color_class(candidate['score'])
            st.markdown("<div class='card'>", unsafe_allow_html=True)

            # Header Row
            header_cols = st.columns([2, 1, 0.8])
            with header_cols[0]:
                st.markdown(f"<strong style='font-size: 1.05rem;'>{candidate['name']}</strong>", unsafe_allow_html=True)
                st.markdown(f"<div style='color: var(--text-secondary); font-size: 0.9rem;'>Rank {candidate['rank']} • <span class='{score_class}'>Score {candidate['score']}%</span></div>", unsafe_allow_html=True)
            with header_cols[1]:
                st.markdown("")
            with header_cols[2]:
                st.markdown(f"<span class='badge {status_class}'>{'Shortlisted' if candidate.get('shortlisted') else 'Pending'}</span>", unsafe_allow_html=True)

            st.markdown("<div style='margin-top: 0.75rem;'></div>", unsafe_allow_html=True)

            # Skills Row
            st.markdown(f"<div style='color: var(--text-secondary); font-size: 0.9rem;'>Skills: {', '.join(candidate['skills']) or 'None'}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='color: var(--text-secondary); font-size: 0.9rem; margin-top: 0.5rem;'>{candidate['text'][:100]}...</div>", unsafe_allow_html=True)

            st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

            # Progress Bar
            progress_val = candidate["score"] / 100
            st.progress(progress_val)

            st.markdown("<div style='margin-top: 0.75rem;'></div>", unsafe_allow_html=True)

            # Action Buttons
            action_cols = st.columns([1, 1, 2])
            with action_cols[0]:
                if st.button("View Details", key=f"view_{candidate['name']}", help="View full details"):
                    st.session_state.selected_candidate = candidate['name']
                    st.session_state.current_page = "Candidate Insights"
                    st.rerun()
            with action_cols[1]:
                shortlisted_value = st.checkbox("Shortlist", value=candidate.get("shortlisted", False), key=f"short_{candidate['name']}")
                candidate["shortlisted"] = shortlisted_value

            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)


def render_shortlisted_page() -> None:
    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Shortlisted Candidates</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-desc'>Your selected candidates for final review</div>", unsafe_allow_html=True)

    shortlisted = [candidate for candidate in st.session_state.results if candidate.get("shortlisted")]
    if not shortlisted:
        st.info("No shortlisted candidates yet.")
        return

    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

    # Export button
    csv_data = export_to_csv(shortlisted)
    col1, col2 = st.columns([1, 3])
    with col1:
        st.download_button("Export CSV", csv_data, "shortlist.csv", "text/csv", type="primary", use_container_width=True)

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # Compare section
    compare_names = st.multiselect("Compare Candidates", [c["name"] for c in shortlisted], max_selections=3)
    if compare_names:
        with st.container():
            st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
            compare_list = [c for c in shortlisted if c["name"] in compare_names]
            compare_cols = st.columns(len(compare_list), gap="large")
            for col, candidate in zip(compare_cols, compare_list):
                with col:
                    score_class = get_score_color_class(candidate['score'])
                    st.markdown(
                        f"<div class='small-card'><strong>{candidate['name']}</strong>"
                        f"<div style='margin-top:0.75rem; font-size:1.3rem; font-weight:700;' class='{score_class}'>{candidate['score']}%</div>"
                        f"<div style='margin-top:0.5rem; color: var(--text-secondary); font-size:0.9rem;'>Rank #{candidate['rank']}</div>"
                        f"<div style='margin-top:0.75rem; font-size:0.85rem;'>{', '.join(candidate['skills'][:2]) or 'None'}</div></div>",
                        unsafe_allow_html=True,
                    )
            st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # Candidates list
    for candidate in shortlisted:
        with st.container():
            score_class = get_score_color_class(candidate['score'])
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            header_cols = st.columns([2, 1])
            with header_cols[0]:
                st.markdown(f"<strong style='font-size: 1.1rem;'>{candidate['name']}</strong>", unsafe_allow_html=True)
                st.markdown(f"<div style='color: var(--text-secondary); font-size: 0.9rem;'>Rank {candidate['rank']} • <span class='{score_class}'>Score {candidate['score']}%</span></div>", unsafe_allow_html=True)
            with header_cols[1]:
                st.markdown("<span class='badge badge-success'>Selected</span>", unsafe_allow_html=True)

            st.markdown("<div style='margin-top: 0.75rem;'></div>", unsafe_allow_html=True)
            st.markdown(f"<div style='color: var(--text-secondary); font-size: 0.9rem;'>Skills: {', '.join(candidate['skills']) or 'No skills'}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)


def render_insights_page() -> None:
    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Candidate Insights</div>", unsafe_allow_html=True)

    if not st.session_state.results:
        st.info("Analyze candidates first to see insights.")
        return

    candidate_names = [candidate["name"] for candidate in st.session_state.results]
    selected_name = st.selectbox("Select Candidate", candidate_names)
    selected_candidate = next((c for c in st.session_state.results if c["name"] == selected_name), None)
    if not selected_candidate:
        return

    # Score breakdown
    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title' style='font-size: 1.1rem;'>Score Breakdown</div>", unsafe_allow_html=True)
    score_cols = st.columns(4, gap="medium")
    skill_score = selected_candidate.get("skill_score", 0)
    similarity_score = selected_candidate.get("similarity_score", 0)
    score_cols[0].metric("Skill Relevance", f"{skill_score}%")
    score_cols[1].metric("Semantic Fit", f"{similarity_score}%")
    score_cols[2].metric("Overall ATS", f"{selected_candidate['score']}%")
    score_cols[3].metric("Rank", f"#{selected_candidate['rank']}")

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # Skills section
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title' style='margin: 0; font-size: 1.05rem;'>Skill Analysis</div>", unsafe_allow_html=True)
    skill_cols = st.columns(2, gap="medium")
    with skill_cols[0]:
        st.markdown(f"<div style='color: var(--text-secondary); font-size: 0.9rem;'><strong>Matched Skills:</strong></div>", unsafe_allow_html=True)
        st.write(", ".join(selected_candidate.get("matched_skills", [])) if selected_candidate.get("matched_skills") else "None")
    with skill_cols[1]:
        st.markdown(f"<div style='color: var(--text-secondary); font-size: 0.9rem;'><strong>Missing Skills:</strong></div>", unsafe_allow_html=True)
        st.write(", ".join(selected_candidate.get("missing_skills", [])) if selected_candidate.get("missing_skills") else "None")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title' style='margin: 0; font-size: 1.05rem;'>Recommended Improvements</div>", unsafe_allow_html=True)
    if selected_candidate.get("missing_skills"):
        st.write(
            "Focus on these missing skills to improve fit: "
            + ", ".join(selected_candidate.get("missing_skills", [])[:5])
        )
    else:
        st.write("Strong skill alignment. Candidate is a good match for the current job profile.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # Extracted skills
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title' style='margin: 0; font-size: 1.05rem;'>Extracted Skills</div>", unsafe_allow_html=True)
    st.write(", ".join(selected_candidate["skills"]) if selected_candidate["skills"] else "No skills extracted")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # Full resume text
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title' style='margin: 0; font-size: 1.05rem;'>Full Resume Text</div>", unsafe_allow_html=True)
    st.text_area("Resume Content", value=selected_candidate['text'], height=300, disabled=True)
    st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    st.set_page_config(page_title="AI Resume Screening Dashboard", page_icon="📄", layout="wide")
    initialize_state()
    
    # Apply theme
    theme_css = THEME_CSS_DARK if st.session_state.dark_mode else THEME_CSS_LIGHT
    st.markdown(theme_css, unsafe_allow_html=True)

    with st.sidebar:
        # Logo Section
        st.markdown(
            "<div style='text-align: center; padding: 1.5rem 0; border-bottom: 1px solid var(--border-color); margin-bottom: 1rem;'>"
            "<h1 style='margin: 0; font-size: 1.5rem; color: var(--accent-primary);'>ATS Pro</h1>"
            "<p style='margin: 0.5rem 0 0; font-size: 0.85rem; color: var(--text-secondary);'>AI Resume Screener</p>"
            "</div>",
            unsafe_allow_html=True
        )
        
        # Theme Toggle
        if st.button("Dark Mode" if not st.session_state.dark_mode else "Light Mode", 
                     key="theme_toggle", use_container_width=True):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
        
        st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
        st.markdown("<div style='height: 1px; background: var(--border-color); margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
        
        # Navigation
        st.markdown(
            "<div style='font-size: 0.8rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px;'>Navigation</div>",
            unsafe_allow_html=True
        )
        
        pages = ["Dashboard", "Upload & Analyze", "Candidate Rankings", "Shortlisted Candidates", "Candidate Insights"]
        
        for page_name in pages:
            is_active = st.session_state.current_page == page_name
            button_style = "primary" if is_active else "secondary"
            
            if st.button(
                f"{page_name}",
                key=f"nav_{page_name}",
                use_container_width=True,
                type=button_style,
                help=f"Go to {page_name}"
            ):
                st.session_state.current_page = page_name
                st.rerun()
        
        st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
        st.markdown("<div style='height: 1px; background: var(--border-color); margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
        
        st.markdown(
            "<div style='padding: 1rem 0; text-align: center; font-size: 0.75rem; color: var(--text-secondary);'>"
            "<p style='margin: 0;'>Professional ATS Dashboard</p>"
            "<p style='margin: 0.25rem 0 0;'>AI-Powered Screening</p>"
            "</div>",
            unsafe_allow_html=True
        )

    # Top Header
    page = st.session_state.current_page
    st.markdown(
        f"<div class='top-header'>"
        f"<h1>{page}</h1>"
        f"<p>AI-powered resume screening and candidate analytics</p>"
        f"</div>",
        unsafe_allow_html=True
    )

    # Page Routing
    if page == "Dashboard":
        render_dashboard_page()
    elif page == "Upload & Analyze":
        render_upload_page()
    elif page == "Candidate Rankings":
        render_rankings_page()
    elif page == "Shortlisted Candidates":
        render_shortlisted_page()
    elif page == "Candidate Insights":
        render_insights_page()


if __name__ == "__main__":
    main()
