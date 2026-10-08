import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from employment.resume import generate_resume, analyze_resume
from core.state import init_state
from ui.theme import apply_theme, section_title

st.set_page_config(
    page_title="AI Career Navigator - Resume",
    page_icon="📄",
    layout="wide",
)
apply_theme()

st.markdown(
    """
    <div class="fg-hero fg-rise" style="padding:34px 38px; margin-bottom:24px;">
        <div class="fg-eyebrow">✦ Resume Studio</div>
        <h1 style="font-size:clamp(30px,3.6vw,46px);">Build a resume that <span class="fg-gradient-text">gets noticed</span>.</h1>
        <p style="font-size:15.5px;">
            Add projects, generate a clean ATS-friendly resume, and get
            suggestions to make it stronger.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------
# Build the resume from the REAL profile saved on the Profile page.
# (Previously this used a hardcoded test profile, so it always showed
# "Priya Sharma" instead of the name the student saved.)
# -----------------------------------------------------------------------
init_state()

user_profile = st.session_state.get("profile", {})

# A resume needs the student's real name — ask them to complete the
# Profile page if they haven't yet.
if not user_profile.get("name"):
    st.warning(
        "Complete your Profile page first. Your resume will then use "
        "the name, email, skills and projects you saved there."
    )
    st.stop()


def _as_project(p):
    """The Profile page stores projects as plain strings, while the
    Resume form stores {title, description} dicts. Normalize everything
    to dicts so the resume generator always gets what it expects."""
    if isinstance(p, str):
        return {"title": p, "description": ""}
    return {
        "title": p.get("title", "Project"),
        "description": p.get("description", ""),
    }


# Projects added here on the Resume page are kept in their own list so
# the shared Profile data stays untouched; they're merged in for the
# resume view only.
if "resume_extra_projects" not in st.session_state:
    st.session_state["resume_extra_projects"] = []

resume_profile = {
    "name": user_profile.get("name", ""),
    "email": user_profile.get("email", ""),
    "degree": user_profile.get("degree", ""),
    "branch": user_profile.get("branch", ""),
    "grad_year": user_profile.get("grad_year", ""),
    "skills": user_profile.get("skills", []),
    "projects": [_as_project(p) for p in user_profile.get("projects", [])]
    + st.session_state["resume_extra_projects"],
    "experience": user_profile.get("experience", "Fresher"),
}

# Use the student's chosen target career if they set one on the
# Careers/Profile page; otherwise fall back to the default.
career_id = user_profile.get("target_career") or "data_analyst"

# Keep the session key in sync for any other modules that read it.
st.session_state.resume_profile = resume_profile

profile = st.session_state.resume_profile

st.caption(
    f"📄 Built from your Profile: **{profile['name']}** • "
    f"{profile['email'] or 'no email yet'} • "
    f"{len(profile['skills'])} skills • "
    f"{len(profile['projects'])} projects"
)

st.subheader("Add a Project")
with st.form("project_form", clear_on_submit=True):
    proj_title = st.text_input("Project Title")
    proj_desc = st.text_area("Project Description")
    submitted = st.form_submit_button("Add Project")
    if submitted and proj_title:
        st.session_state["resume_extra_projects"].append(
            {"title": proj_title, "description": proj_desc}
        )
        # Force a fresh preview so the new project shows up.
        st.session_state["resume_generated"] = False
        st.success(f"Added project: {proj_title}")

if profile["projects"]:
    st.write("**Current projects:**")
    for p in profile["projects"]:
        st.write(f"- {p['title']}: {p['description']}")

# -----------------------------------------------------------------------
# The preview is regenerated fresh on every run from the current
# profile, so an outdated "Priya Sharma" preview can never linger.
# generate_resume() is just local HTML rendering, so this is cheap.
# -----------------------------------------------------------------------
resume_html = generate_resume(profile, career_id)
st.session_state["resume_html"] = resume_html
st.session_state["resume_generated"] = True

st.subheader("Preview")
st.iframe(st.session_state["resume_html"], height=500)

st.download_button(
    label="Download Resume (HTML)",
    data=st.session_state["resume_html"],
    file_name="resume.html",
    mime="text/html"
)

st.subheader("Suggestions")
suggestions = analyze_resume(profile, career_id)
if suggestions:
    for s in suggestions:
        st.write(f"- {s['suggestion']}")
else:
    st.write("No suggestions right now — either you're fully matched, or career data isn't loaded yet.")
