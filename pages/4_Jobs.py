
import streamlit as st
import sys
import os

# Allow imports from the project root.
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

from employment.matching import match_jobs, load_jobs
from ui.theme import apply_theme, section_title

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Career Navigator - Jobs",
    page_icon="💼",
    layout="wide",
)

apply_theme()

# ============================================================
# PAGE HEADER
# ============================================================

st.markdown(
    """
    <div class="fg-hero fg-rise"
         style="padding:34px 38px; margin-bottom:24px;">
        <div class="fg-eyebrow">✦ Opportunity Finder</div>
        <h1 style="font-size:clamp(30px,3.6vw,46px);">
            Jobs & internships
            <span class="fg-gradient-text">matched to you</span>.
        </h1>
        <p style="font-size:15.5px;">
            Ranked by skill fit, with missing skills highlighted so you
            know exactly what to learn next.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# GET SAVED PROFILE
# ============================================================

profile = st.session_state.get("profile", {})

if not isinstance(profile, dict):
    profile = {}

skills = profile.get("skills") or []
career_id = profile.get("target_career")
career_name = profile.get("target_career_name")

# Validate skills.
if not isinstance(skills, list):
    skills = []

skills = [
    skill.strip()
    for skill in skills
    if isinstance(skill, str) and skill.strip()
]

# ============================================================
# FILTER
# ============================================================

job_type_filter = st.radio(
    "Show:",
    options=["All", "Job", "Internship"],
    horizontal=True,
)

section_title("Results", "📋")

# ============================================================
# VALIDATE PROFILE BEFORE MATCHING
# ============================================================

if not skills:
    st.info(
        "Add your skills on the Profile page to get personalized job matches."
    )

elif not career_id:
    st.info(
        "Choose a target career on the Profile page and save your profile "
        "to see personalized job matches."
    )

else:
    # Find jobs based on the saved skills and target career.
    results = match_jobs(skills, career_id)

    # Load job types for filtering.
    all_jobs = load_jobs()

    type_lookup = {
        (job.get("title"), job.get("company")):
        str(job.get("type", "job")).strip().lower()
        for job in all_jobs
    }

    filtered_results = []

    for job in results:
        job_type = type_lookup.get(
            (job["title"], job["company"]),
            "job",
        )

        if job_type_filter == "Job" and job_type != "job":
            continue

        if job_type_filter == "Internship" and job_type != "internship":
            continue

        filtered_results.append((job, job_type))

    # ========================================================
    # DISPLAY RESULTS
    # ========================================================

    if not filtered_results:
        st.info("No opportunities found for the selected filter.")

    else:
        if not career_name:
            career_name = career_id.replace("_", " ").title()

        st.caption(
            f"Matching opportunities for your target career: "
            f"**{career_name}**"
        )

        for job, job_type in filtered_results:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.subheader(job["title"])

                    st.caption(
                        f"{job['company']} • {job_type.capitalize()}"
                    )

                with col2:
                    st.metric(
                        "Match",
                        f"{job['match_pct']}%",
                    )

                missing_skills = job.get("missing", [])

                if missing_skills:
                    st.write(
                        "**Missing skills:** "
                        + ", ".join(missing_skills)
                    )
                else:
                    st.success("All required skills matched!")
