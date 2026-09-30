import streamlit as st
import sys
import os

# So this page can import from the employment/ folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from employment.matching import match_jobs
from ui.theme import apply_theme, section_title

st.set_page_config(
    page_title="AI Career Navigator - Jobs",
    page_icon="💼",
    layout="wide",
)
apply_theme()

st.markdown(
    """
    <div class="fg-hero fg-rise" style="padding:34px 38px; margin-bottom:24px;">
        <div class="fg-eyebrow">✦ Opportunity Finder</div>
        <h1 style="font-size:clamp(30px,3.6vw,46px);">Jobs & internships <span class="fg-gradient-text">matched to you</span>.</h1>
        <p style="font-size:15.5px;">
            Ranked by skill fit, with missing skills highlighted so you
            know exactly what to learn next.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Temporary hardcoded profile for testing (Step 8 will connect real state) ---
skills = ["Python", "SQL", "Excel"]
career_id = "data_analyst"
# ---------------------------------------------------------------------------

job_type_filter = st.radio(
    "Show:",
    options=["All", "Job", "Internship"],
    horizontal=True
)

results = match_jobs(skills, career_id)

section_title("Results", "📋")

# We need job "type" for filtering, but match_jobs() doesn't return it yet.
# Quick fix: re-load jobs here just to filter by type using title+company as the key.
from employment.matching import load_jobs
all_jobs = load_jobs()
type_lookup = {(j["title"], j["company"]): j["type"] for j in all_jobs}

for job in results:
    job_type = type_lookup.get((job["title"], job["company"]), "job")

    if job_type_filter == "Job" and job_type != "job":
        continue
    if job_type_filter == "Internship" and job_type != "internship":
        continue

    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(job["title"])
            st.caption(f"{job['company']} • {job_type.capitalize()}")
        with col2:
            st.metric("Match", f"{job['match_pct']}%")

        if job["missing"]:
            st.write("**Missing skills:** " + ", ".join(job["missing"]))
        else:
            st.success("All required skills matched!")